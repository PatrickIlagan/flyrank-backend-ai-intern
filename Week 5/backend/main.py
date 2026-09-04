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

# 3. Polite Fetcher with Cache
def fetch_page(url: str, cache_filename: str) -> tuple[str, bool]:
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        return html, True

    os.makedirs(CACHE_DIR, exist_ok=True)
    time.sleep(DELAY_BETWEEN_REQUESTS)
    print(f"[FETCH] Live page: {url}...")
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: HTTP status {response.status_code}")
    
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    return response.text, False

# 4. Crawler: Discover First 3 Catalogue Pages
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

# 5. Normalizer: Clean Raw Price String to Float
def clean_price(price_text: str) -> float:
    cleaned = re.sub(r"[^\d.]", "", price_text)
    return float(cleaned) if cleaned else 0.0

# 6. Extractor: Parse Detail Page for a Single Book
def extract_book_record(product_url: str, source_page: str) -> dict:
    path_parts = [p for p in urlparse(product_url).path.split("/") if p and p != "index.html"]
    slug = path_parts[-1] if path_parts else "book"
    cache_filename = f"book-{slug}.html"

    html, was_cached = fetch_page(product_url, cache_filename)
    soup = BeautifulSoup(html, "html.parser")
    
    product_main = soup.select_one(".product_main")
    if not product_main:
        raise ValueError(f"Product main area not found for {product_url}")

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

# 7. Main Runner
def main():
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    print("--- Running Stage 4: Clean, Validate, and Store ---")
    
    raw_books, pages_count = crawl_catalogue(start_url, max_pages=3)
    
    seen_urls = set()
    unique_books = []
    for b in raw_books:
        if b["product_url"] not in seen_urls:
            seen_urls.add(b["product_url"])
            unique_books.append(b)

    print(f"\nProcessing {len(unique_books)} unique books...")
    
    valid_records = []
    error_records = []

    for item in unique_books:
        try:
            raw_record = extract_book_record(item["product_url"], item["source_page"])
            
            # Validate with Pydantic
            validated = BookSchema(**raw_record)
            valid_records.append(validated.model_dump())
        except ValidationError as ve:
            error_records.append({
                "product_url": item["product_url"],
                "error": str(ve)
            })
        except Exception as e:
            error_records.append({
                "product_url": item["product_url"],
                "error": str(e)
            })

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Store valid records idempotently
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
        
    # Store errors if any
    errors_file = os.path.join(OUTPUT_DIR, "errors.json")
    with open(errors_file, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)

    print("\n--- Checkpoint Summary ---")
    print(f"Validated books stored in {books_file}: {len(valid_records)}")
    print(f"Errors recorded in {errors_file}: {len(error_records)}")
    if valid_records:
        first = valid_records[0]
        print(f"Sample book: '{first['title']}' | Price GBP: {first['price_gbp']} (type: {type(first['price_gbp']).__name__})")
        print(f"URL format valid: {first['product_url'].startswith('https://')}")

if __name__ == "__main__":
    main()