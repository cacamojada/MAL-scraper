import csv
import sys
import time
 
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Install them with:")
    print("  pip install beautifulsoup4 requests lxml")
    sys.exit(1)
 
 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
 
BASE_URL = "https://myanimelist.net/topanime.php"
PAGES    = 100
PER_PAGE = 50
 
 
def parse_html(html: str) -> list[dict]:
    """Parse a MAL top anime page and return a list of {rank, name, rating} dicts."""
    soup = BeautifulSoup(html, "lxml")
    results = []
 
    for row in soup.select("tr.ranking-list"):
        rank_tag  = row.select_one("td.rank span")
        title_tag = row.select_one("h3.anime_ranking_h3 a")
        score_tag = row.select_one("span.score-label")
 
        rank   = rank_tag.get_text(strip=True)  if rank_tag  else "N/A"
        name   = title_tag.get_text(strip=True) if title_tag else "N/A"
        rating = score_tag.get_text(strip=True) if score_tag else "N/A"
 
        if name != "N/A":
            results.append({"rank": rank, "name": name, "rating": rating})
 
    return results
 
 
def scrape_page(limit: int) -> list[dict]:
    """Fetch a single page by its limit offset."""
    url = f"{BASE_URL}?limit={limit}"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return parse_html(response.text)
 
 
def scrape_all_pages() -> list[dict]:
    """Loop through all pages and collect every entry."""
    all_data = []
 
    for page in range(PAGES):
        limit = page * PER_PAGE
        print(f"  📄 Page {page + 1}/{PAGES}  (ranks {limit + 1}–{limit + PER_PAGE})")
        try:
            data = scrape_page(limit)
            all_data.extend(data)
            time.sleep(1)  # polite delay to avoid getting blocked
        except Exception as e:
            print(f"  ⚠️  Failed on page {page + 1}: {e}")
 
    return all_data
 
 
def print_results(data: list[dict]) -> None:
    """Pretty-print results to the console."""
    if not data:
        print("No results found.")
        return
 
    col_rank   = max(len(d["rank"])   for d in data)
    col_name   = max(len(d["name"])   for d in data)
    col_rating = max(len(d["rating"]) for d in data)
 
    header = f"{'Rank':<{col_rank}}  {'Anime Name':<{col_name}}  {'Rating':>{col_rating}}"
    print(header)
    print("-" * len(header))
 
    for d in data:
        print(f"{d['rank']:<{col_rank}}  {d['name']:<{col_name}}  {d['rating']:>{col_rating}}")
 
    print(f"\n✅ Scraped {len(data)} anime entries.")
 
 
def save_csv(data: list[dict], filepath: str) -> None:
    """Write results to a CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "name", "rating"])
        writer.writeheader()
        writer.writerows(data)
    print(f"💾 Saved to: {filepath}")
 
 
def main():
    print(f"🔍 Scraping MyAnimeList Top Anime ({PAGES} pages, ~{PAGES * PER_PAGE} entries)...\n")
    data = scrape_all_pages()
    print()
    print_results(data)
    save_csv(data, "results.csv")
 
 
if __name__ == "__main__":
    main()
