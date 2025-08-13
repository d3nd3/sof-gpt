import socket
import sys
import time
from typing import Dict, List, Optional, Tuple
import re

MASTER_HOST = "sof1master.megalag.org"
MASTER_PORT = 28900


class ServerEntry:
    def __init__(self, ip: str, port: int):
        self.ip: str = ip
        # Port returned by master (often GameSpy/query port)
        self.port: int = port
        # Properties retrieved from \info\ query
        self.props: Dict[str, str] = {}
        # Determined game connection port (hostport), filled after enrichment
        self.game_port: Optional[int] = None

    @property
    def hostname(self) -> str:
        return self.props.get("hostname", f"{self.ip}:{self.port}")

    @property
    def mapname(self) -> str:
        return self.props.get("mapname", "?")

    @property
    def numplayers(self) -> int:
        value = self.props.get("numplayers", "0")
        try:
            return int(value)
        except ValueError:
            return 0

    @property
    def maxplayers(self) -> int:
        value = self.props.get("maxplayers", "0")
        try:
            return int(value)
        except ValueError:
            return 0

    def compute_connection_port(self) -> int:
        # Prefer explicit hostport from server info
        hostport_str = self.props.get("hostport")
        if hostport_str is not None:
            # Extract leading digits only (strip stray nulls/garbage)
            m = re.match(r"^(\d+)", str(hostport_str))
            if m:
                try:
                    self.game_port = int(m.group(1))
                    return self.game_port
                except ValueError:
                    pass
        # Many SoF servers report on GameSpy/query port = hostport+1
        # If info did not include hostport, try port-1 as a heuristic
        guessed = max(0, self.port - 1)
        self.game_port = guessed
        return guessed


def _extract_key(handshake_bytes: bytes) -> bytes:
    # Last 6 bytes of the handshake are the key
    return handshake_bytes[-6:]


def _add_char(x: int) -> str:
    if x < 26:
        return chr(x + 65)
    if x < 52:
        return chr(x + 71)
    if x < 62:
        return chr(x - 4)
    if x == 62:
        return "+"
    if x == 63:
        return "/"
    return "A"


def _validate_key(handoff: str, in_key: bytes) -> str:
    # Port of sof-server-lister/query_gs.py ValidateKey to Python 3
    a = 0
    b = 0
    c = 0
    d = 0

    table = list(range(256))

    if len(handoff) > 6:
        raise ValueError("Invalid handoff length")

    for i in range(256):
        a = (a + table[i] + ord(handoff[i % len(handoff)])) & 255
        b = table[a]
        table[a] = table[i]
        table[i] = b

    a = 0
    key = list(in_key)
    in_keylen = len(key)

    for i in range(in_keylen):
        a = (a + key[i] + 1) & 255
        b = table[a]
        c = (c + b) & 255
        d = table[c]
        table[c] = b
        table[a] = d
        key[i] ^= table[(b + d) & 255]

    in_triplets = in_keylen // 3
    i = 0
    out_key = []
    while in_triplets > 0:
        in_triplets -= 1
        b = key[i]
        i += 1
        d = key[i]
        i += 1
        out_key.append(_add_char(b >> 2))
        out_key.append(_add_char(((b & 3) << 4) | (d >> 4)))
        b = key[i]
        i += 1
        out_key.append(_add_char(((d & 15) << 2) | (b >> 6)))
        out_key.append(_add_char(b & 63))
    return "".join(out_key)


def fetch_master_list(timeout_sec: float = 6.0) -> List[ServerEntry]:
    # TCP to master server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_sec)
    s.connect((MASTER_HOST, MASTER_PORT))
    hello = s.recv(1024)
    if not hello:
        s.close()
        return []

    key_secure = _extract_key(hello)
    key_valid = _validate_key("iVn3a3", key_secure)

    pkt_valid = ("\\gamename\\sofretail\\gamever\\1.6\\location\\0\\validate\\" + key_valid + "\\final\\\\queryid\\1.1\\").encode(
        "latin_1"
    )
    s.sendall(pkt_valid)

    s.sendall(b"\\list\\cmp\\gamename\\sofretail\\final\\")

    # Read until close
    data = bytearray()
    while True:
        chunk = s.recv(1024)
        if not chunk:
            break
        data += chunk
    s.close()

    if data.endswith(b"\\final\\"):
        data = data[: -len(b"\\final\\")]

    server_entries: List[ServerEntry] = []
    if len(data) % 6 == 0:
        i = 0
        view = memoryview(data)
        while i < len(data):
            ip = f"{view[i]}.{view[i+1]}.{view[i+2]}.{view[i+3]}"
            port = (view[i + 4] << 8) + view[i + 5]
            server_entries.append(ServerEntry(ip, port))
            i += 6
    return server_entries


def enrich_with_info(servers: List[ServerEntry], per_server_timeout_sec: float = 0.35, limit: Optional[int] = None) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(per_server_timeout_sec)

    to_query = servers if limit is None else servers[:limit]
    for entry in to_query:
        try:
            sock.sendto(b"\\info\\", (entry.ip, entry.port))
            data, _ = sock.recvfrom(4096)
            tokens = data.split(b"\\")
            props: Dict[str, str] = {}
            # tokens[0] is empty or contains header
            for i in range(1, len(tokens) - 1, 2):
                key = tokens[i].decode("latin_1", errors="ignore")
                val = tokens[i + 1].decode("latin_1", errors="ignore")
                props[key] = val
            entry.props = props
        except Exception:
            # ignore timeouts or parse errors
            entry.props = entry.props or {}
        finally:
            # Compute connection port after props set
            entry.compute_connection_port()
    sock.close()


def choose_server_interactively(servers: List[ServerEntry]) -> Optional[ServerEntry]:
    if not servers:
        return None

    # Enrich a reasonable subset first for speed, then sort and print
    enrich_with_info(servers, limit=64)

    # Sort by online players desc, then hostname
    servers.sort(key=lambda s: (-s.numplayers, s.hostname.lower()))

    # Display top N
    max_display = min(50, len(servers))
    print("Available SoF servers:")
    for idx in range(max_display):
        s = servers[idx]
        players = f"{s.numplayers}/{s.maxplayers}" if s.maxplayers else f"{s.numplayers}"
        conn_port = s.game_port if s.game_port is not None else s.port
        print(f"  [{idx}] {s.hostname} | map: {s.mapname} | players: {players} | {s.ip}:{conn_port} (query:{s.port})")

    print("Enter a number to connect, or 's' to search by text, or 'q' to quit")

    while True:
        choice = input("> ").strip()
        if choice.lower() in ("q", "quit", "exit"):
            return None
        if choice.lower().startswith("s"):
            query = choice[1:].strip()
            if not query:
                query = input("Search text: ").strip()
            matches = [s for s in servers if query.lower() in s.hostname.lower() or query.lower() in s.mapname.lower()]
            if not matches:
                print("No matches.")
                continue
            for i, s in enumerate(matches[:50]):
                players = f"{s.numplayers}/{s.maxplayers}" if s.maxplayers else f"{s.numplayers}"
                conn_port = s.game_port if s.game_port is not None else s.port
                print(f"  [m{i}] {s.hostname} | map: {s.mapname} | players: {players} | {s.ip}:{conn_port} (query:{s.port})")
            sub = input("Select match index prefixed with 'm' (e.g., m0), or press Enter to cancel: ").strip()
            if sub.startswith("m") and sub[1:].isdigit():
                mi = int(sub[1:])
                if 0 <= mi < len(matches[:50]):
                    return matches[mi]
            continue
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < max_display:
                return servers[idx]
            print(f"Please enter a number between 0 and {max_display-1}")
        else:
            print("Invalid input. Enter a number, 's' to search, or 'q' to quit.")


def select_server() -> Optional[Tuple[str, int]]:
    try:
        print("Querying master server for available servers...")
        servers = fetch_master_list()
    except Exception as e:
        print(f"Failed to query master server: {e}")
        servers = []

    if not servers:
        print("No servers found from master. You can enter an IP:port manually or press Enter to cancel.")
        manual = input("IP:port > ").strip()
        if not manual:
            return None
        if ":" in manual:
            host, port_str = manual.split(":", 1)
            try:
                return host.strip(), int(port_str)
            except ValueError:
                print("Invalid port.")
                return None
        print("Please include port using IP:port format.")
        return None

    chosen = choose_server_interactively(servers)
    if not chosen:
        return None
    # If we enriched only a subset, ensure chosen has info populated (optional)
    if not chosen.props or chosen.game_port is None:
        try:
            enrich_with_info([chosen], limit=None)
        except Exception:
            pass
    # Fall back to heuristic if still unknown
    port_out = chosen.game_port if chosen.game_port is not None else max(0, chosen.port - 1)
    return chosen.ip, port_out
