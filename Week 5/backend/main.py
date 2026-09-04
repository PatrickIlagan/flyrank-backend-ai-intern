import os
import re
import json
import time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# 1. Configuration
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/PatrickIlagan/flyrank-backend-ai-intern)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT_SECONDS = 10
DELAY_BETWEEN_REQUESTS = 0.5
CACHE_DIR = "cache"
OUTPUT_DIR = "output"

# 2. Pydantic Schema
class BookSchema(BaseModel):
    title: str = Field(..., min_length=1)
    product_url: str = Field(...)
    price_text: str = Field(..., min_length=1)
    price_gbp: float = Field(..., ge=0.0)
    availability_text: str = Field(..., min_length=1)
    rating_text: str = Field(..., min_length=1)
    description: Optional[str] = None
    source_page: str = Field(...)
    fetched_at: str = Field(...)

# 3. Resilient Fetcher with Retry Rules & Cache
def fetch_page(url: str, cache_filename: str, stats: dict) -> tuple[Optional[str], bool]:
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    # 1. Check local cache
    if os.path.exists(cache_path):
        stats["cache_hits"] += 1
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html, True

    # 2. Live request with smart retry logic
    os.makedirs(CACHE_DIR, exist_ok=True)
    max_attempts = 2 # Initial attempt + 1 retry for server errors/timeouts
    
    for attempt in range(1, max_attempts + 1):
        try:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            stats["pages_fetched"] += 1
            print(f"[FETCH] (Attempt {attempt}) {url}...")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
            
            # Non-retryable client errors: 404 (Not Found) or 403 (Forbidden)
            if response.status_code in (403, 404):
                print(f"[SKIP] Non-retryable HTTP {response.status_code} for {url}")
                return None, False
                
            # Retryable server errors (5xx)
            if response.status_code >= 500:
                print(f"[RETRY WARNING] HTTP {response.status_code} on attempt {attempt}")
                if attempt < max_attempts:
                    time.sleep(1.0)
                    continue
                return None, False
                
            if response.status_code == 200:
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                return response.text, False
                
        except (requests.Timeout, requests.ConnectionError) as exc:
            print(f"[TIMEOUT/NETWORK ERROR] {exc} on attempt {attempt}")
            if attempt < max_attempts:
                time.sleep(1.0)
                continue
            return None, False

    return None, False

# 4. Crawler: Discover First 3 Catalogue Pages
def crawl_catalogue(start_url: str, max_pages: int, stats: dict) -> tuple[list[dict], int]:
    current_url = start_url
    discovered_books = []
    pages_crawled = 0

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_name = f"catalogue-page-{pages_crawled}.html"
        html, was_cached = fetch_page(current_url, cache_name, stats)
        
        if not html:
            print(f"[ERROR] Could not load catalogue page: {current_url}")
            break

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

# 5. Price Cleaner
def clean_price(price_text: str) -> float:
    cleaned = re.sub(r"[^\d.]", "", price_text)
    return float(cleaned) if cleaned else 0.0

# 6. Detail Extractor
def extract_book_record(product_url: str, source_page: str, stats: dict) -> Optional[dict]:
    path_parts = [p for p in urlparse(product_url).path.split("/") if p and p != "index.html"]
    slug = path_parts[-1] if path_parts else "book"
    cache_filename = f"book-{slug}.html"

    html, _ = fetch_page(product_url, cache_filename, stats)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    product_main = soup.select_one(".product_main")
    if not product_main:
        return None

    title_el = product_main.select_one("h1")
    title = title_el.get_text(strip=True) if title_el else "Unknown Title"

    price_el = product_main.select_one(".price_color")
    price_text = price_el.get_text(strip=True) if price_el else ""
    price_gbp = clean_price(price_text)

    avail_el = product_main.select_one(".availability")
    availability_text = " ".join(avail_el.get_text(strip=True).split()) if avail_el else ""

    rating_el = product_main.select_one(".star-rating")
    rating_text = ""
    if rating_el:
        for c in rating_el.get("class", []):
            if c != "star-rating":
                rating_text = c
                break

    desc_el = soup.select_one("#product_description + p")
    description = desc_el.get_text(strip=True) if desc_el else None
    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }

# 7. Main Pipeline Runner
def main():
    start_time_iso = datetime.now(timezone.utc).isoformat()
    start_perf = time.perf_counter()

    stats = {
        "start_time": start_time_iso,
        "catalogue_pages": 0,
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0,
        "target_site": "https://books.toscrape.com/"
    }

    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    print("--- Running Stage 5: Failure Survival & Run Report ---")

    raw_books, pages_count = crawl_catalogue(start_url, max_pages=3, stats=stats)
    stats["catalogue_pages"] = pages_count

    # Deduplicate books
    seen_urls = set()
    unique_books = []
    for b in raw_books:
        if b["product_url"] not in seen_urls:
            seen_urls.add(b["product_url"])
            unique_books.append(b)

    # DELIBERATE TEST INJECTION: Add 1 fake/broken URL to prove resilience!
    fake_book = {
        "product_url": "https://books.toscrape.com/catalogue/deliberate-broken-book_9999/index.html",
        "source_page": "https://books.toscrape.com/catalogue/page-3.html"
    }
    unique_books.append(fake_book)
    print(f"\nQueueing {len(unique_books)} books for extraction (includes 1 deliberate broken URL)...")

    valid_records = []
    error_records = []

    for item in unique_books:
        raw_record = extract_book_record(item["product_url"], item["source_page"], stats)
        
        if raw_record is None:
            stats["failed_pages"] += 1
            error_records.append({
                "product_url": item["product_url"],
                "error": "Failed to fetch HTML or missing product content (HTTP 404/5xx or timeout)"
            })
            continue

        try:
            validated = BookSchema(**raw_record)
            valid_records.append(validated.model_dump())
        except ValidationError as ve:
            stats["invalid_records"] += 1
            error_records.append({
                "product_url": item["product_url"],
                "error": str(ve)
            })

    stats["valid_records"] = len(valid_records)
    stats["duration_seconds"] = round(time.perf_counter() - start_perf, 2)

    # Save outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    errors_file = os.path.join(OUTPUT_DIR, "errors.json")
    with open(errors_file, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)

    report_file = os.path.join(OUTPUT_DIR, "run-report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n--- Checkpoint: Run Report ---")
    print(json.dumps(stats, indent=2))
    print(f"\nFinal Status: {len(valid_records)} good records saved; {stats['failed_pages']} failed page survived cleanly!")

if __name__ == "__main__":
    main()