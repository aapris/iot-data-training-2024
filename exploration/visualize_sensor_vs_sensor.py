import pandas as pd
from matplotlib import pyplot as plt

from fvhdata.utils.constants import INTERIM, FIGURES


# https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html
plt.style.use("ggplot")

merged_parquet_path = INTERIM.joinpath("data_all.parquet")
df = pd.read_parquet(merged_parquet_path)


def pre_process_time_series(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    df = df.loc[(df.index >= start) & (df.index < end)]
    df = df[["temperature", "humidity"]].sort_index().resample("1h", label="right", closed="right").mean()
    return df


start = "2024-06-26"
end = "2024-11-01"

sensor1_label = "Mäkelänkatu (asfaltti)"
sensor1_data = df.loc[df["dev-id"].str.endswith("6619")]
assert sensor1_data["dev-id"].nunique() == 1
sensor1_data = pre_process_time_series(sensor1_data, start, end)

sensor2_label = "Jollas (metsä)"
sensor2_data = df.loc[df["dev-id"].str.endswith("6198")]
assert sensor2_data["dev-id"].nunique() == 1
sensor2_data = pre_process_time_series(sensor2_data, start, end)

assert sensor1_data.shape == sensor2_data.shape

for sensor_type in ["temperature", "humidity"]:
    fig, ax = plt.subplots(figsize=(10, 10))
    x = sensor1_data[sensor_type]
    y = sensor2_data[sensor_type]
    # TODO: Change marker and/or color by day/night, for example
    plt.scatter(x=x, y=y, alpha=0.5)
    ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c="black")

    minimum = pd.concat((x, y)).min()
    maximum = pd.concat((x, y)).max()
    ax.set_xlim(minimum, maximum)
    ax.set_ylim(minimum, maximum)

    fontsize = 18
    ax.set_xlabel(f"{sensor_type.title()}, {sensor1_label}", fontsize=fontsize)
    ax.set_ylabel(f"{sensor_type.title()}, {sensor2_label}", fontsize=fontsize)
    ax.set_title(
        f"{sensor1_label} vs. {sensor2_label}\nSensor type: {sensor_type}\nTimeframe: [{start}, {end}]",
        fontsize=fontsize,
    )
    plt.tight_layout()
    plt.savefig(FIGURES.joinpath(f"sensor_vs_sensor_{sensor_type}.png"))
