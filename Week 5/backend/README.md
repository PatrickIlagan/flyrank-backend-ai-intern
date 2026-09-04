# The Polite Scraper (Books to Scrape Pipeline)

A robust, ethical, and polite web scraping pipeline built in **Python 3.11** using **Requests**, **Beautiful Soup**, and **Pydantic**. The pipeline fetches the first 3 catalogue pages of Books to Scrape, visits all 60 book details pages, normalizes messy HTML into clean typed records, validates them against a strict schema, and produces an honest execution report.

Part of **FlyRank AI Backend Engineering Internship: Week 5 (Assignment A9: The polite scraper)**.

---

## Target Classification (Stage 0)

- **Target Website:** Books to Scrape (https://books.toscrape.com/)
- **Site Purpose:** A dedicated public practice sandbox explicitly created for developers to test and learn web scraping.
- **Permission & Robots Check:** Requested `https://books.toscrape.com/robots.txt` which returned `404 Not Found` (no robots file found). Since the site explicitly declares itself as a scraping sandbox, scraping for practice is authorized.
- **Scope Limit:** Exactly the first 3 catalogue pages (60 book records total). No deep crawls or crawling the full store.
- **Data Collected:** Book Title, Product URL, Price, Availability text, Star rating, Description, Source catalogue page URL, and Timestamp (`fetched_at`).
- **Why Appropriate:** This is a zero-risk educational sandbox. The scraper adheres strictly to polite scraping standards: a named User-Agent, a 10-second timeout, local file caching to prevent repeated network hits, and a polite 500ms delay between live requests.
- **Ethics Pledge:** "I will not reuse this code on another site without checking its rules and terms first."

---

## Quickstart: One Command to Run Everything

### Prerequisites
- Python 3.10+ (tested on Python 3.11)

### 1. Clone the Repository
```bash
git clone https://github.com/PatrickIlagan/flyrank-backend-ai-intern.git
cd "flyrank-backend-ai-intern/Week 5/backend"
```

### 2. Set Up Virtual Environment & Install Dependencies
```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Git Bash / Linux / macOS
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### 3. Run the Scraper Pipeline (One Command)
```bash
python main.py
```

Outputs are automatically generated inside the `output/` directory:
- `output/books.json`: Validated, normalized book catalog records.
- `output/errors.json`: Quarantined errors and malformed pages.
- `output/run-report.json`: Execution metrics, cache hits, and failure recovery report.

---

## The Politeness Rules We Follow

1. **Named User-Agent**: Every request identifies itself:
   `FlyRankInternship-A9/1.0 (+https://github.com/PatrickIlagan/flyrank-backend-ai-intern)`
   Site owners checking logs know exactly who is visiting and how to contact the author.
2. **Local Caching (`cache/`)**: Every downloaded catalogue and detail page is cached locally on disk. During development and testing, reruns read from disk without hitting the live site.
3. **Polite Delay**: Enforces at least 0.5s delay (`time.sleep(0.5)`) between consecutive live requests.
4. **Strict Timeouts**: Requests time out after 10 seconds rather than hanging indefinitely.
5. **Selective Retries**: Only retries temporary server errors (`5xx`) or timeouts. Never retries client errors (`404` or `403`).

---

## Data Schema (Pydantic)

Every record is validated against this strict Pydantic model before writing to `output/books.json`:

```python
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
```

---

## Verified Execution Report (`output/run-report.json`)

Here is the verified output from a complete pipeline run:

```json
{
  "start_time": "2026-09-04T16:35:21.444529+00:00",
  "catalogue_pages": 3,
  "pages_fetched": 1,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "target_site": "https://books.toscrape.com/",
  "duration_seconds": 1.95
}
```

- **Clean Survival**: The scraper gracefully survived the deliberate broken URL test (`failed_pages: 1`), keeping all 60 valid book records completely safe and intact in `output/books.json`.

---

## Engineering Insights

### Why No Browser Was Needed
The data on Books to Scrape is already completely present in the server-rendered HTML sent over plain HTTP. Launching a headless browser like Playwright, Selenium, or Puppeteer would only add unnecessary CPU, RAM, and startup latency without any functional benefit.

### Honest Limitations
Static HTML scraping with Requests and Beautiful Soup cannot execute JavaScript. If a target website dynamically renders its content client-side using a single-page app (SPA) framework like React or Vue, a browser automation engine or reverse-engineering hidden internal API endpoints would be required.

---

## Ethics Note

1. **Use Official APIs**: Always check for an official public API first before building a scraper.
2. **Never Bypass Defenses**: Never attempt to circumvent login screens, paywalls, CAPTCHAs, or IP blocks.
3. **Collect Only What You Need**: Limit scope strictly to relevant data and never hoard unnecessary user or proprietary information.

---

## 💭 Experience Notes

### My Experience
This is really cool! I haven't really experimented much with scraping or getting data from websites but this is a really good track to know what is important and what is not like being polite to the admin's server by introducing ourselves. It also came across to me how important error validation and reporting could really be a lifesaver especially when the app/web gets bigger. Caching is also another thing I was quite curious about and how it works, and honestly this helped visualize it better. Overall, a pretty interesting experience reading and testing all the codes.

### Key Takeaways
- **Scraping Politeness & Transparency**: Introducing the scraper via a custom User-Agent, adding deliberate delays, and respecting server bandwidth.
- **The Power of Local Caching**: Saving raw HTML to disk during development so repetitive testing never hammers the target website.
- **Data Hygiene with Pydantic**: Quarantining malformed records into `errors.json` so `books.json` remains strictly schema-compliant.
- **Resilience and Observability**: Handling page failures gracefully so bad URLs never crash the entire pipeline, and using `run-report.json` for honest job audits.


