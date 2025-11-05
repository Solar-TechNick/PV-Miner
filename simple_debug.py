#!/usr/bin/env python3
"""Simple debug script to test miner connectivity without external dependencies."""
import socket
import json
import urllib.request
import urllib.error
import sys


def test_basic_connection(host):
    """Test basic TCP connectivity."""
    print(f"\n1. Testing basic connectivity to {host}...")
    
    # Test common ports
    ports = [80, 443, 4028, 8080]
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"   ✅ Port {port}: Open")
            else:
                print(f"   ❌ Port {port}: Closed")
            sock.close()
        except Exception as e:
            print(f"   ❌ Port {port}: Error - {e}")


def test_http_endpoints(host):
    """Test HTTP endpoints."""
    print(f"\n2. Testing HTTP endpoints on {host}...")
    
    endpoints = [
        "/",
        "/cgi-bin/luci",
        "/cgi-bin/luxcgi", 
        "/cgi-bin/minerApi.cgi",
        "/api/v1/stats",
        "/api/stats",
        "/cgi-bin/get_system_info.cgi",
        "/cgi-bin/minerStatus.cgi"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"http://{host}{endpoint}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PV-Miner-Debug'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                content = response.read().decode('utf-8', errors='ignore')
                
                print(f"   ✅ {endpoint}: HTTP {status} - {len(content)} bytes")
                
                # Check for Antminer/LuxOS indicators
                if any(keyword in content.lower() for keyword in ['antminer', 'luxos', 'bitmain', 'mining']):
                    print(f"      🎯 Mining-related content detected!")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ {endpoint}: HTTP {e.code}")
        except urllib.error.URLError as e:
            print(f"   ❌ {endpoint}: {e.reason}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")


def test_cgminer_api(host):
    """Test CGMiner API on port 4028."""
    print(f"\n3. Testing CGMiner API on {host}:4028...")
    
    commands = ["version", "stats", "summary"]
    
    for cmd in commands:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, 4028))
            
            # Send CGMiner command
            command = json.dumps({"command": cmd, "parameter": ""})
            sock.send(command.encode())
            
            # Receive response
            response = sock.recv(4096).decode('utf-8', errors='ignore')  
            sock.close()
            
            print(f"   ✅ {cmd}: Success - {response[:100]}...")
            
            try:
                data = json.loads(response)
                if 'STATUS' in str(data):
                    print(f"      📊 Valid CGMiner response detected")
            except:
                pass
                
        except socket.timeout:
            print(f"   ⏱️  {cmd}: Timeout")
        except ConnectionRefusedError:
            print(f"   ❌ {cmd}: Connection refused")
        except Exception as e:
            print(f"   ❌ {cmd}: {e}")


def test_authentication(host, username="root", password="root"):
    """Test authentication methods."""
    print(f"\n4. Testing authentication with {username}:{password}...")
    
    # Test JSON-RPC login
    login_payload = json.dumps({
        "id": 1,
        "method": "logon",
        "params": [username, password]
    }).encode()
    
    endpoints = ["/cgi-bin/luci", "/cgi-bin/luxcgi"]
    
    for endpoint in endpoints:
        try:
            url = f"http://{host}{endpoint}"
            req = urllib.request.Request(
                url,
                data=login_payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'PV-Miner-Debug'
                }
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8', errors='ignore')
                print(f"   ✅ {endpoint}: Login response - {content[:100]}...")
                
                if 'session' in content.lower():
                    print(f"      🔑 Session information detected!")
                    
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 simple_debug.py <miner_ip> [username] [password]")
        print("Example: python3 simple_debug.py 192.168.1.212")
        return
    
    host = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "root"
    password = sys.argv[3] if len(sys.argv) > 3 else "root"
    
    print(f"🔍 Debugging connection to {host}")
    print(f"Credentials: {username}:{password}")
    
    test_basic_connection(host)
    test_http_endpoints(host) 
    test_cgminer_api(host)
    test_authentication(host, username, password)
    
    print(f"\n📋 Summary:")
    print(f"If you see ✅ indicators above, those methods are working.")
    print(f"If all tests show ❌, check:")
    print(f"- Is {host} the correct IP address?")
    print(f"- Is the miner powered on and connected to network?")
    print(f"- Are there firewall rules blocking connections?")
    print(f"- Is LuxOS firmware installed and running?")


if __name__ == "__main__":
    main()