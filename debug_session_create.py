#!/usr/bin/env python3
"""Debug session creation."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def debug_session_create():
    """Debug session creation."""
    host = "192.168.1.212"
    username = "root"  
    password = "root"
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("1. Check current session...")
        result = await api._execute_command("session")
        print(f"Current session: {result}")
        
        print("\n2. Try to create a new session with logon...")
        try:
            logon_result = await api._execute_command("logon", f"{username},{password}")
            print(f"Logon result: {logon_result}")
        except Exception as e:
            print(f"Logon failed: {e}")
            
        print("\n3. Check session again after logon attempt...")
        result = await api._execute_command("session")
        print(f"Session after logon: {result}")
        
        print("\n4. Try other session-related commands...")
        
        # Try different session/auth commands
        commands_to_try = [
            ("login", f"{username},{password}"),
            ("auth", f"{username},{password}"),
            ("authenticate", f"{username},{password}"),
            ("sessioncreate", ""),
            ("newsession", ""),
        ]
        
        for cmd, param in commands_to_try:
            try:
                print(f"\nTrying {cmd} with param '{param}'...")
                result = await api._execute_command(cmd, param)
                print(f"  Success: {result}")
            except Exception as e:
                print(f"  Failed: {e}")
        
        print("\n5. Maybe session commands work differently...")
        
        # Try to see if there's a web interface login we need
        session = await api._get_session()
        
        try:
            print("Trying web interface login...")
            async with session.post(
                f"http://{host}/cgi-bin/luci",
                data={"username": username, "password": password}
            ) as response:
                text = await response.text()
                print(f"Web login response: {response.status}")
                print(f"Response text: {text[:200]}...")
        except Exception as e:
            print(f"Web login failed: {e}")
        
    except Exception as e:
        print(f"Debug failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(debug_session_create())