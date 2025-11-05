#!/usr/bin/env python3
"""Debug script to test LuxOS API connection."""
import asyncio
import aiohttp
import json
import sys


async def test_miner_connection(host: str, username: str = "root", password: str = "root"):
    """Test various connection methods to the miner."""
    print(f"Testing connection to miner at {host}...")
    
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Test 1: Basic HTTP connectivity
        print("\n1. Testing basic HTTP connectivity...")
        try:
            async with session.get(f"http://{host}/") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"   Response length: {len(text)} bytes")
                    if "antminer" in text.lower() or "luxos" in text.lower():
                        print("   ✅ Detected Antminer/LuxOS web interface")
                    else:
                        print("   ⚠️  Unknown web interface")
                else:
                    print(f"   ❌ HTTP error: {response.status}")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
        
        # Test 2: Try different API endpoints
        endpoints = [
            "/cgi-bin/luci",
            "/cgi-bin/luxcgi", 
            "/cgi-bin/minerApi.cgi",
            "/api/v1/stats",
            "/api/stats"
        ]
        
        print("\n2. Testing API endpoints...")
        for endpoint in endpoints:
            url = f"http://{host}{endpoint}"
            try:
                # Try JSON-RPC login
                payload = {
                    "id": 1,
                    "method": "logon",  
                    "params": [username, password]
                }
                
                async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as response:
                    print(f"   {endpoint}: Status {response.status}")
                    if response.status == 200:
                        text = await response.text()
                        print(f"     Response: {text[:200]}...")
                        try:
                            data = json.loads(text)
                            print(f"     ✅ Valid JSON response")
                            if "session_id" in str(data):
                                print(f"     ✅ Session ID found!")
                        except json.JSONDecodeError:
                            print(f"     ⚠️  Non-JSON response")
                    elif response.status == 404:
                        print(f"     ❌ Endpoint not found")
                    else:
                        print(f"     ❌ HTTP error: {response.status}")
                        
            except Exception as e:
                print(f"   {endpoint}: ❌ {e}")
        
        # Test 3: Try CGMiner commands
        print("\n3. Testing CGMiner API commands...")
        cgminer_commands = ["version", "stats", "summary"]
        
        for cmd in cgminer_commands:
            try:
                payload = {"command": cmd}
                async with session.post(f"http://{host}/cgi-bin/minerApi.cgi", json=payload) as response:
                    if response.status == 200:
                        text = await response.text()
                        print(f"   {cmd}: ✅ Success - {text[:100]}...")
                    else:
                        print(f"   {cmd}: ❌ Status {response.status}")
            except Exception as e:
                print(f"   {cmd}: ❌ {e}")
        
        # Test 4: Test different authentication methods
        print("\n4. Testing authentication methods...")
        auth_methods = [
            {"method": "logon", "params": [username, password]},
            {"cmd": "logon", "user": username, "pwd": password},
            {"command": "login", "username": username, "password": password}
        ]
        
        for i, auth in enumerate(auth_methods, 1):
            try:
                payload = {"id": 1, **auth}
                async with session.post(f"http://{host}/cgi-bin/luci", json=payload) as response:
                    if response.status == 200:
                        text = await response.text()
                        print(f"   Method {i}: ✅ Success - {text[:100]}...")
                    else:
                        print(f"   Method {i}: ❌ Status {response.status}")
            except Exception as e:
                print(f"   Method {i}: ❌ {e}")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python debug_connection.py <miner_ip> [username] [password]")
        print("Example: python debug_connection.py 192.168.1.212")
        return
    
    host = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "root"
    password = sys.argv[3] if len(sys.argv) > 3 else "root"
    
    await test_miner_connection(host, username, password)


if __name__ == "__main__":
    asyncio.run(main())