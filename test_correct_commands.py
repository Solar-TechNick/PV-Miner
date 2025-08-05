#!/usr/bin/env python3
"""Test the correct LuxOS commands based on official documentation."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_correct_commands():
    """Test the correct LuxOS commands."""
    host = "192.168.1.212"
    username = "root"
    password = "root"
    
    print(f"Testing correct LuxOS commands on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Connect and get session...")
        connected = await api.test_connection()
        print(f"Connected: {connected}")
        print(f"Session ID: {api._luxos_session_id}")
        
        if not api._luxos_session_id:
            print("No session ID - trying to login...")
            login_success = await api.login()
            print(f"Login success: {login_success}")
            print(f"Session ID after login: {api._luxos_session_id}")
        
        session_id = api._luxos_session_id
        if not session_id:
            print("ERROR: No session ID available, cannot test session commands")
            return
            
        print(f"\n2. Test CORRECT pause/resume commands using 'curtail'...")
        
        # Test curtail sleep (pause mining)
        try:
            print(f"Testing curtail sleep (pause)...")
            result = await api._execute_command("curtail", f"{session_id},sleep")
            print(f"Curtail sleep result: {result}")
        except Exception as e:
            print(f"Curtail sleep failed: {e}")
        
        # Wait a moment then wake up
        print("Waiting 3 seconds before wakeup...")
        await asyncio.sleep(3)
        
        try:
            print(f"Testing curtail wakeup (resume)...")
            result = await api._execute_command("curtail", f"{session_id},wakeup")
            print(f"Curtail wakeup result: {result}")
        except Exception as e:
            print(f"Curtail wakeup failed: {e}")
        
        print(f"\n3. Test profile commands...")
        
        # Get available profiles
        try:
            print("Getting available profiles...")
            result = await api._execute_command("profileget", "")
            print(f"Profile get result: {result}")
        except Exception as e:
            print(f"Profile get failed: {e}")
        
        # Test profile setting (this might need session)
        try:
            print(f"Testing profile set...")
            result = await api._execute_command("profileset", f"{session_id},0,0")  # session,board,profile
            print(f"Profile set result: {result}")
        except Exception as e:
            print(f"Profile set failed: {e}")
        
        print(f"\n4. Test other commands that might be useful...")
        
        # Test commands that don't need session
        basic_commands = [
            "limits",      # Get power limits
            "power",       # Get power information  
            "temps",       # Get temperatures
            "fans",        # Get fan information
        ]
        
        for cmd in basic_commands:
            try:
                print(f"\nTesting {cmd}...")
                result = await api._execute_command(cmd, "")
                if "STATUS" in result:
                    status = result["STATUS"][0] if result["STATUS"] else {}
                    print(f"  {cmd}: {status.get('STATUS')} - {status.get('Msg')}")
                else:
                    print(f"  {cmd}: Got response (no STATUS)")
            except Exception as e:
                print(f"  {cmd}: ERROR - {e}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_correct_commands())