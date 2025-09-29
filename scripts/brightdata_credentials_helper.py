#!/usr/bin/env python3
"""
BrightData Credentials Helper
Shows exactly what you need to add to your .env file
"""

print("=" * 70)
print("🌟 BRIGHTDATA CREDENTIALS SETUP HELPER")
print("=" * 70)
print()
print("After creating your BrightData account, you need 4 credentials:")
print()
print("1️⃣  CUSTOMER ID")
print("   Where: Dashboard → Top right corner")
print("   Format: lum-customer-XXXXXXX")
print("   Example: lum-customer-c_kd8f9s3")
print()
print("2️⃣  ZONE USERNAME")
print("   Where: Zones → Your Zone → Username")
print("   Format: lum-customer-XXXXXXX-zone-YYYYYYY")
print("   Example: lum-customer-c_kd8f9s3-zone-residential_proxy")
print()
print("3️⃣  ZONE PASSWORD")
print("   Where: Zones → Your Zone → Password")
print("   Format: Random alphanumeric")
print("   Example: 9k3nf8sn2k4m")
print()
print("4️⃣  API TOKEN (optional but recommended)")
print("   Where: Settings → API Tokens → Create Token")
print("   Format: Long JWT token")
print("   Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
print()
print("=" * 70)
print("📝 COPY THIS TO YOUR .env FILE:")
print("=" * 70)
print()
print("# BrightData Configuration")
print("BRIGHTDATA_CUSTOMER_ID=")
print("BRIGHTDATA_ZONE_USERNAME=")
print("BRIGHTDATA_ZONE_PASSWORD=")
print("BRIGHTDATA_API_TOKEN=")
print()
print("=" * 70)
print("🚀 QUICK START STEPS:")
print("=" * 70)
print()
print("1. Go to: https://brightdata.com/")
print("2. Click 'Start Free Trial' (gets $5 credit)")
print("3. Create a Zone:")
print("   - Go to Zones → Add Zone")
print("   - Choose 'Datacenter' for testing (cheapest)")
print("   - Or 'Residential' for Twitter scraping")
print("4. Get credentials from locations above")
print("5. Paste into .env file")
print()
print("=" * 70)
print("💰 PRICING GUIDE:")
print("=" * 70)
print()
print("• Datacenter Proxy: $0.60/GB (general sites)")
print("• Residential Proxy: $15/GB (Twitter, LinkedIn)")
print("• Web Unlocker: $3/1000 requests (bypasses everything)")
print("• Free Trial: $5 credit (enough for ~300 Twitter scrapes)")
print()
print("=" * 70)
print("📌 FOR TWITTER/X SCRAPING:")
print("=" * 70)
print()
print("Use one of these zone types:")
print("• Residential Proxy Zone (most reliable)")
print("• Web Unlocker (handles all protections)")
print("• ISP Proxy Zone (premium option)")
print()
print("=" * 70)
print("✅ PASTE YOUR CREDENTIALS HERE TO VERIFY FORMAT:")
print("=" * 70)
print()

# Interactive verification
try:
    print("Enter your credentials (or press Ctrl+C to skip):")
    print()

    customer_id = input("BRIGHTDATA_CUSTOMER_ID = ").strip()
    zone_username = input("BRIGHTDATA_ZONE_USERNAME = ").strip()
    zone_password = input("BRIGHTDATA_ZONE_PASSWORD = ").strip()
    api_token = input("BRIGHTDATA_API_TOKEN (optional, press Enter to skip) = ").strip()

    print()
    print("=" * 70)
    print("✅ VALIDATION RESULTS:")
    print("=" * 70)

    # Validate format
    valid = True

    if customer_id.startswith("lum-customer-"):
        print("✅ Customer ID format looks correct")
    else:
        print("⚠️  Customer ID should start with 'lum-customer-'")
        valid = False

    if "-zone-" in zone_username and zone_username.startswith("lum-customer-"):
        print("✅ Zone username format looks correct")
    else:
        print("⚠️  Zone username should be: lum-customer-XXX-zone-YYY")
        valid = False

    if len(zone_password) > 5:
        print("✅ Zone password provided")
    else:
        print("⚠️  Zone password seems too short")
        valid = False

    if api_token and (api_token.startswith("ey") or len(api_token) > 50):
        print("✅ API token format looks correct")
    elif not api_token:
        print("ℹ️  API token not provided (optional)")
    else:
        print("⚠️  API token format might be incorrect")

    if valid:
        print()
        print("=" * 70)
        print("🎉 READY TO USE! Add these to your .env file:")
        print("=" * 70)
        print()
        print(f"BRIGHTDATA_CUSTOMER_ID={customer_id}")
        print(f"BRIGHTDATA_ZONE_USERNAME={zone_username}")
        print(f"BRIGHTDATA_ZONE_PASSWORD={zone_password}")
        if api_token:
            print(f"BRIGHTDATA_API_TOKEN={api_token}")
        print()
        print("Then test with: python scripts/test_brightdata.py")
    else:
        print()
        print("⚠️  Please check your credentials and try again")

except KeyboardInterrupt:
    print("\n\nSkipped credential entry")
    print("Add credentials manually to your .env file")

print()
print("=" * 70)
print("📚 Documentation: docs/BRIGHTDATA_SETUP_GUIDE.md")
print("=" * 70)