import requests
import zipfile
import io
import os
from datetime import datetime, timedelta

# ================= CONFIG =================
BASE_DIR = r"E:\Finance\bhavcopy"
START_DATE = datetime.now() - timedelta(days=365 * 10)
END_DATE = datetime.now()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/zip,application/octet-stream",
    "Referer": "https://www.nseindia.com"
}
# ==========================================

os.makedirs(BASE_DIR, exist_ok=True)

session = requests.Session()
session.headers.update(HEADERS)

current = START_DATE

success, failed = 0, 0

while current <= END_DATE:
    date_str = current.strftime("%d%b%Y").upper()
    year = current.strftime("%Y")

    url = (
        "https://archives.nseindia.com/content/historical/EQUITIES/"
        f"{year}/{current.strftime('%b').upper()}/cm{date_str}bhav.csv.zip"
    )

    year_dir = os.path.join(BASE_DIR, year)
    os.makedirs(year_dir, exist_ok=True)

    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(year_dir)
            success += 1
            print(f"✔ Downloaded: {date_str}")
        else:
            failed += 1

    except Exception:
        failed += 1

    current += timedelta(days=1)

print("\n================ SUMMARY ================")
print(f"Downloaded files : {success}")
print(f"Skipped/holidays : {failed}")
print("========================================")
