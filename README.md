# Severless Crypto Monitor App

This app relies on aws lambda to provide a serverless environment and easy scaleability. At a high level, this project consists of three components:

1. data collection
1. data transformation
1. web app / api layer

Data collection uses a lambda function to call an API and write results to S3.

Transformation also relies on lambda and pandas to determine metrics and structure data for use by the app.

The web app / api layer utilizes FastAPI with Mangum to run on ... you guessed it, lambda!

## Prerequisites for Development

You will need:

1. an aws account
1. docker
1. the `aws cli`
1. the `aws sam cli`

### 1. an aws account

Probably don't need to walk you through this - but on the good news, the app can run full time without incurring any costs it's in current state. After deployment it is paused, and after enabled it stays below the 'free' minimums.

`sam` will utilize your aws account, ideally your user/iam profile will have admin privileges, but at minimum you need to be able to manage these services: cloudformation, cloudwatch, lambda, s3, event bridge, api gateway, steps/state machines, and iam profiles.

### 2. docker

Here are [walkthroughs](https://docs.docker.com/engine/install/) of getting it setup if it's not already installed. The [sam installation pages](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) also have instructions for docker.

### 3. the aws `cli`

This is used to setup your credentials, which sam will utilize. Instructions for installing this [can be found here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-set-up-credentials.html).

You must run `aws configure` to add your credentials in order for `sam` to work.

### 3. the aws `sam` cli

This allows for local instantiation of lambda functions, tests, and helps manage deployments. This page has instructions for [installing sam on different environments](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). The Linux instructions are provided below:

1. Download [the AWS SAM CLI zip file](https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip) to a directory of your choice.
1. unzip installation files: `unzip aws-sam-cli-linux-x86_64.zip -d sam-installation`
1. `sudo ./sam-installation/install`
1. `sam --version`

## Development Cycle

Ok, prereqs out of the way (whew!) here's how to work with the application.

### building and invoking functions

The first step is to get a lambda-like environment setup.

```shell
sam build -t template.yaml
```

Ok, try out a function (hint, it will fail but we'll get to that):

```shell
sam local invoke CryptoCollectorFunction
```

You should see an API call and then a failure writing to s3. Unfortunately the s3 bucket needs to be created for most of local development to work at the moment. To productionize this, we would need to add environment handling (dev, staging, prod) and add handling for local filesystem work.

To get functions to complete you will need to deploy the app (covered in the next section). On the upside, it's easy to delete the stack at the end.

### Deploying

Deploying requires two commands:

```bash
sam build -t template.yaml
sam deploy --guided --config-file samconfig.toml
```

Here's what each command is doing:

`sam build -t template.yaml` this compiles the app, using the cloudformation-like template in [template.yaml](template.yaml). It's SAM specific templating language, but you can use cloudformation yaml as well. See [these docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy.html) for more info. This step is required if the template or functions have been modified.

`sam deploy --guided --config-file samconfig.toml` this will step through deploying the cloudformation stack to AWS. It will ask for confirmation before creating any resources. It utilizes `samconfig.toml` for the configuration. The stack name 'crypto-monitor' is how it will show up in aws.

Unwinding the deployment and deleting all resources requires three commands:

```shell
aws s3 rm s3://cyrpto-watch-data --recursive --dryrun
aws s3 rm s3://aws-sam-cli-managed-default-samclisourcebucket-<id> --recursive --dryrun
aws cloudformation delete-stack --stack-name crypto-monitor
```

Here's what these commands are doing:

`aws s3 rm s3://<...>` the s3 buckets must be empty in order for cloudformation to delete the buckets. You will need to remove the `--dryrun` flag for the commands to acutally run. Unfortunately `sam` adds a unique id to the source code bucket, so you will need to check to see the full name.

`aws cloudformation delete-stack --stack-name crypto-monitor` when all finished testing the app, this command will delete all the resources from aws. One caveat is s3 buckets: the buckets have to be empty before the stack will delete the bucket. These two commands should help:

## Working with python dependencies

Sam will handle deploying package dependencies, but there are a few steps involved. Here's an example of how to install and work with the `requests` python library.

For local development, virtualenv is helpful:

```shell
virtualenv python3.9 venv
pip install requests
```

To make this package available to the `collector` lambda function:

```shell
pip freeze > functions/collector/requirements.txt
sam build -t template.yaml
```

Now package imports should work when you invoke the function locally, or after deploying the application.

## Turning on the state machine

By default the state machine is disabled to prevent the lambda functions from running. Once enabled, it will collect and transform data every minute. To start the process, you can enable the state machine:
https://us-west-2.console.aws.amazon.com/events/home?region=us-west-2#/rules (substitute the region for where the app was deployed).

## API Key Handling

If you want the app to run for more than a few hours, you will need to add an API key for cryptowat.ch, and then add it to the collector function's event so that the api call will include it.

TODO: add the details of how this works.

## Time Log

1. 1st hour:
    - development/architecture plan
    - aws sam setup & testing
1. 2nd and 3rd hour
    - data collection
        - api call python
        - lambda handler
        - iam profiles for aws services
        - write to s3
        - publish and test lambda
        - s3 bucket setup
        - cloudformation stack
1. 4th and 5th hour
    - data transformation (simple)
    - fastapi endpoint (basic)
    - tests (needs moar)
1. 6+
    - documentation
    - summarizing how to scale

## Notes & Additional Learning

This repo is based on the excellent aws lambda guide:
https://github.com/awsdocs/aws-lambda-developer-guide/tree/main/sample-apps/blank-python

And implementation was inspired by these tutorials:
- [fastapi with lambda and api gateway](https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/)
- [stock app with steps & lambda](https://docs.aws.amazon.com/step-functions/latest/dg/sample-lambda-orchestration.html)
- [etl with lambda](https://aws.amazon.com/blogs/industries/etl-ingest-architecture-for-asset-management-based-on-aws-lambda/)


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

