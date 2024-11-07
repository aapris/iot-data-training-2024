# Data

## samples

data/samples contains sample data files for testing, development and AI assistant.

## raw

data/raw contains raw data, downloaded from the web server.
To update it, run this command this directory

```
wget -r -np -nd -N -A "*.geojson,*.parquet" https://bri3.fvh.io/opendata/makelankatu/ https://bri3.fvh.io/opendata/r4c/ -P ./raw/
```

To merge the data into a single file, run the `prepare_raw_data.py` script.

```
python prepare_raw_data.py
```
