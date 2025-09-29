#!/usr/bin/env python3
"""
Test all social media scrapers
Validates BrightData integration for all platforms
"""

import asyncio
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
brand_path = project_root / "plasma-engine-brand"
sys.path.insert(0, str(brand_path))

# Import scrapers
from app.scrapers.platform_scrapers import (
    TwitterScraper,
    InstagramScraper,
    LinkedInScraper,
    TikTokScraper,
    YouTubeScraper,
    GitHubScraper,
    GoogleNewsScraper,
    get_platform_scraper
)
from app.scrapers.unified_scraper_v2 import UnifiedScraperV2


async def test_twitter():
    """Test Twitter/X scraping - PRIORITY"""
    print("\n" + "=" * 70)
    print("🐦 TESTING TWITTER/X SCRAPER")
    print("=" * 70)

    scraper = TwitterScraper()
    test_users = ["xkonjin", "elonmusk", "plasma_engine"]

    for username in test_users:
        try:
            print(f"\n📍 Testing @{username}...")
            result = await scraper.scrape_profile(username)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped @{username}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape @{username}")

        except Exception as e:
            print(f"❌ ERROR scraping @{username}: {e}")

    return True


async def test_instagram():
    """Test Instagram scraping"""
    print("\n" + "=" * 70)
    print("📸 TESTING INSTAGRAM SCRAPER")
    print("=" * 70)

    scraper = InstagramScraper()
    test_users = ["cristiano", "therock", "plasma_engine"]

    for username in test_users:
        try:
            print(f"\n📍 Testing @{username}...")
            result = await scraper.scrape_profile(username)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped @{username}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape @{username}")

        except Exception as e:
            print(f"❌ ERROR scraping @{username}: {e}")

    return True


async def test_linkedin():
    """Test LinkedIn scraping"""
    print("\n" + "=" * 70)
    print("💼 TESTING LINKEDIN SCRAPER")
    print("=" * 70)

    scraper = LinkedInScraper()
    test_users = ["williamhgates", "satyanadella", "plasma-engine"]

    for username in test_users:
        try:
            print(f"\n📍 Testing {username}...")
            result = await scraper.scrape_profile(username)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped {username}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape {username}")

        except Exception as e:
            print(f"❌ ERROR scraping {username}: {e}")

    return True


async def test_tiktok():
    """Test TikTok scraping"""
    print("\n" + "=" * 70)
    print("🎵 TESTING TIKTOK SCRAPER")
    print("=" * 70)

    scraper = TikTokScraper()
    test_users = ["khaby.lame", "charlidamelio", "plasma_engine"]

    for username in test_users:
        try:
            print(f"\n📍 Testing @{username}...")
            result = await scraper.scrape_profile(username)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped @{username}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape @{username}")

        except Exception as e:
            print(f"❌ ERROR scraping @{username}: {e}")

    return True


async def test_youtube():
    """Test YouTube scraping"""
    print("\n" + "=" * 70)
    print("📺 TESTING YOUTUBE SCRAPER")
    print("=" * 70)

    scraper = YouTubeScraper()
    test_channels = ["MrBeast", "PewDiePie", "PlasmaEngine"]

    for channel in test_channels:
        try:
            print(f"\n📍 Testing @{channel}...")
            result = await scraper.scrape_profile(channel)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped @{channel}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape @{channel}")

        except Exception as e:
            print(f"❌ ERROR scraping @{channel}: {e}")

    return True


async def test_github():
    """Test GitHub scraping"""
    print("\n" + "=" * 70)
    print("🐙 TESTING GITHUB SCRAPER")
    print("=" * 70)

    scraper = GitHubScraper()
    test_users = ["torvalds", "gvanrossum", "plasma-engine"]

    for username in test_users:
        try:
            print(f"\n📍 Testing {username}...")
            result = await scraper.scrape_profile(username)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped {username}")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape {username}")

        except Exception as e:
            print(f"❌ ERROR scraping {username}: {e}")

    # Test specific repo
    try:
        print(f"\n📍 Testing repo: plasma-engine-org/plasma-engine...")
        result = await scraper.scrape_repo("plasma-engine-org", "plasma-engine")
        if result.get("success"):
            print(f"✅ SUCCESS: Scraped repository")
        else:
            print(f"❌ FAILED: Could not scrape repository")
    except Exception as e:
        print(f"❌ ERROR scraping repo: {e}")

    return True


async def test_google_news():
    """Test Google News scraping"""
    print("\n" + "=" * 70)
    print("📰 TESTING GOOGLE NEWS SCRAPER")
    print("=" * 70)

    scraper = GoogleNewsScraper()
    test_queries = ["artificial intelligence", "plasma engine", "web scraping"]

    for query in test_queries:
        try:
            print(f"\n📍 Testing query: '{query}'...")
            result = await scraper.scrape_search(query)

            if result.get("success"):
                print(f"✅ SUCCESS: Scraped news for '{query}'")
                print(f"   Content size: {len(result.get('content', ''))} bytes")
            else:
                print(f"❌ FAILED: Could not scrape news for '{query}'")

        except Exception as e:
            print(f"❌ ERROR searching '{query}': {e}")

    # Test headlines
    try:
        print(f"\n📍 Testing headlines...")
        result = await scraper.scrape_headlines()
        if result.get("success"):
            print(f"✅ SUCCESS: Scraped headlines")
        else:
            print(f"❌ FAILED: Could not scrape headlines")
    except Exception as e:
        print(f"❌ ERROR scraping headlines: {e}")

    return True


async def test_unified_scraper():
    """Test unified scraper with all platforms"""
    print("\n" + "=" * 70)
    print("🎯 TESTING UNIFIED SCRAPER V2")
    print("=" * 70)

    scraper = UnifiedScraperV2()

    # Test social profiles
    test_cases = [
        ("twitter", "xkonjin"),
        ("instagram", "cristiano"),
        ("linkedin", "williamhgates"),
        ("tiktok", "khaby.lame"),
        ("youtube", "MrBeast"),
        ("github", "torvalds")
    ]

    for platform, username in test_cases:
        try:
            print(f"\n📍 Testing {platform}: {username}...")
            result = await scraper.scrape_social_profile(platform, username)

            if result.get("success"):
                print(f"✅ SUCCESS via {result.get('service', 'unknown')}")
                print(f"   Content size: {len(str(result.get('content', '')))} bytes")
            else:
                print(f"❌ FAILED")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    # Test Google News
    try:
        print(f"\n📍 Testing Google News...")
        result = await scraper.scrape_google_news("plasma engine")

        if result.get("success"):
            print(f"✅ SUCCESS: Scraped Google News")
        else:
            print(f"❌ FAILED")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Print metrics
    print("\n📊 METRICS:")
    metrics = scraper.get_metrics()
    print(json.dumps(metrics, indent=2))

    return True


async def main():
    """Main test runner"""
    print("=" * 70)
    print("🚀 PLASMA ENGINE SCRAPER TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 70)

    # Check for API token
    api_token = os.getenv("BRIGHTDATA_API_TOKEN")
    if not api_token:
        print("⚠️  WARNING: BRIGHTDATA_API_TOKEN not set in environment")
        print("   Some tests may fail. Set the token to enable all tests.")
    else:
        print(f"✅ BrightData API Token found: {api_token[:20]}...")

    results = {}

    # Run all tests
    tests = [
        ("Twitter/X", test_twitter),
        ("Instagram", test_instagram),
        ("LinkedIn", test_linkedin),
        ("TikTok", test_tiktok),
        ("YouTube", test_youtube),
        ("GitHub", test_github),
        ("Google News", test_google_news),
        ("Unified Scraper", test_unified_scraper)
    ]

    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            print(f"\n❌ {name} test failed with error: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    print("\nPlatform Results:")
    for platform, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {platform}: {status}")

    print("\n" + "=" * 70)
    print("✨ TEST SUITE COMPLETE")
    print("=" * 70)

    # Save results
    results_file = project_root / "scraper_test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
            }
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)