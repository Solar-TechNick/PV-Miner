#!/usr/bin/env python3
"""Debug session command."""
import asyncio
import sys
import os

# Add the custom_components path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'pv_miner'))

from luxos_api import LuxOSAPI


async def debug_session():
    """Debug session command."""
    host = "192.168.1.212"
    
    api = LuxOSAPI(host)
    
    try:
        print("Testing session command directly...")
        result = await api._execute_command("session")
        print(f"Session result: {result}")
        
        # Try to extract session ID manually
        if "SESSION" in result and result["SESSION"]:
            session_info = result["SESSION"][0]
            print(f"Session info: {session_info}")
            if "SessionID" in session_info:
                session_id = session_info["SessionID"]
                print(f"Extracted session ID: {session_id}")
                
                # Test hashboard command with this session ID
                print(f"\nTesting enableboard with session ID: {session_id}")
                hashboard_result = await api._execute_command("enableboard", f"{session_id},0")
                print(f"Enableboard result: {hashboard_result}")
        
    except Exception as e:
        print(f"Debug failed: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(debug_session())