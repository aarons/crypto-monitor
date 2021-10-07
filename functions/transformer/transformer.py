import boto3
from datetime import datetime
from flatten_json import flatten
import json

# TODO: move this to a env parameter file
AWS_BUCKET = 'crypto-monitor-data'
INGEST = 'ingest/'
RAW = 'raw/'

def lambda_handler(event, context):
    """
    This transformer flattens ingested json content for use in a data warehouse.

    High level algorithm:
    For up to 10 files in aws_bucket/ingest/:
        - flatten
        - add timestamp, market, and asset columns
        - add to aws_bucket/raw/ (ok for use in datawarehouse)
        - delete from ingest/

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        str: just says 'ok' cause it's pretty cool
    """
    # Get list of object keys in ingest
    # TODO: boto3 is instantiated with similar values across the app, consider subclassing with defaults preset
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=AWS_BUCKET,
        MaxKeys=10,
        Prefix=INGEST
    )

    for s3_obj in response['Contents']:
        print(f"working on {s3_obj['Key']}")
        stream = client.get_object(Bucket=AWS_BUCKET, Key=s3_obj['Key'])
        file_content = stream['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)

        # flatten the json object to make it easy to work with in a data warehouse
        # each object looks like:
        # 'uniswap-v2:zutweth': {'price_last': 0.1980423702789855, 'price_high': 0.1980423702789855, 'price_low': 0.1980423702789855, 'price_change_percentage': 0, 'price_change_absolute': 0, 'volume': 4.500000000000001, 'volumeQuote': 0.891190666255435}

        flattened = []
        # TODO: making a lot of assumptions about the quality of the data, need to add validations
        for key in json_content.keys():
            market, asset = str.split(key, ':')
            contents = flatten(json_content[key])
            contents['market'] = market
            contents['asset'] = asset
            # TODO: should include timezone information
            contents['created_at'] = s3_obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
            flattened.append(contents)

        new_key = s3_obj['Key'].replace(INGEST, RAW)
        # TODO: should validate that the key name meets expectations
        client.put_object(
            Bucket=AWS_BUCKET,
            ContentType='application/json',
            Key=new_key,
            Body=json.dumps(flattened, ensure_ascii=False),
            )
        print(f"wrote {AWS_BUCKET}/{new_key}")

        # TODO: DRY up use of client/Bucket references, instantiate a bucket object
        r = client.delete_object(
            Bucket=AWS_BUCKET,
            Key=s3_obj['Key']
        )
        if r['DeleteMarker']:
            print(f"deleted {AWS_BUCKET}/{s3_obj['Key']}")
        else:
            raise Exception(f"error deleting {AWS_BUCKET}/{s3_obj['Key']}")
    return "ok"

