import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path


# =========================
# CONFIG
# =========================
GOLD_TICKER = "GC=F"
CRUDE_TICKER = "CL=F"
YEARS = 10
SAVE_MODE = "combined"   
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

GOLD_CSV = DATA_DIR / "Gold10yr.csv"
CRUDE_CSV = DATA_DIR / "Crude10y.csv"
COMBINED_CSV = DATA_DIR / "Goldcrude10y.csv"


# =========================
# STYLE
# =========================
plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "axes.labelcolor": "white",
    "axes.edgecolor": "white",
    "text.color": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "font.size": 11
})


# =========================
# DATA DOWNLOAD + SAVE
# =========================
def download_and_save():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=YEARS * 365)

    gold_df = yf.download(
        GOLD_TICKER,
        start=start_date,
        end=end_date,
        progress=False
    )

    crude_df = yf.download(
        CRUDE_TICKER,
        start=start_date,
        end=end_date,
        progress=False
    )

    # Force Close column to Series (CRITICAL FIX)
    gold_close = gold_df[["Close"]].squeeze().rename("Gold")
    crude_close = crude_df[["Close"]].squeeze().rename("Crude Oil")

    # Align on common trading dates
    combined = pd.concat(
        [gold_close, crude_close],
        axis=1,
        join="inner"
    )

    combined.to_csv(COMBINED_CSV)
    print("✅ Saved combined CSV file")

    return combined



# =========================
# NORMALIZATION
# =========================
# ṣimple normalization
def min_max_normalize(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())


# =========================
# PLOTTING
# =========================
def plot_normalized(df: pd.DataFrame):
    output_dir = Path("output/single_10years")
    output_dir.mkdir(parents=True, exist_ok=True)

    df_norm = df.apply(min_max_normalize)

    corr = df_norm["Gold"].corr(df_norm["Crude Oil"])

    plt.figure(figsize=(12, 6))
    plt.plot(df_norm.index, df_norm["Gold"], label="Gold (Normalized)", linewidth=2)
    plt.plot(df_norm.index, df_norm["Crude Oil"], label="Crude Oil (Normalized)", linewidth=2)

    plt.title("Gold vs Crude Oil (Normalized Closing Prices – Last 10 Years)")
    plt.xlabel("Year")
    plt.ylabel("Normalized Price")
    plt.legend()

    plt.text(
        0.02, 0.95,
        f"Pearson Correlation: {corr:.2f}",
        transform=plt.gca().transAxes,
        bbox=dict(boxstyle="round", facecolor="#1f2937", edgecolor="white")
    )

    plt.tight_layout()
    plt.savefig(output_dir / f"gold_crude_10yrs.png", dpi=200)
    plt.close()


def plot_yearwise(df):
    output_dir = Path("output/q2_yearwise_plots")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    df["Year"] = df.index.year

    for year in sorted(df["Year"].unique()):
        df_year = df[df["Year"] == year]

        # # Skip incomplete years
        # # for current year
        # if len(df_year) < 200:
        #     continue

        df_norm = df_year[["Gold", "Crude Oil"]].apply(min_max_normalize)

        corr = df_norm["Gold"].corr(df_norm["Crude Oil"])

        plt.figure(figsize=(10, 5))
        plt.plot(df_norm.index, df_norm["Gold"], label="Gold (Normalized)", linewidth=2)
        plt.plot(df_norm.index, df_norm["Crude Oil"], label="Crude Oil (Normalized)", linewidth=2)

        plt.title(f"Gold vs Crude Oil - Normalized Prices ({year})")
        plt.xlabel("Date")
        plt.ylabel("Normalized Price")
        plt.legend()

        plt.text(
            0.02, 0.95,
            f"Pearson Correlation: {corr:.2f}",
            transform=plt.gca().transAxes,
            bbox=dict(boxstyle="round", facecolor="#1f2937", edgecolor="white")
        )

        plt.tight_layout()
        plt.savefig(output_dir / f"gold_crude_{year}.png", dpi=200)
        plt.close()


# =========================
# MAIN
# =========================
def main():
    df = download_and_save()
    plot_normalized(df)
    plot_yearwise(df)


if __name__ == "__main__":
    main()
