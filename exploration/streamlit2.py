import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta


def load_data():
    # Load sensor data from parquet file
    df = pd.read_parquet("../data/interim/data_all.parquet")
    return df


def main():
    st.title("Sensor Data Comparison")

    # Load data
    df = load_data()

    # Get unique sensor IDs
    sensor_ids = sorted(df["dev-id"].unique())

    # Create layout with columns
    col1, col2 = st.columns(2)

    # Sensor selection
    with col1:
        sensor1 = st.selectbox("Select first sensor", sensor_ids, key="sensor1")

    with col2:
        sensor2 = st.selectbox("Select second sensor", sensor_ids, key="sensor2")

    # Measurement type selection
    measurement_type = st.selectbox("Select measurement type", ["temperature", "humidity"])

    # Date range selection
    col3, col4 = st.columns(2)

    with col3:
        start_date = st.date_input("Start date", df.index.min().date())

    with col4:
        end_date = st.date_input("End date", df.index.max().date())

    # Convert dates to datetime
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + timedelta(days=1)  # Include the end date

    print(start_datetime, end_datetime)
    # Make sure start_datetime and end_datetime are timezone aware
    start_datetime = start_datetime.tz_localize("UTC")
    end_datetime = end_datetime.tz_localize("UTC")
    # Filter data based on selection and calculate hourly averages
    data1 = df[df["dev-id"] == sensor1].loc[start_datetime:end_datetime]
    data2 = df[df["dev-id"] == sensor2].loc[start_datetime:end_datetime]

    # Resample to hourly averages
    data1_hourly = data1[measurement_type].resample("1h").mean()
    data2_hourly = data2[measurement_type].resample("1h").mean()

    # Create merged dataset for scatter plot
    merged_data = pd.DataFrame(
        {f"{measurement_type}_sensor1": data1_hourly, f"{measurement_type}_sensor2": data2_hourly}
    ).dropna()  # Remove any hours where either sensor has no data

    if not merged_data.empty:
        # Lisätään aikaleima indeksistä omaksi sarakkeeksi tooltippiä varten
        merged_data["timestamp"] = merged_data.index.strftime("%Y-%m-%d %H:%M")

        # Lisätään tuntitieto värikoodausta varten
        merged_data["hour"] = merged_data.index.hour

        # Päivitetty scatter plot
        fig = px.scatter(
            merged_data,
            x=f"{measurement_type}_sensor1",
            y=f"{measurement_type}_sensor2",
            color="hour",  # Värikoodaus tunnin mukaan
            color_continuous_scale=[
                [0.0, "darkblue"],  # 00:00
                [0.25, "skyblue"],  # 06:00
                [0.5, "yellow"],  # 12:00
                [0.75, "orange"],  # 18:00
                [1.0, "darkblue"],  # 24:00
            ],
            labels={
                f"{measurement_type}_sensor1": f"{sensor1} {measurement_type}",
                f"{measurement_type}_sensor2": f"{sensor2} {measurement_type}",
                "hour": "Time of day",  # Väripalkin otsikko
            },
            title=f"Comparison of hourly average {measurement_type} measurements",
            hover_data=["timestamp"],
        )

        # Muokataan väripalkin asetuksia
        fig.update_coloraxes(
            colorbar_ticktext=["00:00", "06:00", "12:00", "18:00", "24:00"], colorbar_tickvals=[0, 6, 12, 18, 24]
        )

        # Asetetaan kuvasuhde 1:1
        fig.update_layout(
            width=600,  # Voit säätää kokoa tarpeen mukaan
            height=600,
            yaxis=dict(
                scaleanchor="x",
                scaleratio=1,
            ),
        )

        # Add identity line
        min_val = min(
            merged_data[f"{measurement_type}_sensor1"].min(), merged_data[f"{measurement_type}_sensor2"].min()
        )
        max_val = max(
            merged_data[f"{measurement_type}_sensor1"].max(), merged_data[f"{measurement_type}_sensor2"].max()
        )
        fig.add_scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            name="Identity line",
            line=dict(dash="dash", color="gray"),
        )

        # Display the plot
        st.plotly_chart(fig)

        # Display basic statistics
        st.subheader("Basic Statistics (Hourly Averages)")
        col5, col6 = st.columns(2)

        with col5:
            st.metric(
                f"Average {measurement_type} (Sensor 1)", f"{merged_data[f'{measurement_type}_sensor1'].mean():.1f}"
            )
            st.metric("Number of hours", len(merged_data))

        with col6:
            st.metric(
                f"Average {measurement_type} (Sensor 2)", f"{merged_data[f'{measurement_type}_sensor2'].mean():.1f}"
            )
            correlation = merged_data[f"{measurement_type}_sensor1"].corr(merged_data[f"{measurement_type}_sensor2"])
            st.metric("Correlation", f"{correlation:.3f}")
    else:
        st.warning("No overlapping data found for the selected sensors and time period.")


if __name__ == "__main__":
    main()
