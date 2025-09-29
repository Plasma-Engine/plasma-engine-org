#!/usr/bin/env python3
"""
Quick ScraperAPI Test - Minimal test to verify API key works
"""

import httpx
import asyncio
import sys


async def test_scraperapi(api_key: str):
    """Quick test of ScraperAPI functionality"""

    print("🚀 Testing ScraperAPI Key...")
    print(f"   Key preview: {api_key[:10]}...")

    # Test 1: Basic request
    print("\n1️⃣ Testing basic API request...")
    params = {
        "api_key": api_key,
        "url": "http://httpbin.org/ip"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get("http://api.scraperapi.com", params=params)
            response.raise_for_status()

            data = response.json()
            print(f"✅ Success! Your IP via ScraperAPI: {data.get('origin', 'Unknown')}")
            print(f"   Credits used: {response.headers.get('X-API-Credits-Used', 'Unknown')}")
            print(f"   Response status: {response.status_code}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            print(f"❌ API key is invalid or has no credits")
        elif e.response.status_code == 401:
            print(f"❌ Authentication failed - check your API key")
        else:
            print(f"❌ HTTP Error: {e.response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Test 2: Simple web scrape
    print("\n2️⃣ Testing web scraping...")
    params = {
        "api_key": api_key,
        "url": "https://example.com"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get("http://api.scraperapi.com", params=params)
            response.raise_for_status()

            html = response.text
            if "Example Domain" in html:
                print(f"✅ Successfully scraped example.com")
                print(f"   Response length: {len(html)} characters")
                print(f"   Credits used: {response.headers.get('X-API-Credits-Used', 'Unknown')}")
            else:
                print(f"⚠️ Received response but content unexpected")

    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return False

    print("\n" + "="*50)
    print("✅ ScraperAPI is working correctly!")
    print("="*50)
    return True


def main():
    """Main entry point"""

    # Check for API key in command line args
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        print("ScraperAPI Quick Test")
        print("="*50)
        print("Enter your ScraperAPI key (or press Ctrl+C to cancel):")
        print("You can find it at: https://dashboard.scraperapi.com/")
        print()

        try:
            api_key = input("API Key: ").strip()
        except KeyboardInterrupt:
            print("\n\nTest cancelled.")
            return 1

    if not api_key:
        print("❌ No API key provided")
        return 1

    # Run the test
    success = asyncio.run(test_scraperapi(api_key))
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())