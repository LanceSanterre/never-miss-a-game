from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Get project root (folder where script is run)
BASE_DIR = Path(__file__).resolve().parent

# Create a data folder inside your project
DATA_DIR = BASE_DIR / "game_data"
DATA_DIR.mkdir(exist_ok=True)

# Output file
output_file = DATA_DIR / "games_data.csv"

def fetch_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def html_table_to_df(html: str, base_url: str = "") -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")

    # Grab the first "real" table
    table = soup.find("table")
    if not table:
        raise ValueError("No <table> found on the page.")

    # Headers: prefer <thead> then fall back to first row th/td
    headers = []
    thead = table.find("thead")
    if thead:
        headers = [th.get_text(" ", strip=True) for th in thead.find_all("th")]
    if not headers:
        first_row = table.find("tr")
        if first_row:
            headers = [cell.get_text(" ", strip=True) for cell in first_row.find_all(["th", "td"])]

    # Rows
    rows = []
    tbody = table.find("tbody") or table
    for tr in tbody.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue

        row = []
        for cell in cells:
            # Text
            txt = cell.get_text(" ", strip=True)

            # If there's a link in the cell, also store the absolute url (optional)
            a = cell.find("a", href=True)
            if a and base_url:
                link = urljoin(base_url, a["href"])
                # store "text (url)" so you keep both
                txt = f"{txt} ({link})" if txt else link

            row.append(txt)

        # Skip header-like duplicates
        if headers and row == headers:
            continue

        rows.append(row)

    # Normalize row lengths
    max_len = max((len(r) for r in rows), default=0)
    rows = [r + [""] * (max_len - len(r)) for r in rows]

    # Make headers match width
    if headers:
        headers = headers + [f"col_{i}" for i in range(len(headers), max_len)]
        df = pd.DataFrame(rows, columns=headers[:max_len])
    else:
        df = pd.DataFrame(rows)

    return df

def scrape_table_to_csv(url: str, out_csv):
    html = fetch_html(url)
    df = html_table_to_df(html, base_url=url)
    df.to_csv(out_csv, index=False)
    return df

date = datetime.today().strftime('%Y-%m-%d')

if __name__ == "__main__":
    url = "https://sportsgamestoday.com/"
    df = scrape_table_to_csv(url, output_file)
    print(df.head(10))
    print(f"\nSaved {len(df)} rows to games.csv")
