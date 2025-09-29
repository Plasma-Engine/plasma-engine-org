#!/usr/bin/env python3
"""
Scrape @xkonjin's latest tweets using ScraperAPI
"""

import asyncio
import httpx
import json
import re
from datetime import datetime
from typing import List, Dict, Any

SCRAPERAPI_KEY = "35e44a7b6f2dcd3a707c4c7f36ff2c1a"


async def scrape_twitter_profile(username: str, max_tweets: int = 10) -> Dict[str, Any]:
    """
    Scrape Twitter/X profile for latest tweets

    Args:
        username: Twitter username (without @)
        max_tweets: Number of tweets to retrieve

    Returns:
        Dictionary with user info and tweets
    """

    print(f"🐦 Scraping @{username}'s latest {max_tweets} tweets...")
    print("=" * 60)

    # Twitter profile URL
    url = f"https://twitter.com/{username}"

    # ScraperAPI parameters
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "render": "true",  # Twitter requires JavaScript
        "device_type": "desktop"
    }

    try:
        async with httpx.AsyncClient(timeout=70) as client:
            print(f"📡 Fetching Twitter profile...")
            response = await client.get("http://api.scraperapi.com", params=params)
            response.raise_for_status()

            html = response.text
            print(f"✅ Retrieved {len(html)} characters of HTML")

            # Extract tweets from HTML (basic parsing)
            tweets = extract_tweets_from_html(html, max_tweets)

            # Also try the timeline URL for better results
            timeline_url = f"https://twitter.com/{username}/with_replies"
            params["url"] = timeline_url

            print(f"\n📡 Fetching timeline for more tweets...")
            timeline_response = await client.get("http://api.scraperapi.com", params=params)

            if timeline_response.status_code == 200:
                timeline_html = timeline_response.text
                timeline_tweets = extract_tweets_from_html(timeline_html, max_tweets)

                # Merge and deduplicate tweets
                all_tweets = merge_tweets(tweets, timeline_tweets)
            else:
                all_tweets = tweets

            return {
                "username": username,
                "profile_url": url,
                "scraped_at": datetime.now().isoformat(),
                "tweet_count": len(all_tweets),
                "tweets": all_tweets[:max_tweets]
            }

    except Exception as e:
        print(f"❌ Error scraping Twitter: {e}")
        return {
            "username": username,
            "error": str(e),
            "tweets": []
        }


def extract_tweets_from_html(html: str, max_tweets: int) -> List[Dict[str, Any]]:
    """
    Extract tweet information from HTML

    Note: This is a simplified extraction. For production,
    use Apify's Twitter actor or a proper HTML parser.
    """

    tweets = []

    # Look for tweet text patterns
    # Twitter's HTML structure varies, so we'll try multiple patterns

    # Pattern 1: Look for tweet text in data attributes
    tweet_pattern = r'data-testid="tweetText"[^>]*>([^<]+)'
    matches = re.findall(tweet_pattern, html)

    for match in matches[:max_tweets]:
        tweets.append({
            "text": clean_text(match),
            "source": "pattern1"
        })

    # Pattern 2: Look for aria-label with tweet content
    aria_pattern = r'aria-label="([^"]*)"'
    aria_matches = re.findall(aria_pattern, html)

    for match in aria_matches:
        if len(match) > 50 and len(match) < 500:  # Likely tweet content
            if not any(t["text"] == clean_text(match) for t in tweets):
                tweets.append({
                    "text": clean_text(match),
                    "source": "pattern2"
                })

    # Pattern 3: Look for specific div classes (Twitter's structure)
    div_pattern = r'<div[^>]*class="[^"]*css-[^"]*"[^>]*>([^<]{20,280})'
    div_matches = re.findall(div_pattern, html)

    for match in div_matches:
        cleaned = clean_text(match)
        if cleaned and not any(t["text"] == cleaned for t in tweets):
            tweets.append({
                "text": cleaned,
                "source": "pattern3"
            })

    # Pattern 4: Look for span elements with tweet content
    span_pattern = r'<span[^>]*>([^<]{20,280})</span>'
    span_matches = re.findall(span_pattern, html)

    for match in span_matches:
        cleaned = clean_text(match)
        if cleaned and not is_navigation_text(cleaned):
            if not any(t["text"] == cleaned for t in tweets):
                tweets.append({
                    "text": cleaned,
                    "source": "pattern4"
                })

    return tweets[:max_tweets]


def clean_text(text: str) -> str:
    """Clean and format extracted text"""

    # Remove HTML entities
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Remove extra whitespace
    text = " ".join(text.split())

    return text.strip()


def is_navigation_text(text: str) -> bool:
    """Check if text is likely navigation/UI element"""

    nav_keywords = [
        "Follow", "Following", "Retweet", "Like", "Reply",
        "Share", "More", "Home", "Explore", "Notifications",
        "Messages", "Bookmarks", "Lists", "Profile", "Settings"
    ]

    return any(keyword.lower() in text.lower() for keyword in nav_keywords)


def merge_tweets(tweets1: List[Dict], tweets2: List[Dict]) -> List[Dict]:
    """Merge and deduplicate tweet lists"""

    all_tweets = tweets1.copy()

    for tweet in tweets2:
        if not any(t["text"] == tweet["text"] for t in all_tweets):
            all_tweets.append(tweet)

    return all_tweets


def display_results(result: Dict[str, Any]):
    """Display scraped tweets in a formatted way"""

    print("\n" + "=" * 60)
    print(f"📊 RESULTS FOR @{result['username']}")
    print("=" * 60)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print(f"✅ Successfully scraped {result['tweet_count']} tweets")
    print(f"🕐 Scraped at: {result['scraped_at']}")
    print(f"🔗 Profile: {result['profile_url']}")

    if result["tweets"]:
        print("\n📝 Latest Tweets:")
        print("-" * 60)

        for i, tweet in enumerate(result["tweets"], 1):
            print(f"\n{i}. {tweet['text'][:280]}")
            if len(tweet['text']) > 280:
                print("   ...")
            print(f"   [Source: {tweet['source']}]")
    else:
        print("\n⚠️ No tweets could be extracted from the HTML")
        print("This might be due to:")
        print("  - Twitter's anti-scraping measures")
        print("  - Changes in Twitter's HTML structure")
        print("  - Account privacy settings")
        print("\nFor better results, consider using Apify's Twitter actor")


async def scrape_with_alternative_method(username: str) -> Dict[str, Any]:
    """
    Alternative scraping method using nitter or other Twitter frontends
    """

    print("\n🔄 Trying alternative method...")

    # Try Nitter instances (Twitter alternative frontend)
    nitter_instances = [
        "nitter.net",
        "nitter.42l.fr",
        "nitter.pussthecat.org"
    ]

    for instance in nitter_instances:
        try:
            url = f"https://{instance}/{username}"
            params = {
                "api_key": SCRAPERAPI_KEY,
                "url": url,
                "render": "false"  # Nitter doesn't need JS
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get("http://api.scraperapi.com", params=params)

                if response.status_code == 200:
                    print(f"✅ Successfully used {instance}")
                    html = response.text

                    # Extract from Nitter's cleaner HTML
                    tweets = extract_nitter_tweets(html, 10)

                    return {
                        "username": username,
                        "source": f"nitter ({instance})",
                        "tweets": tweets
                    }

        except Exception as e:
            print(f"   {instance} failed: {e}")
            continue

    return {"username": username, "error": "All alternative methods failed", "tweets": []}


def extract_nitter_tweets(html: str, max_tweets: int) -> List[Dict[str, Any]]:
    """Extract tweets from Nitter HTML (cleaner structure)"""

    tweets = []

    # Nitter has cleaner HTML structure
    tweet_pattern = r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>'
    matches = re.findall(tweet_pattern, html, re.DOTALL)

    for match in matches[:max_tweets]:
        # Clean HTML tags
        text = re.sub(r'<[^>]+>', '', match)
        text = clean_text(text)

        if text and len(text) > 10:
            tweets.append({
                "text": text,
                "source": "nitter"
            })

    return tweets


async def main():
    """Main function to scrape @xkonjin tweets"""

    print("🚀 Twitter Scraper for @xkonjin")
    print("=" * 60)
    print("Note: Twitter actively prevents scraping.")
    print("For production use, Apify's Twitter actor is recommended.")
    print("=" * 60)

    # Try primary method
    result = await scrape_twitter_profile("xkonjin", max_tweets=10)

    # If no tweets found, try alternative
    if not result.get("tweets"):
        print("\n⚠️ No tweets found with primary method")
        alt_result = await scrape_with_alternative_method("xkonjin")

        if alt_result.get("tweets"):
            result["tweets"] = alt_result["tweets"]
            result["source"] = alt_result.get("source", "alternative")

    # Display results
    display_results(result)

    # Save results to file
    output_file = "xkonjin_tweets.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Results saved to {output_file}")

    print("\n" + "=" * 60)
    print("🎯 Recommendations:")
    print("=" * 60)
    print("1. For reliable Twitter scraping, use Apify's Twitter actor")
    print("2. Twitter's HTML structure changes frequently")
    print("3. Consider using Twitter's API for legitimate use cases")
    print("4. Alternative: Use social media monitoring tools")


if __name__ == "__main__":
    asyncio.run(main())