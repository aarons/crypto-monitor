#!/bin/bash

# TODO: add error handling in case any step fails
# TODO: don't hard code the stack name
sam validate
sam build --use-container
sam deploy --stack-name crypto-monitor --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM --resolve-s3