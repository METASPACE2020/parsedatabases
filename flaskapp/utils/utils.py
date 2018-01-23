import urllib.request
import json
import plotly.graph_objs as go
import requests


def get_config():
    return json.load(open("config.json"))


def _query(config, query, variables={}):
    res = requests.post(config['graphql_url'],
                        json={'query': query, 'variables': variables})
    return _extract_data(res)


def _extract_data(res):
    if not res.headers.get('Content-Type').startswith('application/json'):
        raise Exception(res.text)
    res_json = res.json()
    if 'data' in res_json:
        return res.json()['data']
    else:
        raise Exception(res.json()['errors'][0]['message'])


def getdbs(config):
    query = """
    query getMolecularDatabases  {
        molecularDatabases {
                id, name, version
                }
            }
        """
    data = _query(config, query, {})
    print(data)
    return data['molecularDatabases']


def getdbname(config, db_id):
    q = config['mol_db_url'] + 'databases/{}'.format(db_id)
    print(q)
    response = _extract_data(requests.get(q))
    return response["name"] + response["version"]


def getmf(config, db_id):
    q = config['mol_db_url'] + 'databases/{}/sfs'.format(db_id)
    response = _extract_data(requests.get(q))
    return response


def pie_chart(config, db1_id, db2_id):
    print(db1_id, db2_id)
    mf = [set(getmf(config, db_id)) for db_id in [db1_id, db2_id]]
    labels = [getdbname(config, db_id) for db_id in [db1_id, db2_id]] + ['both', ]
    values = [len(mf[0] - mf[1]), len(mf[1] - mf[0]), len(mf[0] & mf[1])]
    colors = ['#FEBFB3', '#E1396C', '#96D38C']

    traces = [go.Pie(labels=labels, values=values,
                     hoverinfo='label+percent', textinfo='value',
                     textfont=dict(size=20),
                     marker=dict(colors=colors,
                                 line=dict(color='#000000', width=2)))
              ]
    return traces
