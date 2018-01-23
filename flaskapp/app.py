# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from utils import utils

config = utils.get_config()
app = dash.Dash()
#cache = Cache(app.server, config={
#    'CACHE_TYPE': 'filesystem',
#    'CACHE_DIR': 'cache'
#})

def dropdown(dbs, elid):
    return dcc.Dropdown(
        options=[
            {'label': db['name'] + " " + db['version'], 'value': db["id"]} for db in dbs
        ],
        value=[],
        id=elid,
    )

def generate_layout():
    dbs = utils.getdbs(config)
    return html.Div(children=[
        html.H1(children='Database Differences'),
        html.Div(id='hidden_data'),
        html.Div(children='''
            Compare two databases
        '''),
        dropdown(dbs, elid="dbs1"),
        dropdown(dbs, elid="dbs2"),
        dcc.Graph(
            id='pie-chart',
            figure={
                'data': [
                ],
                'layout': go.Layout(
                    xaxis={'title': 'adduct'},
                    yaxis={'title': 'number of molecular formula'},
                    title='Adducts annotated'
                )
            }
        )
    ])

app.layout = generate_layout

@app.callback(
    dash.dependencies.Output('pie-chart', 'figure'),
    [dash.dependencies.Input('dbs1', 'value'), dash.dependencies.Input('dbs2', 'value')]
)
def update_piechart(db1, db2):
    traces = utils.pie_chart(config, db1, db2)
    layout = {}
    payload = {"data": traces,
               "layout": layout}
    return payload




if __name__ == '__main__':
    app.run_server(debug=True)