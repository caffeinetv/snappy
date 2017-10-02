PARAM_ALIASES = {
    'width': 'w',
    'height': 'h',
    'quality': 'q',
    'format': 'fm',
}

LOSSY_IMAGE_FMTS = ('jpg, jpeg')

MAX_IMAGE_W = 2000
MAX_IMAGE_H = MAX_IMAGE_W

TRANSFORMATIONS_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'title': 'Supported Transformations Schema',
    'type': 'object',
    # 'required': [],
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
        'format': {
            'enum': ['jpeg,', 'jpg,', 'png', 'gif', 'webp']
        },
        'quality': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 100
        },
        'dpr': {
            'type': 'integer',
            'minimum': 1,
            'maximum': 8
        },
        'auto': {
            'enum': ['compress']
        }
    }

}
