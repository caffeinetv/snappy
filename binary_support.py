#!/usr/bin/env python
import boto3
import os
import json


print('Adding binary support ...')

client = boto3.client('apigateway')

env = os.environ.get('SERVERLESS_ENV')
proj_name = 'snappy'

response = client.get_rest_apis()

api_id = None
for api in response['items']:
    if api['name'] == '{}-{}'.format(env, proj_name):
        api_id = api['id']

if api_id:
    print('restApiId is: {}'.format(api_id))
    params = {'extensions': 'integrations'}
    response = client.get_export(
        restApiId=api_id, stageName=env, exportType='swagger', parameters=params)
    swagger = json.loads(response['body'].read())
    # print(json.dumps(swagger))

    binary_support = {"x-amazon-apigateway-binary-media-types": [
        'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'text/html']}
    swagger.update(binary_support)
    client.put_rest_api(
        restApiId=api_id, body=json.dumps(swagger).encode())
    client.create_deployment(restApiId=api_id, stageName=env)
    print('Success')

else:
    print('Could not find API for env.: {}'.format(env))
