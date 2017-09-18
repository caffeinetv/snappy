# Snappy

This is our image processing service. It is a replacement for [Imgix](https://docs.imgix.com/apis/url). It is designed to be used behind a CDN, such as CloudFront, to cache the results of the image manipulation. Snappy is also compatible with a subset of [Fastly’s Image Optimizer](https://docs.fastly.com/api/imageopto/#api).

It uses Python 3.6 in AWS Lambda/API Gateway. It is deployed using [Serverless](https://serverless.com/framework/docs/).


## Serverless

This project uses the [Serverless Framework](https://serverless.com/framework/docs/). Install that:

    npm install -g serverless

This project is a little unique in that it has both NodeJS and Python Lambda functions. NodeJS is only used for packaging and deployment, not during runtime.

## Scripts

### Dependencies for Lambda deploy

    ./pip-install-requirements

Looks at `requirements.txt` and installs the packages in the `vendored` directory.

    ./pip-clean

Removes all installed packages in the `vendored` directory.

### Full Deploy

    ./deploy-full -e production

Does a full serverless deploy which creates the CloudFormation stack with all of the resources.

### Fast/Lambda-Only Deploy

    ./deploy-lambdas-only -e devtest

Deploys only the code for the Lambda functions. Very useful for development.

### Rollback

    ./rollback-full -e production 1492235541996

Performs a full serverless rollback to the specified version. To list help and the deployed versions, run:

    ./rollback-full -e devtest

### Logs

All AWS Lambda functions log to CloudWatch Logs. You can login to the console and view them there, or run a script to tail the logs.

    ./tail-logs -e devtest hello


### Testing

We use nose for testing Python code. We also use the `nose-watch` addition for TDD. To run the tests:

    mkvirtualenv
    pip install -r src/dev_requirements.txt
    pip install -r src/requirements.txt
    ./test
