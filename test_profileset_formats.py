#!/usr/bin/env python3
"""Test different profileset parameter formats."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_profileset_formats():
    """Test different profileset parameter formats."""
    host = "192.168.1.212"
    
    api = LuxOSAPI(host)
    
    try:
        # Get session
        await api.test_connection()
        await api.login()
        session_id = api._luxos_session_id
        
        print(f"Session ID: {session_id}")
        
        print("\n1. Testing different profileset parameter formats...")
        
        profile_name = "310MHz"  # Use existing profile
        
        # Try many different parameter formats
        formats_to_try = [
            # Basic formats
            f"{profile_name}",                        # Just profile name
            f"0,{profile_name}",                      # board,profile
            f"{profile_name},0",                      # profile,board
            
            # With session formats  
            f"{session_id},{profile_name}",           # session,profile
            f"{session_id},0,{profile_name}",         # session,board,profile
            f"{session_id},{profile_name},0",         # session,profile,board
            
            # Alternative board identifiers
            f"{session_id},board0,{profile_name}",    # session,board0,profile
            f"{session_id},asc0,{profile_name}",      # session,asc0,profile
            f"{session_id},all,{profile_name}",       # session,all,profile
            
            # Different board numbering
            f"{session_id},1,{profile_name}",         # session,board1,profile (1-indexed?)
            
            # Quoted formats
            f'{session_id},"0","{profile_name}"',     # quoted parameters
            
            # JSON-like format
            f'{{"session":"{session_id}","board":0,"profile":"{profile_name}"}}',
        ]
        
        for i, fmt in enumerate(formats_to_try):
            try:
                print(f"\n{i+1:2d}. Testing format: '{fmt}'")
                result = await api._execute_command("profileset", fmt)
                print(f"    ✅ SUCCESS: {result}")
                # If we get here, this format worked!
                break
            except Exception as e:
                error_msg = str(e).split('Last error:')[-1].strip() if 'Last error:' in str(e) else str(e)
                print(f"    ❌ Failed: {error_msg}")
        
        print("\n2. Let's also check what format devs uses for board identification...")
        
        try:
            devs_result = await api._execute_command("devs", "")
            if "DEVS" in devs_result:
                print("Device board information:")
                for dev in devs_result["DEVS"]:
                    print(f"  ASC: {dev.get('ASC')}, ID: {dev.get('ID')}, Board: {dev.get('Board', 'N/A')}")
        except Exception as e:
            print(f"Devs check failed: {e}")
            
        print("\n3. Maybe profileset works differently - let's try without board ID...")
        
        try:
            print(f"Testing profileset without board: '{session_id},{profile_name}'")
            result = await api._execute_command("profileset", f"{session_id},{profile_name}")
            print(f"✅ SUCCESS without board: {result}")
        except Exception as e:
            error_msg = str(e).split('Last error:')[-1].strip() if 'Last error:' in str(e) else str(e)
            print(f"❌ Failed without board: {error_msg}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_profileset_formats())