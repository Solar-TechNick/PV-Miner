"""LuxOS API client for Antminer communication."""
import asyncio
import json
import logging
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)


class LuxOSAPIError(Exception):
    """Exception raised for LuxOS API errors."""


class LuxOSAPI:
    """Client for communicating with LuxOS API."""

    def __init__(self, host: str, username: str = "root", password: str = "rootz"):
        """Initialize the API client."""
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.session_id: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(self, command: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the LuxOS API."""
        session = await self._get_session()
        
        # LuxOS uses JSON-RPC format
        payload = {
            "id": 1,
            "method": command,
            "params": []
        }
        
        if params:
            # Convert params dict to list format for JSON-RPC
            if command == "logon":
                payload["params"] = [params.get("user", ""), params.get("pwd", "")]
            else:
                payload["params"] = list(params.values()) if params else []

        # Try multiple possible endpoints
        endpoints = [
            f"http://{self.host}/cgi-bin/luci",
            f"http://{self.host}/cgi-bin/luxcgi",
            f"http://{self.host}/cgi-bin/minerApi.cgi"
        ]
        
        for url in endpoints:
            try:
                async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            return data
                        except json.JSONDecodeError:
                            # Some responses might not be JSON
                            return {"result": text}
                    elif response.status == 404:
                        # Try next endpoint
                        continue
                    else:
                        raise LuxOSAPIError(f"HTTP {response.status}: {await response.text()}")
                        
            except aiohttp.ClientError as e:
                # Try next endpoint
                if url == endpoints[-1]:  # Last endpoint
                    raise LuxOSAPIError(f"Connection error: {e}")
                continue
                
        raise LuxOSAPIError("No valid API endpoint found")

    async def login(self) -> bool:
        """Login to the miner and get session ID."""
        try:
            response = await self._make_request("logon", {
                "user": self.username,
                "pwd": self.password
            })
            
            # Handle different response formats
            if isinstance(response, dict):
                # JSON-RPC response format
                if "result" in response and response["result"]:
                    result = response["result"]
                    if isinstance(result, dict) and "session_id" in result:
                        self.session_id = result["session_id"]
                        return True
                    elif isinstance(result, str) and "session" in result.lower():
                        # Some LuxOS versions return session ID as string
                        self.session_id = result
                        return True
                
                # Direct response format
                if "session_id" in response:
                    self.session_id = response["session_id"]
                    return True
                
                # Check for successful login without explicit session ID
                if response.get("STATUS") == "S" or response.get("status") == "OK":
                    self.session_id = "authenticated"
                    return True
            
            _LOGGER.error("Login failed: %s", response)
            return False
                
        except LuxOSAPIError as e:
            _LOGGER.error("Login error: %s", e)
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get miner statistics."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("stats")

    async def get_devs(self) -> Dict[str, Any]:
        """Get device information."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("devs")

    async def get_pools(self) -> Dict[str, Any]:
        """Get mining pool information."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("pools")

    async def get_temps(self) -> Dict[str, Any]:
        """Get temperature information."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("temps")

    async def set_profile(self, profile: int) -> Dict[str, Any]:
        """Set power profile."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("profileset", {"profile": profile})

    async def set_frequency(self, freq: int) -> Dict[str, Any]:
        """Set frequency (overclock/underclock)."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("frequencyset", {"freq": freq})

    async def enable_hashboard(self, board: int) -> Dict[str, Any]:
        """Enable specific hashboard."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("enableboard", {"board": board})

    async def disable_hashboard(self, board: int) -> Dict[str, Any]:
        """Disable specific hashboard."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("disableboard", {"board": board})

    async def pause_mining(self) -> Dict[str, Any]:
        """Pause mining operations."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("pause")

    async def resume_mining(self) -> Dict[str, Any]:
        """Resume mining operations."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("resume")

    async def restart_miner(self) -> Dict[str, Any]:
        """Restart the miner."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("restart")

    async def add_pool(self, url: str, user: str, password: str = "x", priority: int = 0) -> Dict[str, Any]:
        """Add a mining pool."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("addpool", {
            "url": url,
            "user": user,
            "pwd": password,
            "priority": priority
        })

    async def switch_pool(self, pool_id: int) -> Dict[str, Any]:
        """Switch to a different mining pool."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("switchpool", {"id": pool_id})

    async def get_preset_profiles(self) -> Dict[str, Any]:
        """Get available preset profiles."""
        if not self.session_id:
            await self.login()
        
        return await self._make_request("profilelist")

    async def test_connection(self) -> bool:
        """Test if the miner is reachable."""
        try:
            # First try login
            if await self.login():
                # Try to get stats to confirm connection
                try:
                    await self.get_stats()
                    return True
                except LuxOSAPIError:
                    # Login worked but stats failed, still consider it connected
                    return True
            
            # If login fails, try basic CGMiner commands without authentication
            try:
                response = await self._make_request("version")
                if response and (isinstance(response, dict) or isinstance(response, str)):
                    return True
            except LuxOSAPIError:
                pass
                
            return False
        except LuxOSAPIError:
            return False
    
    async def _try_cgminer_command(self, command: str) -> Dict[str, Any]:
        """Try a standard CGMiner command without authentication."""
        session = await self._get_session()
        
        # Try CGMiner API format (simple JSON)
        payload = {"command": command}
        
        try:
            async with session.post(f"http://{self.host}/cgi-bin/minerApi.cgi", json=payload) as response:
                if response.status == 200:
                    text = await response.text()
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"result": text}
        except aiohttp.ClientError:
            pass
            
        # Try simple GET request for basic info
        try:
            async with session.get(f"http://{self.host}/") as response:
                if response.status == 200:
                    return {"status": "reachable"}
        except aiohttp.ClientError:
            pass
            
        raise LuxOSAPIError("No valid connection method found")