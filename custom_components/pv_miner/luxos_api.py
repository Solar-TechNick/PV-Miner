"""LuxOS API client for Antminer communication."""
import asyncio
import json
import logging
import socket
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
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _tcp_command(self, command: str, parameter: str = "") -> Dict[str, Any]:
        """Execute command via TCP API (port 4028) - Official LuxOS method."""
        def _sync_tcp_call():
            try:
                _LOGGER.debug(f"TCP API call to {self.host}:4028 - command: {command}")
                
                # Create TCP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(15)
                
                # Connect to LuxOS TCP API
                sock.connect((self.host, 4028))
                
                # Prepare command in official LuxOS format
                cmd_data = {
                    "command": command,
                    "parameter": parameter
                }
                cmd_json = json.dumps(cmd_data)
                _LOGGER.debug(f"Sending TCP command: {cmd_json}")
                
                # Send command
                sock.send(cmd_json.encode())
                
                # Receive response
                response_data = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    # LuxOS closes connection after response
                    if b'"STATUS"' in response_data and response_data.endswith(b'\x00'):
                        break
                
                sock.close()
                
                # Parse response
                response_str = response_data.decode('utf-8', errors='ignore').rstrip('\x00')
                _LOGGER.debug(f"TCP API response: {response_str[:500]}...")
                
                if not response_str:
                    raise LuxOSAPIError("Empty response from TCP API")
                
                try:
                    data = json.loads(response_str)
                    
                    # Validate response according to LuxOS docs
                    if "STATUS" in data:
                        status_list = data["STATUS"]
                        if status_list and isinstance(status_list, list):
                            status = status_list[0]
                            if status.get("STATUS") == "S":
                                _LOGGER.debug(f"TCP API success: {status.get('Msg', 'No message')}")
                                return data
                            else:
                                error_msg = status.get("Msg", "Unknown error")
                                _LOGGER.error(f"TCP API error: {error_msg}")
                                raise LuxOSAPIError(f"LuxOS API error: {error_msg}")
                    
                    # Some commands might not have STATUS section
                    return data
                    
                except json.JSONDecodeError as e:
                    _LOGGER.error(f"TCP API JSON decode error: {e}, response: {response_str[:200]}")
                    raise LuxOSAPIError(f"Invalid JSON response: {e}")
                    
            except socket.timeout:
                _LOGGER.error(f"TCP API timeout connecting to {self.host}:4028")
                raise LuxOSAPIError("TCP connection timeout")
            except socket.gaierror as e:
                _LOGGER.error(f"TCP API DNS error: {e}")
                raise LuxOSAPIError(f"DNS resolution failed: {e}")
            except ConnectionRefusedError:
                _LOGGER.error(f"TCP API connection refused to {self.host}:4028")
                raise LuxOSAPIError("Connection refused - check if miner is running LuxOS")
            except Exception as e:
                _LOGGER.error(f"TCP API unexpected error: {e}")
                raise LuxOSAPIError(f"TCP connection failed: {e}")
        
        # Run TCP call in thread pool to avoid blocking HA event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_tcp_call)

    async def _http_command(self, command: str, parameter: str = "") -> Dict[str, Any]:
        """Execute command via HTTP API (port 8080) - LuxOS HTTP layer."""
        session = await self._get_session()
        
        payload = {
            "command": command,
            "parameter": parameter
        }
        
        try:
            _LOGGER.debug(f"HTTP API call to {self.host}:8080/api - command: {command}")
            async with session.post(
                f"http://{self.host}:8080/api",
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    _LOGGER.debug(f"HTTP API response: {text[:500]}...")
                    
                    try:
                        data = json.loads(text)
                        
                        # Validate LuxOS response
                        if "STATUS" in data:
                            status_list = data["STATUS"]
                            if status_list and isinstance(status_list, list):
                                status = status_list[0]
                                if status.get("STATUS") == "S":
                                    return data
                                else:
                                    error_msg = status.get("Msg", "Unknown error")
                                    raise LuxOSAPIError(f"HTTP API error: {error_msg}")
                        
                        return data
                        
                    except json.JSONDecodeError as e:
                        _LOGGER.error(f"HTTP API JSON decode error: {e}")
                        raise LuxOSAPIError(f"Invalid JSON response: {e}")
                else:
                    error_text = await response.text()
                    _LOGGER.error(f"HTTP API error {response.status}: {error_text}")
                    raise LuxOSAPIError(f"HTTP {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            _LOGGER.error(f"HTTP API client error: {e}")
            raise LuxOSAPIError(f"HTTP client error: {e}")

    async def _execute_command(self, command: str, parameter: str = "") -> Dict[str, Any]:
        """Execute command using the best available method."""
        last_error = None
        
        # Method 1: TCP API (port 4028) - Official LuxOS recommended method
        try:
            return await self._tcp_command(command, parameter)
        except LuxOSAPIError as e:
            last_error = f"TCP API failed: {e}"
            _LOGGER.debug(last_error)
        
        # Method 2: HTTP API (port 8080) - LuxOS HTTP layer fallback
        try:
            return await self._http_command(command, parameter)
        except LuxOSAPIError as e:
            last_error = f"HTTP API failed: {e}"
            _LOGGER.debug(last_error)
        
        # All methods failed
        error_msg = f"All API methods failed. Last error: {last_error}"
        _LOGGER.error(error_msg)
        raise LuxOSAPIError(error_msg)

    async def test_connection(self) -> bool:
        """Test if the miner is reachable."""
        try:
            _LOGGER.info(f"Testing connection to LuxOS miner at {self.host}")
            result = await self._execute_command("version")
            
            # Check if we got valid version info
            if "STATUS" in result:
                status_list = result["STATUS"]
                if status_list and isinstance(status_list, list):
                    status = status_list[0]
                    if status.get("STATUS") == "S":
                        _LOGGER.info(f"Connection successful: {status.get('Description', 'LuxOS miner')}")
                        return True
            
            _LOGGER.warning("Connection test returned unexpected format")
            return False
            
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get miner statistics."""
        return await self._execute_command("stats")

    async def get_devs(self) -> Dict[str, Any]:
        """Get device information."""
        return await self._execute_command("devs")

    async def get_pools(self) -> Dict[str, Any]:
        """Get mining pool information."""
        return await self._execute_command("pools")

    async def get_summary(self) -> Dict[str, Any]:
        """Get miner summary."""
        return await self._execute_command("summary")

    async def get_version(self) -> Dict[str, Any]:
        """Get version information."""
        return await self._execute_command("version")

    # Authentication-based methods (for web interface access)
    async def login(self) -> bool:
        """Login to the miner web interface (not needed for API calls)."""
        # Note: API calls don't require authentication according to LuxOS docs
        # This is only for web interface access if needed
        _LOGGER.debug("Login not required for LuxOS API calls")
        return True

    async def get_temps(self) -> Dict[str, Any]:
        """Get temperature information."""
        # LuxOS includes temperature data in stats and devs commands
        return await self.get_stats()

    async def set_profile(self, profile: int) -> Dict[str, Any]:
        """Set power profile."""
        return await self._execute_command("profileset", str(profile))

    async def set_frequency(self, freq: int) -> Dict[str, Any]:
        """Set frequency (overclock/underclock)."""
        return await self._execute_command("frequencyset", str(freq))

    async def enable_hashboard(self, board: int) -> Dict[str, Any]:
        """Enable specific hashboard."""
        return await self._execute_command("enableboard", str(board))

    async def disable_hashboard(self, board: int) -> Dict[str, Any]:
        """Disable specific hashboard."""
        return await self._execute_command("disableboard", str(board))

    async def pause_mining(self) -> Dict[str, Any]:
        """Pause mining operations."""
        return await self._execute_command("pause")

    async def resume_mining(self) -> Dict[str, Any]:
        """Resume mining operations."""
        return await self._execute_command("resume")

    async def restart_miner(self) -> Dict[str, Any]:
        """Restart the miner."""
        return await self._execute_command("restart")

    async def add_pool(self, url: str, user: str, password: str = "x", priority: int = 0) -> Dict[str, Any]:
        """Add a mining pool."""
        params = f"{url},{user},{password},{priority}"
        return await self._execute_command("addpool", params)

    async def switch_pool(self, pool_id: int) -> Dict[str, Any]:
        """Switch to a different mining pool."""
        return await self._execute_command("switchpool", str(pool_id))

    async def get_preset_profiles(self) -> Dict[str, Any]:
        """Get available preset profiles."""
        return await self._execute_command("profilelist")