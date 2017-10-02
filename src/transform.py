import logging
import json
import os
import subprocess
import ntpath
import jsonschema

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

TMP_DIR = '/tmp'


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
    basename = ntpath.basename(filename)
    name, ext = basename.split('.')
    if 'w' in operations and 'h' in operations:
        resize = (operations['w'], operations['h'])
        new_size = '{}x{}'.format(*resize)
        args = ['convert', filename, '-thumbnail', new_size]
        if 'fit' in operations:
            # TODO: REMOVEME: only for debugging
            name += '_' + operations['fit']
            if operations['fit'] == 'clip':
                args[-1] += '!'
            elif operations['fit'] == 'crop':
                args[-1] += '^'
                args.extend(['-gravity', 'center', '-extent', new_size])
            elif operations['fit'] == 'bounds':
                pass
        else:
            #
            #  default behaviour is to scale to the specificed bounds
            #  which is the same behaviour as `fit=clip`
            #
            args[-1] += '!'

        if 'auto' in operations and operations['auto'] == 'compress':
            #
            # `thumbnail` already removes any image profile
            # but not the ICC color profile by default
            # so let's remove it as well with `-strip
            #
            args.append('-strip')

        output = os.path.join(
            TMP_DIR, '{}_{}.{}'.format(name, rnd_str(5), ext))
        args.append(output)
        print('args: {}'.format(args))
        im_result = subprocess.check_output(args)
        print(im_result.decode())

    if 'quality' in operations and ('format' in operations or ext.lower in ('jpg', 'jpeg')):
        pass

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
