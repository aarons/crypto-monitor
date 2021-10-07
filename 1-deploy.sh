#!/bin/bash
# TODO: don't hard code the bucket name
# TODO: handle package failures/response codes
sam package --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-1pep0etf19war --output-template-file out.yml
sam deploy --template-file out.yml --stack-name crypto-monitor --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM
