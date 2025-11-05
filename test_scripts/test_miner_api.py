#!/usr/bin/env python3
"""Test LuxOS API hashboard control capabilities"""

import json
import socket
import http.client
from base64 import b64encode

MINER_IP = "192.168.1.210"
USERNAME = "admin"
PASSWORD = "admin"

def test_http_api(endpoint):
    """Test HTTP API endpoint"""
    try:
        # Create basic auth header
        credentials = b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}

        conn = http.client.HTTPConnection(MINER_IP, 8080, timeout=5)
        conn.request("GET", endpoint, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()

        print(f"\n{'='*60}")
        print(f"HTTP API: {endpoint}")
        print(f"Status: {response.status}")
        print(f"{'='*60}")

        if response.status == 200:
            try:
                parsed = json.loads(data)
                print(json.dumps(parsed, indent=2)[:1000])
            except:
                print(data[:1000])
        else:
            print(f"Error: {data[:500]}")

        return response.status == 200
    except Exception as e:
        print(f"HTTP API Error ({endpoint}): {e}")
        return False

def send_cgminer_command(command, parameter=""):
    """Send command to CGMiner API (port 4028)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((MINER_IP, 4028))

        # Build command
        if parameter:
            cmd = {"command": command, "parameter": parameter}
        else:
            cmd = {"command": command}

        request = json.dumps(cmd)
        sock.sendall(request.encode())

        # Receive response
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b'\x00' in chunk:  # Null terminator
                break

        sock.close()

        # Parse response
        response_str = response.decode('utf-8', errors='ignore').rstrip('\x00')

        print(f"\n{'='*60}")
        print(f"CGMiner Command: {command} {parameter}")
        print(f"{'='*60}")

        try:
            parsed = json.loads(response_str)
            print(json.dumps(parsed, indent=2)[:2000])
            return parsed
        except:
            print(response_str[:1000])
            return None

    except Exception as e:
        print(f"CGMiner Error ({command}): {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("LUXOS MINER API TEST")
    print(f"Miner IP: {MINER_IP}")
    print("="*60)

    # Test HTTP API endpoints
    print("\n\n### TESTING HTTP API ###")
    test_http_api("/api/v1/status")
    test_http_api("/api/v1/hashboards")

    # Test CGMiner API commands
    print("\n\n### TESTING CGMINER API ###")

    # Get basic stats
    send_cgminer_command("stats")

    # Get device info
    send_cgminer_command("devs")

    # Check if ATM is running
    send_cgminer_command("atmset")

    # Try to get hashboard info
    send_cgminer_command("asccount")
    send_cgminer_command("asc", "0")

    print("\n\n### HASHBOARD CONTROL TESTS ###")

    # Try disableboard command
    print("\nAttempting to disable board 2...")
    result = send_cgminer_command("disableboard", "2")

    if result:
        print("\n✓ Disableboard command sent successfully!")
        print("Checking result...")
        send_cgminer_command("devs")
    else:
        print("\n✗ Disableboard command failed")

    print("\n" + "="*60)
    print("API Test Complete")
    print("="*60)
