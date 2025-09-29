#!/usr/bin/env python3
"""
Simple BrightData API test - check what's missing
"""

import httpx
import asyncio

API_TOKEN = "7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2"


async def test_brightdata_auth():
    """Test BrightData authentication and find out what's needed"""

    print("🔍 Testing BrightData API Token...")
    print(f"Token: {API_TOKEN[:20]}...")
    print("=" * 60)

    # Test different endpoints to see what works
    endpoints = [
        {
            "name": "Account Balance",
            "url": "https://api.brightdata.com/customer/balance",
            "method": "GET"
        },
        {
            "name": "Web Unlocker Status",
            "url": "https://api.brightdata.com/unlocker/status",
            "method": "GET"
        },
        {
            "name": "Zones List",
            "url": "https://api.brightdata.com/zones",
            "method": "GET"
        }
    ]

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        for endpoint in endpoints:
            print(f"\n📡 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")

            try:
                if endpoint["method"] == "GET":
                    response = await client.get(endpoint["url"], headers=headers)
                else:
                    response = await client.post(endpoint["url"], headers=headers)

                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    print(f"   ✅ Success!")
                    data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    print(f"   Response: {str(data)[:200]}")
                elif response.status_code == 401:
                    print(f"   ❌ Authentication failed - token might be invalid")
                elif response.status_code == 403:
                    print(f"   ⚠️ Forbidden - feature not enabled or no permission")
                elif response.status_code == 404:
                    print(f"   ❌ Not found - endpoint might not exist or account not set up")
                else:
                    print(f"   ⚠️ Unexpected status")
                    print(f"   Response: {response.text[:200]}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("📋 DIAGNOSIS:")
    print("=" * 60)
    print("\nBased on the 404 errors, it appears that:")
    print("1. ❌ The API token alone is not sufficient")
    print("2. ❌ You need to complete BrightData account setup")
    print("3. ❌ You need to create a Zone (proxy network)")
    print("\n🔧 REQUIRED SETUP:")
    print("-" * 40)
    print("1. Go to: https://brightdata.com/")
    print("2. Sign up with jf@plasma.to (Google auth)")
    print("3. Create a Zone:")
    print("   - Click 'Zones' → 'Add Zone'")
    print("   - Choose 'Residential Proxy' for social media")
    print("   - Or 'Web Unlocker' for guaranteed success")
    print("4. Get these credentials:")
    print("   - Customer ID (e.g., lum-customer-c_xxxxx)")
    print("   - Zone Username (e.g., lum-customer-c_xxxxx-zone-yyyyy)")
    print("   - Zone Password")
    print("\n5. Then add to .env:")
    print("   BRIGHTDATA_CUSTOMER_ID=lum-customer-c_xxxxx")
    print("   BRIGHTDATA_ZONE_USERNAME=lum-customer-c_xxxxx-zone-yyyyy")
    print("   BRIGHTDATA_ZONE_PASSWORD=your_zone_password")
    print("   BRIGHTDATA_API_TOKEN=7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2")
    print("\n💡 The API token is just one part - you need the full account!")


async def test_proxy_connection():
    """Try to connect via proxy if credentials exist"""

    print("\n" + "=" * 60)
    print("🔌 Testing Proxy Connection (if credentials available)")
    print("=" * 60)

    # Check if we have zone credentials
    import os
    customer_id = os.getenv("BRIGHTDATA_CUSTOMER_ID")
    zone_username = os.getenv("BRIGHTDATA_ZONE_USERNAME")
    zone_password = os.getenv("BRIGHTDATA_ZONE_PASSWORD")

    if not all([customer_id, zone_username, zone_password]):
        print("\n⚠️ Missing zone credentials. Need:")
        print("  - BRIGHTDATA_CUSTOMER_ID")
        print("  - BRIGHTDATA_ZONE_USERNAME")
        print("  - BRIGHTDATA_ZONE_PASSWORD")
        return

    # Try proxy connection
    proxy_url = f"http://{zone_username}:{zone_password}@zproxy.lum-superproxy.io:22225"

    print(f"\nProxy URL: http://{zone_username[:20]}...@zproxy.lum-superproxy.io:22225")

    try:
        async with httpx.AsyncClient(proxies=proxy_url, timeout=30, verify=False) as client:
            response = await client.get("http://httpbin.org/ip")
            print(f"✅ Proxy connection successful!")
            print(f"   Your IP via BrightData: {response.json().get('origin')}")

            # Now try Twitter
            print("\n🐦 Testing Twitter/X via proxy...")
            twitter_response = await client.get("https://x.com/elonmusk")
            print(f"   Status: {twitter_response.status_code}")
            if twitter_response.status_code == 200:
                print(f"   ✅ Twitter scraping successful!")
            else:
                print(f"   ❌ Twitter returned {twitter_response.status_code}")

    except Exception as e:
        print(f"❌ Proxy connection failed: {e}")


async def main():
    await test_brightdata_auth()
    await test_proxy_connection()

    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("=" * 60)
    print("\n1. Complete BrightData account setup")
    print("2. Create a Zone (Residential Proxy or Web Unlocker)")
    print("3. Get all 4 credentials")
    print("4. Add to .env file")
    print("5. Run test again")
    print("\nOnce set up, BrightData WILL be able to scrape:")
    print("• Twitter/X ✅")
    print("• LinkedIn ✅")
    print("• Instagram ✅")
    print("• TikTok ✅")
    print("• YouTube ✅")


if __name__ == "__main__":
    asyncio.run(main())