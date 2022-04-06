from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv("electricity.csv")

avg_price_each_state = (
    df.groupby("US_State").agg({"Residential Price": "mean"}).reset_index()
)
us_map_fig = px.choropleth(
    data_frame=avg_price_each_state,
    locations="US_State",
    locationmode="USA-states",
    scope="usa",
    color="Residential Price",
    color_continuous_scale="reds",
)

year_min = df["Year"].min()
year_max = df["Year"].max()

app = Dash()

app.layout = html.Div(
    [
        html.H1("Electricity Prices by US States"),
        dcc.Graph(id="map-graph", figure=us_map_fig),
        dcc.RangeSlider(
            id="year-slider",
            min=year_min,
            max=year_max,
            value=[year_min, year_max],
            marks={f"{i}": f"{i}" for i in range(year_min, year_max + 1)},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
