"""LuxOS API client for Antminer communication."""
import asyncio
import json
import logging
import socket
from typing import Any, Dict, List, Optional

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
        self._luxos_session_id: Optional[str] = None

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
                                # "Miner is already active" is expected for wakeup commands, not an error
                                if "already active" in error_msg.lower():
                                    _LOGGER.debug(f"TCP API: {error_msg} (expected)")
                                else:
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
                # Check if it's the "already active" error wrapped in an exception
                error_str = str(e)
                if "already active" in error_str.lower():
                    _LOGGER.debug(f"TCP API: {error_str} (expected)")
                else:
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
        # Don't log "already active" as error - it's expected
        if "already active" not in error_msg.lower():
            _LOGGER.error(error_msg)
        else:
            _LOGGER.debug(error_msg + " (expected)")
        raise LuxOSAPIError(error_msg)

    async def _get_luxos_session_id(self) -> Optional[str]:
        """Get or create a LuxOS session ID."""
        try:
            # First check if we have an existing session
            _LOGGER.debug("Checking existing LuxOS session...")
            result = await self._execute_command("session")
            
            if "SESSION" in result and result["SESSION"]:
                session_info = result["SESSION"][0]
                session_id = session_info.get("SessionID", "")
                
                if session_id:
                    self._luxos_session_id = session_id
                    _LOGGER.debug(f"Using existing session ID: {self._luxos_session_id}")
                    return self._luxos_session_id
            
            # No valid session, create a new one via login
            _LOGGER.debug("No valid session found, creating new session...")
            if await self.login():
                return self._luxos_session_id
                
        except Exception as e:
            _LOGGER.error(f"Failed to get LuxOS session ID: {e}")
        return None

    async def _execute_curtail_command(self, action: str) -> Dict[str, Any]:
        """Execute curtail command with proper error handling and session management."""
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Ensure we have a session ID
                if not self._luxos_session_id:
                    await self._get_luxos_session_id()
                
                if not self._luxos_session_id:
                    raise LuxOSAPIError("No LuxOS session ID available for curtail command")
                
                parameter = f"{self._luxos_session_id},{action}"
                result = await self._execute_command("curtail", parameter)
                
                # Check if the command succeeded
                if "STATUS" in result and result["STATUS"]:
                    status_info = result["STATUS"][0]
                    if status_info.get("STATUS") == "S":
                        _LOGGER.info(f"Curtail {action} command successful")
                        return result
                    else:
                        error_msg = status_info.get("Msg", "Unknown curtail error")
                        
                        # Handle specific curtail errors
                        if "Invalid session_id" in error_msg:
                            _LOGGER.warning(f"Session expired, attempting to renew (attempt {attempt + 1})")
                            self._luxos_session_id = None  # Force session renewal
                            continue
                        elif "already active" in error_msg.lower() and action == "wakeup":
                            # Miner is already running - this is expected and OK
                            _LOGGER.debug("Miner is already active (expected)")
                            return result
                        elif "curtail mode is idle or sleep" in error_msg and action == "wakeup":
                            # The miner might already be awake or in transition
                            _LOGGER.info("Miner may already be awake or transitioning")
                            return result
                        elif "curtail mode is idle or sleep" in error_msg and action == "sleep":
                            # The miner might already be in sleep mode
                            _LOGGER.info("Miner may already be in sleep mode")
                            return result
                        else:
                            raise LuxOSAPIError(f"Curtail {action} failed: {error_msg}")
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    break

                # Don't log "already active" as warning - it's expected
                error_str = str(e)
                if "already active" not in error_str.lower():
                    _LOGGER.warning(f"Curtail {action} attempt {attempt + 1} failed: {e}")
                # Clear session ID to force renewal on next attempt
                self._luxos_session_id = None
                
        raise LuxOSAPIError(f"All curtail {action} attempts failed. Last error: {last_error}")

    async def _execute_session_command(self, command: str, parameter: str) -> Dict[str, Any]:
        """Execute command that requires session ID with retry logic."""
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Ensure we have a session ID
                if not self._luxos_session_id:
                    await self._get_luxos_session_id()
                
                if not self._luxos_session_id:
                    raise LuxOSAPIError(f"No LuxOS session ID available for {command} command")
                
                full_parameter = f"{self._luxos_session_id},{parameter}"
                result = await self._execute_command(command, full_parameter)
                
                # Check if the command succeeded
                if "STATUS" in result and result["STATUS"]:
                    status_info = result["STATUS"][0]
                    if status_info.get("STATUS") == "S":
                        _LOGGER.debug(f"{command} command successful")
                        return result
                    else:
                        error_msg = status_info.get("Msg", f"Unknown {command} error")
                        
                        # Handle session expiry
                        if "Invalid session_id" in error_msg:
                            _LOGGER.warning(f"Session expired during {command}, attempting to renew (attempt {attempt + 1})")
                            self._luxos_session_id = None  # Force session renewal
                            continue
                        else:
                            raise LuxOSAPIError(f"{command} failed: {error_msg}")
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    break
                    
                _LOGGER.warning(f"{command} attempt {attempt + 1} failed: {e}")
                # Clear session ID to force renewal on next attempt
                self._luxos_session_id = None
                
        raise LuxOSAPIError(f"All {command} attempts failed. Last error: {last_error}")

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
                        
                        # Get session ID for commands that need it
                        await self._get_luxos_session_id()
                        
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
        """Login to LuxOS and create a session for advanced commands."""
        try:
            _LOGGER.debug(f"Attempting LuxOS login with {self.username}")
            result = await self._execute_command("logon", f"{self.username},{self.password}")
            
            if "SESSION" in result and result["SESSION"]:
                session_info = result["SESSION"][0]
                if "SessionID" in session_info and session_info["SessionID"]:
                    self._luxos_session_id = session_info["SessionID"]
                    _LOGGER.info(f"LuxOS login successful, session ID: {self._luxos_session_id}")
                    return True
                else:
                    _LOGGER.warning("Login succeeded but no session ID received")
                    return False
            
            _LOGGER.error(f"Login failed: {result}")
            return False
            
        except Exception as e:
            _LOGGER.error(f"Login error: {e}")
            return False

    async def get_temps(self) -> Dict[str, Any]:
        """Get temperature information."""
        # LuxOS includes temperature data in stats and devs commands
        return await self.get_stats()

    async def get_available_profiles(self) -> List[str]:
        """Get list of available profiles dynamically from the miner."""
        try:
            # Use the 'profiles' command to get all available profiles with details
            result = await self._execute_command("profiles", "")
            
            if "PROFILES" in result and result["PROFILES"]:
                profiles = []
                for profile_info in result["PROFILES"]:
                    if "Profile Name" in profile_info:
                        profiles.append(profile_info["Profile Name"])
                
                if profiles:
                    _LOGGER.info(f"Found {len(profiles)} dynamic profiles from miner: {profiles}")
                    return profiles
        except Exception as e:
            _LOGGER.warning(f"Dynamic profile discovery failed: {e}")
        
        # Fallback: check only known working profiles for S21+
        available_profiles = []
        known_s21_profiles = ["default", "310MHz"]
        
        for profile_name in known_s21_profiles:
            try:
                result = await self._execute_command("profileget", profile_name)
                if "PROFILE" in result and result["PROFILE"]:
                    available_profiles.append(profile_name)
                    _LOGGER.debug(f"Found fallback profile: {profile_name}")
            except Exception as e:
                _LOGGER.debug(f"Fallback profile {profile_name} check failed: {e}")
        
        # If no profiles found, return default safe list
        if not available_profiles:
            _LOGGER.warning("No profiles detected, using default list for S21+")
            available_profiles = ["default", "310MHz"]
        
        return available_profiles

    async def get_profile_details(self, profile_name: str) -> Dict[str, Any]:
        """Get details for a specific profile."""
        return await self._execute_command("profileget", profile_name)

    async def get_all_profiles_with_details(self) -> Dict[str, Dict[str, Any]]:
        """Get all available profiles with their detailed information."""
        try:
            result = await self._execute_command("profiles", "")
            
            if "PROFILES" in result and result["PROFILES"]:
                profiles_dict = {}
                for profile_info in result["PROFILES"]:
                    if "Profile Name" in profile_info:
                        profile_name = profile_info["Profile Name"]
                        profiles_dict[profile_name] = {
                            "name": profile_name,
                            "frequency": profile_info.get("Frequency", 0),
                            "hashrate": profile_info.get("Hashrate", 0),
                            "watts": profile_info.get("Watts", 0),
                            "voltage": profile_info.get("Voltage", 0),
                            "step": profile_info.get("Step", "0"),
                            "description": f"{profile_info.get('Frequency', 0)}MHz - {profile_info.get('Hashrate', 0)}TH/s - {profile_info.get('Watts', 0)}W"
                        }
                
                _LOGGER.debug(f"Retrieved detailed info for {len(profiles_dict)} profiles")
                return profiles_dict
        except Exception as e:
            _LOGGER.warning(f"Failed to get detailed profile information: {e}")
        
        return {}

    async def set_profile(self, profile_name: str, board: int = None) -> Dict[str, Any]:
        """Set power profile. LuxOS profileset applies to appropriate boards automatically."""
        # LuxOS profileset format: session_id,profile_name (board ID not needed)
        return await self._execute_session_command("profileset", profile_name)

    async def set_frequency(self, freq: int) -> Dict[str, Any]:
        """Set frequency (overclock/underclock)."""
        return await self._execute_command("frequencyset", str(freq))

    async def enable_hashboard(self, board: int) -> Dict[str, Any]:
        """Enable specific hashboard (pauses ATM temporarily)."""
        return await self._hashboard_control_with_atm("enableboard", board)

    async def disable_hashboard(self, board: int) -> Dict[str, Any]:
        """Disable specific hashboard (pauses ATM temporarily)."""
        return await self._hashboard_control_with_atm("disableboard", board)

    async def _hashboard_control_with_atm(self, command: str, board: int) -> Dict[str, Any]:
        """Control hashboard by temporarily pausing ATM."""
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                # Ensure we have a session ID
                if not self._luxos_session_id:
                    await self._get_luxos_session_id()

                if not self._luxos_session_id:
                    raise LuxOSAPIError(f"No LuxOS session ID available for {command}")

                # Step 1: Disable ATM
                _LOGGER.debug(f"Pausing ATM for {command} on board {board}")
                atm_disable = await self._execute_command("atmset", f"{self._luxos_session_id},enabled=false")

                # Check if ATM was disabled successfully
                if "STATUS" in atm_disable and atm_disable["STATUS"]:
                    status = atm_disable["STATUS"][0]
                    if status.get("STATUS") != "S":
                        _LOGGER.warning(f"ATM disable warning: {status.get('Msg')}")

                # Small delay to let ATM stop
                await asyncio.sleep(0.5)

                # Step 2: Execute hashboard command
                _LOGGER.debug(f"Executing {command} for board {board}")
                board_param = f"{self._luxos_session_id},{board}"
                result = await self._execute_command(command, board_param)

                # Check command result
                if "STATUS" in result and result["STATUS"]:
                    status_info = result["STATUS"][0]
                    if status_info.get("STATUS") == "S":
                        _LOGGER.info(f"{command} board {board} successful")
                    else:
                        error_msg = status_info.get("Msg", f"Unknown {command} error")

                        # Handle session expiry
                        if "Invalid session_id" in error_msg:
                            _LOGGER.warning(f"Session expired during {command}, retrying (attempt {attempt + 1})")
                            self._luxos_session_id = None
                            continue
                        else:
                            _LOGGER.error(f"{command} board {board} failed: {error_msg}")
                            # Continue to re-enable ATM even if command failed

                # Step 3: Verify the change took effect before re-enabling ATM
                _LOGGER.debug(f"Verifying {command} for board {board}")
                await asyncio.sleep(1)  # Give the board time to change state

                verification = await self._execute_command("devs", "")
                expected_state = command == "enableboard"  # True for enable, False for disable

                if "DEVS" in verification and len(verification["DEVS"]) > board:
                    board_data = verification["DEVS"][board]
                    actual_enabled = board_data.get("Enabled", "N") == "Y"

                    if actual_enabled != expected_state:
                        _LOGGER.warning(
                            f"Hashboard {board} {command} command succeeded, but board state did not change. "
                            f"Expected Enabled={expected_state}, got Enabled={actual_enabled}. "
                            f"This LuxOS firmware version may not support per-board control. "
                            f"Consider using power profiles instead for solar following."
                        )
                    else:
                        _LOGGER.info(f"Verified: Board {board} is now {'enabled' if expected_state else 'disabled'}")

                # Step 4: Re-enable ATM
                _LOGGER.debug("Re-enabling ATM")
                atm_enable = await self._execute_command("atmset", f"{self._luxos_session_id},enabled=true")

                # Check if ATM was re-enabled
                if "STATUS" in atm_enable and atm_enable["STATUS"]:
                    status = atm_enable["STATUS"][0]
                    if status.get("STATUS") != "S":
                        _LOGGER.warning(f"ATM re-enable warning: {status.get('Msg')}")

                return result

            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    break

                _LOGGER.warning(f"{command} board {board} attempt {attempt + 1} failed: {e}")
                self._luxos_session_id = None

                # Try to re-enable ATM even after error
                try:
                    if self._luxos_session_id:
                        await self._execute_command("atmset", f"{self._luxos_session_id},enabled=true")
                except:
                    pass

        raise LuxOSAPIError(f"All {command} board {board} attempts failed. Last error: {last_error}")

    async def pause_mining(self) -> Dict[str, Any]:
        """Pause mining operations using curtail sleep."""
        return await self._execute_curtail_command("sleep")

    async def resume_mining(self) -> Dict[str, Any]:
        """Resume mining operations using curtail wakeup."""
        return await self._execute_curtail_command("wakeup")

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