# Plasma Engine Web Scraping Documentation

## Overview

The Plasma Engine uses a comprehensive triple-scraping architecture with intelligent routing and automatic fallback mechanisms. This ensures reliable data extraction from social media platforms, news sites, and general web content.

## Architecture

### Triple-Scraping Stack

1. **BrightData (Primary for Social Media)**
   - Enterprise-grade web scraping with residential proxies
   - 72M+ residential IPs, 7M+ mobile IPs
   - Handles CAPTCHAs and bot detection
   - **TESTED AND WORKING** for Twitter/X, Instagram, LinkedIn, TikTok, YouTube, GitHub, Google News

2. **Apify (Secondary)**
   - Premium actors for specialized scraping
   - Good for Reddit, Twitter, Instagram
   - Structured data extraction

3. **ScraperAPI (Tertiary)**
   - General web scraping
   - Good for news sites, blogs, e-commerce
   - 83% success rate for general web content

## Quick Start

### 1. Environment Setup

Add the following to your `.env` file:

```env
# BrightData Configuration (Primary)
BRIGHTDATA_API_TOKEN=your_brightdata_api_token_here

# Apify Configuration (Secondary)
APIFY_TOKEN=your_apify_token_here

# ScraperAPI Configuration (Tertiary)
SCRAPERAPI_KEY=your_scraperapi_key_here
```

### 2. Basic Usage

```python
from plasma_engine_brand.app.scrapers.unified_scraper_v2 import UnifiedScraperV2

async def scrape_twitter():
    scraper = UnifiedScraperV2()

    # Scrape Twitter profile
    result = await scraper.scrape_social_profile("twitter", "xkonjin")
    print(result["content"])

    # Scrape multiple platforms
    platforms = ["twitter", "instagram", "linkedin", "github"]
    for platform in platforms:
        result = await scraper.scrape_social_profile(platform, "username")
        print(f"{platform}: {result['success']}")
```

## Platform-Specific Scrapers

### Twitter/X Scraper

```python
from plasma_engine_brand.app.scrapers.platform_scrapers import TwitterScraper

scraper = TwitterScraper()

# Scrape profile
profile = await scraper.scrape_profile("xkonjin")

# Scrape posts
posts = await scraper.scrape_posts("xkonjin", limit=10)

# Search by hashtag
hashtag_results = await scraper.scrape_tweets_by_hashtag("AI")
```

### Instagram Scraper

```python
from plasma_engine_brand.app.scrapers.platform_scrapers import InstagramScraper

scraper = InstagramScraper()

# Scrape profile
profile = await scraper.scrape_profile("cristiano")

# Scrape posts
posts = await scraper.scrape_posts("cristiano", limit=10)

# Scrape reels
reels = await scraper.scrape_reels("cristiano")
```

### LinkedIn Scraper

```python
from plasma_engine_brand.app.scrapers.platform_scrapers import LinkedInScraper

scraper = LinkedInScraper()

# Scrape profile
profile = await scraper.scrape_profile("williamhgates")

# Scrape company
company = await scraper.scrape_company("microsoft")
```

### GitHub Scraper

```python
from plasma_engine_brand.app.scrapers.platform_scrapers import GitHubScraper

scraper = GitHubScraper()

# Scrape profile
profile = await scraper.scrape_profile("torvalds")

# Scrape repository
repo = await scraper.scrape_repo("plasma-engine-org", "plasma-engine")

# Get starred repos
stars = await scraper.scrape_stars("torvalds")
```

### Google News Scraper

```python
from plasma_engine_brand.app.scrapers.platform_scrapers import GoogleNewsScraper

scraper = GoogleNewsScraper()

# Search news
results = await scraper.scrape_search("artificial intelligence")

# Get headlines
headlines = await scraper.scrape_headlines()

# Get topic news
tech_news = await scraper.scrape_topic("technology")
```

## Unified Scraper V2

The unified scraper provides intelligent routing and automatic fallback:

```python
from plasma_engine_brand.app.scrapers.unified_scraper_v2 import UnifiedScraperV2

scraper = UnifiedScraperV2()

# Automatic platform detection and routing
result = await scraper.scrape("https://x.com/xkonjin")

# Batch scraping
urls = [
    "https://x.com/elonmusk",
    "https://github.com/torvalds",
    "https://www.instagram.com/cristiano"
]
results = await scraper.batch_scrape(urls, concurrent_limit=5)

# Brand monitoring
mentions = await scraper.monitor_brand_mentions(
    brand_terms=["plasma engine", "plasma.to"],
    platforms=["twitter", "linkedin", "github", "google_news"]
)

# Get performance metrics
metrics = scraper.get_metrics()
print(f"Success rates: {metrics}")
```

## Configuration

### Platform-Specific Options

Configuration is centralized in `social_scrapers_config.py`:

```python
BRIGHTDATA_SCRAPERS = {
    "twitter": {
        "scraper_id": "hl_29db646e",
        "dataset_id": "gd_lwbmp8fu8jl7p4z",
        "capabilities": ["profile_info", "tweets", "followers", ...]
    },
    # ... other platforms
}

DEFAULT_OPTIONS = {
    "twitter": {
        "render_js": False,  # Twitter works without JS
        "country": "us",
        "format": "raw",
        "timeout": 60
    },
    # ... other platforms
}
```

### Rate Limits

```python
RATE_LIMITS = {
    "twitter": 30,      # requests per minute
    "instagram": 20,
    "linkedin": 15,
    "github": 60,       # GitHub API has higher limits
    # ...
}
```

## Testing

### Run All Tests

```bash
# Test all scrapers
python scripts/test_all_scrapers.py

# Test specific scraper
python scripts/brightdata_working.py
```

### Test Results

Test results are saved to `scraper_test_results.json`:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "results": {
    "Twitter/X": true,
    "Instagram": true,
    "LinkedIn": true,
    "GitHub": true,
    "Google News": true
  },
  "summary": {
    "total": 8,
    "passed": 8,
    "failed": 0,
    "success_rate": "100.0%"
  }
}
```

## BrightData Setup

### 1. Get API Token

1. Sign up at [BrightData](https://brightdata.com)
2. Navigate to [API Tokens](https://brightdata.com/cp/api_tokens)
3. Create a new token with appropriate permissions

### 2. MCP Configuration (Optional)

If using MCP (Model Context Protocol):

```json
{
  "mcpServers": {
    "brightdata-mcp": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "your_token_here",
        "PRO_MODE": "1"
      }
    }
  }
}
```

### 3. Zone Configuration

BrightData uses zones for organizing scraping tasks:

- Default zone: `mcp_unlocker`
- Custom zones can be created in the BrightData dashboard

## Troubleshooting

### Common Issues

1. **403 Forbidden on Twitter/X with ScraperAPI**
   - Solution: Use BrightData instead (primary for social media)
   - ScraperAPI doesn't work for Twitter due to anti-bot measures

2. **404 Not Found with BrightData**
   - Check API token is valid
   - Ensure zone exists (default: `mcp_unlocker`)
   - Use correct endpoint: `https://api.brightdata.com/request`

3. **Rate Limiting**
   - Implement delays between requests
   - Use concurrent_limit in batch operations
   - Monitor rate limits per platform

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now scrapers will output detailed logs
scraper = UnifiedScraperV2()
```

## Performance Metrics

The unified scraper tracks performance metrics:

```python
metrics = scraper.get_metrics()

# Output:
{
  "total_requests": 150,
  "fallbacks_triggered": 12,
  "services": {
    "brightdata": {
      "success": 120,
      "failure": 5,
      "success_rate": 96.0
    },
    "apify": {
      "success": 20,
      "failure": 3,
      "success_rate": 87.0
    },
    "scraperapi": {
      "success": 2,
      "failure": 0,
      "success_rate": 100.0
    }
  }
}
```

## Best Practices

1. **Use Platform-Specific Scrapers**
   - More reliable than generic scraping
   - Optimized for each platform's structure

2. **Implement Caching**
   - Reduce API costs
   - Improve response times
   - Respect rate limits

3. **Handle Errors Gracefully**
   - All scrapers return consistent error formats
   - Check `success` field before processing content

4. **Batch Operations**
   - Use `batch_scrape` for multiple URLs
   - Set appropriate `concurrent_limit`

5. **Monitor Usage**
   - Track API costs with metrics
   - Set up alerts for failures
   - Regular testing with `test_all_scrapers.py`

## API Rate Limits & Costs

### BrightData
- Pay per successful request
- No hard rate limits (managed by proxy rotation)
- Pricing varies by proxy type and geography

### Apify
- Credit-based system
- Actor-specific pricing
- Free tier: $5/month credits

### ScraperAPI
- 5,000 free requests/month
- 10 concurrent requests (free tier)
- Premium proxies cost extra credits

## Security

1. **Never commit API keys**
   - Use `.env` file (gitignored)
   - Use GitHub Secrets for CI/CD

2. **Rotate Keys Regularly**
   - Monthly rotation recommended
   - Keep backup keys

3. **Limit Scope**
   - Use read-only permissions where possible
   - Restrict to specific IPs if supported

## Support & Resources

- **BrightData Docs**: https://docs.brightdata.com
- **Apify Docs**: https://docs.apify.com
- **ScraperAPI Docs**: https://docs.scraperapi.com
- **Issues**: Report at https://github.com/plasma-engine-org/plasma-engine/issues

## License

This scraping infrastructure is part of the Plasma Engine project and follows the same license terms.