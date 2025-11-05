#!/usr/bin/env python3
"""Test LuxOS session workflow."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_session_workflow():
    """Test complete session workflow."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing LuxOS session workflow on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Get session information...")
        
        try:
            session_result = await api._execute_command("session", "")
            print(f"Session info: {session_result}")
            
            if "STATUS" in session_result:
                status = session_result["STATUS"][0] if session_result["STATUS"] else {}
                print(f"Session status: {status}")
                
        except Exception as e:
            print(f"Session query failed: {e}")
        
        print("\n2. Try logon command...")
        
        try:
            # Try logon with username/password
            logon_result = await api._execute_command("logon", f"{username},{password}")
            print(f"Logon result: {logon_result}")
            
            if "STATUS" in logon_result:
                status = logon_result["STATUS"][0] if logon_result["STATUS"] else {}
                print(f"Logon status: {status}")
                
                # Look for session_id in the response
                if "result" in logon_result:
                    print(f"Logon result data: {logon_result['result']}")
                    
        except Exception as e:
            print(f"Logon failed: {e}")
        
        print("\n3. Try logon with different formats...")
        
        logon_formats = [
            f"{username},{password}",
            f"user={username},pwd={password}",
            username,
            "",
        ]
        
        session_id = None
        
        for logon_format in logon_formats:
            try:
                print(f"\nTrying logon format: '{logon_format}'")
                result = await api._execute_command("logon", logon_format)
                
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  Status: {status.get('STATUS')} - {status.get('Msg')}")
                    
                    # Try to extract session_id from various places
                    if "result" in result and result["result"]:
                        print(f"  Result: {result['result']}")
                        if isinstance(result["result"], str):
                            session_id = result["result"]
                        elif isinstance(result["result"], dict) and "session_id" in result["result"]:
                            session_id = result["result"]["session_id"]
                            
                    # Also check if there are other fields that might contain session_id
                    for key, value in result.items():
                        if "session" in str(key).lower() or "id" in str(key).lower():
                            print(f"  Found potential session field: {key} = {value}")
                            if not session_id and isinstance(value, str):
                                session_id = value
                                
                    if session_id:
                        print(f"  Extracted session_id: {session_id}")
                        break
                        
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print(f"\n4. Testing hashboard commands with session_id: {session_id}")
        
        if session_id:
            # Test hashboard commands with the session
            board_commands = [
                ("enableboard", f"{session_id},0"),
                ("disableboard", f"{session_id},0"),
                ("enableboard", f"{session_id},1"),
                ("disableboard", f"{session_id},1"),
            ]
            
            for cmd, param in board_commands:
                try:
                    print(f"\nTesting {cmd} with param '{param}'...")
                    result = await api._execute_command(cmd, param)
                    
                    if "STATUS" in result:
                        status = result["STATUS"][0] if result["STATUS"] else {}
                        print(f"  SUCCESS: {status.get('STATUS')} - {status.get('Msg')}")
                    else:
                        print(f"  Response: {result}")
                        
                except Exception as e:
                    print(f"  ERROR: {e}")
        else:
            print("No session_id found, cannot test hashboard commands")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_session_workflow())