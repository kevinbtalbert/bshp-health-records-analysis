import os
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Load data
conditions_path = '/home/cdsw/exported-data/hl7_condition.csv'
claims_path = '/home/cdsw/exported-data/hl7_claims.csv'

conditions_df = pd.read_csv(conditions_path)
claims_df = pd.read_csv(claims_path)


# Step 3: Data Preprocessing
# Example: Standardize column names, handle missing data, etc.
def preprocess_data(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip('"')
    return df

conditions_df = preprocess_data(conditions_df)
claims_df = preprocess_data(claims_df)


# Remove quotation marks and strip whitespaces if any
conditions_df['onsetdatetime'] = conditions_df['onsetdatetime'].str.strip('"').str.strip()
conditions_df['onsetdatetime'] = pd.to_datetime(conditions_df['onsetdatetime'], errors='coerce')
conditions_df['year'] = conditions_df['onsetdatetime'].dt.year
conditions_df['month'] = conditions_df['onsetdatetime'].dt.month

# Filtering to Prediabetes conditions
prediabetes_df = conditions_df[conditions_df['condition_display'].str.contains('Prediabetes', na=False)]

# Dashboard setup
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Prediabetes Management Dashboard"),
    dcc.Tabs(id="tabs", value='tab-heatmap', children=[
        dcc.Tab(label='Heatmap', value='tab-heatmap'),
        dcc.Tab(label='Line Graph', value='tab-linegraph'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-heatmap':
        heatmap_data = prediabetes_df.groupby(['year', 'month']).size().reset_index(name='counts')
        heatmap_fig = px.density_heatmap(heatmap_data, x='month', y='year', z='counts', histfunc="sum", title="Heatmap of Diagnoses by Month and Year")
        return dcc.Graph(figure=heatmap_fig)
    elif tab == 'tab-linegraph':
        line_data = prediabetes_df.groupby('onsetdatetime').size().resample('M').sum().reset_index(name='counts')
        line_fig = px.line(line_data, x='onsetdatetime', y='counts', title="Monthly Trend of Prediabetes Diagnoses")
        return dcc.Graph(figure=line_fig)
    else:
        return dash_no_update
    
if __name__ == '__main__':
    app.run_server(debug=True, port=int(os.getenv('CDSW_APP_PORT')))