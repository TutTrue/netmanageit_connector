#!/usr/bin/env python3
"""
Script to get all Indicators from OpenCTI GraphQL API
This script loops through all pages and counts the total results (IDs only for speed)
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class OpenCTIIndicatorsFetcher:
    def __init__(self, api_url: str, auth_token: str):
        self.api_url = api_url
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        
    def make_request(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Make a GraphQL request to fetch indicators"""
        query = """
        query IndicatorsLinesPaginationQuery($search: String, $count: Int!, $cursor: ID, $filters: FilterGroup, $orderBy: IndicatorsOrdering, $orderMode: OrderingMode) { 
            indicators(search: $search, first: $count, after: $cursor, filters: $filters, orderBy: $orderBy, orderMode: $orderMode) { 
                edges { 
                    node { 
                        id 
                    } 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                    globalCount 
                } 
            } 
        }
        """
        
        variables = {
            "count": 5000,
            "cursor": cursor,
            "orderMode": "desc",
            "orderBy": "created"
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            raise
    
    def fetch_all_indicators(self, output_file: str = "indicators_count.json") -> Dict[str, Any]:
        """Fetch all indicators by looping through all pages (count only, no storage)"""
        print("Starting to fetch all Indicators...")
        print("Mode: COUNT ONLY (no data storage for speed)")
        print("-" * 40)
        
        cursor = None
        page_count = 0
        total_count = 0
        global_count = 0

        all_edges = []
        
        while True:
            page_count += 1
            print(f"Fetching page {page_count}...")
            
            try:
                response = self.make_request(cursor)
                
                # Check for GraphQL errors
                if "errors" in response:
                    print(f"GraphQL errors: {response['errors']}")
                    break
                
                # Extract data
                data = response.get("data", {}).get("indicators", {})
                edges = data.get("edges", [])
                page_info = data.get("pageInfo", {})
                
                has_next = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                global_count = page_info.get("globalCount", 0)
                
                # Count edges in this page
                page_edges_count = len(edges)
                total_count += page_edges_count
                
                print(f"  Page {page_count}: {page_edges_count} indicators (Total so far: {total_count})")
                
                # No storage - just counting for speed

                all_edges.extend(edges)
                # Check if we have more pages
                if not has_next:
                    print("No more pages to fetch.")
                    break

                if page_count > 10:
                    break
                
                # Safety check to prevent infinite loops
                if page_count > 1000:
                    print("Warning: Reached maximum page limit (1000). Stopping.")
                    break
                
                # Small delay to be respectful to the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error on page {page_count}: {e}")
                break
        
        print("-" * 40)
        print("Fetching completed!")
        print(f"Total pages fetched: {page_count}")
        print(f"Total indicators found: {total_count}")
        print(f"Global count from API: {global_count}")
        
        # Create minimal result structure (count only)
        result = {
            "summary": {
                "totalPages": page_count,
                "totalIndicators": total_count,
                "globalCount": global_count,
                "fetchDate": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Save to file
        print(f"Creating count summary file: {output_file}")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        with open("all_observables.json", 'w') as f:
            json.dump(all_edges, f, indent=2)
        
        print(f"Count summary saved to: {output_file}")
        print("Summary:")
        print(f"  - Total pages: {page_count}")
        print(f"  - Total indicators: {total_count}")
        print(f"  - Global count: {global_count}")
        
        return result

def main():
    """Main function"""
    API_URL = "https://opencti.netmanageit.com/graphql"
    AUTH_TOKEN = "56ed1bf8-c1e8-4a88-bcf5-a8519ad6e9a4"
    OUTPUT_FILE = "indicators_count.json"
    
    try:
        fetcher = OpenCTIIndicatorsFetcher(API_URL, AUTH_TOKEN)
        result = fetcher.fetch_all_indicators(OUTPUT_FILE)
        
        # Print final statistics
        summary = result["summary"]
        print("\n" + "=" * 50)
        print("FINAL STATISTICS")
        print("=" * 50)
        print(f"Total Pages Processed: {summary['totalPages']}")
        print(f"Total Indicators Retrieved: {summary['totalIndicators']}")
        print(f"Global Count from API: {summary['globalCount']}")
        print(f"Fetch Date: {summary['fetchDate']}")
        
        # Validate counts
        if summary['totalIndicators'] == summary['globalCount']:
            print("✓ Count validation: PASSED")
        else:
            print("⚠ Count validation: MISMATCH")
            print(f"  Retrieved: {summary['totalIndicators']}")
            print(f"  Expected: {summary['globalCount']}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())