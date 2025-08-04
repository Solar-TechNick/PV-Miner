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

    def __init__(self, host: str, username: str = "root", password: str = "root"):
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

        # Try multiple possible endpoints and methods
        endpoints = [
            # LuxOS endpoints
            (f"http://{self.host}/cgi-bin/luci", "POST"),
            (f"http://{self.host}/cgi-bin/luxcgi", "POST"),
            (f"http://{self.host}/cgi-bin/minerApi.cgi", "POST"),
            # Standard CGMiner endpoints
            (f"http://{self.host}:4028", "TCP"),  # CGMiner API port
            (f"http://{self.host}/api/v1/stats", "GET"),
            (f"http://{self.host}/api/stats", "GET"),
            # Antminer web interface
            (f"http://{self.host}/cgi-bin/get_system_info.cgi", "GET"),
            (f"http://{self.host}/cgi-bin/minerStatus.cgi", "GET"),
        ]
        
        last_error = None
        
        for url, method in endpoints:
            try:
                if method == "POST":
                    async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as response:
                        if response.status == 200:
                            text = await response.text()
                            try:
                                data = json.loads(text)
                                _LOGGER.debug(f"Successful response from {url}: {data}")
                                return data
                            except json.JSONDecodeError:
                                # Some responses might not be JSON
                                _LOGGER.debug(f"Non-JSON response from {url}: {text[:200]}")
                                return {"result": text}
                        elif response.status == 404:
                            _LOGGER.debug(f"Endpoint not found: {url}")
                            continue
                        else:
                            last_error = f"HTTP {response.status} from {url}: {await response.text()}"
                            _LOGGER.debug(last_error)
                            
                elif method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            text = await response.text()
                            try:
                                data = json.loads(text)
                                _LOGGER.debug(f"Successful GET response from {url}")
                                return data
                            except json.JSONDecodeError:
                                _LOGGER.debug(f"Non-JSON GET response from {url}: {text[:200]}")
                                return {"result": text}
                        elif response.status == 404:
                            _LOGGER.debug(f"GET endpoint not found: {url}")
                            continue
                        else:
                            last_error = f"GET HTTP {response.status} from {url}"
                            _LOGGER.debug(last_error)
                            
                elif method == "TCP" and command in ["stats", "summary", "version"]:
                    # Try CGMiner TCP API
                    try:
                        import socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        sock.connect((self.host, 4028))
                        
                        cmd = json.dumps({"command": command, "parameter": ""})
                        sock.send(cmd.encode())
                        
                        response = sock.recv(4096).decode()
                        sock.close()
                        
                        try:
                            data = json.loads(response)
                            _LOGGER.debug(f"Successful TCP response from {self.host}:4028")
                            return data
                        except json.JSONDecodeError:
                            return {"result": response}
                            
                    except Exception as tcp_error:
                        last_error = f"TCP connection failed: {tcp_error}"
                        _LOGGER.debug(last_error)
                        continue
                        
            except aiohttp.ClientError as e:
                last_error = f"Connection error to {url}: {e}"
                _LOGGER.debug(last_error)
                continue
                
        raise LuxOSAPIError(f"No valid API endpoint found. Last error: {last_error}")

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
        # Try CGMiner API first (we know it works)
        try:
            return await self._try_cgminer_tcp("stats")
        except LuxOSAPIError:
            pass
        
        # Fallback to web API
        if not self.session_id:
            await self.login()
        
        return await self._make_request("stats")

    async def get_devs(self) -> Dict[str, Any]:
        """Get device information."""
        # Try CGMiner API first
        try:
            return await self._try_cgminer_tcp("devs")
        except LuxOSAPIError:
            pass
        
        # Fallback to web API
        if not self.session_id:
            await self.login()
        
        return await self._make_request("devs")

    async def get_pools(self) -> Dict[str, Any]:
        """Get mining pool information."""
        # Try CGMiner API first
        try:
            return await self._try_cgminer_tcp("pools")
        except LuxOSAPIError:
            pass
        
        # Fallback to web API
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
            # First try CGMiner API directly using asyncio
            _LOGGER.info(f"Testing CGMiner API connection to {self.host}:4028")
            
            try:
                import asyncio
                import socket
                import json
                
                # Use asyncio for the socket connection
                def _sync_cgminer_test():
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((self.host, 4028))
                        
                        cmd = json.dumps({"command": "version", "parameter": ""})
                        sock.send(cmd.encode())
                        
                        response = sock.recv(4096).decode('utf-8', errors='ignore')
                        sock.close()
                        
                        data = json.loads(response)
                        return "STATUS" in str(data)
                    except Exception:
                        return False
                
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, _sync_cgminer_test)
                
                if result:
                    _LOGGER.info("CGMiner API connection successful")
                    return True
                else:
                    _LOGGER.debug("CGMiner API test failed")
                    
            except Exception as e:
                _LOGGER.debug(f"CGMiner TCP test error: {e}")
            
            # Fallback: Try web-based login
            try:
                if await self.login():
                    _LOGGER.info("Web API login successful")
                    return True
            except Exception as e:
                _LOGGER.debug(f"Web API login failed: {e}")
            
            _LOGGER.error("All connection methods failed")
            return False
            
        except Exception as e:
            _LOGGER.error(f"Connection test error: {e}")
            return False
    
    async def _try_cgminer_tcp(self, command: str) -> Dict[str, Any]:
        """Try CGMiner TCP API directly."""
        import asyncio
        import socket
        
        def _sync_cgminer_call():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                
                # Connect to CGMiner API port
                sock.connect((self.host, 4028))
                
                # Send command
                cmd = json.dumps({"command": command, "parameter": ""})
                sock.send(cmd.encode())
                
                # Receive response
                response = sock.recv(8192).decode('utf-8', errors='ignore')
                sock.close()
                
                # Parse JSON response
                try:
                    data = json.loads(response)
                    return data
                except json.JSONDecodeError:
                    return {"result": response}
                    
            except Exception as e:
                raise LuxOSAPIError(f"CGMiner TCP API failed: {e}")
        
        # Run in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_cgminer_call)
    
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