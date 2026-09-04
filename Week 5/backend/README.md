# The Polite Scraper (Books to Scrape Pipeline)

A robust, ethical, and polite web scraping pipeline built in **Python 3.11** using **Requests**, **Beautiful Soup**, and **Pydantic**. The pipeline fetches the first 3 catalogue pages of Books to Scrape, visits all 60 book details pages, normalizes messy HTML into clean typed records, validates them against a strict schema, and produces an honest execution report.

Part of **FlyRank AI Backend Engineering Internship: Week 5 (Assignment A9: The polite scraper)**.

---

## Target Classification (Stage 0)

- **Target Website:** Books to Scrape (https://books.toscrape.com/)
- **Site Purpose:** A dedicated public practice sandbox explicitly created for developers to test and learn web scraping.
- **Permission & Robots Check:** Requested https://books.toscrape.com/robots.txt which returned 404 Not Found (no robots file found). Since the site explicitly declares itself as a scraping sandbox, scraping for practice is authorized.
- **Scope Limit:** Exactly the first 3 catalogue pages (60 book records total). No deep crawls or crawling the full store.
- **Data Collected:** Book Title, Product URL, Price, Availability text, Star rating, Description, Source catalogue page URL, and Timestamp (etched_at).
- **Why Appropriate:** This is a zero-risk educational sandbox. The scraper adheres strictly to polite scraping standards: a named User-Agent, a 10-second timeout, local file caching to prevent repeated network hits, and a polite 500ms delay between live requests.
- **Ethics Pledge:** "I will not reuse this code on another site without checking its rules and terms first."

---

## Stages & Checklist
- [ ] **Stage 0: Classify Scraping Target**: Classify target site, verify sandbox purpose, check robots.txt, and document scope.
- [ ] **Stage 1: Fetch and Cache HTML**: Implement polite fetch with custom User-Agent, timeout, status check, and local disk cache (cache/catalogue-page-1.html).
- [ ] **Stage 2: Discover Three Catalogue Pages**: Parse pagination, convert relative links to absolute URLs with urljoin, and discover 60 book URLs.
- [ ] **Stage 3: Extract Book Details**: Fetch and cache 60 book detail pages and extract 8 raw fields (including provenance receipts).
- [ ] **Stage 4: Validate Normalized Records**: Normalize prices to floats, validate against Pydantic schema, and write to output/books.json.
- [ ] **Stage 5: Survive Failures, Report the Run**: Handle errors gracefully, retry server errors, survive a fake URL, and generate output/run-report.json.
- [ ] **Stage 6: Publish Scraper Evidence**: Finalize documentation, verify cache is git-ignored, and push.
