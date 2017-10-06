import logging
import json
import os
import subprocess
import ntpath
from copy import copy
import tempfile

# Import our dependencies
import vendored
import jsonschema
import boto3
import magic

from snappy import response
from snappy.settings import TRANSFORMATIONS_SCHEMA, PARAM_ALIASES, LOSSY_IMAGE_FMTS, BUCKET
from snappy.utils import rnd_str, base64_encode
from snappy.s3 import get_s3_obj


# Set up the default logger
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
LOG.info('Loading Lambda Function...')

# Set boto logging to INFO
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.INFO)


class InvalidParamsError(Exception):
    pass


def image_transform(filename, operations):
    """
    Transform the image specified by `filename` using the transformations specified by `operations`
    Returns
    -------
    str
        the filename of the transformed image
    """

    args = ['convert', filename]

    basename = ntpath.basename(filename)
    name, ext = os.path.splitext(basename)
    ext = ext.strip('.')

    if 'w' in operations and 'h' in operations:
        resize = (operations['w'], operations['h'])
        new_size = '{}x{}'.format(*resize)
        args.extend(['-resize', new_size])
        if 'fit' in operations:
            if operations['fit'] == 'clip':
                #
                # ignore the aspect ratio and distort the image so it always
                # generates an image exactly the size specified
                #
                args[-1] += '!'
            elif operations['fit'] == 'crop':
                #
                # `^` is used to resize the image based on the smallest fitting dimension
                # then `-extents` crops exactly the image to the size specified from the center
                #
                args[-1] += '^'
                args.extend(['-gravity', 'center', '-extent', new_size])
            elif operations['fit'] == 'bounds':
                #
                # by default `-resize` will fit the image into the requested size
                # and keep the original aspect ratio
                #
                pass
        else:
            #
            #  default behaviour is to force scaling to the specificed bounds
            #  which is the same behaviour as `fit=clip`
            #
            new_ops = copy(operations)
            new_ops.update({'fit': 'clip'})
            return image_transform(filename, new_ops)

    #
    # if only `w` or `h` is provided, then we scale target side
    # to the specified value, and keep the aspect ratio.
    # `fit` does not apply when only one side is given.
    #
    elif 'w' in operations:
        new_size = '{}x'.format(operations['w'])
        args.extend(['-resize', new_size])
    elif 'h' in operations:
        new_size = 'x{}'.format(operations['h'])
        args.extend(['-resize', new_size])

    if 'auto' in operations and operations['auto'] == 'compress':
        #
        # removes any image profile attached to the image
        #
        args.append('-strip')

    if 'fm' in operations:
        #
        # just use the format as filename extension,
        # then IM will handle conversion automatically
        #
        ext = operations['fm']

    if 'q' in operations:
        q = str(operations['q'])
        if ext in LOSSY_IMAGE_FMTS or 'fm' in operations:
            args.extend(['-quality', q])

    if 'dpr' in operations:
        dpr = str(operations['dpr'])
        # TODO: use `-density` or `-resample` ?

    code, path = tempfile.mkstemp()
    output = path + '.' + ext
    args.append(output)
    LOG.debug('args: {}'.format(args))
    im_result = subprocess.check_output(args)
    LOG.debug('IM output: {}'.format(im_result.decode()))

    return output


def normalize_params(params):

    norm_params = {}

    for k, v in params.items():
        #
        # convert all keys into lower case
        #
        key = k.lower()

        #
        # convert all str values into lower case
        #
        value = v
        if type(v) == str:
            value = v.lower()

        #
        # convert full named keys into aliases
        #

        if key in PARAM_ALIASES:
            key = PARAM_ALIASES[key]

        norm_params[key] = value

    return norm_params


def param_validation(params):
    """
    Normalize and validate the params.
    it silently removes the invalid or not supported operations.
    Returns
    -------
    dict
        the validated and normalized params
    """
    if any(params):

        norm_params = normalize_params(params)

        tmp_params = copy(norm_params)

        #
        # convert all values to the expected type,
        # as all params comes from the query string
        #
        properties = TRANSFORMATIONS_SCHEMA['properties']
        for k, v in tmp_params.items():
            if k in properties and 'type' in properties[k]:
                try:

                    k_type = properties[k]['type']
                    if k_type == 'integer':
                        norm_params[k] = int(v)
                    elif k_type == 'number':
                        norm_params[k] = float(v)
                except ValueError:
                    LOG.warning('Cannot convert to {} to {}'.format(v, k_type))
                    norm_params.pop(k)

        #
        # validate logic of certain operations altogether
        #
        tmp_params = copy(norm_params)

        for k, v in tmp_params.items():
            try:
                item = {k: v}
                jsonschema.validate(item, TRANSFORMATIONS_SCHEMA)
            except jsonschema.ValidationError as ve:
                LOG.warning('Error validating schema for {}'.format(item))
                norm_params.pop(k)

        if 'fit' in norm_params and not ('w' in norm_params or 'h' in norm_params):
            LOG.warning('`fit` is valid only for resize operations')
            norm_params.pop('fit')

        if 'q' in norm_params and 'fm' in norm_params and norm_params['fm'] not in LOSSY_IMAGE_FMTS:
            LOG.warning(
                'Cannot set `quality` with non-lossy formats: {}'.format(norm_params['fm']))
            norm_params.pop('q')

    return norm_params


def make_response(output_img, s3_source_key):
    """
    Build HTTP response for the transformed image.
    Returns
    -------
    dict
        the full response dict as expected by APIGateway/Lambda Proxy
    """
    status_code:
        200
    kwargs = {'isBase64Encoded': True}
    s3_obj = get_s3_obj(BUCKET, s3_source_key)
    mime = magic.Magic(mime=True)
    headers = {'Content-Type': mime(output_img)}
    if s3_obj.cache_control:
        headers.update({'Cache-Control': s3_obj.cache_control})
    with open(output_img, 'rb') as fp:
        bs64_str = base64_encode(fp.read())

    return response.generic(status_code=status_code, body=bs64_str, headers=headers, **kwargs)


def http_transform(s3_key, query_params):
    pass


def parse_event(event):
    s3_keys = event['pathParameters']['proxy']
    raw_ops = event['queryStringParameters']
    return s3_key, raw_ops


def handler(event, context):
    LOG.debug(json.dumps(event, indent=2))
    LOG.debug("Using %s bucket", BUCKET)

    # Do HTTP handling
    method = event['httpMethod']
    if method == 'GET':
        s3_key, raw_ops = parse_event(event)
        if source_filename:
            ops = param_validation(raw_ops)
            if any(ops):
                output_img = image_transform(source_filename, ops)
                return make_response(output_img, s3_key)
            else:
                output_img = source_filename
        else:
            return response.not_found()
        return response.ok("OK")

    else:
        # FIXME: this should be Method Not Allowed
        return response.not_found()


LOG.info('Loaded successfully')
