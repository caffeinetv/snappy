# Snappy

[![Build Status](https://travis-ci.com/caffeinetv/snappy.svg?branch=master)](https://travis-ci.com/caffeinetv/snappy)

Snappy is an image processing service developed by [Caffeine](https://www.caffeine.tv/). It is designed to be used behind a CDN, such as CloudFront, to cache the results of the image manipulation. Snappy is compatible with a subset of both [Imgix](https://docs.imgix.com/apis/url) and [Fastly’s Image Optimizer](https://docs.fastly.com/api/imageopto/#api).

When a request comes in, Snappy will read a file from S3, perform some set of transformation on the image using Imagemagick and return the content of that image to be viewed in a web browser or client.

It uses Python 3.6 and can be deployed to AWS Lambda and API Gateway using the [Serverless Framework](https://serverless.com/framework/docs/).


## Example

1.  An HTML page is loaded in a browser with the following image tag:

        <img src="https://my-snappy.example.com/some/path/to/myfile.jpeg?fit=crop&w=720&auto=compress" />

2.  A request comes in to this service:

        https://my-snappy.example.com/some/path/to/myfile.jpeg?fit=crop&w=720&auto=compress

3.  The service then downloads the file from some S3 bucket:

        s3.get(bucket, "/some/path/to/myfile.jpeg")

4.  In this example, the service performs 2 transformations:
    - Crop the image to 720 pixels wide using Imagemagick
    - Compress the new image using the same format (in this case, JPEG) stripping any image meta-data.

5.  Send the image back as the binary response for the service. Include the proper HTTP headers such as `Content-Type` and forward along any caching headers such as `cache-control` that are set on the S3 object.


## API

### Auth

There is no authentication or authorization process. The service will be deployed behind a CDN performing SSL termination.

### URL

The URL pattern to this service is:

    http://<api-gateway-base>/<path within S3 bucket to file>?<transformations>

### Transformations

All transformations are specified as query string parameters. They can be specified in any order in the URL, though there is an order of operation (defined below)

| Parameter | Aliases | Description | Examples |
| --------- | ------- | ----------- | -------- |
| `width`   | `w`     | Resize the image to a maximum of `width` pixels wide. Values must be an integer between 1 and 2000. | `w=150` `width=200` |
| `height`  | `h`     | Resize the image to a maximum of `height` pixels high. Values must be an integer between 1 and 2000. | `height=90` `w=100&h=80`
| `fit`     |         | Fit the image within the specified bounds. This is applied when resizing an image, so width and height are used from above. Values can be either `crop`, `bounds` or `clip`. ([Imgix reference](https://docs.imgix.com/apis/url/size/fit)) ([Fastly reference](https://docs.fastly.com/api/imageopto/fit)) | `fit=crop` `fit=bounds`
| `format`  | `fm`    | Output the image in the specified format. This may or may not involve converting the image. Values are: jpeg, jpg, png, gif or webp. | `format=jpeg` `fm=png` `fm=jpg` |
| `quality`   | `q`   | The quality of the compressed image to serve. This is only applicable for lossy image formats (JPEG). The default quality is 85%. Value must be an integer between 1 and 100. ([Fastly reference](https://docs.fastly.com/api/imageopto/quality)) | `q=75`
| `dpr`       |       | Device pixel ratio for service responsive images. ([Imgix reference](https://docs.imgix.com/apis/url/dpr)) ([Fastly reference](https://docs.fastly.com/guides/imageopto-setup-use/serving-responsive-images)) | `dpr=2` `dpr=3`
| `auto`      |       | Apply best-effort techniques to compress the image as much as possible. Value must be `compress`. ([Imgix Reference](https://docs.imgix.com/apis/url/auto)) | `auto=compress` |


### Order of Transformations

Although the query string parameters can be specified in any order, transformations are applied in a set order:
1.  `width`, `height` and `fit`
1.  `format` and `quality`
1.  `auto` and `dpr`

### Meta-data removal

When compressing the image, all metadata (for example EXIF, XMP or ICC) should be removed to reduce file size. If an image contains an ICC profile, the data is applied directly to the image to ensure color output is correct.


## Development pre-req: Serverless

This project uses the [Serverless Framework](https://serverless.com/framework/docs/). Install that:

    npm install -g serverless

Yes, we are installing a NodeJS project to deploy a Python application. The serverless framework is just a tool, and a very good one at that, so get over it. :) NodeJS is not used at runtime.

For local testing, you will also want Imagemagick installed. For macOS, that is:

    brew install imagemagick


## Development

We use GitHub Flow as our workflow so to set that up:

1.  Please *Fork* this repository to your own GitHub account
1.  Clone your fork and then setup upstream
        git clone git@github.com:USERNAME/snappy.git
        cd snappy
        git remote add upstream git@github.com:caffeinetv/snappy.git
1.  Now you can create a feature branch
        git checkout -b my-feature
1.  Make changes, commit and push to your fork
        git push origin my-feature
1.  Now submit a pull request for code review
1.  Once the code review has a "LGTM", merge.


## Deployment

This application should be deployable to any AWS account in any AWS region. No bucket names, regions, ARNs or anything like that is hardcoded into the application. Instead, the application reads Environment Variables at startup time from the Lambda execution environment.

There is a deploy script in the repository that takes an environment argument which can be used to switch between deployment targets. Each deployment will only pull images from a single S3 bucket.


## Limits

 - No image will be larger than 5Mb.
 - Images should be limited to no more than 2000x2000 for output.


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

We use nose for testing Python code. We also use the `nose-watch` addition for test driven development (TDD). To run the tests:

    mkvirtualenv
    pip install -r src/dev_requirements.txt
    pip install -r src/requirements.txt
    ./test

You can now edit files and have the tests run any time you save them. Press `Ctrl-C` to stop the TDD flow.


## About Caffine

[Caffeine](https://www.caffeine.tv/about.html) is a new way for you and your friends to enjoy and create live gaming, entertainment, and creative arts broadcasts. Simplicity is at the core of what we do: from our clean design to our simple-to-use tools, we make it incredibly easy for anyone to start broadcasting in no time.

We're hiring: [jobs@caffeine.tv](mailto:jobs@caffeine.tv)


## License

Copyright 2018 Caffeine Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
