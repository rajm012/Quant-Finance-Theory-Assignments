# import pandas as pd
# import matplotlib.pyplot as plt
# from pathlib import Path

# # ==========================================================
# # CONFIG
# # ==========================================================
# SECTOR_DIR = Path("Data-Q3/Sector-10yrs")
# NSE_CSV = Path("Data-Q3/Sector-10yrs/NIFTY_FIFTY.csv")

# SECTOR_FILES = {
#     "Auto": "NIFTY_AUTO.csv",
#     "Banking": "NIFTY_BANK.csv",
#     "Energy": "NIFTY_ENERGY.csv",
#     "FMCG": "NIFTY_FMCG.csv",
#     "Pharma": "NIFTY_PHARMA.csv"
# }

# OUTPUT_DIR = Path("Output-Q3")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# NIFTY_SHARE = 0.65   # NIFTY 50: 65% of NSE (approx as not exact data)
# YEARS = 10

# # ==========================================================
# # STYLE
# # ==========================================================
# plt.rcParams.update({
#     "figure.facecolor": "#0e1117",
#     "axes.facecolor": "#0e1117",
#     "text.color": "white",
#     "font.size": 11
# })

# # ==========================================================
# # LOAD NSE BENCHMARK
# # ==========================================================
# def load_nse_benchmark():
#     df = pd.read_csv(NSE_CSV)
#     df.set_index("Year", inplace=True)

#     df["Total_NSE_MarketCap"] = df["NSE_MarketCap"] / NIFTY_SHARE
#     df["Total_NSE_Volume"] = df["NSE_Volume"] / NIFTY_SHARE

#     return df

# # ==========================================================
# # LOAD SECTOR DATA
# # ==========================================================
# def build_sector_year_data():
#     sector_year = {}

#     for sector, file in SECTOR_FILES.items():
#         df = pd.read_csv(SECTOR_DIR / file)
#         df.columns = df.columns.str.strip()

#         df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#         df = df.dropna(subset=["Date"])
#         df["Year"] = df["Date"].dt.year

#         yearly = df.groupby("Year").agg(
#             MarketCap=("Close", "last"),              # index proxy
#             Volume=("Turnover (₹ Cr)", "sum")         # exact
#         )

#         for year, row in yearly.iterrows():
#             sector_year.setdefault(year, {})
#             sector_year[year][sector] = row

#     return sector_year

# # ==========================================================
# # DONUT PLOT
# # ==========================================================
# def plot_donut(year, data, title, center_text, filename):
#     labels = []
#     sizes = []

#     for sector, (value, pct) in data.items():
#         labels.append(f"{sector}\n{value:,.0f} ({pct:.2f}%)")
#         sizes.append(pct)

#     fig, ax = plt.subplots(figsize=(9, 9))

#     ax.pie(
#         sizes,
#         labels=labels,
#         startangle=140,
#         labeldistance=1.08,
#         wedgeprops=dict(width=0.35, edgecolor="black")
#     )

#     ax.text(
#         0, 0,
#         center_text,
#         ha="center",
#         va="center",
#         fontsize=13,
#         fontweight="bold"
#     )

#     ax.set_title(title, pad=20)
#     plt.tight_layout()
#     plt.savefig(OUTPUT_DIR / filename, dpi=200)
#     plt.close()

# # ==========================================================
# # MAIN
# # ==========================================================
# def main():
#     sector_data = build_sector_year_data()
#     nse = load_nse_benchmark()

#     years = sorted(set(sector_data.keys()) & set(nse.index))[-YEARS:]

#     for year in years:
#         # ---------- Market Cap ----------
#         cap_data = {}
#         for sector, vals in sector_data[year].items():
#             cap = vals["MarketCap"]
#             pct = (cap / nse.loc[year, "Total_NSE_MarketCap"]) * 100
#             cap_data[sector] = (cap, pct)

#         plot_donut(
#             year,
#             cap_data,
#             f"Sectoral Market Cap Share vs NSE ({year})",
#             f"Market Cap\nvs NSE\n{year}",
#             f"marketcap_vs_nse_{year}.png"
#         )

#         # ---------- Volume ----------
#         vol_data = {}
#         for sector, vals in sector_data[year].items():
#             vol = vals["Volume"]
#             pct = (vol / nse.loc[year, "Total_NSE_Volume"]) * 100
#             vol_data[sector] = (vol, pct)

#         plot_donut(
#             year,
#             vol_data,
#             f"Sectoral Volume Share vs NSE ({year})",
#             f"Traded Volume\nvs NSE\n{year}",
#             f"volume_vs_nse_{year}.png"
#         )

#     print("✅ Q3 completed: Sector vs NSE Market Cap & Volume charts generated.")


# if __name__ == "__main__":
#     main()
# =====================================================================



import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ======================================================
# CONFIG
# ======================================================
DATA_DIR = Path("Data-Q3/Sector-10yrs")
NSE_CSV = Path("Data-Q3/Sector-10yrs/NIFTY_FIFTY.csv")

SECTOR_FILES = {
    "Auto": "NIFTY_AUTO.csv",
    "Banking": "NIFTY_BANK.csv",
    "Energy": "NIFTY_ENERGY.csv",
    "FMCG": "NIFTY_FMCG.csv",
    "Pharma": "NIFTY_PHARMA.csv"
}

OUTPUT_DIR = Path("Output-Q3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS_TO_PLOT = 10

# ======================================================
# STYLE
# ======================================================
plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "text.color": "white",
    "font.size": 11
})

# ======================================================
# DATA PREPARATION
# ======================================================
def build_sector_year_data():
    """
    Returns:
    {
        year: {
            sector: {
                "MarketCapProxy": value,
                "Volume": value
            }
        }
    }
    """
    data = {}

    for sector, file in SECTOR_FILES.items():
        df = pd.read_csv(DATA_DIR / file)
        df.columns = df.columns.str.strip()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Year"] = df["Date"].dt.year

        yearly = df.groupby("Year").agg(
            MarketCapProxy=("Close", "last"),        # index-level proxy
            Volume=("Turnover (₹ Cr)", "sum")       # exact
        )

        for year, row in yearly.iterrows():
            data.setdefault(year, {})
            data[year][sector] = row

    return data

# ======================================================
# DONUT PLOT
# ======================================================
def plot_donut(year, values, title, center_text, filename, value_label):
    labels, sizes = [], []

    for sector, val in values.items():
        labels.append(f"{sector}\n{val:,.0f} {value_label}")
        sizes.append(val)

    fig, ax = plt.subplots(figsize=(9, 9))

    ax.pie(
        sizes,
        labels=labels,
        startangle=140,
        labeldistance=1.08,
        wedgeprops=dict(width=0.35, edgecolor="black")
    )

    ax.text(
        0, 0,
        center_text,
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_title(title, pad=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=200)
    plt.close()

# ======================================================
# OPTIONAL: YEARLY INTERPRETATION
# ======================================================
def interpret_year(year, cap_data, vol_data):
    largest_cap = max(cap_data, key=cap_data.get)
    largest_vol = max(vol_data, key=vol_data.get)

    return (
        f"In {year}, {largest_cap} emerged as the largest sector by "
        f"relative market capitalization, while {largest_vol} "
        f"recorded the highest trading activity, indicating strong "
        f"investor participation."
    )

# ======================================================
# MAIN
# ======================================================
def main():
    data = build_sector_year_data()
    years = sorted(data.keys())[-YEARS_TO_PLOT:]

    interpretations = []

    for year in years:
        cap_values = {
            sector: vals["MarketCapProxy"]
            for sector, vals in data[year].items()
        }

        vol_values = {
            sector: vals["Volume"]
            for sector, vals in data[year].items()
        }

        # Market Cap Donut
        plot_donut(
            year,
            cap_values,
            f"Sectoral Market Capitalization Distribution ({year})",
            "Market Cap\n(Index Proxy)",
            f"marketcap_{year}.png",
            ""
        )

        # Volume Donut
        plot_donut(
            year,
            vol_values,
            f"Sectoral Traded Volume Distribution ({year})",
            "Traded Volume\n(₹ Crores)",
            f"volume_{year}.png",
            "Cr"
        )

        interpretations.append(interpret_year(year, cap_values, vol_values))

    # Save interpretations
    with open(OUTPUT_DIR / "yearly_interpretations.txt", "w") as f:
        for line in interpretations:
            f.write(line + "\n\n")

    print("✅ Q3 completed (conceptually correct).")
    print("📁 Charts saved in:", OUTPUT_DIR.resolve())
    print("📝 Interpretations saved to yearly_interpretations.txt")


if __name__ == "__main__":
    main()



