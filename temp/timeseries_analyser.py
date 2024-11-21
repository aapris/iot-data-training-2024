import argparse
import datetime
import logging
import pathlib
from typing import Optional

import isodate
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--device-ids", nargs="+", required=False, help="List of device ids or file with device ids")
    parser.add_argument("--start-time", help="Start datetime (with UTC offset) for data")
    parser.add_argument("--end-time", help="End datetime (with UTC offset) for data")
    parser.add_argument("--data", help="Data file(s) to read", nargs="+")
    parser.add_argument("--groupby", required=True, help="Group by column")
    parser.add_argument("--resample", help="Resample data to frequency (e.g. 1H, 1D)")
    # parser.add_argument("--date", help="Date (UTC) for data (YYYY-MM-DD, yesterday, today)")
    # parser.add_argument("--month", help="Month for data (YYYY-MM)")
    # parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=getattr(logging, args.log))
    if args.start_time:
        start_time = isodate.parse_datetime(args.start_time)
    else:  # Default to 7 days ago, using aware UTC datetime
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    if args.end_time:
        end_time = isodate.parse_datetime(args.end_time)
    else:  # Default to now, using aware UTC datetime
        end_time = datetime.datetime.now(datetime.timezone.utc)
    args.start_time = start_time
    args.end_time = end_time
    # If device-ids is a file, read the file and replace the list of device ids
    if args.device_ids:  # Use pathlib to check whether it is a file
        device_ids = []
        for device_id in args.device_ids:
            if pathlib.Path(device_id).is_file():
                with open(device_id) as f:
                    device_ids.extend(f.read().splitlines())
            else:
                device_ids.append(device_id)
        args.device_ids = device_ids
    return args


def normalize_column(column: pd.Series, max_val: Optional[float] = None) -> pd.Series:
    """
    Normalize a column to values between 0 and 1.
    If value is -1, it is considered as missing value and is not normalized.
    Usage: df = df.apply(normalize_column)
    :param max_val: maximum value for normalization (optional)
    :param column: pd.Series
    :return: pd.Series
    """
    min_val = 0  # we know that the minimum value can be 0
    # Pick indices where value is -1
    missing_indices = column[column == -1].index
    if max_val is None:
        max_val = column.max()
    normalized_column = (column - min_val) / (max_val - min_val)
    # Replace missing values with -1
    normalized_column.loc[missing_indices] = -1
    return normalized_column


def read_data(data_files: list) -> pd.DataFrame:
    """
    Read parquet files from data_files into a DataFrame
    :param data_files: list of file names
    :return: pd.DataFrame
    """
    dfs = []
    for filename in data_files:
        dfs.append(pd.read_parquet(filename))
    # Concatenate all DataFrames into one
    df = pd.concat(dfs)
    return df


def visualize_daily_measurement_counts_per_sensor(df_resampled: pd.DataFrame) -> None:
    # TODO: Add more descriptive labels for sensors
    order = df_resampled.mode().max().sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.boxplot(data=df_resampled, ax=ax, orient="h", order=order)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    fontsize = 18
    ax.set_xlabel("Number of daily measurements", fontsize=fontsize)
    ax.set_ylabel("Sensor", fontsize=fontsize)
    ax.set_title("Sensor reliability assessment: box plot of daily measurement counts", fontsize=fontsize)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, color="#cccccc")
    plt.tight_layout()
    plt.savefig("boxplots.png")


def main():
    args = get_args()
    # Read parquet files from args.data into a DataFrame
    df = read_data(args.data)
    # Drop all columns except args.groupby
    df = df[[args.groupby]]
    # Set value to 0 in all rows where datapoint_id is between 145346 and 145901
    # df = df[df[args.groupby].between("145346", "145901")]
    # Replace NaN values with 0
    df = df.fillna(0)

    # Remove all rows where index is between 2024-07-30 and 2024-08-07
    # df = df[~df.index.to_series().between("2024-07-30", "2024-08-07")]
    df = df[~df.index.to_series().between("2024-09-01", "2024-09-12")]

    print(df.info())
    print(df.head(20))

    # Drop all rows where datapointid is not in args.device_ids
    if args.device_ids:
        df = df[df[args.groupby].isin(args.device_ids)]
    print(df.info())
    print(df.head(20))
    df_resampled = df.resample(args.resample)[args.groupby].value_counts()
    df_resampled = df_resampled.unstack()
    ## Replace all NaN values with 0 # Does not work
    ## df_resampled = df_resampled.fillna(0)
    # Replace all values greater than 1440 with -1
    # df_resampled = df_resampled.where(df_resampled <= 1440, -1)
    # Show all rows where any of the column contains values less than 0
    # print(df_resampled[(df_resampled < 0).any(axis=1)])
    # print(df_resampled)
    # exit()
    # Take math.log of all values
    # df_resampled = np.log(df_resampled)

    visualize_daily_measurement_counts_per_sensor(df_resampled)

    max_val = df_resampled.max().max()
    mean_val = df_resampled.mean().mean()
    median_val = df_resampled.median().median()
    print(f"Max value: {max_val}")
    print(f"Mean value: {mean_val}")
    print(f"Median value: {median_val}")
    # Replace all values greater than median with median
    # new_max = median_val * 2
    # df_resampled = df_resampled.replace(max_val, new_max)
    # df_resampled = df_resampled.where(df_resampled <= median_val, new_max)
    max_val = df_resampled.max().max()
    print(f"New max value: {max_val}")

    # df_resampled = df_resampled.apply(normalize_column, max_val=max_val)
    # print(list(df_resampled["144766"]))
    df_resampled = df_resampled.apply(normalize_column)
    print(df_resampled)
    print(df_resampled.info())
    fig, ax = plt.subplots(figsize=(15, 8))

    # Create a custom color map
    # cmap = mcolors.ListedColormap(
    #     ["#808080", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837"]
    # )
    # bounds = [-1, 0, 0.25, 0.5, 0.75, 1]
    # norm = mcolors.BoundaryNorm(bounds, cmap.N)
    # sns.heatmap(df_resampled, cmap=cmap, norm=norm, cbar_kws={"ticks": bounds})
    # Original
    sns.heatmap(df_resampled, cmap="RdYlGn")
    ax.set(xlabel={args.groupby}, ylabel="Date", title=f"Measurements per {args.groupby} over {args.resample}")
    ticklabels = [df_resampled.index[int(tick)].strftime("%Y-%m-%d") for tick in ax.get_yticks()]
    ax.set_yticklabels(ticklabels)
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    plt.savefig("heatmap.png", dpi=300)
    # plt.savefig("heatmap.pdf", dpi=600)
    plt.show()


if __name__ == "__main__":
    main()
    exit()
