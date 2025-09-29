#!/usr/bin/env python3
"""
Test BrightData using their CLI/SDK directly
"""

import subprocess
import json
import os
import asyncio

API_TOKEN = "7988cfc285ec3fb71793e831557d3ed4976f4b327e03a7e41845e7776d7c8cc2"


async def test_brightdata_cli():
    """Test BrightData via npx CLI"""

    print("=" * 70)
    print("🚀 TESTING BRIGHTDATA VIA NPX CLI")
    print("=" * 70)

    # Set environment variables
    env = os.environ.copy()
    env["API_TOKEN"] = API_TOKEN
    env["PRO_MODE"] = "1"

    # Test scraping Twitter/X with the CLI
    test_urls = [
        "https://x.com/xkonjin",
        "https://x.com/elonmusk",
        "https://www.linkedin.com/in/williamhgates"
    ]

    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        print("-" * 50)

        try:
            # Use the BrightData CLI to scrape
            cmd = [
                "npx", "@brightdata/mcp",
                "scrape",
                "--url", url,
                "--zone", "mcp_unlocker",
                "--render", "true"
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                cwd="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"
            )

            if result.returncode == 0:
                print("✅ Success!")
                output = result.stdout[:1000]
                print(f"Output preview: {output}")

                # Save to file
                filename = f"brightdata_cli_{url.split('/')[-1]}.html"
                with open(filename, "w") as f:
                    f.write(result.stdout)
                print(f"💾 Saved to {filename}")
            else:
                print("❌ Failed")
                print(f"Error: {result.stderr[:500]}")

        except subprocess.TimeoutExpired:
            print("⏱️ Timeout - request took too long")
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_brightdata_node():
    """Test BrightData using Node.js script"""

    print("\n" + "=" * 70)
    print("🔧 TESTING BRIGHTDATA VIA NODE.JS")
    print("=" * 70)

    # Create a Node.js test script
    node_script = """
const { BrightDataClient } = require('@brightdata/sdk');

async function testScraping() {
    const client = new BrightDataClient({
        apiToken: process.env.API_TOKEN,
        zone: 'mcp_unlocker'
    });

    console.log('Testing Twitter/X scraping for @xkonjin...');

    try {
        const result = await client.scrape({
            url: 'https://x.com/xkonjin',
            render: true,
            country: 'us'
        });

        console.log('✅ Success!');
        console.log('Content length:', result.html.length);

        // Check for Twitter content
        if (result.html.includes('xkonjin')) {
            console.log('✅ Found @xkonjin in content!');
        }

        return result;
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

testScraping();
"""

    # Write the Node.js script
    with open("test_brightdata.js", "w") as f:
        f.write(node_script)

    # Run the Node.js script
    env = os.environ.copy()
    env["API_TOKEN"] = API_TOKEN

    try:
        result = subprocess.run(
            ["node", "test_brightdata.js"],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"
        )

        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

    except Exception as e:
        print(f"❌ Error running Node.js test: {e}")


async def check_account_via_cli():
    """Check BrightData account status via CLI"""

    print("\n" + "=" * 70)
    print("🔍 CHECKING ACCOUNT STATUS VIA CLI")
    print("=" * 70)

    env = os.environ.copy()
    env["API_TOKEN"] = API_TOKEN

    commands = [
        ["npx", "@brightdata/mcp", "account", "info"],
        ["npx", "@brightdata/mcp", "zones", "list"],
        ["npx", "@brightdata/mcp", "balance"],
    ]

    for cmd in commands:
        print(f"\n📡 Running: {' '.join(cmd[2:])}")
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org"
            )

            if result.returncode == 0:
                print("✅ Success")
                print(result.stdout[:500])
            else:
                print("❌ Failed")
                print(result.stderr[:500])

        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main execution"""

    print("=" * 70)
    print("🌟 BRIGHTDATA CLI/SDK TEST")
    print("=" * 70)
    print(f"API Token: {API_TOKEN[:20]}...")
    print("=" * 70)

    # Check account status
    await check_account_via_cli()

    # Test CLI scraping
    await test_brightdata_cli()

    # Test Node.js SDK
    await test_brightdata_node()

    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    print("\nIf the tests failed, you need to:")
    print("1. Complete BrightData account setup at https://brightdata.com/")
    print("2. Verify email address")
    print("3. Add payment method (even for free trial)")
    print("4. Wait for account activation")
    print("\nThe MCP server created zones but they need an active account to work.")


if __name__ == "__main__":
    asyncio.run(main())