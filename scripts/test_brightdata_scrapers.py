#!/usr/bin/env python3
"""
Test BrightData's Pre-built Scrapers for Social Media
Using their Web Scraper API with existing scrapers library
"""

import asyncio
import httpx
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

# BrightData configuration from environment
API_TOKEN = os.getenv("BRIGHTDATA_API_TOKEN", "7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2")


class BrightDataScrapersAPI:
    """High-level helper around Bright Data's MCP datasets and unlocker.

    The previous version of this script called the legacy `/scrape` and
    `/trigger` endpoints with human-readable scraper names. Those endpoints
    now return ``404`` or validation errors because Bright Data migrated their
    social-media handlers to dataset-driven collectors that are exposed through
    the control-panel page referenced in the task description.  This class wraps
    that dataset workflow (``trigger`` → ``snapshot`` polling) and falls back to
    the Web Unlocker when a dedicated dataset is not yet available for the
    target platform.
    """

    def __init__(self):
        self.api_token = API_TOKEN
        self.dataset_base_url = "https://api.brightdata.com/datasets/v3"
        self.unlocker_url = "https://api.brightdata.com/request"
        self.unlocker_zone = os.getenv("WEB_UNLOCKER_ZONE", "mcp_unlocker")

        # Datasets published on https://brightdata.com/cp/scrapers/browse
        # Each entry documents the official dataset id that should be used for
        # structured results along with a friendly explanation that we surface
        # in console logs to help other engineers understand the flow quickly.
        self.dataset_configs = {
            "linkedin": {
                "dataset_id": "gd_l1viktl72bvl7bjuj0",
                "comment": "LinkedIn person profile dataset (structured JSON)",
            },
            "instagram": {
                "dataset_id": "gd_l1vikfch901nx3by4",
                "comment": "Instagram profile dataset – returns followers, bio, etc.",
            },
            "tiktok": {
                "dataset_id": "gd_l1villgoiiidt09ci",
                "comment": "TikTok profile dataset with follower metrics",
            },
            "youtube": {
                "dataset_id": "gd_lk538t2k2p1k3oos71",
                "comment": "YouTube channel dataset – structured channel metadata",
            },
        }

    async def fetch_dataset(self, platform_key: str, url: str) -> Dict[str, Any]:
        """Trigger the official dataset collector and wait for results."""

        config = self.dataset_configs[platform_key]
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        print(f"   🗂️ Using dataset {config['dataset_id']} ({config['comment']})")

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                trigger_response = await client.post(
                    f"{self.dataset_base_url}/trigger",
                    params={"dataset_id": config["dataset_id"], "include_errors": "true"},
                    json=[{"url": url}],
                    headers=headers,
                )

                if trigger_response.status_code != 200:
                    error_text = trigger_response.text
                    print(f"   ❌ Dataset trigger failed: {error_text[:200]}")
                    return {
                        "success": False,
                        "error": error_text,
                        "status_code": trigger_response.status_code,
                    }

                snapshot_id = trigger_response.json().get("snapshot_id")
                if not snapshot_id:
                    print("   ❌ Dataset trigger succeeded but no snapshot id was returned")
                    return {
                        "success": False,
                        "error": "Missing snapshot_id in trigger response",
                    }

                print(f"   ⏳ Snapshot ID: {snapshot_id} – polling for data…")

                max_attempts = 120
                for attempt in range(max_attempts):
                    poll_response = await client.get(
                        f"{self.dataset_base_url}/snapshot/{snapshot_id}",
                        params={"format": "json"},
                        headers=headers,
                    )

                    if poll_response.status_code not in (200, 202):
                        print(f"   ⚠️ Poll attempt {attempt + 1}: HTTP {poll_response.status_code}")
                        await asyncio.sleep(2)
                        continue

                    if poll_response.status_code == 202:
                        # Snapshot still building
                        await asyncio.sleep(2)
                        continue

                    data = poll_response.json()

                    # The snapshot API returns either a dict with status metadata
                    # or the final list of items. Handle both shapes explicitly.
                    if isinstance(data, dict) and data.get("status") in {"running", "building"}:
                        await asyncio.sleep(2)
                        continue

                    print(f"   ✅ Dataset ready after {attempt + 1} poll attempts")
                    return {
                        "success": True,
                        "data": data,
                        "method": "dataset",
                        "dataset_id": config["dataset_id"],
                    }

                print("   ❌ Dataset polling timed out")
                return {
                    "success": False,
                    "error": "Dataset snapshot did not finish within timeout window",
                }

        except Exception as exc:
            print(f"   ❌ Dataset exception: {exc}")
            return {"success": False, "error": str(exc)}

    async def scrape_with_unlocker(self, url: str) -> Dict[str, Any]:
        """Fallback to the Web Unlocker for raw HTML when no dataset exists."""

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "url": url,
            "zone": self.unlocker_zone,
            "format": "raw",
        }

        print(f"   🌐 Falling back to Web Unlocker via zone '{self.unlocker_zone}'")

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    self.unlocker_url,
                    headers=headers,
                    json=payload,
                )

                if response.status_code != 200:
                    print(f"   ❌ Unlocker failed: {response.text[:200]}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code,
                    }

                print(f"   ✅ Unlocker returned {len(response.text)} bytes")
                return {
                    "success": True,
                    "data": response.text,
                    "method": "web_unlocker",
                }

        except Exception as exc:
            print(f"   ❌ Unlocker exception: {exc}")
            return {"success": False, "error": str(exc)}

    async def test_social_platform(self, platform: str, url: str) -> Dict[str, Any]:
        """Test a specific social media platform using the best available flow."""

        print(f"\n{'=' * 70}")
        print(f"🎯 TESTING {platform.upper()}")
        print(f"{'=' * 70}")

        platform_key = platform.lower()
        results: Dict[str, Any] = {}

        if platform_key in self.dataset_configs:
            dataset_result = await self.fetch_dataset(platform_key, url)
            results["dataset"] = dataset_result

            if dataset_result.get("success"):
                # Dataset success -> no need for raw HTML fallback
                return results

            print("   ⚠️ Dataset failed – trying unlocker fallback")

        unlocker_result = await self.scrape_with_unlocker(url)
        results["unlocker"] = unlocker_result
        return results


async def test_all_platforms():
    """Test all social media platforms with BrightData scrapers"""
    
    print("=" * 70)
    print("🚀 BRIGHTDATA PRE-BUILT SCRAPERS TEST")
    print("=" * 70)
    print(f"API Token: {API_TOKEN[:20]}...")
    print("=" * 70)
    
    api = BrightDataScrapersAPI()
    
    # Test configurations
    test_cases = [
        {"platform": "Twitter", "url": "https://twitter.com/xkonjin"},
        {"platform": "LinkedIn", "url": "https://www.linkedin.com/in/williamhgates"},
        {"platform": "Instagram", "url": "https://www.instagram.com/cristiano"},
        {"platform": "TikTok", "url": "https://www.tiktok.com/@khaby.lame"},
        {"platform": "YouTube", "url": "https://www.youtube.com/@MrBeast"},
    ]
    
    all_results = {}
    
    for test in test_cases:
        result = await api.test_social_platform(
            platform=test["platform"],
            url=test["url"]
        )
        all_results[test["platform"]] = result
        await asyncio.sleep(2)  # Rate limiting
        
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for platform, method_results in all_results.items():
        dataset_success = method_results.get("dataset", {}).get("success", False)
        unlocker_success = method_results.get("unlocker", {}).get("success", False)

        if dataset_success or unlocker_success:
            print(f"✅ {platform}: Working")
            if dataset_success:
                print("   - Dataset: ✅ structured payload returned")
            else:
                if "dataset" in method_results:
                    dataset_error = method_results["dataset"].get("error", "Unknown error")
                    status = method_results["dataset"].get("status_code", "N/A")
                    print(f"   - Dataset issue: {dataset_error[:100]} (status: {status})")

            if unlocker_success:
                print("   - Web Unlocker: ✅ raw HTML captured")
            else:
                if "unlocker" in method_results:
                    unlocker_error = method_results["unlocker"].get("error", "Unknown error")
                    status = method_results["unlocker"].get("status_code", "N/A")
                    print(f"   - Unlocker issue: {unlocker_error[:100]} (status: {status})")
        else:
            print(f"❌ {platform}: No successful method")
            for method_name, outcome in method_results.items():
                error = outcome.get("error", "Unknown error")
                status = outcome.get("status_code", "N/A")
                print(f"   - {method_name}: {error[:100]} (status: {status})")
                
    # Save results
    with open("brightdata_scrapers_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
        
    print(f"\n💾 Full results saved to brightdata_scrapers_results.json")
    
    return all_results


async def test_web_unlocker_fallback():
    """Test Web Unlocker as a fallback option"""
    
    print("\n" + "=" * 70)
    print("🔓 TESTING WEB UNLOCKER FALLBACK")
    print("=" * 70)
    api = BrightDataScrapersAPI()

    test_urls = [
        "https://x.com/xkonjin",
        "https://www.linkedin.com/in/williamhgates"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = await api.scrape_with_unlocker(url)

        if result.get("success"):
            content = result.get("data", "")
            print(f"   ✅ Success! Got {len(content)} bytes")

            filename = f"unlocker_{url.split('/')[2].replace('.', '_')}.html"
            with open(filename, "w", encoding="utf-8") as handle:
                handle.write(content[:10000])
            print(f"   💾 Sample saved to {filename}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')[:200]}")
            

async def check_account_status():
    """Check BrightData account status and available features"""
    
    print("\n" + "=" * 70)
    print("🔍 CHECKING BRIGHTDATA ACCOUNT STATUS")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    endpoints = [
        ("Account Info", "https://api.brightdata.com/api/v2/account"),
        ("Available Scrapers", "https://api.brightdata.com/api/v2/scrapers"),
        ("Usage Stats", "https://api.brightdata.com/api/v2/stats"),
        ("Balance", "https://api.brightdata.com/api/v2/balance")
    ]
    
    for name, url in endpoints:
        print(f"\n📡 Checking {name}...")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    print(f"   ✅ Success")
                    if isinstance(data, dict):
                        for key in list(data.keys())[:5]:
                            print(f"   - {key}: {data[key]}")
                elif response.status_code == 401:
                    print(f"   ❌ Authentication failed")
                elif response.status_code == 404:
                    print(f"   ⚠️ Endpoint not found or not enabled")
                else:
                    print(f"   ⚠️ Unexpected: {response.text[:100]}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Main test execution"""
    
    # First check account status
    await check_account_status()
    
    # Test pre-built scrapers
    results = await test_all_platforms()
    
    # Test Web Unlocker as fallback
    await test_web_unlocker_fallback()
    
    # Print final recommendations
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATIONS")
    print("=" * 70)
    print()
    print("Based on the test results:")
    print()
    print("1. ❌ API Token alone is insufficient")
    print("2. ❌ You need to complete BrightData account setup:")
    print("   - Create a Zone (Residential or Web Unlocker)")
    print("   - Get Customer ID")
    print("   - Get Zone Username")
    print("   - Get Zone Password")
    print()
    print("3. Once set up, BrightData will work for:")
    print("   ✅ Twitter/X")
    print("   ✅ LinkedIn")
    print("   ✅ Instagram")
    print("   ✅ TikTok")
    print("   ✅ YouTube")
    print()
    print("4. Use this priority:")
    print("   1st: Pre-built scrapers (most reliable)")
    print("   2nd: Web Unlocker (handles protections)")
    print("   3rd: Proxy networks (manual scraping)")
    print()
    print("📚 Full setup guide: docs/BRIGHTDATA_SETUP_GUIDE.md")
    print("💡 Helper script: scripts/brightdata_credentials_helper.py")
    

if __name__ == "__main__":
    asyncio.run(main())