import requests
from pathlib import Path
import time
from bs4 import BeautifulSoup

SCRAPES_DIR = Path("scrapes")
BASE_URL = "https://www.toernooi.nl/ranking/category.aspx"
PER_PAGE = 100

DISCIPLINES = {
    "MS": "4582",
    "WS": "4583",
    "MD": "4584",
    "WD": "4585",
    "XDM": "4586",
    "XDW": "4587",
}


def has_table_data(html: str) -> bool:
    """Check if HTML contains a table with data rows."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return False
    # Check if table has any data rows (td elements)
    return len(table.find_all("td")) > 0


def scrape_discipline(session: requests.Session, key: str, category: str):
    """Scrape all pages for a discipline until no more data."""
    discipline_dir = SCRAPES_DIR / key
    discipline_dir.mkdir(parents=True, exist_ok=True)

    page = 1
    while True:
        filepath = discipline_dir / f"page_{page}.html"
        
        if filepath.exists():
            # Check existing file for data
            if not has_table_data(filepath.read_text(encoding="utf-8")):
                print(f"[{key}] Page {page} has no data, stopping")
                break
            print(f"[{key}] Page {page} already exists, skipping")
            page += 1
            continue

        params = {
            "id": "50874",
            "category": category,
            f"C{category}CS": "0",
            f"C{category}FTYAF": "0",
            f"C{category}FTYAT": "0",
            f"C{category}FOG_4_F2048": "",
            "p": page,
            "ps": PER_PAGE,
        }

        print(f"[{key}] Scraping page {page}...")
        response = session.get(BASE_URL, params=params)
        response.raise_for_status()

        if not has_table_data(response.text):
            print(f"[{key}] Page {page} has no data, stopping")
            break

        filepath.write_text(response.text, encoding="utf-8")
        page += 1
        time.sleep(1)

    print(f"[{key}] Done, scraped {page - 1} pages")


def scrape_all():
    """Scrape all disciplines."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    })

    # Accept cookie wall
    session.post("https://www.toernooi.nl/cookiewall/Save", data={
        "ReturnUrl": "/ranking/category.aspx",
        "SettingsOpen": "false",
    })

    for key, category in DISCIPLINES.items():
        scrape_discipline(session, key, category)

    print("Scraping complete!")


if __name__ == "__main__":
    scrape_all()
