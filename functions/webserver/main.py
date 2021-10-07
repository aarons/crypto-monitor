from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# TODO: look into pyathena package for database connectivity (https://pypi.org/project/pyathena/)
# TODO: add simple dropdown to choose which asset to graph: (select distinct(asset))
# TODO: add a query that computes window functions for various price and volume metrics
# TODO: understand how chart.js works for visualizing data

@app.get("/")
async def root():
  return {"message": "Lots to do still!"}

lambda_handler = Mangum(app)
