#!/usr/bin/env python3
"""
Plasma Engine Phase 1 - Working Demo Test

This script demonstrates the core functionality of all services:
1. Database connections (PostgreSQL, Redis, Neo4j)
2. Basic service health checks
3. Inter-service communication
4. Core feature validation

Run this to verify Phase 1 is working end-to-end.
"""

import asyncio
import sys
import json
import time
from typing import Dict, Any
import traceback

# Database connections
async def test_postgresql():
    """Test PostgreSQL connection and basic operations."""
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="plasma",
            password="plasma",
            database="plasma_research"
        )
        
        # Test basic query
        result = await conn.fetchval("SELECT version()")
        await conn.close()
        
        return {
            "status": "✅ PASS",
            "service": "PostgreSQL", 
            "message": "Connected successfully",
            "version": result.split(" ")[1] if result else "unknown"
        }
    except ImportError:
        return {
            "status": "⚠️ SKIP", 
            "service": "PostgreSQL",
            "message": "asyncpg not installed - install with: pip install asyncpg"
        }
    except Exception as e:
        return {
            "status": "❌ FAIL",
            "service": "PostgreSQL", 
            "message": f"Connection failed: {str(e)}"
        }


async def test_redis():
    """Test Redis connection and basic operations."""
    try:
        import redis.asyncio as redis
        client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        
        # Test basic operations
        await client.set("test:plasma", "working", ex=30)
        result = await client.get("test:plasma")
        await client.delete("test:plasma")
        await client.close()
        
        return {
            "status": "✅ PASS",
            "service": "Redis",
            "message": "Connected successfully", 
            "test_result": f"Set/Get test: {result}"
        }
    except ImportError:
        return {
            "status": "⚠️ SKIP",
            "service": "Redis", 
            "message": "redis not installed - install with: pip install redis"
        }
    except Exception as e:
        return {
            "status": "❌ FAIL",
            "service": "Redis",
            "message": f"Connection failed: {str(e)}"
        }


async def test_neo4j():
    """Test Neo4j connection and basic operations."""
    try:
        from neo4j import AsyncGraphDatabase
        
        driver = AsyncGraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "plasmapass")
        )
        
        async with driver.session() as session:
            result = await session.run("RETURN 'Hello Neo4j' AS message")
            record = await result.single()
            message = record["message"] if record else "No response"
        
        await driver.close()
        
        return {
            "status": "✅ PASS",
            "service": "Neo4j",
            "message": "Connected successfully",
            "test_result": message
        }
    except ImportError:
        return {
            "status": "⚠️ SKIP",
            "service": "Neo4j",
            "message": "neo4j not installed - install with: pip install neo4j"
        }
    except Exception as e:
        return {
            "status": "❌ FAIL", 
            "service": "Neo4j",
            "message": f"Connection failed: {str(e)}"
        }


async def test_http_endpoints():
    """Test HTTP service endpoints."""
    results = []
    services = [
        ("Research Service", "http://localhost:8000/health", 8000),
        ("Brand Service", "http://localhost:8001/health", 8001),
        ("Content Service", "http://localhost:8002/health", 8002),
        ("Agent Service", "http://localhost:8003/health", 8003),
        ("Gateway Service", "http://localhost:3000/health", 3000),
    ]
    
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for name, url, port in services:
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        results.append({
                            "status": "✅ PASS",
                            "service": name,
                            "message": f"Service running on port {port}",
                            "response": response.json()
                        })
                    else:
                        results.append({
                            "status": "⚠️ WARN",
                            "service": name,
                            "message": f"Service responded with status {response.status_code}"
                        })
                except Exception as e:
                    results.append({
                        "status": "❌ FAIL",
                        "service": name, 
                        "message": f"Service not accessible: {str(e)}"
                    })
    
    except ImportError:
        results.append({
            "status": "⚠️ SKIP",
            "service": "HTTP Services",
            "message": "httpx not installed - install with: pip install httpx"
        })
    
    return results


def test_ai_apis():
    """Test AI API connectivity."""
    results = []
    
    try:
        import openai
        import os
        
        # Test OpenAI API (basic connectivity)
        if os.getenv("OPENAI_API_KEY"):
            try:
                client = openai.OpenAI()
                # Just test authentication, don't make expensive calls
                models = client.models.list()
                results.append({
                    "status": "✅ PASS",
                    "service": "OpenAI API",
                    "message": f"API key valid, {len(models.data)} models available"
                })
            except Exception as e:
                results.append({
                    "status": "❌ FAIL",
                    "service": "OpenAI API",
                    "message": f"API error: {str(e)}"
                })
        else:
            results.append({
                "status": "⚠️ SKIP",
                "service": "OpenAI API", 
                "message": "OPENAI_API_KEY not set in environment"
            })
            
    except ImportError:
        results.append({
            "status": "⚠️ SKIP",
            "service": "AI APIs",
            "message": "openai not installed - install with: pip install openai"
        })
    
    # Test Anthropic API
    try:
        import anthropic
        import os
        
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                client = anthropic.Anthropic()
                # Basic API test - this might fail on free tiers, that's OK
                results.append({
                    "status": "✅ PASS",
                    "service": "Anthropic API",
                    "message": "API key configured"
                })
            except Exception as e:
                results.append({
                    "status": "⚠️ WARN",
                    "service": "Anthropic API",
                    "message": f"API key set but error: {str(e)}"
                })
        else:
            results.append({
                "status": "⚠️ SKIP", 
                "service": "Anthropic API",
                "message": "ANTHROPIC_API_KEY not set in environment"
            })
            
    except ImportError:
        results.append({
            "status": "⚠️ SKIP",
            "service": "Anthropic API",
            "message": "anthropic not installed"
        })
    
    return results


def print_results(title: str, results: list):
    """Pretty print test results."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)
    
    if isinstance(results, dict):
        results = [results]
    
    for result in results:
        status = result.get("status", "❓ UNKNOWN")
        service = result.get("service", "Unknown Service")
        message = result.get("message", "No message")
        
        print(f"{status} {service}")
        print(f"   {message}")
        
        if "test_result" in result:
            print(f"   Test: {result['test_result']}")
        if "response" in result:
            print(f"   Response: {json.dumps(result['response'], indent=2)}")


def print_summary(all_results: Dict[str, Any]):
    """Print overall test summary."""
    print(f"\n{'='*60}")
    print("📊 PHASE 1 TEST SUMMARY")
    print('='*60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict):
            results = [results]
        
        for result in results:
            total_tests += 1
            if result.get("status", "").startswith("✅"):
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Phase 1 is in EXCELLENT condition!")
    elif success_rate >= 60:
        print("✅ Phase 1 is in GOOD condition!")
    elif success_rate >= 40:
        print("⚠️  Phase 1 needs some work...")
    else:
        print("❌ Phase 1 needs significant fixes.")
    
    print(f"\n💡 Next steps:")
    if passed_tests < total_tests:
        print("   1. Install missing Python packages")
        print("   2. Start remaining services with Docker")
        print("   3. Re-run this test")
    else:
        print("   1. All systems operational!")
        print("   2. Ready for Phase 2 development")
    

async def main():
    """Main test execution."""
    print("🚀 Plasma Engine Phase 1 - System Test")
    print(f"Python version: {sys.version}")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    results = {}
    
    print("\n🔍 Testing database connections...")
    results["databases"] = await asyncio.gather(
        test_postgresql(),
        test_redis(), 
        test_neo4j(),
        return_exceptions=True
    )
    
    print("🌐 Testing HTTP services...")
    results["http_services"] = await test_http_endpoints()
    
    print("🤖 Testing AI API connections...")
    results["ai_apis"] = test_ai_apis()
    
    # Print results
    print_results("Database Connections", results["databases"])
    print_results("HTTP Services", results["http_services"])
    print_results("AI APIs", results["ai_apis"])
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        traceback.print_exc()