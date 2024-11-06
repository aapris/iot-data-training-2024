# iot-data-training-2024
My year 2024 training codes.

## Objectives

1. Master IoT Sensor Data Analysis
   - Learn techniques for analyzing time series data from IoT sensors
   - Understand data quality assessment and preprocessing
   - Develop skills in handling real-time sensor streams

1. Advanced Data Visualization
   - Create effective visualizations for time series data
   - Implement spatial data visualization techniques
   - Design interactive dashboards for IoT sensor monitoring

1. Forecasting and Prediction
   - Develop time series forecasting models
   - Implement predictive analytics for sensor data
   - Evaluate and validate forecast accuracy

1. Spatial Analysis
   - Detect and analyze regional differences
   - Understand spatial patterns in sensor networks
   - Study environmental and urban microclimate effects

## Data sources

### IoT sensor data

Milesight IoT sensors send the data using LoRaWAN. The data is stored in InfluxDB v2.

Downloadable data:
- https://bri3.fvh.io/opendata/r4c/
- https://bri3.fvh.io/opendata/makelankatu/

Dashboards for above data:
- https://iot.fvh.fi/grafana/d/aduw70oqqdon4c/r4c-laajasalo-and-koivukyla?orgId=6&refresh=30m
- https://iot.fvh.fi/grafana/d/bdvh3ukceuneoa/makelankatu?orgId=6&refresh=30m

### FMI weather data

- https://en.ilmatieteenlaitos.fi/open-data-manual

We gather the weather data and store it into InfluxDB v2
from the FMI API using a custom 
[fmiapi_v2.py](https://github.com/VekotinVerstas/DataManagementScripts/blob/master/FmiAPI/fmiapi_v2.py)
script once in an hour.


```bash
python fmiapi_v2.py --bbox 24.3,59.9,25.7,60.7 --duration 2h
```

### Sample data

Sample data files are available in the `datasamples` directory:
- [24E124136E140283.geojson](datasamples/24E124136E140283.geojson):Example IoT sensor data file containing:
  - Metadata
  - Temperature and humidity measurements at different resolutions:
    - Raw 10-minute data
    - 3-hour aggregates
    - Daily aggregates
- [fmi_observations_weather_multipointcoverage-hki-area-sample.csv](datasamples/fmi_observations_weather_multipointcoverage-hki-area-sample.csv): Weather observation data from FMI stations in Helsinki metropolitan area, including:
  - Air temperature
  - Dew point temperature 
  - Wind speed and direction
  - Gust speed
  - Relative humidity
  - Pressure
  - Visibility
  - Cloud amount
  - Precipitation
  - Snow depth
  
  Data is provided at 10-minute intervals for multiple weather station locations.
- [r4c_latest.geojson](datasamples/r4c_latest.geojson) - Latest measurements from the R4C IoT sensor network and their metadata.
- [r4c_sample.csv](datasamples/r4c_sample.csv) - Sample of the raw 10-minute data from the R4C IoT sensor network.
