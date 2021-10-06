# Project Proposals

This doc contains two parts - how to scale the service, and how to alert on certain conditions (the feature request from the [project requirements doc](project_requirements.md)).

## Scaling

The general structure of the program is setup to enable scaling from the start. With separation of concerns between each stage: [collection](#Collection) -> preperation -> transformation -> API. Each of these could reasonably become their own repo's with more generic functions, to serve multiple data pipelines.

These questions are answered the following sections:

- what would you change if you needed to track many metrics?
  - [Collector](#Collector)
  - [Data Transformation](#Transformation)
- what if you needed to sample them more frequently? [Collector](#Collector)
- what if you had many users accessing your dashboard to view metrics? [API](#API)

### Collection

Currently implemented as a lambda function that calls a single API endpoint and writes to s3.

> **What would you change if you needed to track many metrics?**

For collecting more types of data (more API endpoints) I would generasize the collector lambda function, and have the s3 filestructure represent the API's route that we're calling. For example: `s3://data-ingest/cryptowat.ch/market/summaries/{timestamp}.json`

> **What if you needed to sample them more frequently?**

If data collection continues to be API calls outside the company, then this architecture should last and scale for a long time. S3 can serve up to 3500 PUT requests per second per bucket, so we could connect to a lot of APIs.

Constraints on the current solution:

- about 10gb of memory per lambda, so if we're ingesting larger datasets at once then would need to move to a service that can provision larger instances (such as fargate containers)
- S3 throughput of 3500 PUTs/second - this is a limitation per s3 bucket.

If data ingest starts to occur from clients pushing data then we have no gaurantees on the rate required; moving to streaming ingest such as firehose or kafka would be helpful to de-risk this. Ingest streams can compress data when writing to s3, and "batch" the sources it's writing which saves on overall PUTs/second. Regarding compression, if we are receiving JSON data with text fields, gzipping often results in 25:1 compression, meaning a single s3 bucket could support the equivalent of ~90,000 puts per second without compression (3500 PUT/sec * 25 compression ratio = 87,500 equivalent puts/sec).

S3 filenames are currently encoded with their timestamp down to the second, that could be increased to millisecond to avoid collisions, or the collectors `arn id` could be added for a unique identifier per filename.

For very fast sampling (say thousands of apis or a web crawler) then depending on implementation could see either lots of lambdas being instantiated (if the workload can be easily divided up) or more performant fargate containers used.

### Data Prep

The general design of the pipeline is to ingest without modifying source data - only once things are staged on a persistent storage layer do we attempt to prep the data for analytics use. Data prep involves mapping the schema, validating rows are safe, and de-duplicating the ingest. This separates out concerns, and prevents a schema change or transformation error from causing data loss with streaming sources.

Scaling this involves:
    - staying on lambda until memory requirements are more than 10gb
    - moving to a datawarehouse with ephemeral compute is a reasonable next step (such as snowflake)
    - deduplication becomes expensive to compute for very large scale, so utilizing spark clusters or limiting the amount of data considered (such as previous day or week) can become helpful.

### Data Transformation

This is where all metrics are figured out. Doing this via Lambda is a bit of a hack; generally SQL or Spark for Map Reduce provide helpful constraints that aren't available when trying to do transformations via python.

Some useful constraints of SQL:
    - no branching factor
    - columnar transformations
    - common language and way of doing things

> **what would you change if you needed to track many metrics?**

So first step for scaling data transformations would be to move off python and lambda and onto something that provides a common way of doing things (SQL) - this helps scale organizationally. More people can maintain existing transformations, and help introduce new variations.

From a performance standpoint, relying on ephemeral compute clusters is incredibly helpful to isolate computation, improve available resources, and to keep costs manageable. Snowflake Warehouses or AWS EMR clusters are excellent implementations and would scale for a long time.

As data volume goes up, and the need for predictive analytics becomes higher, then managed Spark via Databricks is highly scaleable and stable.

I have less experience with streaming SQL (such as kafka sql or firehose analytics), but that appears helpful for metrics that don't need a large lookback period, or for cases where aggregates can be referenced/joined via another stream.

### API

This I have less experience with, but from research it appears that hosting it via lambda (using the python Mangum library) is a potential way to keep costs low if lower performance is alright.

> **What if you had many users accessing your dashboard to view metrics?**

When the service needs to be more performant, moving onto AWS Fargate containers helps increase response time and helps with serving many more requests at a time. FastAPI appears to be a very well made and useful backend, and moving data from s3/athena to postgres and redis would dramatically improve response times.

Looking into 3rd party/hosted dashboard solutions is a reasonable alternative to building things in house, if something meets the business needs.

However, for self hosted solutions, other optimizations to help scale:

- introducing routing and multiple containers for high load
- looking at high performant servers instead of serverless architecture
- pre-computing everything that the app serves as much as possible (like a static website, but static/flattened database)
- adding caching where appropriate

## Extending Testing

Given another 5 hours on this project, most of it would be spent on expanding test coverage.

Integration tests are helpful but can be challenging to write, so I would expand on that coverage to make sure all aspects of each integration are covered.

End-to-end test coverage would also be added, to validate that an API call results in correct data transformations after all is said and done.

I would do a few more things here:

- introduce a file handling class, to make local development more seamless when s3 would be inconvenient to work with
- add black and pep8 pre-commit hooks to help with formatting and catching issues up front
- introduce CI/CD for the API portion - this may not be a great fit for AWS SAM's lambda development environment though. Generally those are deployed via cloudformation, and I'm not sure if that integrates well with continuous deployment.
- improve unit testing through mocking libraries and validating surprising API responses don't break things in weird ways
- create better dev, staging, and prod abstractions, so it's safe for developers to experiment

## Feature Request - Alerting on certain conditions

    Feature request: to help the user identify opportunities in real-time, the app will send an alert whenever a metric exceeds 3x the value of its average in the last 1 hour. For example, if the volume of GOLD/BTC averaged 100 in the last hour, the app would send an alert in case a new volume data point exceeds 300. Please write a short proposal on how you would implement this feature request.

The current architecture would support the data side easily. Current volume is already tracked, so we could add two new columns to the transformed data: average volume over the last hour and the current ratio (300% increase for example). For notifications, the easiest thing would be to register a few scenarios (such as volume growing 3x) and then use cloudwatch or a lambda function to check and monitor the ratio column for values that exceed the amount. They would trigger an SNS event when a ratio is exceeded.

I'm less familiar with how to actually ping the user when we have an SNS notification hits the queue. Presumably we would need a subscriber list that cares about a particular metric, and a way to notify them that it has been exceeded (such as an SMS service or open websocket).

It would be fun to sketch out how this would be done with *n* alerts and *n* users - providing users a way to alert on any condition they can query. Presumably this has been architected before, so I'd research approaches published online.















