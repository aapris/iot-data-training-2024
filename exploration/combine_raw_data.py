import argparse
from pathlib import Path

from fvhdata.utils.geojson import combine_geojson
from fvhdata.utils.parquet import combine_parquet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine GeoJSON and/or Parquet files")
    parser.add_argument("--geojson-in", nargs="+", type=Path, help="List of input GeoJSON files")
    parser.add_argument("--geojson-out", type=Path, help="Path for combined GeoJSON output file")
    parser.add_argument("--parquet-in", nargs="+", type=Path, help="List of input Parquet files")
    parser.add_argument("--parquet-out", type=Path, help="Path for combined Parquet output file")
    args = parser.parse_args()

    # Check that at least one input/output pair is provided
    if not ((args.geojson_in and args.geojson_out) or (args.parquet_in and args.parquet_out)):
        parser.error("Provide at least one input/output pair (GeoJSON or Parquet)")

    return args


def main():
    args = parse_args()

    # GeoJSON processing
    if args.geojson_in and args.geojson_out:
        # Use combine_geojson directly and convert to JSON
        combine_geojson(args.geojson_in, args.geojson_out)
        print(f"GeoJSON files combined: {args.geojson_out}")

    # Parquet processing
    if args.parquet_in and args.parquet_out:
        # Create output directory if needed
        args.parquet_out.parent.mkdir(parents=True, exist_ok=True)

        # Combine Parquet files using the utility function
        combine_parquet(args.parquet_in, args.parquet_out)
        print(f"Parquet files combined: {args.parquet_out}")


if __name__ == "__main__":
    main()
