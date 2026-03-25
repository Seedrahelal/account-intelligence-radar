# Consultant Summary — Account Intelligence Radar
**Seedra Helal | Averroa Training | March 2026**

---

## 1. The Problem I Solved

Sales and business development teams waste hours researching
companies manually before outreach — searching Google, reading
multiple pages, and trying to piece together a coherent picture
of who the company is, who leads it, and what they are focused on.

This tool automates that research pipeline. You give it a company
name and an objective, and it returns a structured intelligence
report in minutes — with every claim linked to a source URL.

The business impact is direct: faster pipeline generation,
more informed outreach, and less time wasted on manual research.

---

## 2. Architecture Decisions

### Why three separate APIs instead of one?

Each API does one thing well:
- **SerpAPI** is reliable for discovery — it gives structured
  Google results without dealing with HTML parsing
- **DeepSeek** is used as a decision layer — it reads the search
  results and picks the most relevant URLs, so Firecrawl does not
  waste credits on low-quality pages
- **Firecrawl** handles the hard part — entering websites and
  extracting structured data without writing custom scrapers

This separation makes the pipeline easy to debug and easy to
swap one component without breaking the others.

### Why Streamlit instead of React or Flutter?

I am learning Python and AI — not frontend development.
Streamlit lets me build a working web interface using only
Python, which keeps the focus on the intelligence pipeline
rather than UI complexity.

### Why DeepSeek instead of a bigger model?

Cost and simplicity. DeepSeek is affordable for this use case
and compatible with the OpenAI SDK, which made integration
straightforward. The task — selecting URLs from a list — does
not require a large reasoning model.

### Why structured JSON schema for Firecrawl?

Without a schema, Firecrawl returns raw text that still needs
parsing. With a schema, it returns exactly the fields we need
in a format the app can use directly. This also makes the
output consistent across different companies and industries.

---

## 3. Key Risks and How I Handled Them

### API failures and timeouts
Every API call is wrapped in try/except blocks with specific
error messages for each failure type — timeout, no internet,
402 insufficient balance, invalid JSON response.
If DeepSeek fails, the pipeline falls back to the first 3
search results rather than stopping completely.

### Data quality and duplicates
Firecrawl sometimes extracts the same information from multiple
sources with slightly different wording. I added a cleaning
function that removes case-insensitive duplicates from all list
fields, and deduplicates executives by last name — keeping the
entry with the more descriptive title.

### Secret key exposure
API keys are stored in a `.env` file that is listed in
`.gitignore` — they are never hardcoded in the source code
and never committed to version control.

### LinkedIn scraping
The assignment explicitly prohibits LinkedIn scraping.
The tool does not attempt to access LinkedIn at any point.
For leadership information, it relies on official company
websites, annual reports, and trusted news sources only.

### Traceability
Every report includes a `source_urls` field that lists all
URLs used during extraction. This satisfies the requirement
that every major claim must be linked to at least one source.

---

## 4. What I Would Improve Next

### Semantic duplicate detection
The current deduplication is text-based — it catches exact
and case-insensitive duplicates but misses semantic ones like
"Rail Transportation" and "Rail Transport". A better approach
would use text embeddings to detect similar meanings.

### Full Geography Mode pipeline
Right now Geography Mode returns a list of company names.
The next step is to automatically run the full Company Mode
pipeline for each discovered company and return all reports
in one batch.

### Caching
Running the same company twice costs API credits both times.
Adding a simple cache — storing results by company name and
date — would reduce redundant calls significantly.

### Unit tests
I did not write unit tests in this version due to time
constraints. The highest priority would be tests for the
JSON cleaning function and the URL selection logic, since
those are the most likely points of failure.

### Cost tracking
The tool currently has no visibility into how many API credits
each run consumes. Adding a usage counter would help users
manage their free tier limits.

---

*This project was my first experience building a multi-API
pipeline from scratch.*