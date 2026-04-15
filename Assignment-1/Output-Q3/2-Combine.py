import pandas as pd
from pathlib import Path


INPUT_DIR = Path("5-Pharma")
OUTPUT_DIR = Path("combined")
OUTPUT_DIR.mkdir(exist_ok=True)

SECTOR_NAME = "NIFTY_PHARMA"
OUTPUT_CSV = OUTPUT_DIR / f"{SECTOR_NAME}_combined.csv"


def combine_sector_csvs(input_dir: Path):
    all_dfs = []

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in input folder.")

    for csv_file in csv_files:
        print(f"📄 Reading: {csv_file.name}")

        df = pd.read_csv(csv_file)

        # 🔹 Strip whitespace from column names (CRITICAL FIX)
        df.columns = df.columns.str.strip()

        if "Date" not in df.columns:
            raise ValueError(f"'Date' column missing in {csv_file.name}")

        # 🔹 Parse Date (NSE format: DD-MMM-YYYY)
        df["Date"] = pd.to_datetime(
            df["Date"],
            format="%d-%b-%Y",
            errors="coerce"
        )

        df = df.dropna(subset=["Date"])

        all_dfs.append(df)

    # ---- Combine all CSVs ----
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # ---- Remove overlapping dates ----
    combined_df = combined_df.drop_duplicates(subset=["Date"])

    # ---- FIX: sort chronologically (ascending) ----
    combined_df = combined_df.sort_values("Date")

    # ---- Save ----
    combined_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Combined CSV saved at: {OUTPUT_CSV.resolve()}")

    return combined_df


if __name__ == "__main__":
    combine_sector_csvs(INPUT_DIR)
