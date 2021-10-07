#!/bin/bash
# TODO: add error handling in case validate fails...
sam validate
sam build --use-container
