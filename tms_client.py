import os
import socket
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tms_client")


class TMSConnectionError(Exception):
    pass


class TMSProtocolError(Exception):
    pass


class TMSClient:

    def __init__(self, host: str = None, port: int = None, token: str = None, timeout: float = 6.0):
        self.host = host or os.environ.get("TMS_HOST", "tramway.proxy.rlwy.net")
        self.port = port or int(os.environ.get("TMS_PORT", 17159))
        self.token = token or os.environ.get("TMS_TOKEN", "")
        self.timeout = timeout

    def send_and_receive(self, command: str, recv_time: float = 2.0, max_bytes: int = 8192) -> bytes:
        payload = f"{command}\r\n".encode()

        try:
            sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        except socket.timeout as e:
            raise TMSConnectionError(f"Connection timeout to {self.host}:{self.port}") from e
        except Exception as e:
            raise TMSConnectionError(f"Connection failed: {e}") from e

        sock.settimeout(self.timeout)

        try:
            sock.sendall(payload)
        except Exception as e:
            sock.close()
            raise TMSConnectionError(f"Send failed: {e}") from e

        chunks = []
        deadline = time.time() + recv_time
        sock.settimeout(0.5)

        while time.time() < deadline:
            try:
                chunk = sock.recv(max_bytes)
                if not chunk:
                    break
                chunks.append(chunk)
            except socket.timeout:
                continue
            except Exception as e:
                sock.close()
                raise TMSConnectionError(f"Receive failed: {e}") from e

        sock.close()
        result = b"".join(chunks)
        return result

    def debug_echo(self) -> str:
        cmd = f"CMD:DEBUG_ECHO|AUTH:{self.token}"
        response = self.send_and_receive(cmd)
        return response.decode('utf-8', errors='replace').strip()

    def _redact(self, cmd: str) -> str:
        return cmd.replace(self.token, "***") if self.token else cmd

    def _query_raw(self, cmd: str, retries: int = 3):
        """Send a LOAD_QUERY command with retries. Returns a list of parsed
        loads on success, or {"error": ...} if every attempt faulted
        (timeout, malformed, or partial response -- see TMS fault injection)."""
        last_fault = None
        safe_cmd = self._redact(cmd)
        for attempt in range(1, retries + 1):
            response = self.send_and_receive(cmd)
            raw = response.decode('utf-8', errors='replace').strip()
            logger.info(f"LOAD_QUERY attempt={attempt}/{retries} cmd=\"{safe_cmd}\" response=\"{raw[:200]}\"")

            if not raw:
                last_fault = "TIMEOUT|MSG:No response from TMS (fault injection)"
                continue
            if raw.startswith("ERR|CODE:MALFORMED"):
                last_fault = raw
                continue
            if "END" not in raw and not raw.startswith("ERR"):
                last_fault = f"PARTIAL|MSG:Response missing END terminator: {raw[:100]}"
                continue
            if raw.startswith("ERR"):
                logger.warning(f"LOAD_QUERY error cmd=\"{safe_cmd}\" error=\"{raw}\"")
                return {"error": raw}

            loads = []
            for line in raw.split('\n'):
                line = line.strip()
                if line == "END":
                    break
                if line and ":" in line:
                    load = self.parse_load_details(line)
                    if load:
                        loads.append(load)
            logger.info(f"LOAD_QUERY success cmd=\"{safe_cmd}\" loads_returned={len(loads)}")
            return loads

        logger.error(f"LOAD_QUERY exhausted retries cmd=\"{safe_cmd}\" last_fault=\"{last_fault}\"")
        return {"error": f"ERR|CODE:FAULT_RETRY_EXHAUSTED|MSG:{last_fault}"}

    def load_query(self, origin: str = None, destination: str = None, equipment: str = None,
                    max_results: int = 10, retries: int = 3, broaden_on_fault: bool = True) -> list:
        cmd = f"CMD:LOAD_QUERY|AUTH:{self.token}"
        if origin:
            cmd += f"|ORIG_STATE:{origin}"
        if destination:
            cmd += f"|DEST_STATE:{destination}"
        if equipment:
            cmd += f"|EQTYPE:{equipment}"
        cmd += f"|MAX_RESULTS:{max_results}"

        result = self._query_raw(cmd, retries=retries)
        if not (isinstance(result, dict) and "error" in result):
            return result
        if not broaden_on_fault:
            return result

        # The exact filtered query faulted on every retry. Rather than giving
        # up, drop down to a single broad filter (whichever we have) with a
        # higher result cap, fetch what we can, and filter server-side so we
        # still return live/fresh loads instead of stale or empty data.
        broad_field, broad_value = None, None
        if equipment:
            broad_field, broad_value = "EQTYPE", equipment
        elif origin:
            broad_field, broad_value = "ORIG_STATE", origin
        elif destination:
            broad_field, broad_value = "DEST_STATE", destination
        else:
            return result

        broad_cmd = f"CMD:LOAD_QUERY|AUTH:{self.token}|{broad_field}:{broad_value}|MAX_RESULTS:50"
        broad_result = self._query_raw(broad_cmd, retries=retries)
        if isinstance(broad_result, dict) and "error" in broad_result:
            return result  # broad attempt faulted too; surface the original fault

        def matches(load):
            if origin and load.get("ORIG_STATE", "").strip() != origin:
                return False
            if destination and load.get("DEST_STATE", "").strip() != destination:
                return False
            if equipment and load.get("EQTYPE", "").strip() != equipment:
                return False
            return True

        return [l for l in broad_result if matches(l)]

    def load_get(self, load_id: str, retries: int = 3) -> str:
        cmd = f"CMD:LOAD_GET|AUTH:{self.token}|LOAD_ID:{load_id}"
        safe_cmd = self._redact(cmd)

        for attempt in range(1, retries + 1):
            response = self.send_and_receive(cmd)
            raw = response.decode('utf-8', errors='replace').strip()
            logger.info(f"LOAD_GET attempt={attempt}/{retries} cmd=\"{safe_cmd}\" response=\"{raw[:200]}\"")

            if not raw:
                continue
            if raw.startswith("ERR|CODE:MALFORMED"):
                continue
            if raw.startswith("ERR"):
                return raw

            # Success shape is a single record line followed by an END
            # terminator line; strip the terminator so it doesn't get
            # absorbed into the last field's value.
            first_line = raw.split('\n')[0].strip()
            return first_line

        logger.error(f"LOAD_GET exhausted retries cmd=\"{safe_cmd}\"")
        return "ERR|CODE:FAULT_RETRY_EXHAUSTED|MSG:No valid response after retries"

    def parse_load_details(self, response: str) -> dict:
        details = {}
        # Response format: KEY:VALUE|KEY:VALUE|...
        for pair in response.split('|'):
            if ':' in pair:
                key, value = pair.split(':', 1)
                details[key.strip()] = value.strip()
        return details
