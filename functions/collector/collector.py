import boto3
from datetime import datetime
import json
import requests

# Hardcoding a few values for the proof of concept
# To productionize:
#   - aws bucket name should be configured as an environment variable
#   - extend collector function to take any endpoint at api.cryptowat.ch
#     output would match the api endpoint, for example:
#       s3://crypto-monitor-data/ingest/markets/summaries.json
#   - to scale collectors:
#       - large (>3500 puts/second): switch to firehose or kafka instead of s3 files
#       - extra large: consider fargate containers instead of lambda functions

URI = 'https://api.cryptowat.ch/markets/summaries'
AWS_BUCKET = 'crypto-monitor-data'

def lambda_handler(event, context):
    """
    This collects cryptowatch data and writes to s3

    No postprocessing occurs in this function to limit surface area
    of potential problems. Only most basic validation occurs (that
    we got results data back from the api call).

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        str: Containing path to the written object
    """
    if 'API_KEY' in event:
        params = {'apikey': event['API_KEY']}
    else:
        # see cryptowat.ch to setup an account and api key
        print("making the API call without a key")
        params = {}

    try:
        r = requests.get(URI, params=params)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

    # ok we're good, next to parse the results
    # and print allowance to logs (make sure we're not going to go broke)
    # TODO: should switch to proper logger
    print(r.json()['allowance'])
    results = r.json()['result']

    if len(results) < 100:
        raise Exception(f"expected more than 9000 results from API but got {len(results)} instead")

    filename = f"{round(datetime.now().timestamp())}.json"
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET)
    s3_key = f"ingest/{filename}"
    bucket.put_object(
        ContentType='application/json',
        Key=s3_key,
        Body=json.dumps(
                r.json()['result'],
                ensure_ascii=False),
        )
    print(f"file uploaded to s3: {bucket}/{s3_key}")
    return f"{s3_key}"
