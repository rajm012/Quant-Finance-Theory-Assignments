# import re
# from pathlib import Path
# from typing import List, Dict
# import pdfplumber
# import pandas as pd


# # =========================
# # CONFIG
# # =========================

# INPUT_DIR = Path("nifty")        # folder containing PDFs
# OUTPUT_DIR = Path("output")
# OUTPUT_DIR.mkdir(exist_ok=True)
# OUTPUT_CSV = OUTPUT_DIR / "nifty50_constituents_all_years.csv"


# # =========================
# # HELPERS
# # =========================
# def extract_year_from_filename(filename: str) -> int | None:
#     """
#     Extract year from filenames like:
#     NIFTY_50_Jan2016.pdf
#     """
#     match = re.search(r"Jan(\d{4})", filename)
#     return int(match.group(1)) if match else None


# def extract_rows_from_pdf(pdf_path: Path):
#     """
#     Extract Symbol and Weightage (%) from IISL NIFTY PDFs.
#     Uses column position instead of header names.
#     """
#     year = extract_year_from_filename(pdf_path.name)
#     if year is None:
#         print(f"⚠️ Skipping (year not found): {pdf_path.name}")
#         return []

#     rows = []

#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             table = page.extract_table()
#             if not table:
#                 continue

#             # Skip header row, process data rows
#             for row in table[1:]:
#                 if not row or len(row) < 6:
#                     continue

#                 symbol = row[0]
#                 weight = row[-1]

#                 if not symbol or not weight:
#                     continue

#                 try:
#                     weight = float(weight)
#                 except ValueError:
#                     continue

#                 rows.append({
#                     "Year": year,
#                     "Symbol": symbol.strip(),
#                     "Weightage (%)": weight
#                 })

#     return rows


# # =========================
# # MAIN PIPELINE
# # =========================
# def build_csv_from_folder(input_dir: Path) -> None:
#     if not input_dir.exists():
#         raise FileNotFoundError(f"Input folder not found: {input_dir}")

#     all_rows: List[Dict] = []

#     pdf_files = sorted(input_dir.glob("*.pdf"))
#     if not pdf_files:
#         raise FileNotFoundError("No PDF files found in input folder.")

#     for pdf in pdf_files:
#         print(f"📄 Processing: {pdf.name}")
#         rows = extract_rows_from_pdf(pdf)
#         all_rows.extend(rows)

#     if not all_rows:
#         raise ValueError("No data extracted from PDFs.")

#     df = pd.DataFrame(all_rows)

#     # Sort cleanly
#     df.sort_values(by=["Year", "Weightage (%)"], ascending=[True, False], inplace=True)

#     df.to_csv(OUTPUT_CSV, index=False)
#     print(f"\n✅ CSV saved at: {OUTPUT_CSV.resolve()}")


# # =========================
# # ENTRY POINT
# # =========================
# if __name__ == "__main__":
#     build_csv_from_folder(INPUT_DIR)



# =====================================================================
# =====================================================================


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# CONFIG
# =========================
CSV_PATH = Path("output/nifty50_constituents_all_years.csv")
OUTPUT_DIR = Path("output/q1_charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TOP_N = 10


# =========================
# STYLE SETTINGS
# =========================
plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#0e1117",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "font.size": 11
})


# =========================
# CORE LOGIC
# =========================
def plot_donutOld(year: int, df_year: pd.DataFrame):
    df_top = df_year.nlargest(TOP_N, "Weightage (%)")

    labels = df_top["Symbol"]
    sizes = df_top["Weightage (%)"]

    explode = [0.08 if i < 3 else 0 for i in range(TOP_N)]

    fig, ax = plt.subplots(figsize=(9, 9))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        explode=explode,
        pctdistance=0.78,
        labeldistance=1.05,
        wedgeprops=dict(width=0.35, edgecolor="black")
    )

    # Center text
    ax.text(
        0, 0,
        f"NIFTY 50\nTop 10\n{year}",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_title(
        f"NIFTY 50 - Top 10 Constituents by Weight ({year})",
        pad=20,
        fontsize=13,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"nifty50_top10_{year}.png", dpi=200)
    plt.close()


def plot_donut(year: int, df_year: pd.DataFrame):
    import math
    df_top = df_year.nlargest(TOP_N, "Weightage (%)").reset_index(drop=True)

    labels = df_top["Symbol"]
    sizes = df_top["Weightage (%)"].values
    original_weights = df_top["Weightage (%)"].values

    explode = [0.08 if i < 3 else 0 for i in range(TOP_N)]

    fig, ax = plt.subplots(figsize=(9, 9))

    wedges, texts = ax.pie(
        sizes,
        labels=labels,
        startangle=140,
        explode=explode,
        labeldistance=1.05,
        wedgeprops=dict(width=0.35, edgecolor="black")
    )

    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = 0.75 * math.cos(angle * 3.1416 / 180)
        y = 0.75 * math.sin(angle * 3.1416 / 180)

        ax.text(
            x, y,
            f"{original_weights[i]:.2f}%",
            ha="center",
            va="center",
            fontsize=10,
            color="white"
        )

    # Center annotation (critical clarification)
    ax.text(
        0, 0,
        f"NIFTY 50\nTop 10 Only\n{year}",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_title(
        f"NIFTY 50 – Top 10 Constituents by Weight (Actual NSE %)",
        pad=20,
        fontsize=13,
        fontweight="bold"
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"nifty50_top10_{year}.png", dpi=200)
    plt.close()



# =========================
# DRIVER
# =========================
def main():
    df = pd.read_csv(CSV_PATH)
    years = sorted(df["Year"].unique())

    # ---- CURRENT YEAR ----
    current_year = years[-1]
    plot_donut(current_year, df[df["Year"] == current_year])

    # ---- PAST 11 YEARS ----
    for year in years[-11:]:
        plot_donut(year, df[df["Year"] == year])

    print("✅ Question 1 charts generated successfully.")


if __name__ == "__main__":
    main()

