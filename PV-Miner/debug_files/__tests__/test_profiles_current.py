#!/usr/bin/env python3
"""Test current profile commands."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def test_current_profiles():
    """Test current profile commands."""
    host = "192.168.1.212"
    
    api = LuxOSAPI(host)
    
    try:
        # Get session
        await api.test_connection()
        await api.login()
        session_id = api._luxos_session_id
        
        print(f"Session ID: {session_id}")
        
        print("\n1. Try to get the current profile '310MHz'...")
        
        try:
            result = await api._execute_command("profileget", "310MHz")
            print(f"310MHz profile: {result}")
        except Exception as e:
            print(f"310MHz profile failed: {e}")
        
        print("\n2. Try other possible profile names based on frequency...")
        
        frequency_profiles = [
            "310",
            "320MHz",  # Current frequency from stats
            "320",
            "300MHz",
            "400MHz",
            "500MHz",
            "600MHz",
            "700MHz",
            "710MHz",  # Default frequency
        ]
        
        available_profiles = ["default"]  # We know this one works
        
        for profile in frequency_profiles:
            try:
                result = await api._execute_command("profileget", profile)
                print(f"\n✅ Profile '{profile}' exists:")
                if "PROFILE" in result:
                    prof_info = result["PROFILE"][0]
                    print(f"   Frequency: {prof_info.get('Frequency')} MHz")
                    print(f"   Hashrate: {prof_info.get('Hashrate')} TH/s")
                    print(f"   Watts: {prof_info.get('Watts')} W")
                    print(f"   Voltage: {prof_info.get('Voltage')} V")
                available_profiles.append(profile)
            except Exception as e:
                print(f"❌ Profile '{profile}': {str(e).split('Last error:')[-1].strip()}")
        
        print(f"\n📋 Available profiles: {available_profiles}")
        
        print(f"\n3. Test profileset with correct format...")
        
        if len(available_profiles) > 1:
            # Try to set a profile on board 0
            test_profile = available_profiles[1] if len(available_profiles) > 1 else "default"
            
            try:
                print(f"Testing profileset: session_id={session_id}, board=0, profile={test_profile}")
                result = await api._execute_command("profileset", f"{session_id},0,{test_profile}")
                print(f"Profileset result: {result}")
            except Exception as e:
                print(f"Profileset failed: {e}")
                
                # Try different formats
                formats_to_try = [
                    f"{session_id},{test_profile},0",  # session,profile,board
                    f"0,{test_profile}",               # board,profile (no session?)
                    f"{test_profile},0",               # profile,board
                ]
                
                for fmt in formats_to_try:
                    try:
                        print(f"Trying format: {fmt}")
                        result = await api._execute_command("profileset", fmt)
                        print(f"SUCCESS with format {fmt}: {result}")
                        break
                    except Exception as e2:
                        print(f"Failed with format {fmt}: {str(e2).split('Last error:')[-1].strip()}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(test_current_profiles())