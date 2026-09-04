import os
import requests

# 1. Polite Configuration
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/PatrickIlagan/flyrank-backend-ai-intern)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT_SECONDS = 10
CACHE_DIR = "cache"

# 2. Fetch with Local Caching
def fetch_page(url: str, cache_filename: str) -> str:
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    # Check if we already downloaded this page before
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"[CACHE HIT] Loaded from {cache_path} ({len(html)} bytes)")
        return html

    # If not cached, fetch it politely from the live web
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f"[FETCH] Requesting live page: {url}...")
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    
    # Strict status validation
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}: HTTP status {response.status_code}")
    
    # Save to local cache
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"[FETCH SUCCESS] Saved to {cache_path} ({len(response.text)} bytes, status {response.status_code})")
    return response.text

# 3. Main Runner
def main():
    target_url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_file = "catalogue-page-1.html"
    
    print("--- Running Stage 1 Scraper ---")
    html = fetch_page(target_url, cache_file)
    print(f"Page ready for parsing! Length: {len(html)} characters.")

if __name__ == "__main__":
    main()