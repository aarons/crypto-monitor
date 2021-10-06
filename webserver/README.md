# High Level - Project Components

Data Collection -> Transformation -> Presentation

Data Collection
This uses lambda functions to call an API and write results to S3.

Transformation
This also relies on lambda functions to detect new results in s3, and apply transformations to structure for presentation, and determine things like trends.

Presentation
This utilizes FastAPI running on top of lambda to maintain serverless app state, and provide scaleable service.

## Prerequisites for development

Developing lambda locally requires python version 3.7. These instructions work on Ubuntu, some modification may be needed for OSX.

1. clone the repo locally
1. install python 3.7 if not available

    ```bash
    sudo apt install software-properties-common
    sudo apt-add-repository ppa:deadsnakes/ppa
    sudo apt install python3.7
    ```

1. setup virtual environment

    ```bash
    sudo apt install virtualenv
    virtualenv -p python3.7 env
    source ./env/bin/activate
    pip install -r requirements.txt
    ```

### Webserver Development

The webserver is run via uvicorn with a fastapi backend, and maintained in main.py

1. run uvicorn `uvicorn main:app --reload`

## Time Log

1. 1st hour:
    - development/architecture plan
        - with todo list
    - virtualenv setup
    - webserver basics
        - fastapi skeleton
        - mangum lambda wrapper
    - readme doc & time log
1. 2nd hour
    - data collection
        - api call python
        - lambda handler
        - iam profiles for aws services
        - write to s3
        - publish and test lambda
    - local dev environment
        - add tests
        - evaluate docker vs venv
    - readme updates
1. 3rd hour
    - goal: transformations
1. 4th hour
    - goal: front end setup
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
