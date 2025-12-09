import requests
from bs4 import BeautifulSoup
import io
import zipfile
from pathlib import Path

# specify desired place/folder to store the raw files
raw_dir = Path("../data/raw")
raw_dir.mkdir(parents=True, exist_ok=True) # make directory just in case

for yr in range(2023, 2026):
    # on BTS' website: "Latest Available Data: June 2025" (Q2 2025)
    max_quarters = 2 if yr == 2025 else 4
    
    for qrtr in range(1, max_quarters + 1):
        year = yr
        quarter = qrtr
        geography = "California"

        # URL and query params from cURL
        BASE_URL = "https://transtats.bts.gov/DL_SelectFields.aspx"
        PARAMS = {
            "gnoyr_VQ": "FHK",
            "QO_fu146_anzr": "b4vtv0 n0q Qr56v0n6v10 f748rB"
        }

        # GET the page to get hidden fields
        session = requests.Session()
        html_response = session.get(BASE_URL, params=PARAMS)
        html_response.raise_for_status()

        soup = BeautifulSoup(html_response.text, "html.parser")
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        viewstategen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
        eventval = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]

        # POST the form to mimic clicking "Download"
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategen,
            "__EVENTVALIDATION": eventval,
            "txtSearch": "",
            "cboGeography": geography,
            "cboYear": str(year),
            "cboPeriod": str(quarter),
            "btnDownload": "Download",
            
            # checkboxes of (second-layer) selections (needed columns)
            "YEAR": "on",
            "QUARTER": "on",
            "ORIGIN": "on",
            "DEST": "on",
            "TK_CARRIER_GROUP": "on",
            "MARKET_FARE": "on",
        }

        download_response = session.post(BASE_URL, params=PARAMS, data=data)
        download_response.raise_for_status()

        # save raw ZIP files and extract CSVs to ../data/raw/ as "bts_YEAR_QUARTER.csv"
        zip_path = raw_dir / f"bts_{year}_Q{quarter}.zip"
        with open(zip_path, "wb") as f:
            f.write(download_response.content)

        zbytes = io.BytesIO(download_response.content)
        with zipfile.ZipFile(zbytes) as zf:
            inner_name = zf.namelist()[0]
            csv_path = raw_dir / f"bts_{year}_Q{quarter}.csv"
            with zf.open(inner_name) as zip_csv, open(csv_path, "wb") as csv:
                csv.write(zip_csv.read())
            print("Extracted raw CSV:", csv_path)