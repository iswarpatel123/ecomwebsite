#!/usr/bin/env python3
"""
competitor_pipeline.py — End-to-end Competitor Ads Scraping & Discovery Pipeline

Steps:
1. Discover Brands by Niche (calls admakeai.com/api/trpc/adResearch.discoverNiche)
2. Match Brand Name to Facebook Page ID (calls admakeai.com/api/trpc/adResearch.matchBrandToPage)
3. Fetch Ads for Page ID (calls admakeai.com/api/trpc/adResearch.getCompanyAds)

### Usage Examples:                                                                                                                     
                                                                                                                                                                                                                                                                          
   # Full pipeline from niche discovery to top brand matching and ad fetching                                                            
   python3 scripts/competitor_pipeline.py --niche "office desk"                                                                          
                                                                                                                                         
   # Match a specific brand directly                                                                                                     
   python3 scripts/competitor_pipeline.py --brand "VersaDesk" --niche "office desk"                                                      
                                                                                                                                         
   # Fetch ads directly for a known Facebook Page ID                                                                                     
   python3 scripts/competitor_pipeline.py --page-id 112183837254549                                                                      
                                                                                                                                         
   # Save output to a JSON file                                                                                                          
   python3 scripts/competitor_pipeline.py --niche "office desk" --output results.json  
"""

import argparse
import json
import sys
import requests

# Base tRPC endpoint for admakeai
BASE_URL = "https://admakeai.com/api/trpc"

DEFAULT_HEADERS = {
    "authority": "admakeai.com",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "baggage": "sentry-environment=production,sentry-public_key=299131e12d66765535b4e3ae1768c4bc,sentry-trace_id=25f4dba0151243b8bd53d9aa1ffe78a0,sentry-transaction=%2Ftools%2Ffb-ads-library,sentry-sampled=true,sentry-sample_rand=0.8087696263204484,sentry-sample_rate=1",
    "content-type": "application/json",
    "cookie": "__Host-next-auth.csrf-token=0a8191cc310ae80cbd359c567eea45d7d925945a76ae626ae90ce2e021f42579%7C7ba0298f4bd04a35a0e00c2e24c7042a942da96e92e20e7341ec6c33a27d4f88; __Secure-next-auth.callback-url=https%3A%2F%2Fadmakeai.com%2Fcompetitor-research; cf_clearance=BY5IuHGlEuzwdh29cRBS3yKYfTNl.xYgLBLLqQOUJoQ-1785733323-1.2.1.1-odRY3O1YNZgm4ki8y.P5M5bS2gJ3XNARXt5LhmI6f6DMHB2Kpe1YaRrlsGdmRXch2_b1URwdYRqYR1av1aCgLlotiwSHhjj2D5ecP29xqbEo_DeCSN5BnN2pz007sbgcxqAVOmt.TLpSo2tj38coVGNcfpGK6QxHbDSbvS2RvF8R65DBa5rnU5lEPojaBwnckMAaLZt7L0yUSxmqS8KYUjzc3tnsUx_hl.Ui663qMb.lCb.4Le9eD9kbjkUdrHheBNyUmufPS.J8zch0MhrHL1hPK38EhUxXd2ae.OCkUMNc_kNuX.gGhfSL_FBS.ijc.aLZYT..JPeZTBZoUR6HdBf8WBAV0aNrVzFcwHWopxc; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..wMGX6kabjNBEpP2Y.5JhcgRSMXaIIu6U-PoQmJIbbyx83d-sKE1ipo_M5MDsBO6NRUQ2wCgXLrx9h20dgFstX7YmG40a4oWBEZH51cww-WMBggPa3YvAzFVXGG1MC_U3SaeBtNXF-FdwVjK56VGrhOUeL-nZfTlP8X-aHH7RNR1nHSp8r_UM6dlgPevq0ZkZsUyrngRgsikO_XuBhWpaB-F-UlRKp15PRdC6aYxMyIehnFG8vMkLmQ6ZZoywhZvYJWX4qgHln9QF2rKcUh4mP-nff_E54c1p5RVWvrye3I7P1Qv7kWR-KKzcGIZSW5BebWa4kMmr7lJ0.NRNXPlOnOsfTX3PN2ILwvg",
    "origin": "https://admakeai.com",
    "priority": "u=1, i",
    "referer": "https://admakeai.com/tools/fb-ads-library",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sentry-trace": "25f4dba0151243b8bd53d9aa1ffe78a0-ba611077164356e5-1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
}

def discover_niche(niche: str) -> list:
    """Step 1: Discover brands for a given niche."""
    url = f"{BASE_URL}/adResearch.discoverNiche"
    payload = {"json": {"niche": niche}}
    
    print(f"[*] Discovering brands for niche: {niche!r}...")
    try:
        response = requests.get(url, params={"input": json.dumps(payload)}, headers=DEFAULT_HEADERS)
        if response.status_code != 200:
            response = requests.post(url, json=payload, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        
        data = response.json()
        brands = data.get("result", {}).get("data", {}).get("json", {}).get("brands", [])
        return brands
    except Exception as e:
        print(f"[!] Error discovering niche: {e}", file=sys.stderr)
        return []

def match_brand_to_page(brand_name: str, original_query: str = "") -> dict:
    """Step 2: Match brand name to Facebook Page ID."""
    url = f"{BASE_URL}/adResearch.matchBrandToPage"
    payload = {"json": {"brandName": brand_name, "originalQuery": original_query}}
    
    print(f"[*] Matching brand {brand_name!r} to Facebook Page...")
    try:
        response = requests.get(url, params={"input": json.dumps(payload)}, headers=DEFAULT_HEADERS)
        if response.status_code != 200:
            response = requests.post(url, json=payload, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        
        data = response.json()
        result_json = data.get("result", {}).get("data", {}).get("json", {})
        return result_json
    except Exception as e:
        print(f"[!] Error matching brand to page: {e}", file=sys.stderr)
        return {}

def get_company_ads(page_id: str) -> list:
    """Step 3: Fetch ads for a Facebook page ID."""
    url = f"{BASE_URL}/adResearch.getCompanyAds"
    payload = {"json": {"pageId": page_id}}
    
    print(f"[*] Fetching ads for pageId: {page_id}...")
    try:
        response = requests.get(url, params={"input": json.dumps(payload)}, headers=DEFAULT_HEADERS)
        if response.status_code != 200:
            response = requests.post(url, json=payload, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        
        data = response.json()
        ads = data.get("result", {}).get("data", {}).get("json", {}).get("ads", [])
        return ads
    except Exception as e:
        print(f"[!] Error fetching company ads: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="End-to-end Competitor Ads Pipeline (Niche -> Brands -> PageID -> Ads)")
    parser.add_argument("--niche", type=str, help="Niche keyword to search (e.g., 'office desk')")
    parser.add_argument("--brand", type=str, help="Skip niche discovery and match this specific brand name directly")
    parser.add_argument("--page-id", type=str, help="Skip discovery and matching, fetch ads directly for this page ID")
    parser.add_argument("--output", type=str, help="Optional output JSON file path to save results")
    
    args = parser.parse_args()
    
    output_data = {}

    if args.page_id:
        page_id = args.page_id
        ads = get_company_ads(page_id)
        output_data = {"pageId": page_id, "ads": ads}
        print(f"\n[+] Found {len(ads)} ads for page ID {page_id}")
        
    elif args.brand:
        brand_name = args.brand
        match_result = match_brand_to_page(brand_name, args.niche or "")
        output_data = {"brand": brand_name, "match": match_result}
        best = match_result.get("best", {})
        page_id = best.get("pageId")
        print(f"\n[+] Match Result for {brand_name}:")
        print(json.dumps(match_result, indent=2))
        
        if page_id:
            ads = get_company_ads(page_id)
            output_data["ads"] = ads
            print(f"\n[+] Found {len(ads)} ads for matched page ID {page_id}")
            
    elif args.niche:
        niche = args.niche
        brands = discover_niche(niche)
        output_data = {"niche": niche, "brands": brands}
        print(f"\n[+] Discovered {len(brands)} brands for niche {niche!r}:")
        for b in brands:
            print(f"  - {b.get('name')}: {b.get('why')}")
            
        # Automatically match the first brand or all brands
        if brands:
            first_brand = brands[0].get("name")
            print(f"\n[*] Automatically matching top brand: {first_brand!r}...")
            match_result = match_brand_to_page(first_brand, niche)
            output_data["top_brand_match"] = match_result
            best = match_result.get("best", {})
            page_id = best.get("pageId")
            print(f"    Page ID: {page_id} ({best.get('name')})")
            
            if page_id:
                ads = get_company_ads(page_id)
                output_data["top_brand_ads"] = ads
                print(f"    Fetched {len(ads)} ads for {first_brand} (Page ID: {page_id})")
    else:
        parser.error("Provide at least one of --niche, --brand, or --page-id")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved results to {args.output}")

if __name__ == "__main__":
    main()
