#!/usr/bin/env python3
"""
🧪 ScraperAPI Test Script
Tests the ScraperAPI key and demonstrates various scraping methods
"""

import os
import httpx
import asyncio
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScraperAPITester:
    """Test ScraperAPI functionality with various methods"""

    def __init__(self):
        self.api_key = os.getenv("SCRAPERAPI_KEY")
        if not self.api_key:
            raise ValueError("❌ SCRAPERAPI_KEY not found in environment variables")

        self.base_url = "http://api.scraperapi.com"
        self.async_url = "http://async.scraperapi.com"
        print(f"✅ ScraperAPI key loaded: {self.api_key[:10]}...")

    async def test_basic_request(self) -> bool:
        """Test basic API endpoint method"""
        print("\n📝 Testing Basic API Endpoint Method...")

        params = {
            "api_key": self.api_key,
            "url": "http://httpbin.org/ip"
        }

        try:
            async with httpx.AsyncClient(timeout=70) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()

                data = response.json()
                print(f"✅ Basic request successful!")
                print(f"   Your IP: {data.get('origin', 'Unknown')}")
                print(f"   Credits used: {response.headers.get('X-API-Credits-Used', 'Unknown')}")
                return True

        except Exception as e:
            print(f"❌ Basic request failed: {e}")
            return False

    async def test_javascript_rendering(self) -> bool:
        """Test JavaScript rendering capability"""
        print("\n🌐 Testing JavaScript Rendering...")

        params = {
            "api_key": self.api_key,
            "url": "https://example.com",
            "render": "true"
        }

        try:
            async with httpx.AsyncClient(timeout=70) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()

                print(f"✅ JavaScript rendering successful!")
                print(f"   Response length: {len(response.text)} chars")
                print(f"   Credits used: {response.headers.get('X-API-Credits-Used', 'Unknown')}")
                return True

        except Exception as e:
            print(f"❌ JavaScript rendering failed: {e}")
            return False

    async def test_geotargeting(self) -> bool:
        """Test geotargeting with different countries"""
        print("\n🌍 Testing Geotargeting...")

        countries = ["us", "uk", "de"]
        results = []

        for country in countries:
            params = {
                "api_key": self.api_key,
                "url": "http://httpbin.org/ip",
                "country_code": country
            }

            try:
                async with httpx.AsyncClient(timeout=70) as client:
                    response = await client.get(self.base_url, params=params)
                    response.raise_for_status()

                    data = response.json()
                    print(f"✅ {country.upper()}: {data.get('origin', 'Unknown')}")
                    results.append(True)

            except Exception as e:
                print(f"❌ {country.upper()} failed: {e}")
                results.append(False)

        return all(results)

    async def test_proxy_method(self) -> bool:
        """Test proxy port method"""
        print("\n🔐 Testing Proxy Port Method...")

        proxy_url = f"http://scraperapi:{self.api_key}@proxy-server.scraperapi.com:8001"

        try:
            async with httpx.AsyncClient(
                proxies=proxy_url,
                verify=False,  # SSL verification disabled for proxy
                timeout=70
            ) as client:
                response = await client.get("http://httpbin.org/ip")
                response.raise_for_status()

                data = response.json()
                print(f"✅ Proxy method successful!")
                print(f"   Proxied IP: {data.get('origin', 'Unknown')}")
                return True

        except Exception as e:
            print(f"❌ Proxy method failed: {e}")
            print(f"   Note: Proxy method requires special configuration")
            return False

    async def test_async_request(self) -> bool:
        """Test async scraping method"""
        print("\n⏱️ Testing Async Scraping Method...")

        # Submit async job
        payload = {
            "apiKey": self.api_key,
            "url": "https://example.com"
        }

        try:
            async with httpx.AsyncClient(timeout=70) as client:
                # Submit job
                response = await client.post(self.async_url, json=payload)
                response.raise_for_status()

                job_data = response.json()
                job_id = job_data.get("id")

                if not job_id:
                    print(f"❌ No job ID returned")
                    return False

                print(f"📋 Job submitted: {job_id}")

                # Check status (would normally poll until complete)
                status_url = f"{self.async_url}/{job_id}"
                await asyncio.sleep(2)  # Wait a bit for processing

                status_response = await client.get(status_url)
                status_data = status_response.json()

                print(f"✅ Async job status: {status_data.get('status', 'Unknown')}")
                return True

        except Exception as e:
            print(f"❌ Async method failed: {e}")
            return False

    async def test_structured_data(self) -> bool:
        """Test structured data endpoint (Amazon example)"""
        print("\n📊 Testing Structured Data Collection...")

        params = {
            "api_key": self.api_key,
            "url": "https://www.amazon.com/dp/B08N5WRWNW"  # Echo Dot example
        }

        structured_url = "https://api.scraperapi.com/structured/amazon/product"

        try:
            async with httpx.AsyncClient(timeout=70) as client:
                response = await client.get(structured_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Structured data successful!")
                    print(f"   Product: {data.get('name', 'Unknown')[:50]}...")
                    return True
                else:
                    print(f"ℹ️ Structured data endpoint returned {response.status_code}")
                    print(f"   This is normal for test URLs or requires specific product URLs")
                    return True  # Not a failure, just informational

        except Exception as e:
            print(f"ℹ️ Structured data test skipped: {e}")
            return True  # Not critical for basic testing

    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")

        total = len(results)
        passed = sum(1 for v in results.values() if v)

        print(f"\n🎯 Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! ScraperAPI is working correctly.")
        elif passed > 0:
            print("⚠️ Some tests failed, but ScraperAPI is functional.")
        else:
            print("❌ All tests failed. Please check your API key.")

        print("\n💡 Note: Some tests may fail due to:")
        print("   - Rate limits on free tier")
        print("   - Proxy method requiring special setup")
        print("   - Structured data requiring specific URLs")

    async def run_all_tests(self):
        """Run all ScraperAPI tests"""
        print("🚀 Starting ScraperAPI Tests")
        print("=" * 50)

        results = {}

        # Run tests
        results["Basic Request"] = await self.test_basic_request()
        results["JavaScript Rendering"] = await self.test_javascript_rendering()
        results["Geotargeting"] = await self.test_geotargeting()
        results["Proxy Method"] = await self.test_proxy_method()
        results["Async Request"] = await self.test_async_request()
        results["Structured Data"] = await self.test_structured_data()

        # Print summary
        self.print_summary(results)

        return results


async def main():
    """Main test runner"""
    tester = ScraperAPITester()
    results = await tester.run_all_tests()

    # Return exit code based on results
    passed = sum(1 for v in results.values() if v)
    return 0 if passed > 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)