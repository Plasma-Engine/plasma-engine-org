#!/usr/bin/env python3
"""
Scrape X.com (Twitter) profile using ScraperAPI with advanced settings
"""

import asyncio
import httpx
import json
from datetime import datetime

SCRAPERAPI_KEY = "35e44a7b6f2dcd3a707c4c7f36ff2c1a"


async def scrape_x_profile_advanced(username: str):
    """
    Try multiple methods to scrape X/Twitter profile
    """

    print(f"🐦 Attempting to scrape @{username} from X.com")
    print("=" * 60)

    methods = [
        {
            "name": "X.com with premium proxy",
            "url": f"https://x.com/{username}",
            "params": {
                "api_key": SCRAPERAPI_KEY,
                "url": f"https://x.com/{username}",
                "premium": "true",  # Use premium proxies
                "render": "true",
                "country_code": "us",
                "device_type": "desktop"
            }
        },
        {
            "name": "Mobile X.com",
            "url": f"https://mobile.x.com/{username}",
            "params": {
                "api_key": SCRAPERAPI_KEY,
                "url": f"https://mobile.x.com/{username}",
                "device_type": "mobile",
                "premium": "true"
            }
        },
        {
            "name": "X.com search",
            "url": f"https://x.com/search?q=from%3A{username}&f=live",
            "params": {
                "api_key": SCRAPERAPI_KEY,
                "url": f"https://x.com/search?q=from%3A{username}&f=live",
                "render": "true",
                "premium": "true"
            }
        }
    ]

    for method in methods:
        print(f"\n📡 Trying: {method['name']}")
        print(f"   URL: {method['url']}")

        try:
            async with httpx.AsyncClient(timeout=70) as client:
                response = await client.get(
                    "http://api.scraperapi.com",
                    params=method["params"]
                )

                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    html = response.text
                    print(f"   ✅ Success! Got {len(html)} bytes")

                    # Save HTML for analysis
                    filename = f"{username}_{method['name'].replace(' ', '_')}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"   💾 Saved to {filename}")

                    # Check if we got real content
                    if username.lower() in html.lower():
                        print(f"   ✅ Found username in content!")
                        return {
                            "success": True,
                            "method": method["name"],
                            "html_length": len(html),
                            "filename": filename
                        }
                else:
                    print(f"   ❌ Failed with status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return {"success": False, "error": "All methods failed"}


async def try_api_endpoint_directly():
    """
    Try using ScraperAPI's autoparse feature
    """

    print("\n🔧 Trying ScraperAPI autoparse feature...")

    url = "https://x.com/xkonjin"
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "autoparse": "true",  # Try to get structured data
        "premium": "true"
    }

    try:
        async with httpx.AsyncClient(timeout=70) as client:
            response = await client.get("http://api.scraperapi.com", params=params)

            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Got structured data!")
                    return data
                except:
                    print("ℹ️ Got HTML instead of JSON")
                    return response.text
            else:
                print(f"❌ Failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

    return None


async def get_public_info_alternative():
    """
    Try alternative public endpoints that might work
    """

    print("\n🌐 Trying alternative public methods...")

    # Try to get user info from public sources
    alternatives = [
        {
            "name": "Public timeline embed",
            "url": f"https://publish.twitter.com/oembed?url=https://twitter.com/xkonjin"
        },
        {
            "name": "Profile card",
            "url": f"https://x.com/i/api/1.1/users/show.json?screen_name=xkonjin"
        }
    ]

    for alt in alternatives:
        print(f"\n   Trying: {alt['name']}")

        params = {
            "api_key": SCRAPERAPI_KEY,
            "url": alt["url"],
            "render": "false"  # These don't need JS
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get("http://api.scraperapi.com", params=params)

                if response.status_code == 200:
                    print(f"   ✅ Got response")
                    return response.text
                else:
                    print(f"   ❌ Status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return None


async def main():
    """Main execution"""

    print("🚀 Advanced X/Twitter Scraping Attempt")
    print("=" * 60)
    print("⚠️ Note: Twitter/X has very strong anti-scraping measures")
    print("For reliable access, use:")
    print("  1. Apify's Twitter Scraper actor")
    print("  2. Official Twitter API")
    print("  3. Social media monitoring tools")
    print("=" * 60)

    # Try main scraping
    result = await scrape_x_profile_advanced("xkonjin")

    # Try autoparse
    autoparse_result = await try_api_endpoint_directly()

    # Try alternatives
    alt_result = await get_public_info_alternative()

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if result["success"]:
        print(f"✅ Successfully scraped using: {result['method']}")
        print(f"   HTML saved to: {result['filename']}")
        print(f"   Size: {result['html_length']} bytes")
    else:
        print("❌ Direct scraping failed due to Twitter's protections")

    if autoparse_result:
        print("✅ Got some data from autoparse attempt")

    if alt_result:
        print("✅ Got some data from alternative methods")

    print("\n🎯 RECOMMENDATION:")
    print("-" * 60)
    print("Twitter/X actively blocks scrapers. To get @xkonjin's tweets:")
    print()
    print("1. **Best Option**: Add Apify token and use their Twitter actor")
    print("   - Reliable and maintained")
    print("   - Handles Twitter's anti-bot measures")
    print()
    print("2. **Alternative**: Use Twitter's official API")
    print("   - Requires developer account")
    print("   - Rate limited but legitimate")
    print()
    print("3. **Manual**: Export data from Twitter directly")
    print("   - Settings → Your account → Download an archive")
    print()

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "username": "xkonjin",
        "scraping_result": result,
        "recommendation": "Use Apify Twitter actor for reliable scraping"
    }

    with open("x_scraping_attempt.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to x_scraping_attempt.json")


if __name__ == "__main__":
    asyncio.run(main())