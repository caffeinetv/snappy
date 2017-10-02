import logging
import json
import os
import subprocess
import ntpath

# Import our dependencies
import vendored

import boto3

from snappy import response
from snappy.settings import DEFAULT_FIT_BG_COLOR
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
    # TODO: FIXME: only for debugging
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

        output = os.path.join(TMP_DIR, '{}_{}.{}'.format(name, rnd_str(5), ext))
        args.append(output)
        print ('args: {}'.format(args))
        im_result = subprocess.check_output(args)
        print (im_result.decode())
    return output

def param_validation(params):
    """
    Validate the params and raise an Exception in case invalid or not supported operations
    Returns
    -------
    dict
        the validated params
    """
    pass

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
