#!/usr/bin/env python3
"""Debug Home Assistant switch issue."""
import asyncio
import sys
import os
import traceback

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def debug_switch_issue():
    """Debug the specific switch turn_off issue."""
    host = "192.168.99.202"
    username = "root"
    password = "root"
    
    print(f"🔍 Debugging Home Assistant switch issue on {host}")
    
    api = LuxOSAPI(host, username, password)
    
    try:
        print("\n1. Testing connection...")
        connected = await api.test_connection()
        print(f"   Connected: {connected}")
        
        if not connected:
            print("❌ Cannot connect to miner!")
            return
            
        print(f"   Session ID: {api._luxos_session_id}")
        
        print("\n2. Testing pause_mining() (switch turn_off)...")
        try:
            result = await api.pause_mining()
            print(f"   ✅ pause_mining() result: {result}")
            
            # Check the result structure
            if "STATUS" in result and result["STATUS"]:
                status = result["STATUS"][0]
                print(f"   Status: {status.get('STATUS')} - {status.get('Msg')}")
                if status.get('STATUS') == 'S':
                    print("   ✅ Command succeeded!")
                else:
                    print(f"   ❌ Command failed: {status.get('Msg')}")
            else:
                print(f"   ⚠️  Unexpected result format: {result}")
                
        except Exception as e:
            print(f"   ❌ pause_mining() failed: {e}")
            print(f"   📋 Full traceback:")
            traceback.print_exc()
            
        print("\n3. Testing resume_mining() (switch turn_on)...")
        try:
            await asyncio.sleep(2)  # Wait a bit
            result = await api.resume_mining()
            print(f"   ✅ resume_mining() result: {result}")
            
            # Check the result structure
            if "STATUS" in result and result["STATUS"]:
                status = result["STATUS"][0]
                print(f"   Status: {status.get('STATUS')} - {status.get('Msg')}")
                if status.get('STATUS') == 'S':
                    print("   ✅ Command succeeded!")
                else:
                    print(f"   ❌ Command failed: {status.get('Msg')}")
            else:
                print(f"   ⚠️  Unexpected result format: {result}")
                
        except Exception as e:
            print(f"   ❌ resume_mining() failed: {e}")
            print(f"   📋 Full traceback:")
            traceback.print_exc()
            
        print("\n4. Testing session renewal...")
        try:
            # Force session renewal
            old_session = api._luxos_session_id
            api._luxos_session_id = None
            print(f"   Cleared session ID (was: {old_session})")
            
            # This should trigger session renewal
            result = await api.pause_mining()
            print(f"   New session ID: {api._luxos_session_id}")
            print(f"   ✅ Session renewal worked: {result['STATUS'][0]['Msg'] if 'STATUS' in result else 'Unknown'}")
            
        except Exception as e:
            print(f"   ❌ Session renewal failed: {e}")
            traceback.print_exc()
        
        print("\n✅ Debug completed!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        traceback.print_exc()
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(debug_switch_issue())