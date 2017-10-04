import logging
import json
import os
import subprocess
import ntpath
import jsonschema
from copy import copy
import tempfile

# Import our dependencies
import vendored

import boto3

from snappy import response
from snappy.settings import TRANSFORMATIONS_SCHEMA, PARAM_ALIASES, LOSSY_IMAGE_FMTS
from snappy.utils import rnd_str


# Set up the default logger
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
LOG.info('Loading Lambda Function...')

# Set boto logging to INFO
logging.getLogger('botocore').setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.INFO)


# TODO: remove try/except after setting local envs.
try:
    # Environment variable config
    SERVERLESS_ENV = os.environ['SERVERLESS_ENV']
    BUCKET = os.environ['BUCKET']
except:
    pass


class InvalidParamsError(Exception):
    pass


def download_s3_obj(bucket, key):
    pass


def get_obj_metadata(bucket, key):
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
    Raise an InvalidParamsError in case of invalid or not supported operations
    Returns
    -------
    dict
        the validated and normalized params
    """
    if any(params):

        params = normalize_params(params)

        try:
            jsonschema.validate(params, TRANSFORMATIONS_SCHEMA)
        except jsonschema.ValidationError as ve:
            LOG.exception('Error validating schema for {}'.format(params))
            raise InvalidParamsError(
                'Error validating params. Details: {}'.format(ve))

        if 'fit' in params and not ('w' in params or 'h' in params):
            raise InvalidParamsError(
                '`fit` is valid only for resize operations')

        if 'q' in params and 'fm' in params and params['fm'] not in LOSSY_IMAGE_FMTS:
            raise InvalidParamsError(
                'Cannot set `quality` with non-lossy formats: {}'.format(params['fm']))

    return params


def make_response(image_data, s3_metadata):
    pass


def http_transform(s3_key, query_params):
    # image_data = transform()
    pass


def handler(event, context):
    LOG.debug(json.dumps(event, indent=2))
    LOG.debug("Using %s bucket", BUCKET)

    # Do HTTP handling
    method = event['httpMethod']
    if method == 'GET':

        # TODO Add code here

        return response.ok("OK")

    else:
        return response.not_found()


LOG.info('Loaded successfully')
