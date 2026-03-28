#!/usr/bin/env python3
"""
bots/anglers/fetch_stocking.py
Download and parse Alberta's 2025 fish stocking schedule.

Usage:
    cd /opt/telebots
    source venv/bin/activate
    python3 bots/anglers/fetch_stocking.py
"""
import sys
from pathlib import Path
import requests
import pandas as pd
from io import BytesIO

# Configuration
STOCKING_URL = "https://open.alberta.ca/dataset/ae7521d6-7629-4b69-ac45-857fc798c10c/resource/e20f96fd-4f6b-442a-acd5-984b96608fa5/download/epa-fish-stocking-planned-dates-2025.xlsx"
OUTPUT_FILE = Path(__file__).parent / "knowledge_base" / "stocking_2025.txt"


def download_excel(url: str) -> BytesIO:
    """Download Excel file and return as BytesIO object."""
    print(f"Downloading from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    print(f"Downloaded {len(response.content)} bytes")
    return BytesIO(response.content)


def parse_stocking_data(excel_file: BytesIO) -> str:
    """Parse Excel file and format as clean text grouped by region."""
    print("Parsing Excel file...")

    # Read Excel file (header is in row 6, data starts at row 8)
    df = pd.read_excel(excel_file, sheet_name=0, header=6)

    # Display column names for debugging
    print(f"Columns found: {list(df.columns)}")

    # Clean up column names (remove extra spaces, standardize)
    df.columns = df.columns.str.strip()

    # Drop rows where all values are NaN
    df = df.dropna(how='all')

    # Sort by region and water body
    # Column names in 2025 file: DISTRICT, WATERBODY NAME, LATITUDE, LONGITUDE,
    # SPECIES, PROPOSED SIZE STOCKED - CM, PLANNED STOCKING NUMBER, PLANNED STOCKING DATE
    region_col = next((col for col in df.columns if 'district' in col.lower() or 'region' in col.lower()), None)
    waterbody_col = next((col for col in df.columns if 'waterbody' in col.lower()), None)
    species_col = next((col for col in df.columns if 'species' in col.lower()), None)
    number_col = next((col for col in df.columns if 'number' in col.lower()), None)
    size_col = next((col for col in df.columns if 'size' in col.lower() or 'stocked' in col.lower()), None)
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)

    if not all([region_col, waterbody_col, species_col]):
        print("Warning: Could not identify all required columns")
        print("Available columns:", list(df.columns))
        # Use first few columns as fallback
        region_col = df.columns[0] if len(df.columns) > 0 else None
        waterbody_col = df.columns[1] if len(df.columns) > 1 else None
        species_col = df.columns[2] if len(df.columns) > 2 else None

    # Sort by region and waterbody
    sort_cols = [col for col in [region_col, waterbody_col] if col is not None]
    if sort_cols:
        df = df.sort_values(by=sort_cols)

    # Build formatted text
    output = []
    output.append("ALBERTA FISH STOCKING SCHEDULE 2025")
    output.append("=" * 80)
    output.append("")
    output.append("Planned stocking dates for Alberta waters in 2025.")
    output.append("Source: Government of Alberta Open Data Portal")
    output.append("")

    # Group by region
    if region_col:
        for region, region_df in df.groupby(region_col, dropna=False):
            if pd.isna(region):
                region = "Unknown Region"

            output.append("")
            output.append(f"{'=' * 80}")
            output.append(f"REGION: {region}")
            output.append(f"{'=' * 80}")
            output.append("")

            # Group by waterbody within region
            if waterbody_col:
                for waterbody, wb_df in region_df.groupby(waterbody_col, dropna=False):
                    if pd.isna(waterbody):
                        continue

                    output.append(f"  {waterbody}")
                    output.append(f"  {'-' * (len(str(waterbody)) + 2)}")

                    # List each stocking event
                    for _, row in wb_df.iterrows():
                        parts = []

                        if species_col and pd.notna(row.get(species_col)):
                            parts.append(f"Species: {row[species_col]}")

                        if number_col and pd.notna(row.get(number_col)):
                            parts.append(f"Number: {int(row[number_col]) if isinstance(row[number_col], (int, float)) else row[number_col]}")

                        if size_col and pd.notna(row.get(size_col)):
                            parts.append(f"Size: {row[size_col]}")

                        if date_col and pd.notna(row.get(date_col)):
                            date_val = row[date_col]
                            if isinstance(date_val, pd.Timestamp):
                                date_val = date_val.strftime('%Y-%m-%d')
                            parts.append(f"Date: {date_val}")

                        if parts:
                            output.append(f"    • {', '.join(parts)}")

                    output.append("")
    else:
        # Fallback: just list all entries
        for _, row in df.iterrows():
            parts = []
            for col in df.columns:
                if pd.notna(row[col]):
                    parts.append(f"{col}: {row[col]}")
            if parts:
                output.append(f"  • {', '.join(parts)}")

    output.append("")
    output.append("=" * 80)
    output.append(f"Total entries: {len(df)}")
    output.append("=" * 80)

    return "\n".join(output)


def main():
    """Main function to download, parse, and save stocking data."""
    try:
        # Download Excel file
        excel_data = download_excel(STOCKING_URL)

        # Parse and format data
        formatted_text = parse_stocking_data(excel_data)

        # Save to file
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(formatted_text, encoding='utf-8')

        print(f"\n✓ Saved to: {OUTPUT_FILE}")
        print(f"  File size: {OUTPUT_FILE.stat().st_size} bytes")
        print(f"  Lines: {len(formatted_text.splitlines())}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
