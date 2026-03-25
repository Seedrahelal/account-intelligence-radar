### Responsible for Google search via SerpAPI
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERP_ENDPOINT = "https://serpapi.com/search" # API Endpoint
REQUEST_TIMEOUT = 30 # Maximum waiting time in seconds
MAX_SEARCH_RESULTS = 10 # Number of search results from which the AI ​​selects


def search_company(company_name, objective):
    print(f" Searching for: {company_name}")

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print(" Error: SERPAPI_KEY not found in .env")
        return []

    params = {
        "q": f"{company_name} {objective}",
        "api_key": api_key,
        "num": MAX_SEARCH_RESULTS
    }

    try:
        response = requests.get(
            SERP_ENDPOINT,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if not response.ok:
            print(f" Error from SerpAPI: {response.status_code}")
            return []

        data = response.json()
        print("Available keys:", data.keys())
        print(json.dumps(data, indent=2))
        results = []

        knowledge = data.get("knowledge_graph", {})
        if knowledge:
            kg_url = (
                knowledge.get("website") or
                knowledge.get("source", {}).get("link") or
                ""
            )
            if kg_url:
                results.append({
                    "title": knowledge.get("title", company_name),
                    "url": kg_url,
                    "snippet": knowledge.get("description", ""),
                    "source_type": "knowledge_graph"
                })

        for item in data.get("organic_results", []):
            url = (
                item.get("link") or
                item.get("url") or
                item.get("href") or
                ""
            )
            title = (
                item.get("title") or
                item.get("name") or
                ""
            )
            snippet = (
                item.get("snippet") or
                item.get("description") or
                item.get("summary") or
                ""
            )

            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source_type": "organic"
                })

        for item in data.get("news_results", []):
            url = (
                item.get("link") or
                item.get("url") or
                ""
            )
            title = item.get("title") or ""
            snippet = item.get("snippet") or ""

            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source_type": "news"
                })

        if not results:
            print("No results found")
            return []

        print(f" Found {len(results)} results")
        return results

    except requests.exceptions.Timeout:
        print(f" Timeout after {REQUEST_TIMEOUT} seconds")
        return []

    except requests.exceptions.ConnectionError:
        print(" No internet connection")
        return []

    except requests.exceptions.RequestException as e:
        print(f" Error in request: {e}")
        return []

    except Exception as e:
        print(f" Unexpected error: {e}")
        return []


def search_companies_by_geography(location, sectors, objective):
    
    print(f" Searching for companies in: {location} | Sectors: {sectors}")

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print(" Error: SERPAPI_KEY not found in .env")
        return []

    params = {
        "q": f"top companies in {location} {sectors} industry",
        "api_key": api_key,
        "num": MAX_SEARCH_RESULTS
    }

    try:
        response = requests.get(
            SERP_ENDPOINT,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if not response.ok:
            print(f" Error from SerpAPI: {response.status_code}")
            return []

        data = response.json()
        results = []

        for item in data.get("organic_results", []):
            url = (
                item.get("link") or
                item.get("url") or
                ""
            )
            title = item.get("title") or ""
            snippet = (
                item.get("snippet") or
                item.get("description") or
                ""
            )

            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source_type": "organic"
                })

        knowledge = data.get("knowledge_graph", {})
        if knowledge:
            kg_url = (
                knowledge.get("website") or
                knowledge.get("source", {}).get("link") or
                ""
            )
            if kg_url:
                results.append({
                    "title": knowledge.get("title", ""),
                    "url": kg_url,
                    "snippet": knowledge.get("description", ""),
                    "source_type": "knowledge_graph"
                })

        if not results:
            print(" No results found")
            return []

        print(f" Found {len(results)} results")
        return results

    except requests.exceptions.Timeout:
        print(f" Connection timed out after {REQUEST_TIMEOUT} seconds")
        return []

    except requests.exceptions.ConnectionError:
        print(" No internet connection")
        return []

    except requests.exceptions.RequestException as e:
        print(f" Request error: {e}")
        return []

    except Exception as e:
        print(f" Unexpected error: {e}")
        return []