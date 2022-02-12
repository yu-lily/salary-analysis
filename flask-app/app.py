from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
app = Flask(__name__)
@app.route('/')
def index():
    df = pd.read_csv('../data/processed.tsv', sep='\t')
    
    fig = px.scatter(df, x='yoe_total', y='tc')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)