### Responsible for analyzing links and selecting the best ones via DeepSeek
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MAX_SELECTED_URLS = 5
BASE_URL_DEEPSEEK="https://api.deepseek.com"


def analyze_and_select_urls(search_results, company_name, objective):
    print(f" Analyzing {len(search_results)} search results...")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print(" Error: DEEPSEEK_API_KEY not found in .env")
        return []

    if not search_results:
        print(" Error: search results list is empty")
        return []

    formatted_results = ""
    for i, result in enumerate(search_results):
        formatted_results += f"""
                            [{i}] Title: {result.get('title', '')}
                                URL: {result.get('url', '')}
                                Snippet: {result.get('snippet', '')}
                                Type: {result.get('source_type', '')}
                            """

    messages = [
        {
            "role": "system",
            "content": """You are an expert in analyzing business intelligence sources.
            Your task is to select the best URLs for accurate company information.
            Prefer: official websites, annual reports, trusted news sources.
            Avoid: personal blogs, forums, unreliable websites.
            You must respond with JSON only, no additional text."""
        },
        {
            "role": "user",
            "content": f"""Company: {company_name}
                            Objective: {objective}
                            Available URLs:{formatted_results}
                            Select the best {MAX_SELECTED_URLS} URLs to achieve the objective.
                            Respond with JSON only in exactly this format:
                            {{
                                "selected_indices": [0, 2, 4],
                                "reasoning": "brief reason for selection"
                            }}"""
        }
    ]

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=BASE_URL_DEEPSEEK
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )

        raw_response = response.choices[0].message.content
        print(f" DeepSeek response: {raw_response}")

        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

        parsed = json.loads(cleaned)
        selected_indices = parsed.get("selected_indices", [])
        reasoning = parsed.get("reasoning", "")

        print(f" DeepSeek selected {len(selected_indices)} URLs")
        print(f" Reasoning: {reasoning}")

        selected_results = []
        for i in selected_indices:
            if 0 <= i < len(search_results):
                selected_results.append(search_results[i])

        return selected_results

    except json.JSONDecodeError:
        print(" Error: DeepSeek did not return valid JSON")
        print(" Falling back to first 3 results")
        return search_results[:3]

    except Exception as e:
        if "402" in str(e):
            print(" Error 402: Insufficient DeepSeek balance")
            print(" Falling back to first 3 results")
            return search_results[:3]

        print(f" Unexpected error: {e}")
        return []

def extract_company_names(search_results, location, sectors):

    print(f" Extracting company names from search results...")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print(" Error: DEEPSEEK_API_KEY not found in .env")
        return []

    if not search_results:
        print(" Error: search results list is empty")
        return []

    formatted_results = ""
    for i, result in enumerate(search_results):
        formatted_results += f"""
                                [{i}] Title: {result.get('title', '')}
                                    Snippet: {result.get('snippet', '')}
                                """

    messages = [
        {
            "role": "system",
            "content": """You are an expert in identifying company names from search results.
            Extract only real company names that match the given location and sectors.
            You must respond with JSON only, no additional text."""
        },
        {
            "role": "user",
            "content": f"""Location: {location}
            Sectors: {sectors}

            Search results:
            {formatted_results}

            Extract up to 5 real company names that are based in {location} 
            and operate in these sectors: {sectors}

            Respond with JSON only in exactly this format:
            {{
                "companies": ["Company A", "Company B", "Company C"],
                "reasoning": "brief reason for selection"
            }}"""
        }
    ]

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=BASE_URL_DEEPSEEK
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )

        raw_response = response.choices[0].message.content
        print(f" DeepSeek response: {raw_response}")

        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

        parsed = json.loads(cleaned)
        companies = parsed.get("companies", [])
        reasoning = parsed.get("reasoning", "")

        print(f" Found {len(companies)} companies: {companies}")
        print(f" Reasoning: {reasoning}")

        return companies

    except json.JSONDecodeError:
        print(" Error: DeepSeek did not return valid JSON")
        return []

    except Exception as e:
        if "402" in str(e):
            print(" Error 402: Insufficient DeepSeek balance")
        else:
            print(f" Unexpected error: {e}")
        return []
    
    