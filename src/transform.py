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

from snappy import response
from snappy.settings import TRANSFORMATIONS_SCHEMA, PARAM_ALIASES, LOSSY_IMAGE_FMTS, DEFAULT_QUALITY_RATE, AGRESSIVE_QUALITY_RATE
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


def is_lossy(ext, ops):
    return ('fm' in ops and ops['fm'] in LOSSY_IMAGE_FMTS) or ext in LOSSY_IMAGE_FMTS

def size_with_dpr(size, ops):
    if 'dpr' in ops:
        size = (s*float(ops['dpr']) for s in size)
    return size

def image_transform(filename, ops):
    """
    Transform the image specified by `filename` using the transformations specified by `ops` (operations)
    Returns
    -------
    str
        the filename of the transformed image
    """
    

    args = ['convert', filename]

    basename = ntpath.basename(filename)
    name, ext = os.path.splitext(basename)
    ext = ext.strip('.')

    if 'w' in ops and 'h' in ops:
        resize = (ops['w'], ops['h'])
        resize = size_with_dpr(resize, ops)
        new_size = '{}x{}'.format(*resize)
        args.extend(['-resize', new_size])
        if 'fit' in ops:
            if ops['fit'] == 'clip':
                #
                # same behavior as `bounds` for compatibility, may be removed later
                # https://github.com/caffeinetv/snappy/issues/5
                # 
                #
                pass
            elif ops['fit'] == 'crop':
                #
                # `^` is used to resize the image based on the smallest fitting dimension
                # then `-extents` crops exactly the image to the size specified from the center
                #
                args[-1] += '^'
                args.extend(['-gravity', 'center', '-extent', new_size])
            elif ops['fit'] == 'bounds':
                #
                # by default `-resize` will fit the image into the requested size
                # and keep the original aspect ratio
                #
                pass
        else:
            #
            # ignore the aspect ratio and distort the image so it always
            # generates an image exactly the size specified
            #
            args[-1] += '!'


    #
    # if only `w` or `h` is provided, then we scale the target side
    # to the specified value, and keep the aspect ratio.
    # `fit` does not apply when only one side is given.
    #
    elif 'w' in ops:
        resize = size_with_dpr((ops['w'],), ops)
        new_size = '{}x'.format(*resize)
        args.extend(['-resize', new_size])
    elif 'h' in ops:
        resize = size_with_dpr((ops['h'],), ops)
        new_size = 'x{}'.format(*resize)
        args.extend(['-resize', new_size])

    
    #
    # if `dpr` is provided with no resize, then we just scale the image 
    #
    elif 'dpr' in ops:
        scale_factor = '{}%'.format(float(ops['dpr'])*100)
        args.extend(['-scale', scale_factor])        

    if 'fm' in ops:
        #
        # just use the format as filename extension,
        # then IM will handle conversion automatically
        #
        ext = ops['fm']


    if 'auto' in ops and ops['auto'] == 'compress':
        #
        # removes any image profile attached to the image
        #
        args.append('-strip')

        #
        # this will overide any existing `q` operation
        #
        if is_lossy(ext, ops) and 'q' not in ops:
            new_ops = copy(ops)
            new_ops.update({'q': AGRESSIVE_QUALITY_RATE})
            return image_transform(filename, new_ops)


    if is_lossy(ext, ops):
        if 'q' in ops:
            q = str(ops['q'])
            args.extend(['-quality', q])
        else:
            args.extend(['-quality', str(DEFAULT_QUALITY_RATE)])
    

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
