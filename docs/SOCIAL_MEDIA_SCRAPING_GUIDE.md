# 📱 Social Media Scraping Guide - Platform-Specific Strategies

## Overview
This guide provides detailed strategies for scraping each major social media platform using our dual Apify + ScraperAPI architecture.

## 🚀 Platform-Specific Implementation

### 1. X (Twitter) Scraping

#### Primary: Apify Twitter Scraper
```python
from plasma_engine_brand.scrapers.apify_client import ApifyScraper

async def scrape_twitter(query: str, max_items: int = 100):
    """Scrape Twitter/X using Apify"""
    scraper = ApifyScraper()

    # Use Apify's Twitter scraper actor
    results = await scraper.scrape_social(
        platform="twitter",
        query=query,  # Can be hashtag, username, or keyword
        max_items=max_items
    )

    # Process tweets
    for tweet in results["items"]:
        print(f"@{tweet['author']}: {tweet['text']}")
        print(f"Likes: {tweet['likes']}, Retweets: {tweet['retweets']}")
```

#### Fallback: ScraperAPI with JavaScript Rendering
```python
async def scrape_twitter_fallback(query: str):
    """Fallback Twitter scraping via ScraperAPI"""
    scraper = ScraperAPIClient()

    # Twitter search URL (public view)
    url = f"https://twitter.com/search?q={query}&f=live"

    # Must enable JavaScript rendering for Twitter
    html = await scraper.scrape(
        url=url,
        render_js=True,
        device_type="desktop"
    )

    # Parse the HTML to extract tweets
    # Note: This is less reliable than Apify
```

**Best Practices for Twitter/X:**
- Use Apify for real-time monitoring
- Track engagement metrics (likes, retweets, replies)
- Monitor trending hashtags
- Set up alerts for brand mentions

---

### 2. LinkedIn Scraping

#### Primary: Apify LinkedIn Scraper
```python
async def scrape_linkedin_posts(company_url: str):
    """Scrape LinkedIn company posts"""
    scraper = ApifyScraper()

    results = await scraper.scrape_social(
        platform="linkedin",
        query=company_url,
        max_items=50
    )

    # Extract professional insights
    for post in results["posts"]:
        print(f"Company: {post['company']}")
        print(f"Content: {post['text']}")
        print(f"Reactions: {post['reactions']}")
```

#### LinkedIn-Specific Considerations:
- **Rate Limiting**: LinkedIn is aggressive with rate limits
- **Authentication**: Some content requires login
- **B2B Focus**: Extract company info, job postings, professional content
- **Compliance**: Be extra careful with LinkedIn's ToS

**Fallback Strategy:**
```python
# ScraperAPI with session management for LinkedIn
async def scrape_linkedin_with_session():
    scraper = ScraperAPIClient()

    # Use session to maintain state
    content = await scraper.scrape(
        url="https://www.linkedin.com/company/example",
        render_js=True,
        session_number=12345,  # Maintain session
        premium_proxy=True  # LinkedIn often requires premium proxies
    )
```

---

### 3. Instagram Scraping

#### Primary: Apify Instagram Scraper
```python
async def scrape_instagram_profile(username: str):
    """Scrape Instagram profile and posts"""
    scraper = ApifyScraper()

    results = await scraper.scrape_social(
        platform="instagram",
        query=f"@{username}",
        max_items=30
    )

    # Process visual content
    for post in results["posts"]:
        print(f"Caption: {post['caption']}")
        print(f"Likes: {post['likes']}")
        print(f"Image URL: {post['image_url']}")
        print(f"Hashtags: {post['hashtags']}")
```

**Instagram-Specific Features:**
- **Visual Content**: Always capture image/video URLs
- **Hashtag Analysis**: Track trending hashtags
- **Stories**: Consider story scraping (24-hour content)
- **Reels**: Track short-form video performance

---

### 4. TikTok Scraping

#### Strategy: ScraperAPI (TikTok is challenging for Apify)
```python
async def scrape_tiktok_profile(username: str):
    """Scrape TikTok profile using ScraperAPI"""
    scraper = ScraperAPIClient()

    url = f"https://www.tiktok.com/@{username}"

    # TikTok requires specific configuration
    content = await scraper.scrape(
        url=url,
        render_js=True,
        device_type="mobile",  # TikTok optimized for mobile
        country_code="us",  # Geo-targeting important for TikTok
        premium_proxy=True
    )

    # Parse video metrics
    # Consider using structured data if available
```

**TikTok Challenges:**
- **Heavy JavaScript**: Requires full rendering
- **Geo-restrictions**: Content varies by region
- **Rapid changes**: TikTok frequently updates anti-bot measures
- **Mobile-first**: Better results with mobile user agents

---

### 5. Reddit Scraping

#### Primary: Apify Reddit Scraper
```python
async def scrape_reddit_subreddit(subreddit: str, sort: str = "hot"):
    """Scrape Reddit subreddit posts and comments"""
    scraper = ApifyScraper()

    results = await scraper.scrape_social(
        platform="reddit",
        query=f"r/{subreddit}",
        max_items=100,
        sort=sort  # hot, new, top, controversial
    )

    # Process discussions
    for post in results["posts"]:
        print(f"Title: {post['title']}")
        print(f"Upvotes: {post['score']}")
        print(f"Comments: {post['num_comments']}")

        # Get top comments
        for comment in post.get("comments", [])[:5]:
            print(f"  - {comment['text']} ({comment['score']} points)")
```

**Reddit Best Practices:**
- **Monitor relevant subreddits**: Track industry discussions
- **Sentiment analysis**: Reddit has honest feedback
- **Comment threads**: Deep insights in comments
- **API alternative**: Reddit has official API for some use cases

---

### 6. YouTube Scraping

#### Strategy: ScraperAPI with Structured Data
```python
async def scrape_youtube_channel(channel_url: str):
    """Scrape YouTube channel information"""
    scraper = ScraperAPIClient()

    # YouTube channel page
    content = await scraper.scrape(
        url=channel_url,
        render_js=True,
        autoparse=True  # Try to get structured data
    )

    # For video comments (high value for sentiment)
    video_url = "https://www.youtube.com/watch?v=VIDEO_ID"
    comments = await scraper.scrape(
        url=f"{video_url}&sort=top",
        render_js=True
    )
```

**YouTube Considerations:**
- **Video metadata**: Views, likes, duration
- **Comments**: Rich source of feedback
- **Transcripts**: Available for many videos
- **Channel analytics**: Subscriber counts, video frequency

---

## 📰 Blog & News Site Scraping

### General Blog Scraping Strategy
```python
async def scrape_blog_efficiently(blog_url: str):
    """Efficient blog scraping with ScraperAPI"""
    scraper = ScraperAPIClient()

    # Most blogs don't need JS rendering
    content = await scraper.scrape(
        url=blog_url,
        render_js=False,  # Faster and cheaper
        autoparse=True  # Get structured content if available
    )

    # For RSS feeds (many blogs have them)
    rss_url = f"{blog_url}/feed"
    feed = await scraper.scrape(rss_url)
```

### News Site Scraping
```python
async def scrape_news_sites(urls: List[str]):
    """Batch scrape multiple news sites"""
    scraper = ScraperAPIClient()

    # Batch processing for efficiency
    results = await scraper.scrape_batch(
        urls=urls,
        render_js=False,  # Most news sites work without JS
        country_code="us"  # Some sites show different content by region
    )

    return results
```

**News Site Best Practices:**
- **Paywall detection**: Check for paywall indicators
- **Article extraction**: Focus on main content, ignore ads
- **Publication dates**: Critical for news monitoring
- **Author information**: Track journalist coverage

---

## 🔄 Unified Scraping Workflow

### Intelligent Platform Router
```python
class PlatformRouter:
    """Route scraping requests to optimal service"""

    PLATFORM_MAPPING = {
        # Social Media - Apify Primary
        "twitter.com": ("apify", "twitter"),
        "x.com": ("apify", "twitter"),
        "linkedin.com": ("apify", "linkedin"),
        "instagram.com": ("apify", "instagram"),
        "reddit.com": ("apify", "reddit"),

        # Video Platforms - ScraperAPI Primary
        "tiktok.com": ("scraperapi", "tiktok"),
        "youtube.com": ("scraperapi", "youtube"),

        # News & Blogs - ScraperAPI Primary
        "medium.com": ("scraperapi", "blog"),
        "techcrunch.com": ("scraperapi", "news"),
        "reuters.com": ("scraperapi", "news"),

        # E-commerce - ScraperAPI Structured
        "amazon.com": ("scraperapi_structured", "amazon_product"),
        "ebay.com": ("scraperapi_structured", "ebay_product")
    }

    @classmethod
    def route(cls, url: str) -> tuple:
        """Determine best scraper for URL"""
        from urllib.parse import urlparse

        domain = urlparse(url).netloc.lower()

        # Remove www. prefix
        domain = domain.replace("www.", "")

        return cls.PLATFORM_MAPPING.get(
            domain,
            ("scraperapi", "general")  # Default fallback
        )
```

---

## ⚡ Performance Optimization

### Concurrent Scraping Pattern
```python
async def scrape_multiple_platforms(targets: Dict[str, List[str]]):
    """Scrape multiple platforms concurrently"""

    tasks = []

    for platform, queries in targets.items():
        if platform in ["twitter", "linkedin", "instagram", "reddit"]:
            # Use Apify for social media
            task = scrape_with_apify(platform, queries)
        else:
            # Use ScraperAPI for others
            task = scrape_with_scraperapi(platform, queries)

        tasks.append(task)

    # Run all scraping tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return process_results(results)
```

### Caching Strategy
```python
class ScrapingCache:
    """Cache scraped content to reduce API calls"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = {
            "twitter": 300,  # 5 minutes for real-time
            "news": 1800,  # 30 minutes for news
            "blog": 3600,  # 1 hour for blogs
            "profile": 86400  # 24 hours for profiles
        }

    async def get_or_scrape(self, url: str, scraper_func, content_type: str):
        # Check cache first
        cached = await self.redis.get(f"scrape:{url}")
        if cached:
            return json.loads(cached)

        # Scrape if not cached
        result = await scraper_func(url)

        # Cache with appropriate TTL
        ttl = self.ttl.get(content_type, 3600)
        await self.redis.setex(
            f"scrape:{url}",
            ttl,
            json.dumps(result)
        )

        return result
```

---

## 🚨 Error Handling & Fallbacks

### Comprehensive Error Handler
```python
class ScrapingErrorHandler:
    """Handle scraping errors with automatic fallbacks"""

    @staticmethod
    async def scrape_with_fallback(url: str):
        """Try multiple scraping methods with fallbacks"""

        # Determine primary method
        primary_service, platform = PlatformRouter.route(url)

        try:
            # Try primary method
            if primary_service == "apify":
                return await ApifyScraper().scrape_social(platform, url)
            else:
                return await ScraperAPIClient().scrape(url)

        except Exception as primary_error:
            logger.warning(f"Primary scraping failed: {primary_error}")

            # Try fallback
            try:
                if primary_service == "apify":
                    # Fallback to ScraperAPI
                    return await ScraperAPIClient().scrape(url, render_js=True)
                else:
                    # Fallback to Apify if available
                    return await ApifyScraper().scrape_general(url)

            except Exception as fallback_error:
                logger.error(f"All scraping methods failed: {fallback_error}")

                # Return error info
                return {
                    "error": True,
                    "url": url,
                    "primary_error": str(primary_error),
                    "fallback_error": str(fallback_error),
                    "timestamp": datetime.now().isoformat()
                }
```

---

## 📊 Monitoring & Analytics

### Scraping Metrics Tracker
```python
class ScrapingMetrics:
    """Track scraping performance and costs"""

    def __init__(self):
        self.metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "apify_credits": 0,
            "scraperapi_credits": 0,
            "avg_response_time": 0,
            "fallback_triggered": 0
        }

    async def log_request(self, service: str, success: bool, credits: int, duration: float):
        """Log scraping request metrics"""

        self.metrics["requests"] += 1

        if success:
            self.metrics["successes"] += 1
        else:
            self.metrics["failures"] += 1

        if service == "apify":
            self.metrics["apify_credits"] += credits
        else:
            self.metrics["scraperapi_credits"] += credits

        # Update average response time
        current_avg = self.metrics["avg_response_time"]
        total_requests = self.metrics["requests"]
        self.metrics["avg_response_time"] = (
            (current_avg * (total_requests - 1) + duration) / total_requests
        )

    def get_report(self):
        """Generate metrics report"""
        return {
            **self.metrics,
            "success_rate": self.metrics["successes"] / max(self.metrics["requests"], 1),
            "total_credits": self.metrics["apify_credits"] + self.metrics["scraperapi_credits"],
            "estimated_cost": self.calculate_cost()
        }
```

---

## 🎯 Quick Reference

| Platform | Primary Service | Fallback | Best For |
|----------|----------------|----------|----------|
| Twitter/X | Apify | ScraperAPI + JS | Real-time mentions, trends |
| LinkedIn | Apify | ScraperAPI + Premium | B2B insights, job market |
| Instagram | Apify | ScraperAPI + JS | Visual content, hashtags |
| TikTok | ScraperAPI + JS | Apify | Short-form video trends |
| Reddit | Apify | ScraperAPI | Community sentiment |
| YouTube | ScraperAPI | - | Video comments, metadata |
| Blogs | ScraperAPI | - | Long-form content |
| News | ScraperAPI | - | High-volume, fast updates |

## 🔑 Key Takeaways

1. **Use Apify for social media** - Better success rates with built-in actors
2. **Use ScraperAPI for general web** - More cost-effective for simple scraping
3. **Always implement fallbacks** - Ensure data collection continuity
4. **Cache aggressively** - Reduce API costs and improve speed
5. **Monitor metrics** - Track success rates and optimize routing
6. **Respect rate limits** - Implement proper delays and rotation
7. **Handle errors gracefully** - Log failures for debugging
8. **Use structured data when available** - Easier parsing and better reliability