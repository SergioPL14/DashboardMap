import plotly.express as px
import yaml
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import mapUtils as mu

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"
json_body = {'username': config['user'], 'password': config['pwd']}

app = Dash(__name__)

mapInfo = mu.getMapInfo()

fig = px.scatter_mapbox(mapInfo, lat="latitude", lon="longitude", color="Colour", size="SizeDots", color_discrete_map={
    "grey": "grey",
    "green": "green",
    "yellow": "yellow",
    "grey": "grey",
    "black": "black",
    "lightgreen": "lightgreen",
    "black": "black"},
                        hover_data=["StudyNumber", "Country", "Status", "id", "Address"], custom_data=["url"], zoom=2,
                        height=900)

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

                Find below the link to the Veeva Vault page of the selected site.
            """)
        ])
        ,
        html.Div(id='selected-data')
    ])
])


@app.callback(
    Output('selected-data', 'children'),
    Input('dashboard-map', 'selectedData')
)
def display_selected_data(selectedData):
    try:
        return html.A(selectedData["points"][0]["customdata"][0], href=selectedData["points"][0]["customdata"][0],
                      target="_blank")
    except Exception as e:
        return "No site selected."


if __name__ == '__main__':
    app.run(host='0.0.0.0')
