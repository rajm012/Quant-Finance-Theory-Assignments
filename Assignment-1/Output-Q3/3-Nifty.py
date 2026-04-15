import yfinance as yf
import pandas as pd
from pathlib import Path


def save_nse_benchmark_csv(
    start="2016-01-01",
    end="2026-01-01",
    output_path="output/nse_benchmark_yearly.csv"
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Download NIFTY 50
    nifty = yf.download(
        "^NSEI",
        start=start,
        end=end,
        progress=False,
        group_by="column"   # important
    )

    if nifty.empty:
        raise RuntimeError("❌ Failed to download NIFTY 50 data")

    # 🔹 FIX: flatten MultiIndex columns
    if isinstance(nifty.columns, pd.MultiIndex):
        nifty.columns = nifty.columns.get_level_values(0)

    nifty = nifty.reset_index()
    nifty["Year"] = nifty["Date"].dt.year

    # 🔹 SAFE aggregation
    yearly = nifty.groupby("Year").agg(
        NSE_MarketCap=("Close", "last"),   # index proxy
        NSE_Volume=("Volume", "sum")       # volume proxy
    )

    yearly.to_csv(output_path)
    print(f"✅ NSE benchmark CSV saved at: {output_path.resolve()}")

    return yearly


if __name__ == "__main__":
    save_nse_benchmark_csv()
