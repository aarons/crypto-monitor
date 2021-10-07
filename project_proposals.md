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





