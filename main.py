import json

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import yaml
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import mapUtils as mu

# vault_domain_name = "candidate-tech-services---sergio.veevavault.com"
# version = "v22.1"
# user = "sergio.pina@candidate.com"
# pwd = "1MyPassword!"
#


with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"
json_body = {'username': config['user'], 'password': config['pwd']}

styles = {
    'pre': {
        'border': 'thin lightgrey solid'
    }
}

app = Dash(__name__)


def numbers_to_colours(argument):
    switcher = {
        0: "Inactive",
        1: "Active",
        2: "Archived",
    }
    return switcher.get(argument, "Non site")


mapInfo = mu.getMapInfo()

fig = px.scatter_mapbox(mapInfo, lat="latitude", lon="longitude", color="status__v", color_discrete_map={
    "Inactive": "orange",
    "active__v": "green",
    "Archived": "grey",
    "Non site": "black"}, custom_data=["id", "status__v", "address_line_1__clin", "url"], zoom=2, height=700)

fig.update_layout(clickmode='event+select', mapbox_style="open-street-map", mapbox_zoom=2, mapbox_center_lat=41,
                  margin={"r": 0, "t": 0, "l": 0, "b": 0})

app.layout = html.Div([
    dcc.Graph(
        id='dashboard-map',
        figure=fig
    ),

    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Study information**

                Find below the information regarding the selected site.
            """),
            html.Div(id='selected-data')
        ])
    ])
])


@app.callback(
    Output('selected-data', 'children'),
    Input('dashboard-map', 'selectedData'))
def display_selected_data(selectedData):
    try:
        return selectedData["points"][0]["customdata"] #["url"]
    except Exception as e:
        print("No selected data yet.")
        return "No site selected."


if __name__ == '__main__':
    app.run(host='0.0.0.0')
