import logging
import json
import os
import subprocess
import ntpath

# Import our dependencies
import vendored

import boto3

from snappy import response


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
	output = os.path.join(TMP_DIR, basename)
	if 'w' in operations and 'h' in operations:
		resize = (operations['w'], operations['h'])
		args = ['convert', filename, '-resize', '{}x{}'.format(*resize)]
		if 'fit' in operations:
			if operations['fit'] == 'clip':
				
		else:
			args[-1] += '!'
		args.append(output)
		print ('args: {}'.format(args))
		im_result = subprocess.check_output(args)
		print (im_result.decode())
	return output

def param_validation():
	pass

def make_response(image_data, s3_metadata):
	pass


def http_transform(s3_key, query_params):
	image_data = transform()


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
