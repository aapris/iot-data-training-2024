import pandas as pd
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from fvhdata.utils.constants import INTERIM, FIGURES


plt.style.use("ggplot")

merged_parquet_path = INTERIM.joinpath("data_all.parquet")
df = pd.read_parquet(merged_parquet_path)

aggregated = df.groupby("dev-id").mean()

plt.figure(figsize=(12, 10))


unique_ids = aggregated.index
colors = cm.viridis([i / len(unique_ids) for i in range(len(unique_ids))])  # Colormap

for i, (dev_id, row) in enumerate(aggregated.iterrows()):
    plt.scatter(row["temperature"], row["humidity"], color=colors[i], s=100)
    plt.text(row["temperature"], row["humidity"], dev_id, fontsize=10)

plt.title("Average temperature vs. average humidity for each sensor")
plt.xlabel("Average temperature")
plt.ylabel("Average humidity")
plt.tight_layout()
plt.show()
plt.savefig(FIGURES.joinpath("average_temperature_humidity_per_sensor.png"))
