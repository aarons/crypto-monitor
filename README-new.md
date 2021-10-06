# Severless Crypto Monitor App

This app relies on lambda to provide a serverless environment and easy scaleability.

At a high level, this project consists of three components:

1. data collection
1. data transformation
1. web app / api layer

Data Collection
This uses lambda functions to call an API and write results to S3.

Transformation
This also relies on lambda functions and applies transformations to determine metrics and structure data for use by the app.

Web App / API Layer
This is fairly simple, and utilizes FastAPI with Mangum on lambda

## Prerequisites for development

This relies on `aws sam` to develop lambda functions locally. It allows for local instantiation of lambda functions, tests, and helps manage deployments. There is some configuration involved if you haven't used `sam` before.

```shell
sam build-image
sam local start-lambda
aws lambda invoke --function-name "HelloWorldFunction" --endpoint-url "http://127.0.0.1:3001" --no-verify-ssl out.txt --env-vars .env

```

Maybe; sam package --output-template-file package.yaml --s3-bucket bucketname

Deploying!

It's helpful to see this running in a production like environment to get the full impact. So... here's how to deploy the cloudformation stack. It's also straightforward to unwind.

```bash
sam build -t template.yaml
sam deploy --guided --config-file samconfig.toml
aws cloudformation delete-stack --stack-name crypto-monitor
```

We'll unpack what each command is doing:

`sam build -t template.yaml` this compiles the app, using the cloudformation-like template in template.yaml. It's SAM specific templating language, but you can use cloudformation yaml as well. See these docs for more info. This step is required before doing any deployments if the template or functions have been modified.

`sam deploy --guided --config-file samconfig.toml` this will step through deploying the cloudformation stack to AWS. It will ask for confirmation before creating any resources. It utilizes samconfig.toml as a set of defaults, although since it's a guided process it will ask if you want to change any of those values (it's sensitive, so changes introduced here often fail). One caveat - the s3_bucket seems to get overwritten with SAMs preference, it appears to be early version software.

`aws cloudformation delete-stack --stack-name crypto-monitor` when all finished testing the app, this command will delete all the resources from aws. One caveat is s3 buckets with contents, the buckets have to be empty before the stack will delete the bucket.


## Local Development

Sam will handle package dependencies, but there are a few steps:
pip install requests
pip freeze > functions/collector/requirements.txt
sam build -t template.yaml
sam local invoke CryptoCollectorFunction --event env.json
Create event.json with api keys

So first is git checkout, then sam built -t template, then might need the guided deploy to create an s3 target bucket for local validation.

https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-lambda.html
sam local start-lambda
aws lambda invoke --function-name "HelloWorldFunction" --endpoint-url "http://127.0.0.1:3001" --no-verify-ssl out.txt

## Deployment

Turning on the state machine:
https://us-west-2.console.aws.amazon.com/events/home?region=us-west-2#/rules


## Time Log

1. 1st hour:
    - development/architecture plan
    - aws sam setup & testing
    - readme doc
1. 2nd hour
    - data collection
        - api call python
        - lambda handler
        - iam profiles for aws services
        - write to s3
        - publish and test lambda
        - s3 bucket
        - cloudformation stack
1. 3rd hour
    - documentation and tests
1. 4th hour
    - goal: fastapi endpoints
    - goal: api gateway setup
1. 5th hour
    - goal: wrap up documentation
    - goal: summarize how to scale


## Notes & Additional Learning

This repo is based on the excellent aws lambda guide:
https://github.com/awsdocs/aws-lambda-developer-guide/tree/main/sample-apps/blank-python

And implementation was inspired by these tutorials:

- [fastapi with lambda and api gateway](https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/)
- [stock app with steps & lambda](https://docs.aws.amazon.com/step-functions/latest/dg/sample-lambda-orchestration.html)
- [etl with lambda](https://aws.amazon.com/blogs/industries/etl-ingest-architecture-for-asset-management-based-on-aws-lambda/)


# Todo

This is the development plan, it starts with a simple local app that could be deployed via docker to an ec2 instance. After v0 it switches to serverless architecture for better scaling.

## Todo v0 (local only / docker)

[x] data collection -> data/ingest_timesamp.json
[x] data transformation
    [x] read next ingest
    [ ] read last 24 hour metrics
    [ ] compute metrics
    [ ] write 24 hour metrics
    [ ] delete ingest
[ ] graphql strawberry
    [ ] setup endpoints
    [ ] setup data model
    [ ] validate queries

## Todo v1 (steps / lambda)

## Time Tracker

## Time Log

1. 1st hour:
    - documentation
        - project requirements
        - development/architecture plan
        - todo list / time log
        - readme
    - git repo setup
    - data collection (very basic, signed up for account as well)
1. 2nd hour
    - data transformer
        - get filelist
        - load earliest
        - load metrics
        - calculate
        - write metrics
        - delete earliest file
    - setup .env file and config
1. 3rd hour
1. 4th hour
    - goal: front end setup
    - goal: fastapi endpoints
    - goal: api gateway setup
1. 5th hour
    - goal: wrap up documentation
    - goal: summarize how to scale


## Todo v1 (lambda/steps simple version)

[ ] setup data collection (v1)
    [ ] create lambda function
        [ ] support single api endpoint for v1
        [ ] payload is submitted/config driven
        [ ] simple data validation
        [ ] writes to s3 ingest/raw bucket
        [ ] update cloudformation scripts
        [ ] tests
            [ ] that lambda calls the api
            [ ] that payload is as expected
            [ ] that response validation works
            [ ] that response is written to s3
            [ ] that s3 is structured as json
    [ ] setup steps orchestration
        [ ] look into how to do this
        [ ] simple 1 minute trigger with desired payload
        [ ] update cloudformation scripts
    [ ] simple deploy script

[ ] setup dev environment
    [ ] docker (with lambda?)
    [ ] update readme with getting started
    [ ] document deploy process

[ ] setup data transformation (v1 a)
    [ ] create new lambda function with pandas
        [ ] trigger when new data arrives in s3
            [ ] may need sns topic
        [ ] loads last few days, trims to 24 hours
            [ ] aggregates for webview
                [ ] overwrites aggregate to single s3 file
            [ ] advanced metrics for webview
                [ ] overwrites s3 files for each metric
    [ ] setup s3 lifecycle rules
        [ ] deprecate old data to keep filecount/cost low
        [ ] no versioning to keep costs low
    [ ] shares deploy script with data collector
    [ ] tests
        [ ] that lambda triggers on new data in s3
        [ ] that metrics are updated
        [ ] that metrics are valid & correct

[ ] documentation
    [ ] update program diagram
    [ ] document scaling plan
    [ ] update readme with transformation development
    [ ] update deploy process

[ ] setup data webview/service
    [x] setup simple fastapi endpoint ('/')
        [x] wrap in mangan for lambdas
        [ ] setup api gateway
        [ ] deploy lambda and test
    [ ] template html frontpage
        [ ] include chart.js
        [ ] need labels and datasets from json
        [ ] visualize json data
    [ ] add selections for other charts
    [ ] figure out streaming results to webclient
    [ ] deploy: share with data collection/transforms


developer happiness
    local environment: docker
        could use lambda faker,
        or work with dev lambdas
    infrastructure
        use cloudformation or other aws service
        ideally one for dev (v1) and one for prod (v2)
    scaling plan
        sketch out scaling plan for each component

Reconsider the web service
Instead of lambda - utilize fargate so that we can have long running jobs with scheduled updates
See this: https://medium.com/analytics-vidhya/data-visualization-using-fastapi-and-easycharts-493eda3b1f3d

Or... for the web service
- fastapi on lambda
- users browser requests async updates to charts (each minute)
- invokes lambda function each time, with an endpoint that just sends the updated chart data

