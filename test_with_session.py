#!/usr/bin/env python3
"""Test LuxOS commands with the discovered session ID."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_with_session():
    """Test commands with the session ID we found."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    session_id = "xfVSzSvc"  # From previous test
    
    print(f"Testing LuxOS commands with session_id: {session_id}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Verify session is still active...")
        
        try:
            session_result = await api._execute_command("session", "")
            print(f"Current session: {session_result}")
            
            if "SESSION" in session_result:
                current_session = session_result["SESSION"][0]["SessionID"]
                print(f"Current session ID: {current_session}")
                if current_session != session_id:
                    session_id = current_session
                    print(f"Updated session_id to: {session_id}")
        except Exception as e:
            print(f"Session check failed: {e}")
        
        print(f"\n2. Testing hashboard commands with session_id: {session_id}")
        
        # Test hashboard commands with the session
        board_commands = [
            ("enableboard", f"{session_id},0"),
            ("enableboard", f"{session_id},1"), 
            ("enableboard", f"{session_id},2"),
        ]
        
        for cmd, param in board_commands:
            try:
                print(f"\nTesting {cmd} with param '{param}'...")
                result = await api._execute_command(cmd, param)
                
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  SUCCESS: {status.get('STATUS')} - {status.get('Msg')}")
                    print(f"  Full result: {result}")
                else:
                    print(f"  Response: {result}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print(f"\n3. Test disableboard commands (CAREFUL - this will disable hashboards)")
        
        # Test just one disable command to see if it works
        try:
            print(f"\nTesting disableboard for board 0...")
            result = await api._execute_command("disableboard", f"{session_id},0")
            
            if "STATUS" in result:
                status = result["STATUS"][0] if result["STATUS"] else {}
                print(f"  Disable result: {status.get('STATUS')} - {status.get('Msg')}")
                
                # Immediately re-enable it
                print(f"  Re-enabling board 0...")
                enable_result = await api._execute_command("enableboard", f"{session_id},0")
                if "STATUS" in enable_result:
                    enable_status = enable_result["STATUS"][0] if enable_result["STATUS"] else {}
                    print(f"  Re-enable result: {enable_status.get('STATUS')} - {enable_status.get('Msg')}")
                    
        except Exception as e:
            print(f"  ERROR: {e}")
        
        print(f"\n4. Test other session-based commands...")
        
        # Test other commands that might need session
        other_commands = [
            ("profileset", f"{session_id},0"),  # Set profile 0
            ("restart", session_id),            # Restart with session
        ]
        
        for cmd, param in other_commands:
            try:
                print(f"\nTesting {cmd} with param '{param}'...")
                
                # Skip restart for safety
                if cmd == "restart":
                    print("  SKIPPED: restart command for safety")
                    continue
                    
                result = await api._execute_command(cmd, param)
                
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  Result: {status.get('STATUS')} - {status.get('Msg')}")
                else:
                    print(f"  Response: {result}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_with_session())