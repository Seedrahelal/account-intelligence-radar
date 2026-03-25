###Responsible for extracting information from selected links
import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {
            "type": "string",
            "description": "Official company name"
        },
        "headquarters": {
            "type": "string",
            "description": "Company headquarters location"
        },
        "business_units": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of business units or divisions"
        },
        "products_and_services": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Main products and services offered"
        },
        "target_industries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Industries the company serves"
        },
        "key_executives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "title": {"type": "string"}
                }
            },
            "description": "Named executives with titles from official sources only"
        },
        "strategic_initiatives": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recent strategic initiatives: AI, ERP, expansions, investments"
        }
    },
    "required": #It tells Firecrawl: These fields are mandatory — if you don't find them, there's a problem.
    [ 
        "company_name",
        "headquarters"
    ]
}

def extract_company_data(selected_urls, company_name, objective):

    print(f" Extracting data from {len(selected_urls)} URLs...")

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print(" Error: FIRECRAWL_API_KEY not found in .env")
        return None

    if not selected_urls:
        print(" Error: no URLs to extract from")
        return None

    url_strings = []
    for result in selected_urls:
        url = result.get("url", "")
        if url:
            url_strings.append(url)

    if not url_strings:
        print(" Error: no valid URLs found")
        return None

    print(f" URLs to extract from:")
    for url in url_strings:
        print(f"   - {url}")

    extraction_prompt = f"""
                        Extract detailed information about {company_name}.
                        Objective: {objective}

                        Focus on:
                        - Company headquarters and official identifiers
                        - Business units, products, and services
                        - Key executives (only from official sources)
                        - Recent strategic initiatives and investments
                        - Target industries and markets

                        Only extract information that is explicitly stated in the page.
                        Do not guess or infer information that is not present.
                        """

    try:
        firecrawl = FirecrawlApp(api_key=api_key)

        response = firecrawl.extract(
            urls=url_strings,
            prompt=extraction_prompt,
            schema=EXTRACTION_SCHEMA
        )

        if not response or not response.data:
            print(" Error: Firecrawl returned empty data")
            return None

        extracted_data = response.data

        extracted_data = clean_extracted_data(extracted_data)
        extracted_data["source_urls"] = url_strings

        print(" Extraction completed successfully")
        return extracted_data

    except Exception as e:
        error_message = str(e)

        if "401" in error_message:
            print(" Error 401: Invalid Firecrawl API key")
        elif "402" in error_message:
            print(" Error 402: Insufficient Firecrawl credits")
        elif "timeout" in error_message.lower():
            print(" Error: Firecrawl request timed out")
        elif "not ready" in error_message.lower():
            print(" Error: Firecrawl extraction not ready yet")
        else:
            print(f" Unexpected error: {error_message}")

        return None
    

def clean_extracted_data(data):
    """
    Removes duplicate entries from extracted data
    Handles case-insensitive duplicates and duplicate executives
    """

    if not data:
        return data

    # Clean simple string lists — case-insensitive deduplication
    # Keeps the first occurrence, removes later duplicates
    list_fields = [
        "business_units",
        "products_and_services",
        "target_industries",
        "strategic_initiatives"
    ]

    for field in list_fields:
        original_list = data.get(field, [])
        seen = set()
        cleaned_list = []

        for item in original_list:
            # Normalize: lowercase + strip whitespace = comparison key
            normalized = item.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                cleaned_list.append(item.strip().title())

        data[field] = cleaned_list

    # Clean executives — deduplicate by last name
    # If same last name appears twice, keep the one with longer title
    executives = data.get("key_executives", [])
    seen_lastnames = {}

    for exec in executives:
        name = exec.get("name", "").strip()
        title = exec.get("title", "").strip()

        if not name:
            continue

        # Extract last name as the deduplication key
        last_name = name.split()[-1].lower()

        if last_name not in seen_lastnames:
            seen_lastnames[last_name] = exec
        else:
            # Keep the entry with the longer, more descriptive title
            existing_title = seen_lastnames[last_name].get("title", "")
            if len(title) > len(existing_title):
                seen_lastnames[last_name] = exec

    data["key_executives"] = list(seen_lastnames.values())

    return data

