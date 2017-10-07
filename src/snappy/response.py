"""Standard API Gateway response objects"""

import json


def generic(status_code, body, headers=None, **kwargs):
    """Generic JSON response"""

    base_resp = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,Accept,X-Amz-Date,X-Api-Key,X-Amz-Security-Token,x-client-type,x-client-version'
        },
        'body': body
    }

    if headers:
        base_resp['headers'].update(headers)

    base_resp.update(kwargs)

    return base_resp


def ok(body):
    """200 Success JSON response"""
    return generic(200, body)


def error(status_code, errors):
    """Generic error response"""
    body = {
        'errors': errors
    }
    return generic(status_code, json.dumps(body))


def bad_request():
    """400 Bad Request response"""
    errors = {
        '_request': ['bad request']
    }
    return error(400, errors)


def unauthorized():
    """401 Unauthorized response"""
    errors = {
        '_token': ['the access token is invalid']
    }
    return error(401, errors)


def not_found():
    """404 Not Found response"""
    errors = {
        '_resource': ['not found']
    }
    return error(404, errors)


def unprocessable(errors):
    """422 Not Found response"""
    return error(422, errors)


def internal_server_error(message='Internal server error'):
    """500 Internal server error response"""
    errors = {
        '_internal': message
    }
    return error(500, errors)


def method_not_allowed(message='Method Not Allowed'):
    """405 Method Not Allowed error response"""
    errors = {
        '_internal': message
    }
    return error(405, errors)
