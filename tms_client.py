import os
import socket
import time


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
        return b"".join(chunks)

    def debug_echo(self) -> str:
        cmd = f"CMD:DEBUG_ECHO|AUTH:{self.token}"
        response = self.send_and_receive(cmd)
        return response.decode('utf-8', errors='replace').strip()

    def load_query(self, origin: str = None, destination: str = None, equipment: str = None, max_results: int = 10) -> list:
        cmd = f"CMD:LOAD_QUERY|AUTH:{self.token}"
        if origin:
            cmd += f"|ORIG_STATE:{origin}"
        if destination:
            cmd += f"|DEST_STATE:{destination}"
        if equipment:
            cmd += f"|EQTYPE:{equipment}"
        cmd += f"|MAX_RESULTS:{max_results}"
        response = self.send_and_receive(cmd)
        raw = response.decode('utf-8', errors='replace').strip()

        # Parse multiple records until END
        loads = []
        for line in raw.split('\n'):
            line = line.strip()
            if line == "END":
                break
            if line.startswith("ERR"):
                return {"error": line}
            if line and ":" in line:
                load = self.parse_load_details(line)
                if load:
                    loads.append(load)
        return loads

    def load_get(self, load_id: str) -> str:
        cmd = f"CMD:LOAD_GET|AUTH:{self.token}|LOAD_ID:{load_id}"
        response = self.send_and_receive(cmd)
        return response.decode('utf-8', errors='replace').strip()

    def parse_load_details(self, response: str) -> dict:
        details = {}
        # Response format: KEY:VALUE|KEY:VALUE|...
        for pair in response.split('|'):
            if ':' in pair:
                key, value = pair.split(':', 1)
                details[key.strip()] = value.strip()
        return details
