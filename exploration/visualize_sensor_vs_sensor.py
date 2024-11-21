import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import argparse
from pathlib import Path

from fvhdata.utils.constants import INTERIM, FIGURES

# https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html
plt.style.use("ggplot")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Compare sensor measurements")
    parser.add_argument("--start", type=str, default="2024-06-26", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2024-11-01", help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--sensor-pairs", nargs="+", default=["6619,6635"], help='Comma-separated sensor ID pairs (e.g., "6619,6635")'
    )
    parser.add_argument("--output-dir", type=Path, default=FIGURES, help="Output directory for figures")
    return parser.parse_args()


def pre_process_time_series(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    df = df.loc[(df.index >= start) & (df.index < end)]
    df = df[["temperature", "humidity"]].sort_index().resample("1h", label="right", closed="right").mean()
    return df


def create_comparison_plot(
    sensor1_data: pd.DataFrame,
    sensor2_data: pd.DataFrame,
    sensor1_label: str,
    sensor2_label: str,
    sensor_type: str,
    start: str,
    end: str,
    output_dir: Path,
) -> None:
    """Create comparison scatter plot with additional statistics."""
    fig, ax = plt.subplots(figsize=(12, 10))
    x = sensor1_data[sensor_type]
    y = sensor2_data[sensor_type]

    # Add time-based coloring
    times = sensor1_data.index.hour
    scatter = plt.scatter(x=x, y=y, c=times, alpha=0.5, cmap="twilight")
    plt.colorbar(scatter, label="Hour of day")

    # Add identity line
    ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c="black", label="1:1 line")

    # Calculate statistics
    correlation = x.corr(y)
    rmse = np.sqrt(((x - y) ** 2).mean())
    bias = (x - y).mean()

    # Add statistics to plot
    stats_text = f"Correlation: {correlation:.3f}\n" f"RMSE: {rmse:.3f}\n" f"Bias: {bias:.3f}"
    ax.text(
        0.05,
        0.95,
        stats_text,
        transform=ax.transAxes,
        bbox=dict(facecolor="white", alpha=0.8),
        verticalalignment="top",
        fontsize=12,
    )

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
    plt.show()
    plt.savefig(output_dir.joinpath(f"sensor_vs_sensor_{sensor_type}_{sensor1_label}_{sensor2_label}.png"))
    plt.close()


def main():
    args = parse_arguments()

    # Load data
    df = pd.read_parquet(INTERIM.joinpath("data_all.parquet"))

    # Define sensor mappings
    sensor_mapping = {
        "6157": "Yliskylä (asfaltti)",
        "6167": "Kruunuvuorenranta (asfaltti)",
        "6198": "Jollas (metsä)",
        "6080": "Koivukylä (metsä)",
        "6155": "Koivukylä (asfaltti)",
        "6619": "Mäkelänkatu (asfaltti)",
        "6635": "Mäkelänkatu (puisto)",
    }

    # Process each sensor pair
    for pair in args.sensor_pairs:
        sensor1_id, sensor2_id = pair.split(",")

        sensor1_data = df.loc[df["dev-id"].str.endswith(sensor1_id)]
        sensor2_data = df.loc[df["dev-id"].str.endswith(sensor2_id)]

        sensor1_data = pre_process_time_series(sensor1_data, args.start, args.end)
        sensor2_data = pre_process_time_series(sensor2_data, args.start, args.end)

        for sensor_type in ["temperature", "humidity"]:
            create_comparison_plot(
                sensor1_data,
                sensor2_data,
                sensor_mapping[sensor1_id],
                sensor_mapping[sensor2_id],
                sensor_type,
                args.start,
                args.end,
                args.output_dir,
            )


if __name__ == "__main__":
    main()
