from datetime import datetime
import json
import numpy
import os
import pandas as pd
import time

DATA_DIR = 'data/'
METRICS_DIR = 'metrics/'

# find earliest data file to ingest
# this returns a filename
def discover_data() -> str:
    data_files = os.listdir(DATA_DIR)
    if not data_files:
        # no data to ingest or work with
        raise Exception("no new data to ingest")
    return numpy.sort(data_files)[0]

# find latest metrics file to annotate
def discover_metrics() -> dict:
    metric_files = os.listdir(METRICS_DIR)
    if not metric_files:
        return None
    return numpy.sort(metric_files)[-1] # metrics filename

def load_file(filename) -> dict:
    with open(f"{DATA_DIR}{filename}", "r") as o:
        data = json.load(o)
    return data

def timestamp(filename) -> datetime:
    # returns a timestamp based on a filename with an encoded epoc
    epoc = int(filename.rstrip('.json'))
    return datetime.fromtimestamp(epoc)

def prep_dataframe(dataset, timestamp):
    # convert dict to dataframe
    df = pd.DataFrame.from_dict(dataset, orient='index', columns=["value"])

    # change the default index (dict keys, which are the names of the coins)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'coins'}, inplace=True)
    df['updated_at'] = timestamp

    # filter for coins traded on the binance market
    # about 307 coins that are mapped to usd
    df = df[df.coins.str.startswith('market:binance') & df.coins.str.endswith('usd')]

    # the 'coins' string encodes several data points
    # it looks like: market:binance-us:aaveusd
    # these next lines split the string into the three components
    # and then merges the new columns back to the original dataframe
    components = df.coins.str.split(pat=':', expand=True).rename(columns={0: 'market', 1: 'exchange', 2: 'coin'})
    df = df.merge(components, how='left', left_index=True, right_index=True)

    # The dataset now looks like:
    #                     coins     value            updated_at  market    exchange      coin
    # market:binance-us:aaveusd  307.7500   2021-10-03 17:24:17  market  binance-us   aaveusd
    #  market:binance-us:adausd    2.2437   2021-10-03 17:24:17  market  binance-us    adausd

    # for now we aren't tracking markets & exchanges,
    # next step is to select only needed columns and drop any duplicate rows
    # the dataset is sorted by the original keys, so keeping the first dupe
    # should be a consistent mapping.
    # The market and exchange should be kept in production to differentiate correctly
    df = df[['updated_at', 'coin', 'value']].drop_duplicates(subset='coin', keep='first')
    return df

def transform_dataframe(prepped, metrics):
    df = metrics.append(prepped)
    # In addition, the application will present the selected metric's "rank".
    # The "rank" of the metric helps the user understand how the metric is changing relative to other similar metrics,
    # as measured by the standard deviation of the metric over the last 24 hours.
    # For example in the crypto data source, if the standard deviations of the volume
    #   of BNT/BTC, GOLD/BTC and CBC/ETH were 100, 200 and 300 respectively,
    #   then rank(CBC/ETH)=1/3, rank(GOLD/BTC)=2/3 and rank(BNT/BTC)=3/3.

if __name__ == 'main':
    try:
        data_filename = discover_data()
    except:
        print("No data to ingest")
        exit
    raw_data = load_file(data_filename)
    prepped = prep_dataframe(raw_data, timestamp(data_filename))

    metrics_filename = discover_metrics()
    if not metrics_filename:
        metrics = pd.DataFrame(None, None, columns=['updated_at','coin','value'])
    else:
        metrics = load_file(metrics_filename)

    df = transform_dataframe(prepped, metrics)
    write_metrics(df)

