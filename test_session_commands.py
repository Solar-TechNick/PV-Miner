#!/usr/bin/env python3
"""Test LuxOS commands with different parameter formats."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_session_commands():
    """Test commands with different parameter formats."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing LuxOS command parameter formats on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. First, let's see if there are session-related commands...")
        
        # Try to find session/login related commands
        session_commands = [
            ("login", ""),
            ("logon", ""),
            ("session", ""),
            ("auth", ""),
        ]
        
        for cmd, param in session_commands:
            try:
                print(f"\nTesting {cmd}...")
                result = await api._execute_command(cmd, param)
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  {cmd}: {status.get('STATUS', 'Unknown')} - {status.get('Msg', 'No message')}")
                    if "result" in result:
                        print(f"  Result: {result['result']}")
                else:
                    print(f"  {cmd}: Response: {result}")
            except Exception as e:
                print(f"  {cmd}: ERROR - {e}")
        
        print("\n2. Try hashboard commands with different parameter formats...")
        
        # Different parameter format attempts
        board_id = "0"
        test_formats = [
            f"board_id={board_id}",           # Key-value format
            f"board={board_id}",              # Alternative key
            f"asc={board_id}",                # ASC format (from devs output)
            f"id={board_id}",                 # Simple id
            f"0,{board_id}",                  # Session_id,board_id with dummy session
            f"null,{board_id}",               # Null session
            f",{board_id}",                   # Empty session
            board_id,                         # Just board_id
        ]
        
        for param_format in test_formats:
            try:
                print(f"\nTesting enableboard with param '{param_format}'...")
                result = await api._execute_command("enableboard", param_format)
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  SUCCESS: {status.get('STATUS', 'Unknown')} - {status.get('Msg', 'No message')}")
                    break  # If this works, no need to try other formats
                else:
                    print(f"  Response: {result}")
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print("\n3. Try alternative command names for pause/resume...")
        
        # Alternative command names
        pause_commands = [
            "pause",
            "stop",
            "halt",
            "suspend",
            "pauseall",
            "quit",
        ]
        
        for cmd in pause_commands:
            try:
                print(f"\nTesting {cmd}...")
                result = await api._execute_command(cmd, "")
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  {cmd}: {status.get('STATUS', 'Unknown')} - {status.get('Msg', 'No message')}")
                else:
                    print(f"  {cmd}: Response received")
            except Exception as e:
                print(f"  {cmd}: ERROR - {e}")
        
        print("\n4. Check what commands are actually available...")
        
        # Try to get command list
        try:
            print("Attempting to get help or command list...")
            for help_cmd in ["help", "commands", "list", "api"]:
                try:
                    result = await api._execute_command(help_cmd, "")
                    print(f"  {help_cmd}: Got response!")
                    if "STATUS" in result:
                        status = result["STATUS"][0] if result["STATUS"] else {}
                        print(f"    Status: {status}")
                    break
                except Exception as e:
                    print(f"  {help_cmd}: {e}")
        except Exception as e:
            print(f"Help command test failed: {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_session_commands())