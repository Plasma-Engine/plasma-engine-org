# 🌟 BrightData Integration Setup Guide

## Overview
BrightData (formerly Luminati) is an enterprise-grade web scraping solution that works where others fail, including Twitter/X, LinkedIn, and other heavily protected sites.

## 🔑 Required Credentials

To use BrightData with Plasma Engine, you need **4 pieces of information**:

### 1. Customer ID
- Format: `lum-customer-XXXXXXX`
- Example: `lum-customer-c_kd8f9s3`
- Where to find: [BrightData Dashboard](https://brightdata.com/cp/dashboard) → Top right corner

### 2. Zone Username
- Format: `lum-customer-XXXXXXX-zone-YYYYYYY`
- Example: `lum-customer-c_kd8f9s3-zone-residential_proxy`
- Where to find: Zones → Your Zone → Username

### 3. Zone Password
- Format: Random string
- Example: `9k3nf8sn2k4m`
- Where to find: Zones → Your Zone → Password

### 4. API Token (for Web Unlocker & Datasets)
- Format: Long alphanumeric string
- Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Where to find: [API Tokens Page](https://brightdata.com/cp/api_tokens)

## 📝 Step-by-Step Setup

### Step 1: Create BrightData Account
1. Go to https://brightdata.com/
2. Click "Start Free Trial" (7-day trial with $5 credit)
3. Complete registration

### Step 2: Create a Zone (Proxy Network)
1. Go to [Zones Page](https://brightdata.com/cp/zones)
2. Click "Add Zone"
3. Choose zone type:
   - **Residential** ($15/GB) - Best for social media
   - **Datacenter** ($0.60/GB) - Cost-effective for general sites
   - **Mobile** ($24/GB) - For mobile apps
   - **ISP** ($17/GB) - Premium residential
4. Name your zone (e.g., "plasma_engine_zone")
5. Save zone

### Step 3: Get Your Credentials
1. **Customer ID**:
   - Look at top-right corner of dashboard
   - Copy the `lum-customer-XXXXXXX` value

2. **Zone Credentials**:
   - Go to Zones → Your Zone
   - Copy Username (full string including zone name)
   - Copy Password

3. **API Token**:
   - Go to [Settings → API Tokens](https://brightdata.com/cp/api_tokens)
   - Click "Create Token"
   - Select permissions:
     - ✅ Web Unlocker
     - ✅ SERP API
     - ✅ Datasets
   - Copy the generated token

### Step 4: Add to Environment Variables

Add these to your `.env` file or GitHub Secrets:

```env
# BrightData Configuration
BRIGHTDATA_CUSTOMER_ID=lum-customer-XXXXXXX
BRIGHTDATA_ZONE_USERNAME=lum-customer-XXXXXXX-zone-YYYYYYY
BRIGHTDATA_ZONE_PASSWORD=your_zone_password_here
BRIGHTDATA_API_TOKEN=your_api_token_here
```

### Step 5: Add to GitHub Secrets

```bash
# Add each secret to GitHub
gh secret set BRIGHTDATA_CUSTOMER_ID --repo Plasma-Engine/plasma-engine-org
gh secret set BRIGHTDATA_ZONE_USERNAME --repo Plasma-Engine/plasma-engine-org
gh secret set BRIGHTDATA_ZONE_PASSWORD --repo Plasma-Engine/plasma-engine-org
gh secret set BRIGHTDATA_API_TOKEN --repo Plasma-Engine/plasma-engine-org
```

## 🚀 Quick Test

Once configured, test BrightData:

```python
from plasma_engine_brand.app.scrapers.brightdata_client import BrightDataClient

async def test_brightdata():
    client = BrightDataClient()

    # Test proxy connection
    html = await client.scrape_with_proxy(
        url="https://httpbin.org/ip",
        proxy_type="datacenter"
    )
    print(f"Your IP via BrightData: {html}")

    # Test Twitter scraping (this should work!)
    result = await client.scrape_social_media(
        platform="twitter",
        url="https://twitter.com/elonmusk"
    )
    print(f"Twitter data: {result}")
```

## 💰 Pricing & Credits

### Free Trial
- **$5 free credit** for 7 days
- Enough for ~300 residential requests
- Or ~8,000 datacenter requests

### Pay-As-You-Go Pricing
| Service | Price | Use Case |
|---------|-------|----------|
| **Datacenter** | $0.60/GB | General websites |
| **Residential** | $15/GB | Social media, geo-targeting |
| **Mobile** | $24/GB | Mobile apps, highest success |
| **ISP** | $17/GB | Premium residential |
| **Web Unlocker** | $3/1000 requests | Difficult sites |
| **SERP API** | $3.50/1000 searches | Google, Bing results |
| **Datasets** | $0.001/record | Pre-collected data |

### Cost Examples
- Scraping 1,000 tweets: ~$3-5
- 10,000 news articles: ~$6
- 1,000 LinkedIn profiles: ~$15

## 🎯 What BrightData Can Scrape

### ✅ Works Great With BrightData
- **Twitter/X** - Even with aggressive blocking
- **LinkedIn** - Full profiles and posts
- **Instagram** - Posts, stories, reels
- **TikTok** - Videos and profiles
- **Facebook** - Public pages
- **Amazon** - Products with anti-bot
- **Google** - Search results
- **Any Cloudflare site** - Bypasses protection

### 🔄 Integration with Plasma Engine

BrightData is integrated as a **third-tier fallback**:

1. **Primary**: Apify (social media specialists)
2. **Secondary**: ScraperAPI (general web, cost-effective)
3. **Tertiary**: BrightData (when others fail, enterprise needs)

```python
# Automatic fallback chain
try:
    # Try Apify first for social media
    result = await apify.scrape()
except:
    try:
        # Fallback to ScraperAPI
        result = await scraperapi.scrape()
    except:
        # Final fallback to BrightData
        result = await brightdata.scrape()
```

## 🛠️ Advanced Features

### 1. Sticky Sessions
Maintain the same IP across requests:
```python
await client.scrape_with_proxy(
    url="https://example.com",
    session_id="my-session-123"
)
```

### 2. Geographic Targeting
Target specific countries/cities:
```python
await client.scrape_with_proxy(
    url="https://example.com",
    country="us",
    city="New York"
)
```

### 3. Web Unlocker
Bypass any protection:
```python
result = await client.web_unlocker(
    url="https://heavily-protected-site.com",
    render_js=True
)
```

### 4. Datasets API
Get pre-collected data:
```python
tweets = await client.scrape_social_media(
    platform="twitter",
    url="https://twitter.com/username"
)
```

## 📊 Monitoring Usage

Check your usage and balance:

```python
stats = await client.get_usage_stats()
print(f"Balance: ${stats['balance']}")
print(f"Usage this month: ${stats['monthly_usage']}")
```

Or via dashboard: https://brightdata.com/cp/billing

## 🚨 Important Notes

1. **Start with Datacenter proxies** - Much cheaper for testing
2. **Use Residential only when needed** - For social media and geo-specific content
3. **Monitor usage carefully** - Costs can add up with residential proxies
4. **Cache aggressively** - Don't re-scrape unnecessarily
5. **Use datasets when available** - Pre-collected data is cheaper

## 🔗 Useful Links

- [BrightData Dashboard](https://brightdata.com/cp/dashboard)
- [API Documentation](https://docs.brightdata.com/api-reference)
- [Web Unlocker Docs](https://docs.brightdata.com/web-unlocker)
- [Datasets Catalog](https://brightdata.com/products/datasets)
- [Proxy Manager](https://brightdata.com/products/proxy-manager)
- [Status Page](https://status.brightdata.com/)

## ✅ Setup Checklist

- [ ] Create BrightData account
- [ ] Create a zone (start with Datacenter)
- [ ] Get Customer ID
- [ ] Get Zone Username & Password
- [ ] Generate API Token
- [ ] Add credentials to `.env`
- [ ] Add to GitHub Secrets
- [ ] Test with simple request
- [ ] Test Twitter scraping
- [ ] Monitor initial usage

## 💡 Tips for Twitter/X Scraping

Since you specifically need Twitter scraping:

1. **Use the Twitter Dataset** - Most reliable
   ```python
   result = await client.scrape_social_media(
       platform="twitter",
       url=f"https://twitter.com/xkonjin"
   )
   ```

2. **Or use Web Unlocker** - Handles all protections
   ```python
   result = await client.web_unlocker(
       url="https://x.com/xkonjin",
       render_js=True
   )
   ```

3. **Or use Residential Proxy** - Direct scraping
   ```python
   html = await client.scrape_with_proxy(
       url="https://x.com/xkonjin",
       proxy_type="residential",
       country="us"
   )
   ```

---

**Note**: BrightData is the most powerful but also most expensive option. Use it when Apify and ScraperAPI fail, or when you need enterprise-grade reliability.