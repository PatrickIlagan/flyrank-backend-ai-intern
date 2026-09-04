import os
import json
import time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# 1. Configuration
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/PatrickIlagan/flyrank-backend-ai-intern)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT_SECONDS = 10
DELAY_BETWEEN_REQUESTS = 0.5
CACHE_DIR = "cache"

# 2. Polite Fetcher with Cache
def fetch_page(url: str, cache_filename: str) -> tuple[str, bool]:
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    # Cache hit: instant local read
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html, True

    # Cache miss: polite live request
    os.makedirs(CACHE_DIR, exist_ok=True)
    time.sleep(DELAY_BETWEEN_REQUESTS)
    print(f"[FETCH] Live page: {url}...")
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: HTTP status {response.status_code}")
    
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    return response.text, False

# 3. Crawler: Discover First 3 Catalogue Pages
def crawl_catalogue(start_url: str, max_pages: int = 3) -> tuple[list[dict], int]:
    current_url = start_url
    discovered_books = []
    pages_crawled = 0

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_name = f"catalogue-page-{pages_crawled}.html"
        html, was_cached = fetch_page(current_url, cache_name)
        status = "CACHE HIT" if was_cached else "FETCH"
        print(f"[{status}] Catalogue page {pages_crawled}: {current_url}")

        soup = BeautifulSoup(html, "html.parser")
        book_links = soup.select("article.product_pod h3 a")
        
        for link in book_links:
            href = link.get("href")
            absolute_url = urljoin(current_url, href)
            discovered_books.append({
                "product_url": absolute_url,
                "source_page": current_url
            })

        next_button = soup.select_one("li.next a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    return discovered_books, pages_crawled

# 4. Extractor: Parse Detail Page for a Single Book
def extract_book_record(product_url: str, source_page: str) -> dict:
    # Build clean cache filename from the URL slug
    path_parts = [p for p in urlparse(product_url).path.split("/") if p and p != "index.html"]
    slug = path_parts[-1] if path_parts else "book"
    cache_filename = f"book-{slug}.html"

    html, was_cached = fetch_page(product_url, cache_filename)
    soup = BeautifulSoup(html, "html.parser")
    
    product_main = soup.select_one(".product_main")
    if not product_main:
        raise ValueError(f"Product main area not found for {product_url}")

    # Title
    title_el = product_main.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else "Unknown Title"

    # Price text
    price_el = product_main.select_one(".price_color")
    price_text = price_el.get_text(strip=True) if price_el else ""

    # Availability text (collapse whitespace)
    avail_el = product_main.select_one(".availability")
    availability_text = " ".join(avail_el.get_text(strip=True).split()) if avail_el else ""

    # Rating text (from CSS classes: e.g. "star-rating Three")
    rating_el = product_main.select_one(".star-rating")
    rating_text = ""
    if rating_el:
        classes = rating_el.get("class", [])
        for c in classes:
            if c != "star-rating":
                rating_text = c
                break

    # Description (under #product_description)
    desc_el = soup.select_one("#product_description + p")
    description = desc_el.get_text(strip=True) if desc_el else None

    # Provenance
    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }

# 5. Main Runner
def main():
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    print("--- Running Stage 3: Extracting Raw Book Records ---")
    
    # 1. Discover books across first 3 catalogue pages
    raw_books, pages_count = crawl_catalogue(start_url, max_pages=3)
    
    # Deduplicate by URL
    seen_urls = set()
    unique_books = []
    for b in raw_books:
        if b["product_url"] not in seen_urls:
            seen_urls.add(b["product_url"])
            unique_books.append(b)

    print(f"\nDiscovered {len(unique_books)} unique book pages across {pages_count} catalogue pages.")
    print("Extracting book details...\n")

    # 2. Extract details for all 60 books
    extracted_records = []
    for idx, item in enumerate(unique_books, start=1):
        record = extract_book_record(item["product_url"], item["source_page"])
        extracted_records.append(record)
        if idx % 10 == 0 or idx == len(unique_books):
            print(f"Processed {idx}/{len(unique_books)} books...")

    # 3. Print Checkpoint Results
    print("\n--- Checkpoint: Sample Raw Record ---")
    print(json.dumps(extracted_records[0], indent=2))
    
    print("\n--- Checkpoint Summary ---")
    print(f"detail_pages={len(extracted_records)}")

if __name__ == "__main__":
    main()