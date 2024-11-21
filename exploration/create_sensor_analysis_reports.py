import pandas as pd
from ydata_profiling import ProfileReport

from fvhdata.utils.constants import INTERIM, REPORTS


merged_parquet_path = INTERIM.joinpath("data_all.parquet")
df = pd.read_parquet(merged_parquet_path)
# Move the index to a "time" column, so it can be referenced
# in the "sortby" parameter of ProfileReport.
df = df.reset_index()

out_dir = REPORTS.joinpath("ydata-profiling")
out_dir.mkdir(parents=True, exist_ok=True)

for i, sensor_name in enumerate(df["dev-id"].unique(), start=1):
    print(f"\nCreating sensor analysis report {i}/{df['dev-id'].nunique()}")
    sensor_data = df.loc[df["dev-id"] == sensor_name, df.columns.drop("dev-id")]

    # Keep only part of the data to speed up the processing
    sensor_data = sensor_data.tail(10_000)
    # Alternatively, filter by start & end date
    # start = "2024-10-01"
    # end = "2024-11-01"
    # sensor_data = sensor_data.loc[(sensor_data["time"] >= start) & (sensor_data["time"] < end)]

    # https://docs.profiling.ydata.ai/latest/features/time_series_datasets/
    # Automatically identify time-series variables cia "tsmode" parameter.
    # Chronologically order the time-series via "sortby" parameter.
    profile = ProfileReport(sensor_data, tsmode=True, sortby="time", title=f"Time-series EDA of sensor {sensor_name}")

    profile.to_file(out_dir.joinpath(f"report_timeseries_{sensor_name}.html"))
