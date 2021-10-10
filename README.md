# Severless Crypto Monitor App

This app is based on [these project requirements](project_requirements.md). It collects crypocurrency metrics, structures data for use in many applications, and provides a simple api endpoint.

AWS serverless architecture is used to provide easy scaleability. At a high level, this project consists of three components:

1. data collection
1. data transformation
1. web app / api layer

## Key Project Files

```shell
├── athena_queries
│   └── create_market_summaries.sql  # schema for transformed data stored in s3
├── example_data
│   ├── ingest.json  # example output of collector.py
│   └── raw.json     # example output of transformer.py
├── functions        # lambda functions
│   ├── collector
│   │   └── collector.py   # collects data from an external source
│   ├── transformer
│   │   └── transformer.py # transforms collected data for analytics
│   └── webserver
│       └── main.py        # api endpoint for exploring data
├── statemachine
│   └── crypto_monitor.asl.json  # the overall workflow for amazon steps
├── 1-deploy.sh # helpful deployment shell script
├── README.md   # this doc
├── project_requirements.md # a brief of the project deliverables
├── requirements.txt # python libraries needed
├── samconfig.toml   # default config for aws sam
└── template.yaml    # cloudformation template
```

## Prerequisites for Development

You will need:

1. docker
1. `aws` cli
1. aws `sam` cli
1. this repo and python 3.9

### 1. docker

Here are [walkthroughs](https://docs.docker.com/engine/install/) of getting it setup if it's not already installed. 

### 2. the `aws` cli

The `aws` cli is used to manage credentials for aws `sam`. Instructions for installing `aws` cli [can be found here](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

You must run `aws configure` to add your credentials after installing.

### 3. the aws `sam` cli

This allows for local instantiation of lambda functions, tests, and helps manage deployments. This page has instructions for [installing sam on different environments](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). 

For Ubuntu:

```shell
curl https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip --location -o aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
sam --version
```

For OSX (requires [homebrew](https://docs.brew.sh/Installation)):

```shell
brew tap aws/tap
brew install aws-sam-cli
sam --version
```

### 1. this repo and python 3.9

This repo was developed using python 3.9 - other python3 versions should work, but that would be the safest to setup. It's also helpful to have a virtual environment to safely install packages. I like to use `virtualenv` but other environment handlers should also work.

Python 3.9 and virtualenv for Ubuntu:

```shell
sudo apt install python3.9
sudo apt install virtualenv
```

For OSX - installation instructions [for python3](https://docs.python-guide.org/starting/install3/osx/), and then for virtualenv it's:

```shell
python3 -m pip install --user virtualenv
```

After cloning this repo install the required packages:

```shell
git clone git@github.com:aarons/serverless-crypto-monitor.git
cd serverless-crypto-monitor
virtualenv -p python3.9 venv
source venv/bin/activate
pip install -r requirements.txt
```

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

You should see an API call and a failure writing to s3. The s3 bucket needs to be created for local development to work at the moment. A cloudformation stack is used, which makes creating (and deleting) AWS resources simpler.

### Deploying

This will deploy a cloudformation stack called 'crypto-monitor'. The serverless implementation means it will run without incurring costs beyond s3 storage (due to staying under aws free monthly minimums).

 Deploying requires two commands:

```bash
sam build --use-container
sam deploy
```

Here's what each command is doing:

`sam build --use-container` this compiles the app, using the cloudformation-like template in [template.yaml](template.yaml). It's SAM specific templating language, but you can use cloudformation yaml as well. See [these docs](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy.html) for more info.

`sam deploy` will step through deploying the cloudformation stack to AWS. There are two phases: uploading the compiled code to an s3 bucket for the apps source code, then building the stack. It utilizes [`samconfig.toml`](samconfig.toml) for the configuration options. Options can be optionally overridden at the command line, see [this reference for more info](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html).

#### Turning on the state machine

The state machine is disabled by default to prevent the lambda functions from running. Once enabled, it will collect and transform data every minute. To start the process, you can enable the state machine:
https://us-west-2.console.aws.amazon.com/events/home?region=us-west-2#/rules (substitute the region for where the app was deployed).

### Un-Deploying

Unwinding the deployment and deleting all resources requires three commands:

```shell
aws s3 rm s3://crypto-monitor-data --recursive --dryrun
aws s3 rm s3://aws-sam-cli-managed-default-samclisourcebucket-<id> --recursive --dryrun
aws cloudformation delete-stack --stack-name crypto-monitor
```

Here's what these commands are doing:

`aws s3 rm s3://<...>` the s3 buckets must be empty before cloudformation will delete the buckets. You will need to remove the `--dryrun` flag for the commands to acutally run. One bucket is the apps source code, and the other is the data it has downloaded and modified.

`aws cloudformation delete-stack --stack-name crypto-monitor` this command will delete all the resources from aws.

## Working with lambda and python packages

Lambda functions need their dependencies packaged and deployed alongside. Sam will use the requirements.txt file in each functions subdirectory to know what to build.

Here's an example of how to install and work with the `requests` python library.

```shell
virtualenv python3.9 venv
pip install requests
pip freeze > functions/collector/requirements.txt
sam build -t template.yaml
```

Now package imports should work when you invoke the function locally, or after deploying the application.

## Data Collector

[The collector](functions/collector/collector.py) is a fairly simple function. It will call cryptowatch every minute, and write the json response to `s3://crypto-monitor-data/ingest/<timestamp>.json`

Helpful AWS links to see it running (normalized to the us-west-2 region):

- [the lambda function details](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions)
- [the state machine logs](https://us-west-2.console.aws.amazon.com/states/home?region=us-west-2#/statemachines)

To run this locally: `sam local invoke CryptoCollectorFunction`

### To Productionize the data collector

Lots of things are needed to make this production ready:

- unit tests
- integration tests
  - that lambda calls the cryptowatch api
  - that payload is as expected
  - that response validation works
  - that response is written to s3
  - that s3 is structured as json
- payload is submitted/config driven
- output key includes api endpoint (example: s3://.../market/summaries/output.json)
- api_key is handled as an environment variable
- monitoring and alerting when the function has errors (cloudwatch / pagerduty integration)

### To Scale the Collector

**What would you change if you needed to track many metrics?**

For collecting more types of data (more API endpoints) I would generalize the collector function to be parameter driven, accepting many endpoints at a single api. The s3 filestructure represent the API's route that we're calling. For example: `s3://.../cryptowat.ch/market/summaries/{timestamp}.json`

**What if you needed to sample them more frequently?**

If data collection continues to be calls to APIs outside the company, then this architecture should last and scale for a long time. S3 can handle up to 3500 PUT requests per second per bucket, so we could connect to a lot of APIs.

There is a constraint of 10gb of memory per lambda, so if we're ingesting larger datasets at once then would need to move to a service that can provision larger instances (suach as fargate containers).

If data ingest starts to occur from clients pushing data to montecarlo, then we have no gaurantees on the rate required. Moving to streaming ingest such as firehose or kafka would be helpful to de-risk this. Ingest streams can compress data when writing to s3, and "batch" the sources it's writing which saves on overall PUTs/second. Regarding compression, if we are receiving JSON data with text fields, gzipping averages a 25:1 compression, meaning a single s3 bucket could support the equivalent of ~90,000 puts per second without compression (3500 PUT/sec * 25 compression ratio = 87,500 equivalent puts/sec).

## Data Transformer

This has a simple goal of structuring data for use in downstream systems. It takes files ingested by the collector and flattens them, adds a timestamp column of when data arrived, and writes out to `s3://crypto-monitor-data/raw/<timestamp>.json`.

The details and logs can also be found on the lambda function and state machine pages:

- [the lambda function details](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions)
- [the state machine logs](https://us-west-2.console.aws.amazon.com/states/home?region=us-west-2#/statemachines)

To run this locally: `sam local invoke CryptoTransformer` 

It is helpful to invoke the `CryptoCollectorFunction` just before, so that there is data available to transform. 

### To Productionize the data transformer

- should rename this function to 'prep' or 'load', it's not adding metrics
- unit tests
- integration tests
- data quality tests during execution
  - that loaded data is json
  - that transformed data set has the same number of rows
  - that written data is valid/json
- consider triggering this function when new files are added to /ingest, instead of looking for files in ingest to process - this would prevent the transformer getting stuck on several invalid files/data (it would continually try them if the 'queue' filled up with bad data)
- monitoring and alerting in case of failure
- alert if files stay in the /ingest folder for too long

### To Scale the transformer

Since this function is mostly responsible for flattening data the memory and cpu requirements stay pretty low. It can process a lot of ingest files at once very quickly, so remaining a lambda function (or group of lambdas for different ingest pipelines) should be sufficient for a long time.

One *very* helpful function at this stage is to introduce de-duplication which is both memory and cpu intensive.

Scaling de-duplication involves:

- staying on lambda until memory requirements are more than 10gb
- moving to a datawarehouse with ephemeral compute is a reasonable next step (such as snowflake)
- utilizing spark clusters or limiting the amount of data considered (such as previous day or week) when scale is terabytes an hour or more

## Webserver

This is where people are able to view all the handy metrics in nice graphs. Or it would be if it was built out.

The basic webserver is deployed, so it is possible to send traffic and test endpoints. You can find the endpoint by going to [API Gateway](https://us-west-2.console.aws.amazon.com/apigateway/main/apis?region=us-west-2) and navigating to `APIs > crypto monitor > stages > Prod`. The `invoke URL` can be clicked on, which will instantiate the lambda and pass traffic to FastAPI.

To run this locally:

```shell
uvicorn main:app --reload --app-dir functions/webserver/
```

### To Productionize the Webserver

Need to do all the things, my first priorities would be:

- look into [pyathena package](https://pypi.org/project/pyathena/) for athena database connectivity
- add simple dropdown to choose which asset to graph: (select distinct(asset))
- add a query that computes window functions for various price and volume metrics
- understand how chart.js works for visualizing data

### To scale the webserver

**What if you had many users accessing your dashboard to view metrics?**

When the service needs to be more performant, moving onto AWS Fargate containers helps increase response time and helps with serving many more requests at a time.

FastAPI appears to be a very well made and should scale to handle more volume. I would consider adding strawberry graphql for a more flexible API endpoint.

Serving database queries should move from athena to postgres and eventually redis to dramatically improve response times. Also, flattening / precomputing metrics so that joins are not required will help improve query response time.

Alternatively to the above, I would look for hosted dashboarding systems that help with UI and exploration (such as Tableau or Periscope).

## Regarding Metrics

This app is missing a metrics generation step. Normally this would be done after loading data into `raw` / `athena`. It's not present due to lack of time.

For early scale I would add views in athena with window functions to compute the needed metrics. I wouldn't recommend computing the metrics via python/pandas, as it's easy to get transformations with large branching factors that are challenging to support. It's best to normalize on SQL as long as possible because it will allow more people to maintain existing transformations, and make it safer to introduce new ones.

As volume goes up we would move from views to materialized tables. These could be orchestrated through aws steps or something like airflow.

We would eventually expand to support predictive analytics. Spark is great at this, but can be challenging to run on AWS EMR (as of a few years ago), so using a managed service such as Databricks is really handy. That can be orchestrated via airflow so that notebooks stay in source code.

## Addendum

### Extending Testing

Given another 5 hours on this project, most of it would be spent on adding and expanding test coverage. This is vital to enable multiple developers to safely work on a production application.

Once test coverage is present, I would prioritize:

- introduce a file handling class, to make local development possible without s3
- add black and flake8 pre-commit hooks to help with code formatting and catching issues up front
- create better dev, staging, and prod abstractions, so it's safe for developers to experiment
- introducing CI/CD

### Feature Request - Alerting on certain conditions

> Feature request: to help the user identify opportunities in real-time, the app will send an alert whenever a metric exceeds 3x the value of its average in the last 1 hour. For example, if the volume of GOLD/BTC averaged 100 in the last hour, the app would send an alert in case a new volume data point exceeds 300. Please write a short proposal on how you would implement this feature request.

The trailing 24 hour volume is already tracked by the collector, so we would add two new columns to the transformed data:

- average volume over the last hour
- the current volumes ratio compared to the average (300% increase for example)

For notifications v1 it would be easier to provide a few discrete scenarios (such as volume growing 300%) and then use cloudwatch or a lambda function to check and monitor the ratio column for values that exceed the amount. This would trigger an SNS event when a ratio is exceeded.

I'm less familiar with how to actually ping the user when we have an SNS notification hits the queue. Presumably we would need a subscriber list and a way to notify them that it has been exceeded (such as an SMS service, email, or open websocket).

It would be fun to sketch out how this would be done with *n* alerts and *n* users - presumably this has been architected before, so I'd research approaches published online.

### API Key Handling & Environment Variables

The app will work for a few hours each day without having an API key for cryptowat.ch. An api key is needed to keep it running full time though.

For now the key is passed in as a dict to the lambda_function via the event bridge. To set it, go the [event bridge for your region](https://us-west-2.console.aws.amazon.com/events/home?region=us-west-2#/rules).

Edit the rule for the step functions state machine, and under the 'selected targets' section, add `{ "API_KEY": "xyz" }` to the 'Constant (JSON text)' option. This will pass the key into the `event` variable for the function.

TODO: Obviously, this should be handled as an environment variable for the lambda function.

### Time Log

1st hour:

- development/architecture plan
- aws sam setup & testing
- cloudformation and stack familiarity

2nd and 3rd hour:

- data collection
  - api call python
  - lambda handler
  - iam profiles for aws services
  - write to s3
  - publish and test lambda
  - s3 bucket setup
  - cloudformation stack

4th and 5th hour:

- data transformation
- athena data validation
- fastapi endpoint (super basic)
- api gateway setup via cloudformation

6+ hours:

- documentation
- summarizing how to scale

### Notes & Additional Learning

This repo is based on the excellent aws lambda guide:
https://github.com/awsdocs/aws-lambda-developer-guide/tree/main/sample-apps/blank-python

And implementation was inspired by these tutorials:
- [fastapi with lambda and api gateway](https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/)
- [stock app with steps & lambda](https://docs.aws.amazon.com/step-functions/latest/dg/sample-lambda-orchestration.html)
- [etl with lambda](https://aws.amazon.com/blogs/industries/etl-ingest-architecture-for-asset-management-based-on-aws-lambda/)
