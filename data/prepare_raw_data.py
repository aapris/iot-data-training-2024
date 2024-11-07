import pandas as pd
import geopandas as gpd

# Merge GeoJSON files
print("Merging GeoJSON files")
geojson1 = gpd.read_file("raw/r4c_all_latest.geojson")
geojson2 = gpd.read_file("raw/makelankatu_latest.geojson")
merged_geojson = pd.concat([geojson1, geojson2], ignore_index=True)
merged_geojson.to_file("raw/metadata_all.geojson", driver="GeoJSON")
print("Merged GeoJSON file saved to raw/metadata_all.geojson")

# Merge Parquet files
print("Merging Parquet files")
parquet1 = pd.read_parquet("raw/r4c_all.parquet")
parquet2 = pd.read_parquet("raw/makelankatu.parquet")
merged_parquet = pd.concat([parquet1, parquet2], ignore_index=True)
merged_parquet.to_parquet("raw/data_all.parquet")
print("Merged Parquet file saved to raw/data_all.parquet")
