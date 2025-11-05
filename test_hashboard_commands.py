#!/usr/bin/env python3
"""Test LuxOS hashboard control commands."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_hashboard_commands():
    """Test hashboard control commands."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing LuxOS hashboard commands on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Testing connection...")
        connected = await api.test_connection()
        print(f"Connection result: {connected}")
        
        if not connected:
            print("Connection failed, exiting...")
            return
        
        print("\n2. Testing available commands...")
        
        # Test commands that might work without session
        basic_commands = [
            ("version", ""),
            ("stats", ""),
            ("devs", ""),
            ("pools", ""),
            ("summary", ""),
        ]
        
        for cmd, param in basic_commands:
            try:
                print(f"\nTesting {cmd}...")
                result = await api._execute_command(cmd, param)
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  {cmd}: {status.get('STATUS', 'Unknown')} - {status.get('Msg', 'No message')}")
                else:
                    print(f"  {cmd}: Response received (no STATUS section)")
            except Exception as e:
                print(f"  {cmd}: ERROR - {e}")
        
        print("\n3. Testing hashboard commands (these will likely fail without session)...")
        
        # These commands require session_id
        hashboard_commands = [
            ("enableboard", "0"),      # Try board 0 without session
            ("disableboard", "0"),     # Try board 0 without session
            ("pause", ""),             # Try pause without session
            ("resume", ""),            # Try resume without session
        ]
        
        for cmd, param in hashboard_commands:
            try:
                print(f"\nTesting {cmd} with param '{param}'...")
                result = await api._execute_command(cmd, param)
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  {cmd}: {status.get('STATUS', 'Unknown')} - {status.get('Msg', 'No message')}")
                else:
                    print(f"  {cmd}: Response received")
            except Exception as e:
                print(f"  {cmd}: ERROR - {e}")
        
        print("\n4. Let's see what a login/session attempt looks like...")
        
        # Try some session-based approaches
        try:
            # Try to get a session somehow
            print("Attempting to establish session...")
            login_result = await api.login()
            print(f"Login result: {login_result}")
            
        except Exception as e:
            print(f"Login attempt failed: {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_hashboard_commands())