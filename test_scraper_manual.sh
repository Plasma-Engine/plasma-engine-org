#!/bin/bash

# Simple ScraperAPI test using curl
# Usage: ./test_scraper_manual.sh YOUR_SCRAPERAPI_KEY

echo "🧪 ScraperAPI Manual Test"
echo "========================="

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your ScraperAPI key as an argument"
    echo "Usage: ./test_scraper_manual.sh YOUR_SCRAPERAPI_KEY"
    exit 1
fi

API_KEY=$1
echo "✅ Using API key: ${API_KEY:0:10}..."

# Test 1: Basic IP check
echo ""
echo "📝 Test 1: Basic IP Check"
echo "-------------------------"
RESPONSE=$(curl -s "http://api.scraperapi.com?api_key=$API_KEY&url=http://httpbin.org/ip")

if [ $? -eq 0 ]; then
    echo "✅ Request successful!"
    echo "Response preview:"
    echo "$RESPONSE" | head -c 200
    echo "..."
else
    echo "❌ Request failed"
fi

# Test 2: Scrape example.com
echo ""
echo "📝 Test 2: Scrape example.com"
echo "-----------------------------"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://api.scraperapi.com?api_key=$API_KEY&url=https://example.com")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Successfully scraped example.com (HTTP $RESPONSE)"
else
    echo "❌ Failed to scrape (HTTP $RESPONSE)"
fi

# Test 3: Check credits with headers
echo ""
echo "📝 Test 3: Credit Usage Check"
echo "-----------------------------"
CREDITS=$(curl -s -D - "http://api.scraperapi.com?api_key=$API_KEY&url=http://httpbin.org/headers" | grep -i "x-api-credits" | head -1)

if [ -n "$CREDITS" ]; then
    echo "✅ Credit info: $CREDITS"
else
    echo "⚠️ Could not retrieve credit information"
fi

echo ""
echo "========================="
echo "✅ Test Complete!"
echo ""
echo "If all tests passed, your ScraperAPI key is working correctly!"
echo "You can now use it in the Plasma Engine Brand service."