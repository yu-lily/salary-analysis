from flask import Flask, render_template, request
import pandas as pd
import json
import plotly
import plotly.express as px
app = Flask(__name__)

df = pd.read_csv('../data/processed.tsv', sep='\t')

locations = df['location'].value_counts()[:10].index.tolist()
genders = df['gender'].value_counts()[:10].index.tolist()
companies = df['company'].value_counts()[:10].index.tolist()
countries = df['country'].value_counts()[:10].index.tolist()

df = df[df['yoe_total'] <= 10]
df = df[df['degree'] != 'phd']


@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return create_vis(request.args)
   
@app.route('/')
def index():
    return render_template('index.html',  graphJSON=create_vis(), locations=locations, genders=genders, companies=companies, countries=countries)

def create_vis(args={}):
    location = args.get('location', None)
    gender = args.get('gender', None)
    company = args.get('company', None)
    country = args.get('country', None)
    temp_df = df
    if location and location != 'All':
        temp_df = temp_df[temp_df['location'] == location]
    if gender and gender != 'All':
        temp_df = temp_df[temp_df['gender'] == gender]
    if company and company != 'All':
        temp_df = temp_df[temp_df['company'] == company]
    if country and country != 'All':
        temp_df = temp_df[temp_df['country'] == country]
    n = len(temp_df)
    grped = temp_df.groupby(['degree', 'yoe_total']).agg({'tc': ['mean', 'median', 'std']})
    grped.columns = grped.columns.map('_'.join)
    grped['lower'] = grped['tc_mean'] - grped['tc_std']
    grped['upper'] = grped['tc_mean'] + grped['tc_std']
    
    fig = px.line(grped,
        x=grped.index.get_level_values('yoe_total'),
        y='tc_mean',
        color=grped.index.get_level_values('degree'),
        labels={
            "x": "Years of Experience",
            "tc_mean": "Total Compensation ($)",
            "color": "Degree Level"
        },
        title="Compensation by Degree Level and Years of Experience")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return {'plot': graphJSON, 'n': n}