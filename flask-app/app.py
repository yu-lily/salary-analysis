from flask import Flask, render_template, request
import pandas as pd
import json
import plotly
import plotly.express as px
app = Flask(__name__)

df = pd.read_csv('../data/processed.tsv', sep='\t')

locations = df['location'].value_counts()[:10].index.tolist()

df = df[df['yoe_total'] <= 10]
df = df[df['degree'] != 'phd']




@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return create_vis(request.args.get('data'))
   
@app.route('/')
def index():
    return render_template('index.html',  graphJSON=create_vis(), locations=locations)

def create_vis(location = 'San Francisco, CA'):
    temp_df = df[df['location'] == location]
    grped = temp_df.groupby(['degree', 'yoe_total']).agg({'tc': ['mean', 'count', 'median', 'std']})
    grped.columns = grped.columns.map('_'.join)
    grped['lower'] = grped['tc_mean'] - grped['tc_std']
    grped['upper'] = grped['tc_mean'] + grped['tc_std']
    
    fig = px.line(grped, x=grped.index.get_level_values('yoe_total'), y='tc_mean', color=grped.index.get_level_values('degree'))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON
