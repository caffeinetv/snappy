import os

try:
    # Environment variable config
    SERVERLESS_ENV = os.environ['SERVERLESS_ENV']
    BUCKET = os.environ['BUCKET']
    AWS_REGION = os.environ['REGION']
except KeyError:
    SERVERLESS_ENV = 'dev'
    AWS_REGION = 'us-west-2'
    BUCKET = 'testing'


PARAM_ALIASES = {
    'width': 'w',
    'height': 'h',
    'quality': 'q',
    'format': 'fm',
}

LOSSY_IMAGE_FMTS = ('jpg', 'jpeg', 'webp')

DEFAULT_QUALITY_RATE = 85
AGRESSIVE_QUALITY_RATE = 45

SUPPORTED_FORMATS = ['jpeg', 'jpg', 'png', 'gif', 'webp']

MAX_IMAGE_W = 2000
MAX_IMAGE_H = MAX_IMAGE_W

TRANSFORMATIONS_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Supported Transformations Schema',
    'type': 'object',
    'properties': {
        'w': {
            'type': 'integer',
            'minimum': 1,
            'maximum': MAX_IMAGE_W
        },
        'h': {
            'type': 'integer',
            'minimum': 1,
            'maximum': MAX_IMAGE_H
        },
        'fit': {
            'enum': ['clip', 'crop', 'bounds']
        },
        'fm': {
            'enum': SUPPORTED_FORMATS
        },
        'q': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 100
        },
        'dpr': {
            'type': 'number',
            'minimum': 1,
            'maximum': 8
        },
        'auto': {
            'enum': ['compress']
        }
    }

}
