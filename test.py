from serpapi import GoogleSearch
import plotly as plotly
import pandas as pd
import json
import plotly.express as px
from flask import Flask, render_template, request
params = {
  "engine": "google_scholar_author",
  "author_id": "GfuDovEAAAAJ",
  "api_key": "aa7ea17b21a4546a1ae56a6ff309c092520a60157353380f06e119f9133b2f18"
}

search = GoogleSearch(params)
results = search.get_dict()
cited_by = results["cited_by"]['graph']
print((cited_by))


def notdash(data=cited_by):
  df = pd.DataFrame(data)
  fig = px.bar(df, x='year', y='citations',
               barmode='group')
  graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
  print(graphJSON)
  return graphJSON

#notdash()