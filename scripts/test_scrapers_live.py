#!/usr/bin/env python3
"""
Live test for all social media scrapers
Tests Instagram, LinkedIn, TikTok, YouTube, GitHub, and Google News
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

from app.scrapers.platform_scrapers import (
    InstagramScraper,
    LinkedInScraper,
    TikTokScraper,
    YouTubeScraper,
    GitHubScraper,
    GoogleNewsScraper,
    TwitterScraper
)
from app.scrapers.brightdata_client import BrightDataClient


async def test_instagram():
    """Test Instagram scraping"""
    print("\n" + "=" * 70)
    print("📸 TESTING INSTAGRAM SCRAPER")
    print("=" * 70)

    scraper = InstagramScraper()
    test_accounts = [
        "cristiano",      # Cristiano Ronaldo
        "therock",        # Dwayne Johnson
        "kimkardashian"   # Kim Kardashian
    ]

    results = {}

    for username in test_accounts:
        print(f"\n🔍 Testing Instagram: @{username}")
        print(f"   URL: https://www.instagram.com/{username}")

        try:
            result = await scraper.scrape_profile(username)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual Instagram content
                if "instagram" in result["content"].lower():
                    print(f"   ✅ Verified: Instagram content detected")

                results[username] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[username] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[username] = {"success": False, "error": str(e)}

    return results


async def test_linkedin():
    """Test LinkedIn scraping"""
    print("\n" + "=" * 70)
    print("💼 TESTING LINKEDIN SCRAPER")
    print("=" * 70)

    scraper = LinkedInScraper()
    test_profiles = [
        "williamhgates",   # Bill Gates
        "satyanadella",    # Satya Nadella
        "reidhoffman"      # Reid Hoffman
    ]

    results = {}

    for username in test_profiles:
        print(f"\n🔍 Testing LinkedIn: {username}")
        print(f"   URL: https://www.linkedin.com/in/{username}")

        try:
            result = await scraper.scrape_profile(username)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual LinkedIn content
                if "linkedin" in result["content"].lower():
                    print(f"   ✅ Verified: LinkedIn content detected")

                results[username] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[username] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[username] = {"success": False, "error": str(e)}

    return results


async def test_tiktok():
    """Test TikTok scraping"""
    print("\n" + "=" * 70)
    print("🎵 TESTING TIKTOK SCRAPER")
    print("=" * 70)

    scraper = TikTokScraper()
    test_accounts = [
        "khaby.lame",      # Khaby Lame
        "charlidamelio",   # Charli D'Amelio
        "zachking"         # Zach King
    ]

    results = {}

    for username in test_accounts:
        print(f"\n🔍 Testing TikTok: @{username}")
        print(f"   URL: https://www.tiktok.com/@{username}")

        try:
            result = await scraper.scrape_profile(username)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual TikTok content
                if "tiktok" in result["content"].lower():
                    print(f"   ✅ Verified: TikTok content detected")

                results[username] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[username] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[username] = {"success": False, "error": str(e)}

    return results


async def test_youtube():
    """Test YouTube scraping"""
    print("\n" + "=" * 70)
    print("📺 TESTING YOUTUBE SCRAPER")
    print("=" * 70)

    scraper = YouTubeScraper()
    test_channels = [
        "MrBeast",         # MrBeast
        "PewDiePie",       # PewDiePie
        "mkbhd"            # Marques Brownlee
    ]

    results = {}

    for channel in test_channels:
        print(f"\n🔍 Testing YouTube: @{channel}")
        print(f"   URL: https://www.youtube.com/@{channel}")

        try:
            result = await scraper.scrape_profile(channel)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual YouTube content
                if "youtube" in result["content"].lower() or "ytimg" in result["content"].lower():
                    print(f"   ✅ Verified: YouTube content detected")

                results[channel] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[channel] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[channel] = {"success": False, "error": str(e)}

    return results


async def test_github():
    """Test GitHub scraping"""
    print("\n" + "=" * 70)
    print("🐙 TESTING GITHUB SCRAPER")
    print("=" * 70)

    scraper = GitHubScraper()

    results = {}

    # Test profiles
    test_users = [
        "torvalds",        # Linus Torvalds
        "gvanrossum",      # Guido van Rossum
        "karpathy"         # Andrej Karpathy
    ]

    for username in test_users:
        print(f"\n🔍 Testing GitHub Profile: {username}")
        print(f"   URL: https://github.com/{username}")

        try:
            result = await scraper.scrape_profile(username)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual GitHub content
                if "github" in result["content"].lower():
                    print(f"   ✅ Verified: GitHub content detected")

                results[f"profile_{username}"] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[f"profile_{username}"] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[f"profile_{username}"] = {"success": False, "error": str(e)}

    # Test repository
    print(f"\n🔍 Testing GitHub Repository: facebook/react")
    print(f"   URL: https://github.com/facebook/react")

    try:
        result = await scraper.scrape_repo("facebook", "react")

        if result.get("success") and result.get("content"):
            content_size = len(result.get("content", ""))
            print(f"   ✅ SUCCESS! Got {content_size:,} bytes")
            results["repo_facebook_react"] = {
                "success": True,
                "size": content_size
            }
        else:
            print(f"   ❌ FAILED: No content retrieved")
            results["repo_facebook_react"] = {"success": False}

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["repo_facebook_react"] = {"success": False, "error": str(e)}

    return results


async def test_google_news():
    """Test Google News scraping"""
    print("\n" + "=" * 70)
    print("📰 TESTING GOOGLE NEWS SCRAPER")
    print("=" * 70)

    scraper = GoogleNewsScraper()

    results = {}

    # Test search queries
    test_queries = [
        "artificial intelligence",
        "climate change",
        "technology startups"
    ]

    for query in test_queries:
        print(f"\n🔍 Testing Google News Search: '{query}'")
        print(f"   URL: https://news.google.com/search?q={query.replace(' ', '%20')}")

        try:
            result = await scraper.scrape_search(query)

            if result.get("success") and result.get("content"):
                content_size = len(result.get("content", ""))
                print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

                # Check if we got actual Google News content
                if "google" in result["content"].lower() or "news" in result["content"].lower():
                    print(f"   ✅ Verified: Google News content detected")

                results[f"search_{query}"] = {
                    "success": True,
                    "size": content_size,
                    "timestamp": result.get("timestamp")
                }
            else:
                print(f"   ❌ FAILED: No content retrieved")
                results[f"search_{query}"] = {"success": False, "error": "No content"}

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results[f"search_{query}"] = {"success": False, "error": str(e)}

    # Test headlines
    print(f"\n🔍 Testing Google News Headlines")
    print(f"   URL: https://news.google.com")

    try:
        result = await scraper.scrape_headlines()

        if result.get("success") and result.get("content"):
            content_size = len(result.get("content", ""))
            print(f"   ✅ SUCCESS! Got {content_size:,} bytes")
            results["headlines"] = {
                "success": True,
                "size": content_size
            }
        else:
            print(f"   ❌ FAILED: No content retrieved")
            results["headlines"] = {"success": False}

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["headlines"] = {"success": False, "error": str(e)}

    return results


async def test_twitter_again():
    """Test Twitter/X scraping again for comparison"""
    print("\n" + "=" * 70)
    print("🐦 TESTING TWITTER/X SCRAPER (Verification)")
    print("=" * 70)

    scraper = TwitterScraper()

    print(f"\n🔍 Testing Twitter: @xkonjin")
    print(f"   URL: https://x.com/xkonjin")

    try:
        result = await scraper.scrape_profile("xkonjin")

        if result.get("success") and result.get("content"):
            content_size = len(result.get("content", ""))
            print(f"   ✅ SUCCESS! Got {content_size:,} bytes")

            if "twitter" in result["content"].lower() or "x.com" in result["content"].lower():
                print(f"   ✅ Verified: Twitter/X content detected")

            return {"xkonjin": {"success": True, "size": content_size}}
        else:
            print(f"   ❌ FAILED: No content retrieved")
            return {"xkonjin": {"success": False}}

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return {"xkonjin": {"success": False, "error": str(e)}}


async def main():
    """Main test runner"""
    print("=" * 70)
    print("🚀 COMPREHENSIVE SOCIAL MEDIA SCRAPER TEST")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 70)

    # Check for API token
    api_token = os.getenv("BRIGHTDATA_API_TOKEN")
    if api_token:
        print(f"✅ BrightData API Token found: {api_token[:20]}...")
    else:
        print("⚠️  WARNING: BRIGHTDATA_API_TOKEN not set")
        print("   Tests may fail without proper authentication")

    print("\nTesting all platforms with BrightData scraping...")
    print("This may take a few minutes...\n")

    # Run all tests
    all_results = {}

    # Test each platform
    tests = [
        ("Twitter", test_twitter_again),
        ("Instagram", test_instagram),
        ("LinkedIn", test_linkedin),
        ("TikTok", test_tiktok),
        ("YouTube", test_youtube),
        ("GitHub", test_github),
        ("Google News", test_google_news)
    ]

    for platform_name, test_func in tests:
        try:
            print(f"\n{'='*30} {platform_name} {'='*30}")
            results = await test_func()
            all_results[platform_name] = results
            await asyncio.sleep(2)  # Rate limiting between platforms
        except Exception as e:
            print(f"\n❌ {platform_name} test crashed: {e}")
            all_results[platform_name] = {"error": str(e)}

    # Generate summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)

    platform_stats = {}

    for platform, results in all_results.items():
        if isinstance(results, dict) and "error" not in results:
            successes = sum(1 for r in results.values() if isinstance(r, dict) and r.get("success"))
            total = len(results)
            platform_stats[platform] = {
                "success": successes,
                "total": total,
                "rate": f"{(successes/total*100):.0f}%" if total > 0 else "N/A"
            }

            print(f"\n{platform}:")
            print(f"  Success: {successes}/{total} ({platform_stats[platform]['rate']})")

            # Show individual results
            for key, result in results.items():
                if isinstance(result, dict):
                    status = "✅" if result.get("success") else "❌"
                    size = f"{result.get('size', 0):,} bytes" if result.get("size") else "Failed"
                    print(f"    {status} {key}: {size}")
        else:
            print(f"\n{platform}: ❌ Test failed")
            platform_stats[platform] = {"error": True}

    # Save results
    output_file = project_root / "scraper_test_results_live.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "platforms": all_results,
            "summary": platform_stats
        }, f, indent=2)

    print(f"\n📁 Results saved to: {output_file}")

    # Overall success calculation
    total_platforms = len([p for p in platform_stats.values() if "error" not in p])
    successful_platforms = len([p for p in platform_stats.values() if p.get("success", 0) > 0])

    print("\n" + "=" * 70)
    print("🏁 TEST COMPLETE")
    print("=" * 70)
    print(f"Platforms with successful scrapes: {successful_platforms}/{total_platforms}")

    if successful_platforms == total_platforms:
        print("✅ ALL PLATFORMS WORKING!")
    else:
        print(f"⚠️  Some platforms need attention")

    return successful_platforms == total_platforms


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)