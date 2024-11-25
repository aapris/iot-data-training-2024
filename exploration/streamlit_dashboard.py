from datetime import timedelta

import streamlit as st
import pandas as pd
import altair as alt

from fvhdata.utils.constants import INTERIM


def app_title():
    st.title("Interactive Sensor Data Visualization")
    st.markdown(
        """
        Analyze sensor data interactively by exploring temperature and humidity
        averages per sensor. Use the filters to adjust the visualization dynamically.
        """
    )


@st.cache_data(ttl=timedelta(hours=1))
def load_data(parquet_path):
    return pd.read_parquet(parquet_path)


def aggregate_data(df):
    return df.groupby("dev-id").median().reset_index()


def add_sidebar_filters(aggregated):
    st.sidebar.header("Filters")

    # Device ID filter
    unique_ids = aggregated["dev-id"].unique().tolist()
    selected_ids = st.sidebar.multiselect("Select Device IDs", unique_ids, default=unique_ids)

    # Temperature range filter
    min_temp, max_temp = st.sidebar.slider(
        "Temperature Range",
        float(aggregated["temperature"].min()),
        float(aggregated["temperature"].max()),
        (float(aggregated["temperature"].min()), float(aggregated["temperature"].max())),
    )

    # Humidity range filter
    min_humidity, max_humidity = st.sidebar.slider(
        "Humidity Range",
        float(aggregated["humidity"].min()),
        float(aggregated["humidity"].max()),
        (float(aggregated["humidity"].min()), float(aggregated["humidity"].max())),
    )

    return selected_ids, min_temp, max_temp, min_humidity, max_humidity


def filter_data(aggregated, selected_ids, min_temp, max_temp, min_humidity, max_humidity):
    filtered = aggregated[
        (aggregated["dev-id"].isin(selected_ids))
        & (aggregated["temperature"] >= min_temp)
        & (aggregated["temperature"] <= max_temp)
        & (aggregated["humidity"] >= min_humidity)
        & (aggregated["humidity"] <= max_humidity)
    ]
    # Rename columns for better tooltip labels
    return filtered.rename(columns={"temperature": "Average Temperature", "humidity": "Average Humidity"})


def create_altair_chart(filtered_data, padding=0.1):
    # Calculate padding for axes
    temp_min, temp_max = filtered_data["Average Temperature"].min(), filtered_data["Average Temperature"].max()
    hum_min, hum_max = filtered_data["Average Humidity"].min(), filtered_data["Average Humidity"].max()

    temp_range = temp_max - temp_min
    hum_range = hum_max - hum_min

    # Add padding to limits
    x_min = temp_min - (temp_range * padding)
    x_max = temp_max + (temp_range * padding)
    y_min = hum_min - (hum_range * padding)
    y_max = hum_max + (hum_range * padding)

    return (
        alt.Chart(filtered_data)
        .mark_circle(size=300)
        .encode(
            x=alt.X("Average Temperature", title="Average Temperature", scale=alt.Scale(domain=(x_min, x_max))),
            y=alt.Y("Average Humidity", title="Average Humidity", scale=alt.Scale(domain=(y_min, y_max))),
            color=alt.Color("dev-id:N", legend=alt.Legend(title="Device IDs")),
            tooltip=[
                "dev-id",
                alt.Tooltip("Average Temperature", title="Average Temperature"),
                alt.Tooltip("Average Humidity", title="Average Humidity"),
            ],
        )
        .properties(width=800, height=600, title="Average Temperature vs. Humidity (Interactive)")
        .interactive()
    )


def main():
    # st.set_page_config(layout="wide")
    app_title()

    df = load_data(INTERIM.joinpath("data_all.parquet"))
    aggregated = aggregate_data(df)

    selected_ids, min_temp, max_temp, min_humidity, max_humidity = add_sidebar_filters(aggregated)
    filtered_data = filter_data(aggregated, selected_ids, min_temp, max_temp, min_humidity, max_humidity)

    if not filtered_data.empty:
        st.subheader("Interactive Scatter Plot")
        st.altair_chart(create_altair_chart(filtered_data))
    else:
        st.warning("No data matches the selected filters. Adjust the filters to display the plot.")


if __name__ == "__main__":
    main()
