import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# SQLite Configuration
SQLITE_DB = "/home/worpl/lab/greenhouse_data.db"
engine = create_engine(f"sqlite:///{SQLITE_DB}")

# Load all data for Greenhouse 1
def load_data():
    query = """
    SELECT * FROM greenhouse_data
    WHERE greenhouse_id = 1
    """
    df = pd.read_sql(query, engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Aggregate data into 2-hour intervals
def aggregate_data(df):
    if df.empty:
        return df

    df = df.drop_duplicates(subset="timestamp")
    df = df.set_index("timestamp")

    numeric_columns = ["value", "growth_rate"]
    aggregated = df[numeric_columns].resample("2H").mean()
    aggregated["sensor_type"] = df["sensor_type"].resample("2H").ffill()
    aggregated = aggregated.reset_index()

    return aggregated

# Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Greenhouse 1 Data Visualization"),
    dcc.Graph(id="temperature-graph"),
    dcc.Graph(id="humidity-graph"),
    dcc.Graph(id="growth-rate-graph"),
    dcc.Interval(id="interval-component", interval=60*1000, n_intervals=0)  # Auto-update every minute
])

@app.callback(
    [
        Output("temperature-graph", "figure"),
        Output("humidity-graph", "figure"),
        Output("growth-rate-graph", "figure"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_graphs(_):
    # Load and aggregate data
    df = load_data()
    df = aggregate_data(df)

    if df.empty:
        return (
            px.line(title="No data available for Temperature"),
            px.line(title="No data available for Humidity"),
            px.line(title="No data available for Growth Rate"),
        )

    # Filter data by sensor type
    temp_df = df[df["sensor_type"] == "temperature"]
    humidity_df = df[df["sensor_type"] == "humidity"]

    # Build figures
    temp_fig = px.line(
        temp_df,
        x="timestamp",
        y="value",
        title="Temperature (°C) - Aggregated Every 2 Hours",
        labels={"value": "Temperature (°C)", "timestamp": "Time"}
    )

    humidity_fig = px.line(
        humidity_df,
        x="timestamp",
        y="value",
        title="Humidity (%) - Aggregated Every 2 Hours",
        labels={"value": "Humidity (%)", "timestamp": "Time"}
    )

    growth_rate_fig = px.line(
        df,
        x="timestamp",
        y="growth_rate",
        title="Growth Rate (%) - Aggregated Every 2 Hours",
        labels={"growth_rate": "Growth Rate (%)", "timestamp": "Time"}
    )

    return temp_fig, humidity_fig, growth_rate_fig

if __name__ == "__main__":
    app.run_server(debug=True)
