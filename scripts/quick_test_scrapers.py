#!/usr/bin/env python3
"""
Quick test for each social media scraper
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "plasma-engine-brand"))

from app.scrapers.brightdata_client import BrightDataClient

# Set API token
os.environ["BRIGHTDATA_API_TOKEN"] = "7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2"


async def test_platform(name: str, url: str):
    """Test a single platform"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"URL: {url}")
    print('='*60)

    client = BrightDataClient()

    try:
        result = await client.scrape(url)
        size = len(result)
        print(f"✅ SUCCESS: Got {size:,} bytes")

        # Check for platform-specific content
        if name == "Twitter" and ("twitter" in result.lower() or "x.com" in result.lower()):
            print("✅ Verified: Twitter content detected")
        elif name == "Instagram" and "instagram" in result.lower():
            print("✅ Verified: Instagram content detected")
        elif name == "LinkedIn" and "linkedin" in result.lower():
            print("✅ Verified: LinkedIn content detected")
        elif name == "TikTok" and "tiktok" in result.lower():
            print("✅ Verified: TikTok content detected")
        elif name == "YouTube" and ("youtube" in result.lower() or "ytimg" in result.lower()):
            print("✅ Verified: YouTube content detected")
        elif name == "GitHub" and "github" in result.lower():
            print("✅ Verified: GitHub content detected")
        elif name == "Google News" and ("google" in result.lower() or "news" in result.lower()):
            print("✅ Verified: Google News content detected")

        # Save sample
        filename = f"sample_{name.lower().replace(' ', '_')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result[:50000])  # Save first 50KB
        print(f"💾 Saved sample to {filename}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def main():
    """Test all platforms"""
    print("=" * 60)
    print("QUICK SOCIAL MEDIA SCRAPER TEST")
    print("=" * 60)

    # Test platforms
    tests = [
        ("Twitter", "https://x.com/xkonjin"),
        ("Instagram", "https://www.instagram.com/cristiano"),
        ("LinkedIn", "https://www.linkedin.com/in/williamhgates"),
        ("TikTok", "https://www.tiktok.com/@khaby.lame"),
        ("YouTube", "https://www.youtube.com/@MrBeast"),
        ("GitHub", "https://github.com/torvalds"),
        ("Google News", "https://news.google.com/search?q=artificial+intelligence")
    ]

    results = {}

    for name, url in tests:
        try:
            results[name] = await test_platform(name, url)
            await asyncio.sleep(3)  # Rate limiting
        except Exception as e:
            print(f"Error testing {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    successes = sum(1 for v in results.values() if v)
    total = len(results)

    for platform, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{platform}: {status}")

    print(f"\nTotal: {successes}/{total} platforms working")
    print(f"Success Rate: {(successes/total*100):.0f}%")

    if successes == total:
        print("\n🎉 ALL PLATFORMS WORKING!")
    elif successes > 0:
        print(f"\n⚠️  {successes} platforms working, {total-successes} need attention")
    else:
        print("\n❌ No platforms working - check API token")

    return successes == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)