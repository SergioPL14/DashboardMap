import plotly.express as px
import yaml
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from flask import request

import mapUtils as mu

# with open('config.yaml') as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)
# api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"
# json_body = {'username': config['user'], 'password': config['pwd']}

app = Dash(__name__)
server = app.server

# mapInfo = mu.getMapInfo()
#
# fig = px.scatter_mapbox(mapInfo, lat="latitude", lon="longitude", color="State", size="SizeDots",
#                         hover_data=["StudyNumber", "Country", "Status", "id", "Address"], color_discrete_map={
#         "closing_state__v": "grey",
#         "active_state__v": "green",
#         "candidate_state__v": "yellow",
#         "archived__v": "grey",
#         "not_selected_state__v": "black",
#         "initiating_state__v": "lightgreen",
#         "Non site": "black"}, custom_data=["url"], zoom=2, height=900)
#
# fig.update_layout(clickmode='event+select', mapbox_style="open-street-map", mapbox_zoom=2, mapbox_center_lat=41,
#                   margin={"r": 0, "t": 0, "l": 0, "b": 0})

app.layout = html.Div([
    # dcc.Graph(
    #     id='dashboard-map',
    #     figure=fig
    # ),

    # html.Div(className='row', children=[
    html.Div([
        dcc.Markdown("""
                **Study information**

                Find below the link to the Veeva Vault page of the selected site.
            """)
    ])
    # ,
    # html.Div(id='selected-data')
    # # ])
])


@app.callback(
    Output('selected-data', 'children'),
    Input('dashboard-map', 'selectedData'))
def display_selected_data(selectedData):
    try:
        item = selectedData["points"][0]["customdata"]
        return html.A(selectedData["points"][0]["customdata"][0], href=selectedData["points"][0]["customdata"][0],
                      target="_blank")
        # return html.A(selectedData["points"][0]["customdata"][0])
    except Exception as e:
        print("No selected data yet.")
        return "No site selected."


@server.post('/')
def background_process():
    try:
        msg = request.args.get('message', 0, type=str)
        return "############### MESSAGE RECEIVED ################" + msg
    except Exception as e:
        return "############### MESSAGE NOT RECEIVED ################"

    # return request.form.get('message')
    # return 'Hello, World!'


# @app.server('/', methods=['GET', 'POST'])
# def parse_request():
#     data = request.data  # data is empty
#     # need posted data here


# app.scripts.append_script({("""
# var parentDomain = '';
#
# window.addEventListener('message', (event) => {
#    console.log('message received from parent:  ' + event.data,event);
#    parentDomain = event.data;
# },false);
#     """)})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
