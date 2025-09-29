# 🎯 BrightData Complete Setup Guide for Social Media Scraping

## ⚠️ IMPORTANT: API Token Alone Is Not Enough!

The tests show that having just the API token (`7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2`) returns 404 errors for all endpoints. You need a **complete BrightData account setup** with zones configured.

## 🔴 Current Status: NOT WORKING

All API calls return 404 because:
1. ❌ No BrightData account exists for `jf@plasma.to`
2. ❌ No zones (proxy networks) configured
3. ❌ No customer ID assigned
4. ❌ API token not linked to an active account

## ✅ What You Need to Do

### Step 1: Create BrightData Account

1. **Go to**: https://brightdata.com/
2. **Click**: "Start Free Trial" (top right)
3. **Sign up with**: 
   - Email: `jf@plasma.to`
   - Use Google authentication (since you don't use passwords)
4. **Verify** your email if needed
5. **Complete** the onboarding process

### Step 2: Create Your First Zone

Once logged in:

1. **Navigate to**: Dashboard → Zones (left sidebar)
2. **Click**: "Add Zone" or "Create Zone"
3. **Choose zone type**:

   | Zone Type | Price | Best For | Twitter/X Support |
   |-----------|-------|----------|-------------------|
   | **Web Unlocker** | $3/1000 requests | All sites | ✅ BEST |
   | **Residential Proxy** | $15/GB | Social media | ✅ WORKS |
   | **ISP Proxy** | $17/GB | Premium residential | ✅ WORKS |
   | **Datacenter Proxy** | $0.60/GB | General sites | ❌ NO |

   **For Twitter/X scraping, choose**: Web Unlocker or Residential Proxy

4. **Configure the zone**:
   - Name: `plasma_social_scraper`
   - Target sites: Enable all social media
   - Country: United States (or your preference)

5. **Save** the zone

### Step 3: Collect Your Credentials

After creating the zone, gather these 4 credentials:

#### 1. Customer ID
- **Location**: Top-right corner of dashboard
- **Format**: `lum-customer-c_XXXXXXX`
- **Example**: `lum-customer-c_kd8f9s3`

#### 2. Zone Username
- **Location**: Zones → Your Zone → Connection Settings
- **Format**: `lum-customer-c_XXXXXXX-zone-ZONENAME`
- **Example**: `lum-customer-c_kd8f9s3-zone-plasma_social_scraper`

#### 3. Zone Password
- **Location**: Zones → Your Zone → Connection Settings
- **Format**: Random string
- **Example**: `9k3nf8sn2k4m`
- **Note**: You can regenerate this if needed

#### 4. API Token (Re-generate after account creation)
- **Location**: Settings → API Tokens
- **Action**: Create new token with these permissions:
  - ✅ Web Unlocker API
  - ✅ Proxy API
  - ✅ Datasets API
  - ✅ SERP API

### Step 4: Update Your .env File

Replace the current single token with all 4 credentials:

```env
# BrightData Complete Configuration
BRIGHTDATA_CUSTOMER_ID=lum-customer-c_XXXXXXX
BRIGHTDATA_ZONE_USERNAME=lum-customer-c_XXXXXXX-zone-plasma_social_scraper
BRIGHTDATA_ZONE_PASSWORD=your_zone_password_here
BRIGHTDATA_API_TOKEN=new_token_from_account
```

### Step 5: Add to GitHub Secrets

```bash
# Add all 4 secrets
gh secret set BRIGHTDATA_CUSTOMER_ID --body "lum-customer-c_XXXXXXX"
gh secret set BRIGHTDATA_ZONE_USERNAME --body "lum-customer-c_XXXXXXX-zone-plasma_social_scraper"
gh secret set BRIGHTDATA_ZONE_PASSWORD --body "your_zone_password_here"
gh secret set BRIGHTDATA_API_TOKEN --body "new_token_from_account"
```

## 🚀 What Will Work After Setup

### Method 1: Web Unlocker (Recommended for Twitter)
```python
import httpx

headers = {
    "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "url": "https://x.com/xkonjin",
    "country": "us",
    "render_js": True
}

response = await client.post(
    "https://api.brightdata.com/unlocker/request",
    headers=headers,
    json=payload
)
# This will return the full HTML of the Twitter profile
```

### Method 2: Proxy Network
```python
# Build proxy URL
proxy_url = f"http://{BRIGHTDATA_ZONE_USERNAME}:{BRIGHTDATA_ZONE_PASSWORD}@zproxy.lum-superproxy.io:22225"

# Use with any HTTP client
async with httpx.AsyncClient(proxies=proxy_url) as client:
    response = await client.get("https://x.com/xkonjin")
    # This routes through BrightData's residential IPs
```

### Method 3: Pre-built Datasets (if available)
```python
headers = {
    "Authorization": f"Bearer {BRIGHTDATA_API_TOKEN}"
}

payload = {
    "dataset_id": "twitter_profiles",
    "url": "https://x.com/xkonjin"
}

response = await client.post(
    "https://api.brightdata.com/datasets/v3/trigger",
    headers=headers,
    json=payload
)
# Returns structured Twitter data
```

## 💰 Costs After Setup

### With $5 Free Trial Credit:
- **Web Unlocker**: ~1,666 requests
- **Residential Proxy**: ~333 MB of data (hundreds of profiles)
- **Datacenter Proxy**: ~8.3 GB of data (thousands of pages)

### Twitter/X Scraping Specifically:
- Cost per profile: ~$0.003 (Web Unlocker)
- Cost per 100 tweets: ~$0.30 (Web Unlocker)
- Cost per profile: ~$0.015 (Residential Proxy)

## 📋 Setup Checklist

- [ ] Create BrightData account at https://brightdata.com/
- [ ] Use email: `jf@plasma.to` with Google auth
- [ ] Activate free trial ($5 credit)
- [ ] Create a zone (Web Unlocker or Residential)
- [ ] Get Customer ID from dashboard
- [ ] Get Zone Username from zone settings
- [ ] Get Zone Password from zone settings
- [ ] Generate new API Token with all permissions
- [ ] Update .env with all 4 credentials
- [ ] Add all 4 to GitHub Secrets
- [ ] Test with `python scripts/test_brightdata_complete.py`

## 🔧 Troubleshooting

### Still getting 404 errors?
1. **Account not activated**: Check email for verification
2. **Zone not created**: Must have at least one zone
3. **Wrong API endpoint**: Different accounts have different endpoints
4. **Token permissions**: Regenerate with all permissions

### Getting 401 Unauthorized?
1. **Token expired**: Generate a new one
2. **Wrong customer ID**: Check dashboard
3. **Zone credentials wrong**: Check zone settings

### Getting 403 Forbidden?
1. **Insufficient credits**: Add payment method
2. **Zone type wrong**: Use Residential or Web Unlocker for social media
3. **Target site blocked**: Upgrade to Web Unlocker

## 📞 Support

- **BrightData Support**: https://brightdata.com/contact
- **Live Chat**: Available in dashboard
- **Documentation**: https://docs.brightdata.com/
- **Status Page**: https://status.brightdata.com/

## ⏰ Next Steps

1. **Immediate**: Create BrightData account
2. **5 minutes**: Set up first zone
3. **10 minutes**: Get all credentials
4. **15 minutes**: Update .env and test
5. **Success**: Scrape @xkonjin tweets!

---

**Remember**: The API token alone (`7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2`) is just a random string without an account. You MUST complete the full setup to make it work.