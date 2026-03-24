# %% parsing
from bs4 import BeautifulSoup
import polars as pl
from pathlib import Path

SCRAPES_DIR = Path("scrapes")


def parse_player_table(html_path: str) -> pl.DataFrame | None:
    """Parse HTML table and extract Speler, Lidnummer, Speelsterkte columns."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table")
    if not table:
        return None

    # Build column index accounting for colspan
    header_cells = table.find_all("th")
    col_indices = {}
    idx = 0
    for th in header_cells:
        name = th.get_text(strip=True)
        if name:
            col_indices[name] = idx
        colspan = int(th.get("colspan", 1))  # pyright: ignore[reportArgumentType]
        idx += colspan

    target_cols = ["Speler", "Lidnummer", "Speelsterkte"]
    for col in target_cols:
        if col not in col_indices:
            raise ValueError(f"Column '{col}' not found in table headers")

    # Extract data rows
    data = {col: [] for col in target_cols}
    rows = table.find_all("tr")[1:]  # Skip header row

    for row in rows:
        cells = row.find_all("td")
        if len(cells) > max(col_indices[c] for c in target_cols):
            for col in target_cols:
                data[col].append(cells[col_indices[col]].get_text(strip=True))

    return pl.DataFrame(data)


def parse_discipline(discipline: str) -> pl.DataFrame:
    """Parse all pages for a discipline and add discipline column."""
    discipline_dir = SCRAPES_DIR / discipline
    html_files = sorted(discipline_dir.glob("page_*.html"))
    if not html_files:
        return pl.DataFrame()

    dfs = [df for f in html_files if (df := parse_player_table(str(f))) is not None]
    if not dfs:
        return pl.DataFrame()

    combined = pl.concat(dfs)
    return combined.with_columns(pl.lit(discipline).alias("Discipline"))


def parse_all() -> pl.DataFrame:
    """Parse all disciplines and combine into one DataFrame."""
    disciplines = [d.name for d in SCRAPES_DIR.iterdir() if d.is_dir()]
    if not disciplines:
        raise ValueError("No discipline directories found. Run scrape.py first.")

    dfs = [df for d in disciplines if len(df := parse_discipline(d)) > 0]
    return pl.concat(dfs)


if __name__ == "__main__":
    df = parse_all()
    print(df)
    import time
    df.write_csv(f"player_table_{int(time.time())}.csv")
