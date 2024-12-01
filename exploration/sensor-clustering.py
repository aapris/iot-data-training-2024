import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import sys


def load_and_prepare_data(file_path):
    """
    Load sensor data and prepare it for clustering analysis
    """
    # Read the parquet file
    df = pd.read_parquet(file_path)
    # Take df.index as time column
    df["time"] = df.index
    # Filter out measurements outside of 2024-07-01 and 2024-08 -31
    df = df[(df["time"] >= "2024-07-01") & (df["time"] <= "2024-08-31")]

    # Convert time column to datetime if not already in datetime format
    # if not pd.api.types.is_datetime64_any_dtype(df['time']):
    #    df['time'] = pd.to_datetime(df['time'])

    # Pivot the data to get sensors as columns
    temp_df = df.pivot(index="time", columns="dev-id", values="temperature").reset_index()
    humid_df = df.pivot(index="time", columns="dev-id", values="humidity").reset_index()

    return temp_df, humid_df


def calculate_sensor_features(temp_df, humid_df):
    """
    Calculate statistical features for each sensor
    """
    features = []

    # Skip 'time' column if it exists
    temp_columns = [col for col in temp_df.columns if col != "time"]
    humid_columns = [col for col in humid_df.columns if col != "time"]

    for sensor in temp_columns:
        if sensor in humid_columns:  # Make sure sensor exists in both dataframes
            sensor_features = {
                "sensor_id": sensor,
                "temp_mean": temp_df[sensor].mean(),
                "temp_std": temp_df[sensor].std(),
                "temp_range": temp_df[sensor].max() - temp_df[sensor].min(),
                "humid_mean": humid_df[sensor].mean(),
                "humid_std": humid_df[sensor].std(),
                "humid_range": humid_df[sensor].max() - humid_df[sensor].min(),
                "temp_humid_corr": temp_df[sensor].corr(humid_df[sensor]),
            }
            features.append(sensor_features)

    return pd.DataFrame(features)


def cluster_sensors(features_df, n_clusters=3):
    """
    Perform K-means clustering on sensor features
    """
    # Select numerical columns for clustering
    feature_columns = [
        "temp_mean",
        "temp_std",
        "temp_range",
        "humid_mean",
        "humid_std",
        "humid_range",
        "temp_humid_corr",
    ]

    # Scale the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df[feature_columns])

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)

    # Add cluster assignments to the features dataframe
    features_df["cluster"] = clusters

    return features_df, kmeans.cluster_centers_


def visualize_clusters(features_df, temp_df, humid_df):
    """
    Create visualizations of the clustering results
    """
    # Plot 1: Scatter plot of temperature mean vs humidity mean
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        features_df["temp_mean"], features_df["humid_mean"], c=features_df["cluster"], cmap="viridis"
    )
    plt.xlabel("Mean Temperature")
    plt.ylabel("Mean Humidity")
    plt.title("Sensor Clusters: Temperature vs Humidity")
    plt.colorbar(scatter, label="Cluster")
    plt.show()

    # Plot 2: Box plots for each cluster
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    sns.boxplot(data=features_df, x="cluster", y="temp_mean", ax=ax1)
    ax1.set_title("Temperature Distribution by Cluster")

    sns.boxplot(data=features_df, x="cluster", y="humid_mean", ax=ax2)
    ax2.set_title("Humidity Distribution by Cluster")

    plt.tight_layout()
    plt.show()


# Main analysis function
def analyze_sensor_clusters(file_path, n_clusters=3):
    """
    Perform complete sensor clustering analysis
    """
    # Load and prepare data
    temp_df, humid_df = load_and_prepare_data(file_path)

    # Calculate features
    features_df = calculate_sensor_features(temp_df, humid_df)

    # Perform clustering
    clustered_df, cluster_centers = cluster_sensors(features_df, n_clusters)

    # Visualize results
    visualize_clusters(clustered_df, temp_df, humid_df)

    return clustered_df, temp_df, humid_df


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Käyttö: python sensor-clustering.py <tiedostopolku>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Analysoi data
    clustered_df, temp_df, humid_df = analyze_sensor_clusters(file_path)

    # Tarkastele tuloksia
    print(clustered_df.groupby("cluster").agg({"temp_mean": ["mean", "count"], "humid_mean": "mean"}))
