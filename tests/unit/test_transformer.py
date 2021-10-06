import transformer as t
from datetime import datetime

def test_metrics_timestamp():
    filename = "1633307658.json"
    correct_date = datetime(2021, 10, 3, 17, 34, 18)
    calculated_timestamp = t.metrics_timestamp(filename)

    assert calculated_timestamp == correct_date
