#!/usr/bin/env python3
import requests
import json
import sys
import argparse

def fetch_namelix_logos(keywords, max_length=25, extensions=None, require_domains=True):
    url = "https://namelix.com/generate"
    
    payload = {
        "keywords": keywords,
        "description": "DTC ecommerce brand related to keywords",
        "blacklist": "",
        "max_length": max_length,
        "style": "default",
        "random": "low",
        "extensions": extensions if extensions else ["com"],
        "require_domains": require_domains,
        "prev_names": [],
        "prev_references": [],
        "ban_history": [],
        "saved": [],
        "premium_index": 0,
        "page": 0,
        "num": 3,
        "seed": 871557358,
        "category": ""
    }
    
    headers = {
        "authority": "namelix.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://namelix.com",
        "priority": "u=1, i",
        "referer": f"https://namelix.com/app/?keywords={keywords}",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Filter items with "hasDomain": false and extract businessName
        business_names = []
        for logo in data.get("logos", []):
            if not logo.get("hasDomain", True):  # Only include items without domain
                business_name = logo.get("businessName")
                if business_name:
                    business_names.append(business_name)
        
        return business_names
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Namelix brand names without domains")
    parser.add_argument("keyword", help="Keyword to search for brand names")
    parser.add_argument("--max-length", type=int, default=25, help="Maximum length of brand name")
    parser.add_argument("--num", type=int, default=3, help="Number of results to fetch")
    
    args = parser.parse_args()
    
    # Fetch logos for the provided keyword
    business_names = fetch_namelix_logos(
        args.keyword, 
        max_length=args.max_length,
        require_domains=False
    )
    
    print(business_names)