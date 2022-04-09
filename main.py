from dash import Dash, dcc, html, dash_table, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv("electricity.csv")

year_min = df["Year"].min()
year_max = df["Year"].max()

app = Dash(
    external_stylesheets=[dbc.themes.LUX],
    title="Avg Electricity Prices in the US",
)

app.layout = html.Div(
    [
        html.Nav(
            [
                html.H1(
                    "Electricity Prices by US States",
                    style={"padding": "0.5rem 1rem", "color": "#F5F5F5"},
                ),
                dcc.RangeSlider(
                    id="year-slider",
                    min=year_min,
                    max=year_max,
                    value=[year_min, year_max],
                    marks={
                        f"{i}": f"{i}" for i in range(year_min, year_max + 1)
                    },
                    className="form-range",
                ),
            ],
            className="navbar navbar-dark bg-dark",
        ),
        html.Div(
            html.Div(
                [
                    dcc.Graph(
                        id="map-graph",
                        style={"width": "100%", "height": "100%"},
                    ),
                ],
                style={
                    "width": "100%",
                    "height": "100%",
                },
            ),
            style={
                "width": "70%",
                "height": "800px",
                "margin": "auto",
                "display": "block",
                # "border": "3px #5c5c5c solid",
                "overflow": "hidden",
            },
        ),
        dash_table.DataTable(
            id="info-table",
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
        ),
    ]
)


def query_dataframe_by_years(data_frame, years_range):
    """
    Query the given DataFrame by years range (e.g. from 1990 to 2017).

    :param data_frame: the DataFrame to query.
    :type data_frame: pd.DataFrame
    :param years_range: a list of 2 integers represent the years to query for.
    :type years_range: list of int
    :return: a new DataFrame containing records from the selected years.
    :rtype: pd.DataFrame
    """
    return data_frame[
        (data_frame["Year"] >= years_range[0])
        & (data_frame["Year"] <= years_range[1])
    ]


def query_dataframe_by_state_name(data_frame, state_name):
    """
    Query the given DataFrame by the given name of any US state.

    :param data_frame: the DataFrame to query.
    :type data_frame: pd.DataFrame
    :param state_name: a name of any US state.
    :type state_name: str
    :return: a new DataFrame containing records of the desired state.
    :rtype: pd.DataFrame
    """
    return data_frame[data_frame["US_State"] == state_name]


def plot_map(data_frame):
    """
    Plot a choropleth map given the DataFrame. The given DataFrame must have
    a column contains two-letter state abbreviations and the
    `locationmode='USA-states'`.

    :param data_frame: the DataFrame to plot the map.
    :type data_frame: pd.DataFrame
    :return: a plot figure
    :rtype: plotly.graph_objects.Figure
    """
    us_map_fig = px.choropleth(
        data_frame=data_frame,
        locations="US_State",
        locationmode="USA-states",
        scope="usa",
        color="Residential Price",
        color_continuous_scale="reds",
    )
    return us_map_fig


@app.callback(
    Output(component_id="map-graph", component_property="figure"),
    Input(component_id="year-slider", component_property="value"),
)
def update_map_by_years_range(years_range: list):
    filtered_df = query_dataframe_by_years(df, years_range)
    avg_price_each_state = (
        filtered_df.groupby("US_State")
        .agg({"Residential Price": "mean"})
        .reset_index()
    )

    us_map_fig = plot_map(avg_price_each_state)
    return us_map_fig


@app.callback(
    Output(component_id="info-table", component_property="data"),
    Input(component_id="year-slider", component_property="value"),
    Input(component_id="map-graph", component_property="clickData"),
)
def update_datatable(years_range: list, clicked_data: dict):
    try:
        state_name = clicked_data["points"][0]["location"]
        df_by_years = query_dataframe_by_years(df, years_range)
        filtered_df = query_dataframe_by_state_name(df_by_years, state_name)
    except TypeError:
        filtered_df = query_dataframe_by_years(df, years_range)

    return filtered_df.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
