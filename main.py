import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import json

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
us_cities = us_cities.query("State in ['New York', 'Ohio']")

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


us_cities['Status'] = np.random.randint(0, 3, us_cities.shape[0])
us_cities['Status'] = us_cities['Status'].apply(numbers_to_colours)
us_cities['Links'] = "https://www.google.com"
print(us_cities)

fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", color="Status", color_discrete_map={
    "Inactive": "orange",
    "Active": "green",
    "Archived": "grey",
    "Non site": "black"}, custom_data=["City", "State", "Links"], zoom=3, height=700)

fig.update_layout(clickmode='event+select', mapbox_style="open-street-map", mapbox_zoom=4, mapbox_center_lat=41,
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
        # print(selectedData["points"][0]["customdata"])
        items = selectedData["points"][0]["customdata"]
        # for i, item in enumerate(items):
        #     item = item + ", "
        #     items[i] = item
        # return items[2]
        print(items[2])
        return html.Div([dcc.Markdown("""Info: 
        """ + items[0] + """,
        """ + items[1]), html.A(items[2], href=items[2], target="_blank")])
    except Exception as e:
        print("No selected data yet.")
        # return json.dumps(selectedData, indent=2)
        return "No site selected."


if __name__ == '__main__':
    app.run_server(debug=True)
