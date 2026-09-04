# Week 5

## Goals
- Understand web scraping ethics, target classification, and polite scraping rules.
- Build a resilient scraping pipeline with caching, timeouts, and user-agent identification.
- Extract structured data from HTML pages and normalize raw fields into typed values.
- Validate scraped records using Pydantic schemas and survive broken pages with a run report.

## Tasks
- [x] **Backend Track: The Polite Scraper (Assignment A9)**: Built a 7-stage polite scraping pipeline for Books to Scrape with caching, Beautiful Soup parsing, Pydantic schema validation, and failure survival. See `backend/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### My Experience
This is really cool! I haven't really experimented much with scraping or getting data from websites but this is a really good track to know what is important and what is not like being polite to the admin's server by introducing ourselves. It also came across to me how important error validation and reporting could really be a lifesaver especially when the app/web gets bigger. Caching is also another thing I was quite curious about and how it works, and honestly this helped visualize it better. Overall, a pretty interesting experience reading and testing all the codes.

### Key Takeaways
- **Scraping Politeness & Transparency**: Introducing the scraper via a custom User-Agent, adding deliberate delays, and respecting server bandwidth.
- **The Power of Local Caching**: Saving raw HTML to disk during development so repetitive testing never hammers the target website.
- **Data Hygiene with Pydantic**: Quarantining malformed records into `errors.json` so `books.json` remains strictly schema-compliant.
- **Resilience and Observability**: Handling page failures gracefully so bad URLs never crash the entire pipeline, and using `run-report.json` for honest job audits.

## Notes
- Full project code, setup guide, and documentation live in `backend/`.



