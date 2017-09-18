import logging
import json
import os

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


# Environment variable config
SERVERLESS_ENV = os.environ['SERVERLESS_ENV']
BUCKET = os.environ['BUCKET']


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
