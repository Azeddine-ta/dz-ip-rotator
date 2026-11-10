#!/usr/bin/env python3
"""
DZ IP ROTATOR & ROUTE OPTIMIZER (Algérie Télécom Ultimate Edition v5.0)
Universal, Zero-Dependency WAN IP Rotator, Gaming Ping Hunter, and Latency Optimizer.

Supported Hardware & Protocols:
  - Huawei EchoLife / OptiXstar (HG8145X6, HG8145V5, HG8245H, HG8245W5)
  - FiberHome (HG6145F1, HG6145D2, HG6143D, AN5506)

Developer : Azeddine
Telegram  : https://t.me/x4D7217A7A6F
"""

import os
import sys
import time
import json
import ssl
import base64
import socket
import struct
import getpass
import argparse
import subprocess
import urllib.request
import urllib.parse
import re
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- Config & Cache Paths ---
CONFIG_DIR = Path.home() / ".config" / "dz-ip-changer"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"
LEGACY_CONFIG = Path.home() / ".config" / "huawei-ip-changer" / "config.json"

CURRENT_LANG = "en"

# --- Algérie Télécom IP Pools Intelligence ---
AT_POOLS = {
    "105": {
        "name": "105.x.x.x Pool",
        "desc": "Algérie Télécom Modern FTTH Core (Fastest route to Marseille/Europe)",
        "desc_fr": "Cœur FTTH Moderne Algérie Télécom (Transit rapide vers Marseille/Europe)",
        "prefixes": ["105."]
    },
    "154": {
        "name": "154.x.x.x Pool",
        "desc": "Algérie Télécom Expansion Pool (High-Throughput FTTH & LTE)",
        "desc_fr": "Pool d'Expansion Algérie Télécom (Très haut débit FTTH & LTE)",
        "prefixes": ["154."]
    },
    "41": {
        "name": "41.x.x.x Pool",
        "desc": "Algérie Télécom Classic Core (Broad international peering & legacy routes)",
        "desc_fr": "Cœur Classique Algérie Télécom (Interconnexions internationales larges)",
        "prefixes": ["41."]
    },
    "197": {
        "name": "197.x.x.x Pool",
        "desc": "Algérie Télécom Regional Broadband (Common on Oran / Regional BRAS)",
        "desc_fr": "Haut Débit Régional Algérie Télécom (Courant sur Oran / BRAS régionaux)",
        "prefixes": ["197."]
    }
}

BENCHMARK_TARGETS = [
    ("Cloudflare DNS", "1.1.1.1", 53),
    ("Twitch Ingest / Fastly", "151.101.2.167", 443),
    ("Discord EU Voice", "162.159.130.233", 443),
    ("Quad9 DNS", "9.9.9.9", 53),
    ("Google DNS", "8.8.8.8", 53),
]

# --- Internationalization (EN / FR) ---
I18N = {
    "en": {
        "title": "Algérie Télécom WAN & Route Optimizer v5.0",
        "router_target": "Router Target",
        "hardware_os": "Hardware/OS",
        "internet_wan": "Internet WAN",
        "current_ip": "Current IP",
        "pool_subnet": "Pool Subnet",
        "ping_latency": "Ping Latency",
        "public_badge": "Public 1:1",
        "cgnat_badge": "CGNAT",
        "menu_rotate": "⚡ Fast IP Rotate (Instant Single Cycle)",
        "menu_pool": "🎯 Target Specific IP Pool (105.x, 154.x, 41.x, 197.x)",
        "menu_ping": "🎮 Smart Gaming Route Hunter (Target Ping < X ms)",
        "menu_unique": "💎 Rotate Until Never-Seen IP (Permanent Unique)",
        "menu_timer": "⏱️ Auto-Rotate Timer Loop",
        "menu_bench": "📊 Multi-Server Latency Benchmark",
        "menu_history": "📜 View IP History",
        "menu_copy": "📋 Copy Current IP to Clipboard",
        "menu_creds": "🔑 Reconfigure Router Credentials",
        "menu_lang": "🌐 Switch Language / Changer de langue (FR)",
        "menu_refresh": "🔄 Refresh Dashboard",
        "menu_quit": "🚪 Quit",
        "press_key": "Press a key [1-8, 0, l, r, q]: ",
        "rotation_completed": "✨ IP ROTATION COMPLETED",
        "ip_transition": "IP Transition",
        "assigned_pool": "Assigned Pool",
        "network_route": "Network Route",
        "cycle_time": "Cycle Time",
        "bras_node": "BRAS & Node",
        "copied": "[Copied to Clipboard]",
        "faster": "faster!",
        "resetting_session": "Resetting session (PPPoE Down)...",
        "negotiating_lease": "Negotiating lease (PADI / PADR)...",
        "validating_ip": "Leased IP: {ip} (Validating...)",
        "handshaking": "Handshaking with router...",
        "press_enter": "Press Enter to return to dashboard...",
        "re_cycling": "Re-cycling: {reason}",
        "target_filter": "Requiring IP starting with {pools}",
        "latency_target": "Ping must be < {ms} ms",
        "bench_title": "Multi-Server Latency Benchmark (Gaming & CDNs)",
        "bench_probing": "Probing European transit and DNS nodes...",
        "pool_selector_title": "Algérie Télécom IP Pool Selector",
        "pool_105": "105.x.x.x - Modern FTTH Pool (Fastest Europe Peering)",
        "pool_154": "154.x.x.x - Expansion Pool (High-Throughput FTTH/4G)",
        "pool_41": "41.x.x.x  - Classic Core Pool (Broad peering)",
        "pool_197": "197.x.x.x - Regional Broadband Pool",
        "pool_dual": "Dual Fast - Either 105.x OR 154.x",
        "pool_custom": "Custom Prefix / Subnet (e.g. 105.106., 41.107.)",
        "pool_back": "Back to Main Menu",
        "lang_prompt": "Select Language / Choisissez la langue:\n  [1] English (EN)\n  [2] Français (FR)\nChoice / Choix [1-2, default: 1]: ",
        "copied_success": "✓ Copied {ip} to clipboard!",
        "clipboard_not_found": "Clipboard tool not found. IP is {ip}",
        "history_empty": "No IP rotations recorded yet.",
        "history_title": "Persistent WAN IP History & Log",
        "total_rotations": "Total Rotations Recorded: {count}"
    },
    "fr": {
        "title": "Optimiseur & Rotateur WAN Algérie Télécom v5.0",
        "router_target": "Cible Routeur",
        "hardware_os": "Matériel/OS",
        "internet_wan": "Internet WAN",
        "current_ip": "IP Actuelle",
        "pool_subnet": "Sous-Réseau",
        "ping_latency": "Latence Ping",
        "public_badge": "Public 1:1",
        "cgnat_badge": "CGNAT",
        "menu_rotate": "⚡ Changer l'IP Immédiatement (Cycle Rapide)",
        "menu_pool": "🎯 Cibler un Pool d'IP (105.x, 154.x, 41.x, 197.x)",
        "menu_ping": "🎮 Chasseur de Ping Gaming (Ping Cible < X ms)",
        "menu_unique": "💎 Obtenir une IP Inédite (Jamais vue)",
        "menu_timer": "⏱️ Boucle de Rotation Automatique",
        "menu_bench": "📊 Test de Latence Multi-Serveurs",
        "menu_history": "📜 Historique des Adresses IP",
        "menu_copy": "📋 Copier l'IP Actuelle dans le Presse-Papier",
        "menu_creds": "🔑 Reconfigurer les Identifiants du Routeur",
        "menu_lang": "🌐 Switch Language / Changer de langue (EN)",
        "menu_refresh": "🔄 Actualiser le tableau",
        "menu_quit": "🚪 Quitter",
        "press_key": "Appuyez sur une touche [1-8, 0, l, r, q] : ",
        "rotation_completed": "✨ ROTATION D'IP TERMINÉE",
        "ip_transition": "Transition IP",
        "assigned_pool": "Pool Attribué",
        "network_route": "Type de Réseau",
        "cycle_time": "Temps du Cycle",
        "bras_node": "Noeud BRAS",
        "copied": "[Copié dans le Presse-Papier]",
        "faster": "plus rapide !",
        "resetting_session": "Réinitialisation de la session (PPPoE Down)...",
        "negotiating_lease": "Négociation du bail (PADI / PADR)...",
        "validating_ip": "IP Attribuée: {ip} (Validation en cours...)",
        "handshaking": "Connexion avec le routeur...",
        "press_enter": "Appuyez sur Entrée pour revenir au menu...",
        "re_cycling": "Nouvelle tentative: {reason}",
        "target_filter": "Exige une IP commençant par {pools}",
        "latency_target": "La latence doit être < {ms} ms",
        "bench_title": "Test de Latence Multi-Serveurs (Jeux & CDNs)",
        "bench_probing": "Test des routes européennes et serveurs DNS...",
        "pool_selector_title": "Sélecteur de Pool Algérie Télécom",
        "pool_105": "105.x.x.x - Pool FTTH Moderne (Meilleur transit Europe)",
        "pool_154": "154.x.x.x - Pool d'Expansion (Très haut débit FTTH/4G)",
        "pool_41": "41.x.x.x  - Pool Classique (Interconnexions larges)",
        "pool_197": "197.x.x.x - Pool Régional Haut Débit",
        "pool_dual": "Rapide Double - Soit 105.x OU 154.x",
        "pool_custom": "Préfixe / Sous-réseau Personnalisé (ex: 105.106., 41.107.)",
        "pool_back": "Retour au Menu Principal",
        "lang_prompt": "Select Language / Choisissez la langue:\n  [1] English (EN)\n  [2] Français (FR)\nChoice / Choix [1-2, default: 1]: ",
        "copied_success": "✓ IP {ip} copiée dans le presse-papier !",
        "clipboard_not_found": "Outil presse-papier non trouvé. IP : {ip}",
        "history_empty": "Aucune rotation d'IP enregistrée pour le moment.",
        "history_title": "Historique Permanent des Adresses WAN IP",
        "total_rotations": "Total des Rotations Enregistrées : {count}"
    }
}

def tr(key: str, **kwargs) -> str:
    lang_dict = I18N.get(CURRENT_LANG, I18N["en"])
    template = lang_dict.get(key, I18N["en"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template

# --- Compact ASCII Banner (48 Chars - Perfect on Termux / Mobile / Terminal) ---
def print_banner():
    banner = f"""\033[1;36m  ___  ____    ___ ____   ___  ___ _____ ___  ____  
 |   \\/__  /  |_ _|  _ \\ | _ \\/ _ \\_   _/ _ \\| _ \\ 
 | |) | / /    | ||  _/  |   / (_) || || (_) |   / 
 |___/ /_/    |___|_|    |_|_\\___/ |_| \\___/|_|_\\ \033[0m
       \033[1;32m⚡ Algérie Télécom Optimizer v5.0 ⚡\033[0m
      \033[1;33mDev: \033[1;35mAzeddine\033[0m  •  \033[1;34mhttps://t.me/x4D7217A7A6F\033[0m
"""
    print(banner)

# ==============================================================================
# 1. CROSS-PLATFORM GATEWAY AUTO-DISCOVERY (Linux, OpenWrt, Termux, Windows)
# ==============================================================================

def detect_default_gateway() -> str:
    """Auto-detect router IP across Linux, Termux, OpenWrt, and Windows."""
    try:
        if os.path.exists('/proc/net/route'):
            with open('/proc/net/route', 'r') as f:
                for line in f.readlines()[1:]:
                    fields = line.strip().split()
                    if len(fields) >= 3 and fields[1] == '00000000':
                        return socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))
    except Exception:
        pass

    if os.name == 'nt':
        try:
            out = subprocess.check_output("netstat -rn", shell=True).decode()
            for line in out.splitlines():
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0] in ("0.0.0.0", "Default"):
                    return parts[2]
        except Exception:
            pass

    # macOS / BSD default route
    if sys.platform == 'darwin':
        try:
            out = subprocess.check_output(["route", "-n", "get", "default"], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                if "gateway:" in line:
                    return line.split("gateway:")[1].strip()
        except Exception:
            pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 80))
        local_ip = s.getsockname()[0]
        s.close()
        parts = local_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.1"
    except Exception:
        pass

    return "192.168.1.1"

# ==============================================================================
# 2. NETWORK TELEMETRY, CGNAT & BENCHMARK
# ==============================================================================

def unescape_js_string(s: str) -> str:
    return re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), s)

def format_uptime(seconds_str: str) -> str:
    try:
        s = int(seconds_str)
        hours = s // 3600
        minutes = (s % 3600) // 60
        sec = s % 60
        return f"{hours:02d}h {minutes:02d}m {sec:02d}s"
    except Exception:
        return f"{seconds_str}s"

def identify_ip_pool(ip: str) -> tuple:
    if not ip or ip in ("0.0.0.0", "None"):
        return "Unknown", "No IP lease", "\033[1;30m"
    
    first = ip.split(".")[0]
    if first == "100":
        parts = [int(p) for p in ip.split(".") if p.isdigit()]
        if len(parts) >= 2 and 64 <= parts[1] <= 127:
            desc = "Carrier-Grade NAT (Shared Pool)" if CURRENT_LANG == "en" else "NAT Opérateur (Ports fermés)"
            return "CGNAT RFC6598", desc, "\033[1;33m"
    elif first == "10":
        desc = "Carrier-Grade NAT (Private Subnet)" if CURRENT_LANG == "en" else "NAT Privé (Sous-réseau 10.x)"
        return "Private 10.x", desc, "\033[1;31m"
    
    if first in AT_POOLS:
        info = AT_POOLS[first]
        desc = info["desc"] if CURRENT_LANG == "en" else info.get("desc_fr", info["desc"])
        return info["name"], desc, "\033[1;36m"
        
    desc = "Algérie Télécom Public Network" if CURRENT_LANG == "en" else "Réseau Public Algérie Télécom"
    return f"{first}.x.x.x Pool", desc, "\033[1;32m"

def measure_ping_tcp(host="1.1.1.1", port=53, timeout=1.5) -> float:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    t0 = time.time()
    try:
        s.connect((host, port))
        t1 = time.time()
        s.close()
        return round((t1 - t0) * 1000.0, 1)
    except Exception:
        return -1.0

def run_benchmark() -> list:
    results = []
    for label, host, port in BENCHMARK_TARGETS:
        lat = measure_ping_tcp(host, port, timeout=1.8)
        results.append((label, host, lat))
    return results

def check_cgnat(router_ip: str) -> tuple:
    if not router_ip or router_ip == "0.0.0.0":
        return False, "No IP", "Unknown"
    
    parts = [int(p) for p in router_ip.split(".") if p.isdigit()]
    if len(parts) == 4:
        if parts[0] == 100 and (64 <= parts[1] <= 127):
            return True, "CGNAT (100.64.0.0/10)", router_ip
        if parts[0] == 10:
            return True, "Private (10.0.0.0/8)", router_ip

    ext_ip = None
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=1.2, context=ctx) as r:
            ext_ip = r.read().decode("utf-8").strip()
    except Exception:
        pass

    if ext_ip:
        if ext_ip == router_ip:
            return False, "Public 1:1 (Direct Route)", ext_ip
        else:
            return True, f"CGNAT (Public: {ext_ip})", ext_ip
            
    return False, "Public 1:1 (Direct)", router_ip

def is_cgnat_ip(ip: str) -> bool:
    parts = [int(p) for p in ip.split(".") if p.isdigit()]
    if len(parts) == 4:
        if parts[0] == 100 and (64 <= parts[1] <= 127):
            return True
        if parts[0] == 10 or (parts[0] == 192 and parts[1] == 168):
            return True
    return False

def copy_to_clipboard(text: str) -> bool:
    for cmd in [
        ["termux-clipboard-set"],
        ["pbcopy"],
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
        ["clip"]
    ]:
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p.communicate(text.encode("utf-8"))
            if p.returncode == 0:
                return True
        except Exception:
            continue
    return False

def send_os_notification(title: str, message: str):
    try:
        subprocess.run(["notify-send", "-a", "DZ IP Optimizer", title, message], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_single_keypress() -> str:
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# --- History Storage ---

def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history(history: list):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-500:], f, indent=2)

# ==============================================================================
# 3. MULTI-VENDOR ROUTER DRIVERS
# ==============================================================================

class BaseRouterDriver:
    def __init__(self, host, port, username, password, protocol=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.protocol = protocol
        self.base_url = None
        self.vendor_name = "Generic"
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    def determine_protocol(self):
        if self.protocol:
            self.base_url = f"{self.protocol}://{self.host}:{self.port}"
            return

        proto_candidates = ["http", "https"] if self.port == 80 else ["https", "http"]
        for proto in proto_candidates:
            test_url = f"{proto}://{self.host}:{self.port}/"
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                with self.opener.open(req, timeout=2.5) as resp:
                    if resp.status in (200, 302, 401, 403, 404):
                        self.protocol = proto
                        self.base_url = f"{proto}://{self.host}:{self.port}"
                        return
            except Exception:
                continue

        default_proto = "http" if self.port == 80 else "https"
        self.protocol = default_proto
        self.base_url = f"{default_proto}://{self.host}:{self.port}"

    def login(self) -> bool:
        raise NotImplementedError

    def logout(self):
        pass

    def get_full_wan_status(self) -> dict:
        raise NotImplementedError

    def reconnect_pppoe(self, delay: float = 1.0) -> bool:
        raise NotImplementedError


class HuaweiDriver(BaseRouterDriver):
    def __init__(self, host, port, username, password, protocol=None):
        super().__init__(host, port, username, password, protocol)
        self.vendor_name = "Huawei OptiXstar/EchoLife"
        self.sid_cookie = None
        self.wan_domain = None
        self.wan_name = None

    def determine_protocol(self):
        if self.protocol:
            self.base_url = f"{self.protocol}://{self.host}:{self.port}"
            return

        # 1. Probe HTTPS first (Huawei ONTs in Algeria serve HTTPS on port 80)
        try:
            test_url = f"https://{self.host}:{self.port}/asp/GetRandCount.asp"
            req = urllib.request.Request(test_url, data=b"", headers={"User-Agent": "Mozilla/5.0"})
            with self.opener.open(req, timeout=2.0) as resp:
                data = resp.read().decode("utf-8", errors="ignore").strip().lstrip("\ufeff").strip("'\" \r\n")
                if re.match(r"^[0-9a-fA-F]{16,}$", data):
                    self.protocol = "https"
                    self.base_url = f"https://{self.host}:{self.port}"
                    return
        except Exception:
            pass

        # 2. Probe HTTP
        try:
            test_url = f"http://{self.host}:{self.port}/asp/GetRandCount.asp"
            req = urllib.request.Request(test_url, data=b"", headers={"User-Agent": "Mozilla/5.0"})
            with self.opener.open(req, timeout=2.0) as resp:
                data = resp.read().decode("utf-8", errors="ignore").strip().lstrip("\ufeff").strip("'\" \r\n")
                if re.match(r"^[0-9a-fA-F]{16,}$", data):
                    self.protocol = "http"
                    self.base_url = f"http://{self.host}:{self.port}"
                    return
        except Exception:
            pass

        # 3. Default fallback
        self.protocol = "https"
        self.base_url = f"https://{self.host}:{self.port}"

    def _request(self, path: str, data: dict = None, extra_headers: dict = None) -> str:
        if not self.base_url:
            self.determine_protocol()

        url = self.base_url + path
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Referer": self.base_url + "/index.asp"
        }
        if self.sid_cookie:
            headers["Cookie"] = self.sid_cookie
        if extra_headers:
            headers.update(extra_headers)

        encoded_data = urllib.parse.urlencode(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=encoded_data, headers=headers)
        try:
            with self.opener.open(req, timeout=8) as resp:
                set_cookie = resp.headers.get("Set-Cookie")
                if set_cookie and "Cookie=" in set_cookie:
                    self.sid_cookie = set_cookie.split(";")[0]
                return resp.read().decode("utf-8", errors="ignore")
        except urllib.error.URLError as e:
            # Auto-fallback from HTTPS to HTTP if port 80 or SSL mismatch encountered
            err_str = str(e).lower()
            if ("wrong_version_number" in err_str or "ssl" in err_str) and self.base_url.startswith("https://"):
                self.protocol = "http"
                self.base_url = f"http://{self.host}:{self.port}"
                retry_url = self.base_url + path
                req_retry = urllib.request.Request(retry_url, data=encoded_data, headers=headers)
                with self.opener.open(req_retry, timeout=8) as resp:
                    set_cookie = resp.headers.get("Set-Cookie")
                    if set_cookie and "Cookie=" in set_cookie:
                        self.sid_cookie = set_cookie.split(";")[0]
                    return resp.read().decode("utf-8", errors="ignore")
            raise

    def login(self) -> bool:
        self.determine_protocol()

        # Check for temporary lockout cooldown
        try:
            check_req = urllib.request.Request(f"{self.base_url}/", headers={"User-Agent": "Mozilla/5.0"})
            with self.opener.open(check_req, timeout=2.5) as r:
                page_text = r.read().decode("utf-8", errors="ignore")
                m_lock = re.search(r'var\s+LockLeftTime\s*=\s*[\'"](\d+)[\'"]', page_text)
                if m_lock and int(m_lock.group(1)) > 0:
                    raise RuntimeError(f"Huawei router is temporarily locked ({m_lock.group(1)}s cooldown remaining due to 3 failed attempts). Please wait for the cooldown to finish.")
        except RuntimeError:
            raise
        except Exception:
            pass

        try:
            token_resp = self._request("/asp/GetRandCount.asp", data={})
            token = token_resp.strip().lstrip("\ufeff").strip("'\" \r\n")
            if not re.match(r"^[0-9a-fA-F]{16,}$", token):
                raise RuntimeError("Invalid token format received from Huawei router.")
        except Exception as e:
            raise RuntimeError(f"Could not reach Huawei router at {self.base_url} ({e})")

        pwd_b64 = base64.b64encode(self.password.encode("utf-8")).decode("utf-8")
        login_data = {
            "UserName": self.username,
            "PassWord": pwd_b64,
            "Language": "english",
            "x.X_HW_Token": token
        }
        headers = {"Cookie": "Cookie=body:Language:english:id=-1"}
        self._request("/login.cgi", data=login_data, extra_headers=headers)
        
        if not self.sid_cookie or "sid=" not in self.sid_cookie:
            raise RuntimeError("Huawei Authentication failed: Incorrect password or session busy. (On HG8145X6/OptiXstar, verify password on the router sticker or try 'admin').")
        return True

    def logout(self):
        if not self.sid_cookie:
            return
        try:
            self._request("/logout.cgi?RequestFile=html/logout.html", data={})
        except Exception:
            pass
        finally:
            self.sid_cookie = None

    def get_ont_token(self) -> str:
        resp = self._request("/html/bbsp/wan/wan.asp")
        m = re.search(r'id=["\'](?:hwonttoken|onttoken)["\']\s+value=["\']([a-fA-F0-9]+)["\']', resp)
        if not m:
            m = re.search(r'name=["\']onttoken["\']\s+id=["\']onttoken["\']\s+value=["\']([a-fA-F0-9]+)["\']', resp)
        if not m:
            raise RuntimeError("Unable to extract onttoken from Huawei WAN configuration.")
        return m.group(1)

    def get_full_wan_status(self) -> dict:
        resp = self._request("/html/bbsp/common/wan_list_cache_wan.asp")
        ppp_matches = re.findall(r'new\s+WanPPP\(([^)]+)\)', resp)
        if not ppp_matches:
            raise RuntimeError("No active WanPPP configuration returned from router.")
        
        selected_wan = None
        for raw_args in ppp_matches:
            args = [unescape_js_string(arg.strip().strip('"\'')) for arg in raw_args.split(",")]
            service_list = args[27].upper() if len(args) > 27 else ""
            if "INTERNET" in service_list or selected_wan is None:
                selected_wan = args

        domain = selected_wan[0] if len(selected_wan) > 0 else ""
        status = selected_wan[5] if len(selected_wan) > 5 else "Unknown"
        name = selected_wan[8] if len(selected_wan) > 8 else "Unknown"
        ip = selected_wan[14] if len(selected_wan) > 14 else "0.0.0.0"
        gateway = selected_wan[15] if len(selected_wan) > 15 else "0.0.0.0"
        dns = selected_wan[18] if len(selected_wan) > 18 else ""
        ac_name = selected_wan[38] if len(selected_wan) > 38 else ""
        uptime = selected_wan[40] if len(selected_wan) > 40 else "0"

        self.wan_domain = domain
        self.wan_name = name

        return {
            "driver": "Huawei",
            "domain": domain,
            "status": status,
            "name": name,
            "ip": ip,
            "gateway": gateway,
            "dns": dns,
            "bras": ac_name,
            "uptime_seconds": uptime
        }

    def reconnect_pppoe(self, delay: float = 1.0) -> bool:
        if not self.wan_domain:
            self.get_full_wan_status()

        onttoken = self.get_ont_token()
        disable_params = {
            "GROUP_a_y.Enable": "0",
            "GROUP_a_y.ConnectionTrigger": "AlwaysOn",
            "x.X_HW_Token": onttoken
        }
        self._request(f"/set.cgi?GROUP_a_y={self.wan_domain}&RequestFile=html/bbsp/wan/wan.asp", data=disable_params)
        
        time.sleep(delay)

        onttoken = self.get_ont_token()
        enable_params = {
            "GROUP_a_y.Enable": "1",
            "GROUP_a_y.ConnectionTrigger": "AlwaysOn",
            "x.X_HW_Token": onttoken
        }
        self._request(f"/set.cgi?GROUP_a_y={self.wan_domain}&RequestFile=html/bbsp/wan/wan.asp", data=enable_params)
        return True


# --- Pure Python AES-128-CBC Engine (Zero External Dependencies) ---
FH_AES_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]
FH_AES_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

def fh_aes_encrypt(plaintext: str) -> str:
    key_bytes = bytes([i + 111 for i in range(16)])  # b'opqrstuvwxyz{|}~'
    iv = list(key_bytes)
    
    # Key expansion
    w = [list(key_bytes[i:i+4]) for i in range(0, 16, 4)]
    for i in range(4, 44):
        temp = list(w[i-1])
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [FH_AES_SBOX[b] for b in temp]
            temp[0] ^= FH_AES_RCON[(i // 4) - 1]
        w.append([w[i-4][j] ^ temp[j] for j in range(4)])
    round_keys = [[w[r*4 + c//4][c%4] for c in range(16)] for r in range(11)]

    def xtime(a):
        return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

    def encrypt_block(block):
        state = list(block)
        for i in range(16): state[i] ^= round_keys[0][i]
        for rnd in range(1, 10):
            state = [FH_AES_SBOX[b] for b in state]
            state = [
                state[0], state[5], state[10], state[15],
                state[4], state[9], state[14], state[3],
                state[8], state[13], state[2], state[7],
                state[12], state[1], state[6], state[11]
            ]
            new_state = [0] * 16
            for c in range(4):
                idx = c * 4
                s0, s1, s2, s3 = state[idx], state[idx+1], state[idx+2], state[idx+3]
                t = s0 ^ s1 ^ s2 ^ s3
                new_state[idx] = s0 ^ t ^ xtime(s0 ^ s1)
                new_state[idx+1] = s1 ^ t ^ xtime(s1 ^ s2)
                new_state[idx+2] = s2 ^ t ^ xtime(s2 ^ s3)
                new_state[idx+3] = s3 ^ t ^ xtime(s3 ^ s0)
            state = [new_state[i] ^ round_keys[rnd][i] for i in range(16)]

        state = [FH_AES_SBOX[b] for b in state]
        state = [
            state[0], state[5], state[10], state[15],
            state[4], state[9], state[14], state[3],
            state[8], state[13], state[2], state[7],
            state[12], state[1], state[6], state[11]
        ]
        return [state[i] ^ round_keys[10][i] for i in range(16)]

    raw = plaintext.encode("utf-8")
    pad_len = 16 - (len(raw) % 16)
    padded = raw + bytes([pad_len] * pad_len)

    out = []
    for i in range(0, len(padded), 16):
        blk = [padded[i+j] ^ iv[j] for j in range(16)]
        enc = encrypt_block(blk)
        out.extend(enc)
        iv = enc
    return bytes(out).hex().upper()


class FiberHomeDriver(BaseRouterDriver):
    def __init__(self, host, port, username, password, protocol=None):
        super().__init__(host, port, username, password, protocol)
        self.vendor_name = "FiberHome"
        self.session_id = None
        
        import http.cookiejar
        self.cookie_jar = http.cookiejar.CookieJar()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPSHandler(context=ctx)
        )

    def _request(self, endpoint: str, data: dict = None) -> dict:
        if not self.base_url:
            self.determine_protocol()

        url = f"{self.base_url}{endpoint}"
        encoded_data = urllib.parse.urlencode(data).encode("utf-8") if data else None
        
        # Clean headers matching browser requests exactly
        host_header = self.host if self.port in (80, 443) else f"{self.host}:{self.port}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)",
            "Referer": f"{self.protocol}://{host_header}/",
            "Origin": f"{self.protocol}://{host_header}",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        req = urllib.request.Request(url, data=encoded_data, headers=headers)
        try:
            with self.opener.open(req, timeout=7) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                try:
                    return json.loads(text)
                except Exception:
                    return {"raw": text}
        except urllib.error.HTTPError as he:
            # Gracefully handle 403/401/500 errors from BOA web server
            return {"error": he.code, "msg": str(he)}
        except Exception as ex:
            return {"error": -1, "msg": str(ex)}

    def login(self) -> bool:
        self.determine_protocol()
        
        # 1. Fetch clean session ID
        res = self._request("/cgi-bin/ajax?ajaxmethod=get_login_user")
        if not isinstance(res, dict) or "sessionid" not in res:
            res = self._request("/cgi-bin/ajax", data={"ajaxmethod": "get_login_user"})
            
        self.session_id = res.get("sessionid", "") if isinstance(res, dict) else ""
        if not self.session_id:
            raise RuntimeError("Could not acquire session ID from FiberHome router.")

        # 2. Encrypt password with pure Python AES-128
        encrypted_pass = fh_aes_encrypt(self.password)
        login_payload = {
            "ajaxmethod": "do_login",
            "username": self.username,
            "loginpd": encrypted_pass,
            "port": 0,
            "sessionid": self.session_id
        }
        
        resp = self._request("/cgi-bin/ajax", data=login_payload)
        if isinstance(resp, dict):
            res_code = resp.get("login_result")
            if res_code == 0:
                return True
            elif res_code in (1, 4):
                raise RuntimeError("FiberHome Authentication failed: Incorrect username or password (check credentials on router sticker, or try 'user' / 'user').")
            elif res_code == 2:
                # Session collision: reset stale session and retry
                self._request("/cgi-bin/ajax", data={
                    "ajaxmethod": "do_logout",
                    "username": "common",
                    "sessionid": self.session_id
                })
                # Re-fetch session id and retry once
                res2 = self._request("/cgi-bin/ajax?ajaxmethod=get_login_user")
                if isinstance(res2, dict) and res2.get("sessionid"):
                    self.session_id = res2["sessionid"]
                    login_payload["sessionid"] = self.session_id
                    resp2 = self._request("/cgi-bin/ajax", data=login_payload)
                    if isinstance(resp2, dict) and resp2.get("login_result") == 0:
                        return True
                raise RuntimeError("FiberHome: User already logged in elsewhere. Please logout from browser.")
            elif "error" in resp:
                raise RuntimeError(f"FiberHome HTTP Error {resp['error']}: {resp.get('msg', 'Forbidden')}")
            else:
                raise RuntimeError(f"FiberHome login failed (result code: {res_code})")
        
        raise RuntimeError("FiberHome returned invalid response during login.")

    def logout(self):
        if self.session_id:
            try:
                self._request("/cgi-bin/ajax", data={
                    "ajaxmethod": "do_logout",
                    "username": "common",
                    "sessionid": self.session_id
                })
            except Exception:
                pass

    def get_full_wan_status(self) -> dict:
        if not self.session_id:
            self.login()

        base = self._request(f"/cgi-bin/ajax?ajaxmethod=get_base_info&sessionid={self.session_id}")
        if isinstance(base, dict) and base.get("session_valid") == 0:
            self.login()
            base = self._request(f"/cgi-bin/ajax?ajaxmethod=get_base_info&sessionid={self.session_id}")

        model = base.get("ModelName", "HG6145") if isinstance(base, dict) and "error" not in base else "FiberHome ONT"
        uptime = str(base.get("uptime") or base.get("UpTime") or "0") if isinstance(base, dict) else "0"

        ip = "0.0.0.0"
        gw = "0.0.0.0"
        dns = ""
        wan_name = f"FiberHome {model}"
        status = "Disconnected"

        wan_resp = self._request(f"/cgi-bin/ajax?ajaxmethod=get_allwan_info_broadBand&sessionid={self.session_id}")
        if isinstance(wan_resp, dict) and (wan_resp.get("session_valid") == 0 or "error" in wan_resp):
            self.login()
            wan_resp = self._request(f"/cgi-bin/ajax?ajaxmethod=get_allwan_info_broadBand&sessionid={self.session_id}")

        wan_list = wan_resp.get("wan", []) if isinstance(wan_resp, dict) else []
        selected = None
        for w in wan_list:
            svc = str(w.get("ServiceList", "")).upper()
            iporppp = w.get("iporppp")
            if iporppp == 2 or ("INTERNET" in svc and "VOIP" not in svc):
                selected = w
                break
        if not selected and wan_list:
            selected = wan_list[0]

        if selected:
            raw_ip = selected.get("ExternalIPAddress") or selected.get("IPAddress") or "0.0.0.0"
            ip = str(raw_ip).replace("_point_", ".").strip()
            raw_gw = selected.get("DefaultGateway") or selected.get("RemoteIPAddress") or "0.0.0.0"
            gw = str(raw_gw).replace("_point_", ".").strip()
            raw_dns = selected.get("DNSServers") or selected.get("DNS") or ""
            dns = str(raw_dns).replace("_point_", ".").strip()
            wan_name = selected.get("Name") or f"FiberHome {model}"
            status = selected.get("ConnectionStatus") or selected.get("Status") or "Connected"
            uptime = str(selected.get("Uptime") or uptime)

        # Fallback to external IP probe if local interface returned 0.0.0.0 or 403
        if ip in ("0.0.0.0", "", None):
            _, _, ext_ip = check_cgnat("1.1.1.1")
            if ext_ip and ext_ip not in ("0.0.0.0", "Unknown"):
                ip = ext_ip
                status = "Connected"

        return {
            "driver": "FiberHome",
            "domain": "WAN1",
            "status": status,
            "name": wan_name,
            "ip": ip,
            "gateway": gw,
            "dns": dns,
            "bras": "FH_BRAS",
            "uptime_seconds": uptime
        }

    def reconnect_pppoe(self, delay: float = 1.0) -> bool:
        if not self.session_id:
            self.login()
        payload = {
            "ajaxmethod": "set_onu_reboot",
            "sessionid": self.session_id
        }
        try:
            self._request("/cgi-bin/ajax", data=payload)
        except Exception:
            pass
        return True


def detect_router_vendor(host: str, port: int) -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))

    for proto in ["https", "http"]:
        # 1. Huawei Check (RandCount hex token)
        try:
            req = urllib.request.Request(f"{proto}://{host}:{port}/asp/GetRandCount.asp")
            with opener.open(req, timeout=1.8) as r:
                data = r.read().decode("utf-8", errors="ignore").strip().lstrip("\ufeff").strip("'\" \r\n")
                if re.match(r"^[0-9a-fA-F]{16,}$", data):
                    return "huawei"
        except Exception:
            pass

        # 2. FiberHome Check (Ajax login method)
        try:
            req = urllib.request.Request(f"{proto}://{host}:{port}/cgi-bin/ajax?ajaxmethod=get_login_user")
            with opener.open(req, timeout=1.8) as r:
                if r.status in (200, 302):
                    return "fiberhome"
        except Exception:
            pass

        # 3. General root banner check
        try:
            req = urllib.request.Request(f"{proto}://{host}:{port}/")
            with opener.open(req, timeout=1.8) as r:
                body = r.read().decode("utf-8", errors="ignore").lower()
                if "fiberhome" in body:
                    return "fiberhome"
                if "huawei" in body:
                    return "huawei"
        except Exception:
            pass

    return "huawei"

def create_driver(vendor: str, host: str, port: int, user: str, password: str) -> BaseRouterDriver:
    v = (vendor or "").lower().strip()
    if v == "fiberhome":
        return FiberHomeDriver(host=host, port=port, username=user, password=password)
    else:
        return HuaweiDriver(host=host, port=port, username=user, password=password)

# ==============================================================================
# 4. SAFETY CIRCUIT BREAKER & ROTATION ENGINE
# ==============================================================================

class CircuitBreaker:
    def __init__(self, max_failures=3):
        self.max_failures = max_failures
        self.consecutive_failures = 0

    def record_success(self):
        self.consecutive_failures = 0

    def record_failure(self) -> bool:
        self.consecutive_failures += 1
        return self.consecutive_failures >= self.max_failures

    def trip_warning(self):
        print("\n" + "!"*56)
        print("  \033[1;31m⚠️  CIRCUIT BREAKER (Anti-Lockout Protection)\033[0m")
        print("!"*56)
        print("  3 consecutive reconnection timeouts detected.")
        print("  Rotation safely paused to prevent BRAS port lockout.")
        print("!"*56 + "\n")

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def render_spinner(frame_idx: int, elapsed: float, state_text: str):
    icon = SPINNER_FRAMES[frame_idx % len(SPINNER_FRAMES)]
    sys.stdout.write(f"\r  \033[1;36m{icon}\033[0m [{elapsed:4.1f}s] {state_text:<42}")
    sys.stdout.flush()

def matches_target_pools(ip: str, target_prefixes: list) -> bool:
    if not target_prefixes:
        return True
    for p in target_prefixes:
        p_clean = p.strip()
        if not p_clean:
            continue
        if not p_clean.endswith(".") and "." not in p_clean:
            p_clean = p_clean + "."
        if ip.startswith(p_clean):
            return True
    return False

def render_rotation_delta_card(old_ip: str, new_ip: str, old_ping: float, new_ping: float, 
                               duration: float, attempts: int, new_status: dict, cgnat_label: str, copied: bool):
    old_pool, _, _ = identify_ip_pool(old_ip)
    new_pool, new_desc, _ = identify_ip_pool(new_ip)

    if old_ping > 0 and new_ping > 0:
        diff = round(new_ping - old_ping, 1)
        if diff < 0:
            ping_delta_str = f"\033[1;32m{new_ping} ms (▼ {abs(diff)} ms {tr('faster')})\033[0m"
        elif diff > 0:
            ping_delta_str = f"\033[1;33m{new_ping} ms (▲ +{diff} ms)\033[0m"
        else:
            ping_delta_str = f"{new_ping} ms"
    else:
        ping_delta_str = f"{new_ping} ms"

    nat_badge = f"\033[1;32m✓ {cgnat_label}\033[0m" if "Public" in cgnat_label else f"\033[1;33m⚠ {cgnat_label}\033[0m"
    clip_badge = f" \033[1;32m{tr('copied')}\033[0m" if copied else ""

    print("\n╭" + "─"*58 + "╮")
    print(f"│            {tr('rotation_completed')}            │".center(58))
    print("├" + "─"*58 + "┤")
    print(f"│  {tr('ip_transition')} : \033[1;31m{old_ip}\033[0m ➔ \033[1;32m{new_ip}\033[0m{clip_badge}")
    print(f"│  {tr('assigned_pool')} : \033[1;36m{new_pool}\033[0m ({new_desc[:26]})")
    print(f"│  {tr('network_route')} : {nat_badge}")
    print(f"│  {tr('ping_latency')}  : {old_ping} ms ➔ {ping_delta_str}")
    print(f"│  {tr('bras_node')}   : {new_status.get('bras', 'N/A')} (GW: {new_status.get('gateway', '0.0.0.0')})")
    print(f"│  {tr('cycle_time')}   : {duration:.2f}s ({attempts} {'attempt' if attempts == 1 else 'attempts'})")
    print("╰" + "─"*58 + "╯")

def perform_smart_rotation(
    client: BaseRouterDriver, 
    until_different=False, 
    unique_ever=False, 
    target_pools=None, 
    max_ping_ms=0,
    max_attempts=15,
    timeout=25,
    quiet=False
) -> tuple:
    circuit_breaker = CircuitBreaker()
    history = load_history()
    seen_ips = {item["new_ip"] for item in history} if unique_ever else set()
    
    current = client.get_full_wan_status()
    old_ip = current['ip']
    old_ping = measure_ping_tcp("1.1.1.1", 53)
    
    if not quiet:
        pool_name, _, _ = identify_ip_pool(old_ip)
        print(f"\n[*] {tr('current_ip')} : \033[1;33m{old_ip}\033[0m [{pool_name}] (BRAS: {current.get('bras', 'N/A')})")
        if target_pools:
            print(f"[*] {tr('target_filter', pools=', '.join(target_pools))}")
        if max_ping_ms > 0:
            print(f"[*] {tr('latency_target', ms=max_ping_ms)}")
    
    attempt = 1
    total_start = time.time()
    frame_idx = 0
    
    is_fh = isinstance(client, FiberHomeDriver)
    effective_timeout = max(timeout, 70) if is_fh else timeout

    while attempt <= max_attempts:
        cycle_start = time.time()
        ok = client.reconnect_pppoe()
        if ok is False and not quiet:
            print(f"\n\033[1;31m[!] Warning: Router did not accept reconnection command. Check credentials/model.\033[0m")
        
        new_ip = None
        new_status = None
        elapsed = 0
        
        while elapsed < effective_timeout:
            time.sleep(1.0 if is_fh else 0.5)
            frame_idx += 1
            elapsed = time.time() - cycle_start
            
            try:
                st = client.get_full_wan_status()
                curr_status = st["status"]
                curr_ip = st["ip"]
                
                if is_fh and elapsed < 15 and curr_ip == old_ip:
                    if not quiet:
                        render_spinner(frame_idx, elapsed, "Rebooting ONT...")
                    continue

                if not quiet:
                    if curr_status == "Disconnected":
                        render_spinner(frame_idx, elapsed, tr("resetting_session"))
                    elif curr_status == "Connecting":
                        render_spinner(frame_idx, elapsed, tr("negotiating_lease"))
                    elif curr_status == "Connected" and curr_ip not in ("0.0.0.0", ""):
                        render_spinner(frame_idx, elapsed, tr("validating_ip", ip=curr_ip))
                        new_ip = curr_ip
                        new_status = st
                        break
                    else:
                        render_spinner(frame_idx, elapsed, f"State: {curr_status}...")
                else:
                    if curr_status == "Connected" and curr_ip not in ("0.0.0.0", ""):
                        new_ip = curr_ip
                        new_status = st
                        break
            except Exception:
                if not quiet:
                    render_spinner(frame_idx, elapsed, tr("handshaking"))

        if not quiet:
            sys.stdout.write("\r" + " "*60 + "\r")
            sys.stdout.flush()
        
        if not new_ip:
            if circuit_breaker.record_failure():
                circuit_breaker.trip_warning()
                return old_ip, None
            if not quiet:
                print(f"\033[1;31m[!] Timeout ({effective_timeout}s).\033[0m")
            return old_ip, None

        circuit_breaker.record_success()

        # Filter Verification
        re_cycle_reason = None
        if until_different and new_ip == old_ip:
            re_cycle_reason = f"Identical IP ({new_ip})"
        elif unique_ever and new_ip in seen_ips:
            re_cycle_reason = f"Previously seen IP ({new_ip})"
        elif target_pools and not matches_target_pools(new_ip, target_pools):
            re_cycle_reason = f"Target mismatch [{', '.join(target_pools)}] (got {new_ip})"
        elif max_ping_ms > 0:
            ping_val = measure_ping_tcp("1.1.1.1", 53)
            if ping_val > max_ping_ms:
                re_cycle_reason = f"Ping {ping_val}ms > {max_ping_ms}ms"

        if re_cycle_reason:
            if not quiet:
                print(f"  \033[1;33m[Attempt {attempt}/{max_attempts}] ↺ {tr('re_cycling', reason=re_cycle_reason)}\033[0m")
            attempt += 1
            time.sleep(1.0)
            continue
        
        break

    if attempt > max_attempts:
        if not quiet:
            print(f"\033[1;31m[!] Max attempts reached ({max_attempts}).\033[0m")
        return old_ip, new_ip

    total_duration = time.time() - total_start
    new_ping = measure_ping_tcp("1.1.1.1", 53)
    is_cgnat, cgnat_label, _ = check_cgnat(new_ip)

    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "old_ip": old_ip,
        "new_ip": new_ip,
        "duration": f"{total_duration:.2f}s",
        "bras": new_status.get("bras", "N/A"),
        "latency_ms": new_ping,
        "cgnat": cgnat_label,
        "pool": identify_ip_pool(new_ip)[0]
    }
    history.append(record)
    save_history(history)

    copied = copy_to_clipboard(new_ip)
    send_os_notification("DZ WAN IP Changed", f"New IP: {new_ip} ({total_duration:.1f}s)")

    if not quiet:
        render_rotation_delta_card(
            old_ip=old_ip,
            new_ip=new_ip,
            old_ping=old_ping,
            new_ping=new_ping,
            duration=total_duration,
            attempts=attempt,
            new_status=new_status,
            cgnat_label=cgnat_label,
            copied=copied
        )
    return old_ip, new_ip

# ==============================================================================
# 5. REST MICRO-DAEMON SERVER (`--serve <port>`)
# ==============================================================================

class RotatorApiHandler(BaseHTTPRequestHandler):
    client: BaseRouterDriver = None

    def _send_json(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/help"):
            self._send_json({
                "app": "DZ IP Rotator REST Daemon v5.0",
                "developer": "Azeddine (https://t.me/x4D7217A7A6F)",
                "endpoints": {
                    "GET /status": "Current WAN status, IP, CGNAT, Latency",
                    "GET /bench": "Multi-server latency benchmark",
                    "POST /rotate": "Execute instant IP rotation",
                    "GET /rotate": "Rotate with query params (?pool=105,154&max_ping=30)"
                }
            })
        elif path == "/status":
            try:
                self.client.login()
                st = self.client.get_full_wan_status()
                lat = measure_ping_tcp("1.1.1.1", 53)
                is_cgnat, cgnat_label, _ = check_cgnat(st["ip"])
                pool_name, pool_desc, _ = identify_ip_pool(st["ip"])
                self._send_json({
                    "status": "ok",
                    "ip": st["ip"],
                    "pool": pool_name,
                    "pool_desc": pool_desc,
                    "cgnat": is_cgnat,
                    "cgnat_label": cgnat_label,
                    "latency_ms": lat,
                    "gateway": st.get("gateway", "0.0.0.0"),
                    "bras": st.get("bras", "N/A"),
                    "uptime_seconds": st.get("uptime_seconds", "0")
                })
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)

        elif path == "/bench":
            results = run_benchmark()
            self._send_json({"status": "ok", "benchmark": results})

        elif path == "/rotate":
            self._handle_rotate(query)
        else:
            self._send_json({"status": "error", "message": "Not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/rotate":
            self._handle_rotate(query)
        else:
            self._send_json({"status": "error", "message": "Not found"}, 404)

    def _handle_rotate(self, query):
        pools_raw = query.get("pool", [""])[0]
        pools = [p.strip() for p in pools_raw.split(",") if p.strip()] if pools_raw else []
        max_ping = float(query.get("max_ping", [0])[0])

        try:
            self.client.login()
            t0 = time.time()
            old_ip, new_ip = perform_smart_rotation(
                self.client,
                until_different=True,
                target_pools=pools,
                max_ping_ms=max_ping,
                quiet=True
            )
            duration = round(time.time() - t0, 2)
            lat = measure_ping_tcp("1.1.1.1", 53)
            is_cgnat, cgnat_label, _ = check_cgnat(new_ip)
            pool_name, _, _ = identify_ip_pool(new_ip)

            self._send_json({
                "status": "success",
                "old_ip": old_ip,
                "new_ip": new_ip,
                "duration_seconds": duration,
                "latency_ms": lat,
                "pool": pool_name,
                "cgnat": is_cgnat,
                "cgnat_label": cgnat_label
            })
        except Exception as e:
            self._send_json({"status": "error", "message": str(e)}, 500)

def start_rest_daemon(client: BaseRouterDriver, port=8080):
    RotatorApiHandler.client = client
    server = HTTPServer(("0.0.0.0", port), RotatorApiHandler)
    print("\n" + "═"*58)
    print(f"  🚀 DZ IP REST API Running on port \033[1;32m{port}\033[0m")
    print("═"*58)
    print(f"  • Status endpoint : GET  http://localhost:{port}/status")
    print(f"  • Rotate endpoint : POST http://localhost:{port}/rotate")
    print(f"  • Benchmark       : GET  http://localhost:{port}/bench")
    print("\n  Press Ctrl+C to terminate server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDaemon terminated.")

# ==============================================================================
# 6. CONFIGURATION WIZARD & CREDENTIALS
# ==============================================================================

def load_saved_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    elif LEGACY_CONFIG.exists():
        try:
            with open(LEGACY_CONFIG, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config_data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass

def prompt_language_choice() -> str:
    print("\n  🌐 Select Language / Choisissez la langue:")
    print("    [1] English (EN)")
    print("    [2] Français (FR)")
    choice = input("  Choice / Choix [1-2, default: 1]: ").strip()
    return "fr" if choice == "2" else "en"

def run_setup_wizard() -> dict:
    print("\n" + "═"*56)
    print("  🔑 Router Setup & Auto-Discovery Wizard")
    print("═"*56)

    current_cfg = load_saved_config()
    detected_gw = detect_default_gateway()
    default_host = current_cfg.get("host", detected_gw)
    default_port = current_cfg.get("port", 80)
    default_user = current_cfg.get("username", "telecomadmin")

    print(f"\n[?] Auto-detected default gateway: \033[1;36m{detected_gw}\033[0m")
    host_input = input(f"Router IP / Host [{default_host}]: ").strip()
    host = host_input if host_input else default_host

    port_input = input(f"Router Web Port [{default_port}]: ").strip()
    try:
        port = int(port_input) if port_input else default_port
    except ValueError:
        port = default_port

    detected_vendor = detect_router_vendor(host, port)
    print(f"[?] Auto-detected router brand: \033[1;32m{detected_vendor.upper()}\033[0m")
    print("  [1] Huawei EchoLife / OptiXstar (HG8145X6, HG8145V5, HG8245)")
    print("  [2] FiberHome (HG6145, HG6143, AN5506)")
    vendor_ch = input("Select brand [1-2, default: auto-detected]: ").strip()

    if vendor_ch == "1": vendor = "huawei"
    elif vendor_ch == "2": vendor = "fiberhome"
    else: vendor = detected_vendor

    print("\nCommon Username Presets:")
    if vendor == "fiberhome":
        print("  [1] user (Default Algérie Télécom FiberHome user)")
        print("  [2] admin")
        print("  [3] telecomadmin")
        print("  [4] Custom username")
        preset = input("Select username preset [1-4, default: 1]: ").strip()
        if preset == "2": username = "admin"
        elif preset == "3": username = "telecomadmin"
        elif preset == "4": username = input("Enter custom username: ").strip()
        else: username = "user"
    else:
        print("  [1] telecomadmin (Default Algérie Télécom Superuser)")
        print("  [2] admin")
        print("  [3] root")
        print("  [4] Custom username")
        preset = input("Select username preset [1-4, default: 1]: ").strip()
        if preset == "2": username = "admin"
        elif preset == "3": username = "root"
        elif preset == "4": username = input("Enter custom username: ").strip()
        else: username = default_user if default_user else "telecomadmin"

    default_pass = current_cfg.get("password", "")
    pass_prompt = f"Enter router password for '{username}'"
    if default_pass:
        pass_prompt += f" [press Enter to keep saved]: "
    else:
        pass_prompt += ": "

    password = input(pass_prompt).strip()
    if not password and default_pass:
        password = default_pass
    while not password:
        print("Password cannot be empty.")
        password = input(f"Enter router password for '{username}': ").strip()

    if any('\u0600' <= c <= '\u06ff' for c in password):
        print("\033[1;33m⚠️ Warning: Your password contains Arabic characters. Verify your keyboard language layout!\033[0m")

    print("\nTesting connection...")
    driver = create_driver(vendor, host, port, username, password)
    try:
        driver.login()
        st = driver.get_full_wan_status()
        driver.logout()
        print(f"\033[1;32m✓ Verified connection to '{st.get('name', 'Router')}' (IP: {st['ip']})\033[0m")
    except Exception as e:
        print(f"\033[1;31m✗ Verification failed: {e}\033[0m")
        retry = input("Save credentials anyway? (y/N): ").strip().lower()
        if retry != "y":
            sys.exit(1)

    cfg = {
        "vendor": vendor,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "lang": CURRENT_LANG
    }
    save_config(cfg)
    print(f"\033[1;32m✓ Saved to {CONFIG_FILE}\033[0m\n")
    return cfg

def resolve_credentials(args) -> dict:
    global CURRENT_LANG
    saved = load_saved_config()

    # Determine language
    if args.lang:
        CURRENT_LANG = "fr" if args.lang.lower().startswith("fr") else "en"
    elif "lang" in saved:
        CURRENT_LANG = saved["lang"]
    elif not args.json and not args.rotate and not args.status and not args.bench:
        # Prompt only on interactive startup
        CURRENT_LANG = prompt_language_choice()
        saved["lang"] = CURRENT_LANG
        save_config(saved)

    if args.host or args.user or args.password:
        return {
            "vendor": args.vendor or "huawei",
            "host": args.host or detect_default_gateway(),
            "port": args.port or 80,
            "username": args.user or "telecomadmin",
            "password": args.password or "",
            "lang": CURRENT_LANG
        }

    env_user = os.environ.get("ROUTER_USER") or os.environ.get("HUAWEI_ROUTER_USER")
    env_pass = os.environ.get("ROUTER_PASS") or os.environ.get("HUAWEI_ROUTER_PASS")
    if env_user and env_pass:
        return {
            "vendor": os.environ.get("ROUTER_VENDOR", "huawei"),
            "host": os.environ.get("ROUTER_HOST", detect_default_gateway()),
            "port": int(os.environ.get("ROUTER_PORT", 80)),
            "username": env_user,
            "password": env_pass,
            "lang": CURRENT_LANG
        }

    if saved.get("username") and saved.get("password"):
        if "vendor" not in saved:
            saved["vendor"] = detect_router_vendor(saved.get("host", "192.168.100.1"), saved.get("port", 80))
        saved["lang"] = CURRENT_LANG
        return saved

    return run_setup_wizard()

# ==============================================================================
# 7. INTERACTIVE TUI DASHBOARD
# ==============================================================================

def print_status_dashboard(client: BaseRouterDriver):
    st = client.get_full_wan_status()
    latency = measure_ping_tcp("1.1.1.1", 53)
    is_cgnat, cgnat_label, _ = check_cgnat(st['ip'])
    pool_name, pool_desc, pool_color = identify_ip_pool(st['ip'])

    if st['ip'] in ("0.0.0.0", "None", "", None):
        cgnat_badge = "\033[1;31m✗ No IP\033[0m"
    elif is_cgnat:
        cgnat_badge = f"\033[1;33m⚠ {cgnat_label}\033[0m"
    else:
        cgnat_badge = f"\033[1;32m✓ {tr('public_badge')}\033[0m"
    lat_color = "\033[1;32m" if latency < 35 else ("\033[1;33m" if latency < 60 else "\033[1;31m")
    ping_badge = f"{lat_color}{latency} ms\033[0m (1.1.1.1)"

    print("\n╭" + "─"*58 + "╮")
    print(f"│  🌐 {tr('title')}")
    print("├" + "─"*58 + "┤")
    print(f"│  {tr('router_target')}: {client.base_url}")
    print(f"│  {tr('hardware_os')}  : {client.vendor_name}")
    print(f"│  {tr('internet_wan')} : {st['name']} ● \033[1;32m{st['status']}\033[0m (Uptime: {format_uptime(st.get('uptime_seconds', 0))})")
    print("├" + "─"*58 + "┤")
    print(f"│  {tr('current_ip')}   : \033[1;32m{st['ip']}\033[0m [{cgnat_badge}]")
    print(f"│  {tr('pool_subnet')}  : {pool_color}{pool_name}\033[0m │ BRAS: {st.get('bras', 'N/A')}")
    print(f"│  {tr('ping_latency')} : {ping_badge} │ DNS: {st.get('dns', 'N/A')}")
    print("╰" + "─"*58 + "╯")

def view_history():
    history = load_history()
    print("\n" + "═"*60)
    print(f"  📜 {tr('history_title')}")
    print("═"*60)
    if not history:
        print(f"  {tr('history_empty')}")
    else:
        print(f"  {tr('total_rotations', count=len(history))}\n")
        print("  Recent 10:")
        for idx, entry in enumerate(history[-10:], 1):
            lat = f"{entry.get('latency_ms', '--')}ms"
            pool = entry.get('pool', '')
            print(f"  {idx:2d}. [{entry['timestamp']}] {entry['old_ip']:<15} ➔ {entry['new_ip']:<15} [{lat:<6}] {pool}")
    print("═"*60)

def interactive_pool_selector(client: BaseRouterDriver):
    print("\n" + "═"*58)
    print(f"  🎯 {tr('pool_selector_title')}")
    print("═"*58)
    print(f"  [1] ⚡ {tr('pool_105')}")
    print(f"  [2] 🚀 {tr('pool_154')}")
    print(f"  [3] 🏛️ {tr('pool_41')}")
    print(f"  [4] 📍 {tr('pool_197')}")
    print(f"  [5] 🌟 {tr('pool_dual')}")
    print(f"  [6] ✍️  {tr('pool_custom')}")
    print(f"  [b] {tr('pool_back')}\n")
    
    choice = input("Select [1-6, b]: ").strip().lower()
    targets = []
    
    if choice == "1": targets = ["105."]
    elif choice == "2": targets = ["154."]
    elif choice == "3": targets = ["41."]
    elif choice == "4": targets = ["197."]
    elif choice == "5": targets = ["105.", "154."]
    elif choice == "6":
        custom = input("Enter prefix (e.g. 105.106, 154): ").strip()
        if custom:
            targets = [p.strip() for p in custom.split(",") if p.strip()]
    elif choice == "b":
        return

    if not targets:
        print("Invalid selection.")
        return

    perform_smart_rotation(client, target_pools=targets)
    input(f"\n{tr('press_enter')}")

def interactive_benchmark_screen():
    print("\n" + "═"*60)
    print(f"  📊 {tr('bench_title')}")
    print("═"*60)
    print(f"  {tr('bench_probing')}\n")
    
    results = run_benchmark()
    print(f"  {'Service / Target':<26} │ {'IP Address':<15} │ {'Latency'}")
    print("  " + "─"*56)
    for label, host, lat in results:
        if lat > 0:
            color = "\033[1;32m" if lat < 35 else ("\033[1;33m" if lat < 60 else "\033[1;31m")
            lat_str = f"{color}{lat:5.1f} ms\033[0m"
        else:
            lat_str = "\033[1;31mTimeout\033[0m"
        print(f"  {label:<26} │ {host:<15} │ {lat_str}")
    print("═"*60)

def toggle_language():
    global CURRENT_LANG
    CURRENT_LANG = "en" if CURRENT_LANG == "fr" else "fr"
    cfg = load_saved_config()
    cfg["lang"] = CURRENT_LANG
    save_config(cfg)

def interactive_menu(client: BaseRouterDriver):
    print_banner()
    while True:
        try:
            client.login()
            print_status_dashboard(client)
        except Exception as e:
            print(f"\n\033[1;31m[Error] {e}\033[0m")
            print("  [1] Reconfigure credentials")
            print("  [q] Exit")
            ch = input("Select: ").strip().lower()
            if ch == "1":
                cfg = run_setup_wizard()
                client = create_driver(cfg["vendor"], cfg["host"], cfg["port"], cfg["username"], cfg["password"])
                continue
            else:
                break

        print(f"\n  \033[1;36m[1]\033[0m {tr('menu_rotate')}")
        print(f"  \033[1;36m[2]\033[0m {tr('menu_pool')}")
        print(f"  \033[1;36m[3]\033[0m {tr('menu_ping')}")
        print(f"  \033[1;36m[4]\033[0m {tr('menu_unique')}")
        print(f"  \033[1;36m[5]\033[0m {tr('menu_timer')}")
        print(f"  \033[1;36m[6]\033[0m {tr('menu_bench')}")
        print(f"  \033[1;36m[7]\033[0m {tr('menu_history')}")
        print(f"  \033[1;36m[8]\033[0m {tr('menu_copy')}")
        print(f"  \033[1;36m[0]\033[0m {tr('menu_creds')}")
        print(f"  \033[1;36m[l]\033[0m {tr('menu_lang')}")
        print(f"  \033[1;36m[r]\033[0m {tr('menu_refresh')}   \033[1;36m[q]\033[0m {tr('menu_quit')}\n")

        print(tr("press_key"), end="", flush=True)
        choice = get_single_keypress().lower()
        print(choice)

        if choice == "1":
            perform_smart_rotation(client, until_different=False)
            input(f"\n{tr('press_enter')}")
        elif choice == "2":
            interactive_pool_selector(client)
        elif choice == "3":
            threshold_in = input("Target max ping (ms) [default: 25]: ").strip()
            max_ms = float(threshold_in) if threshold_in else 25.0
            perform_smart_rotation(client, max_ping_ms=max_ms)
            input(f"\n{tr('press_enter')}")
        elif choice == "4":
            perform_smart_rotation(client, unique_ever=True)
            input(f"\n{tr('press_enter')}")
        elif choice == "5":
            try:
                interval_input = input("Interval (minutes) [default: 10]: ").strip()
                interval_min = float(interval_input) if interval_input else 10.0
                interval_sec = interval_min * 60
                print(f"\n[*] Auto-rotation loop ({interval_min} min). Ctrl+C to stop.")
                while True:
                    perform_smart_rotation(client, until_different=True)
                    time.sleep(interval_sec)
            except KeyboardInterrupt:
                print("\nStopped.")
                time.sleep(1)
        elif choice == "6":
            interactive_benchmark_screen()
            input(f"\n{tr('press_enter')}")
        elif choice == "7":
            view_history()
            input(f"\n{tr('press_enter')}")
        elif choice == "8":
            st = client.get_full_wan_status()
            if copy_to_clipboard(st['ip']):
                print(f"\033[1;32m{tr('copied_success', ip=st['ip'])}\033[0m")
            else:
                print(f"\033[1;33m{tr('clipboard_not_found', ip=st['ip'])}\033[0m")
            time.sleep(1.2)
        elif choice == "0":
            cfg = run_setup_wizard()
            client = create_driver(cfg["vendor"], cfg["host"], cfg["port"], cfg["username"], cfg["password"])
        elif choice == "l":
            toggle_language()
        elif choice == "r":
            continue
        elif choice in ("q", "\x03", "\x1b"):
            print("Exiting.")
            client.logout()
            break

# ==============================================================================
# 8. CLI PARSER & MAIN ENTRY POINT
# ==============================================================================

def main():
    if os.name == 'nt':
        os.system("")  # Enable ANSI escape sequences on Windows console

    parser = argparse.ArgumentParser(
        description="DZ IP ROTATOR & ROUTE OPTIMIZER (Algérie Télécom Edition v5.0)"
    )
    parser.add_argument("-r", "--rotate", action="store_true", help="Rotate WAN IP immediately and exit")
    parser.add_argument("-u", "--until-different", action="store_true", help="Rotate until leased IP differs from current")
    parser.add_argument("-p", "--pool", default="", help="Target IP pool or prefix (e.g. '105', '154', '41', or '105.106.')")
    parser.add_argument("--unique-ever", action="store_true", help="Rotate until leased IP was never seen in history")
    parser.add_argument("--max-ping", type=float, default=0, help="Rotate until ping latency to 1.1.1.1 is under X ms")
    parser.add_argument("--bench", action="store_true", help="Run multi-server latency benchmark and exit")
    parser.add_argument("-s", "--status", action="store_true", help="Show live WAN dashboard and exit")
    parser.add_argument("--history", action="store_true", help="Print persistent rotation history and exit")
    parser.add_argument("-c", "--configure", action="store_true", help="Run interactive credential setup wizard")
    parser.add_argument("--lang", choices=["en", "fr"], default=None, help="Set language: 'en' for English, 'fr' for Français")
    parser.add_argument("--serve", type=int, default=0, metavar="PORT", help="Run as lightweight REST API daemon on port (e.g. 8080)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON (ideal for scripts & bots)")
    parser.add_argument("--vendor", choices=["huawei", "fiberhome"], default=None, help="Force router driver vendor")
    parser.add_argument("--host", default=None, help="Router IP / Gateway (default: auto-detected)")
    parser.add_argument("--port", type=int, default=None, help="Router Port (default: 80)")
    parser.add_argument("--user", default=None, help="Router username")
    parser.add_argument("--password", default=None, help="Router password")
    parser.add_argument("--timeout", type=int, default=25, help="Reconnection timeout in seconds (default: 25s)")
    args = parser.parse_args()

    if args.history:
        view_history()
        return

    if args.bench:
        interactive_benchmark_screen()
        return

    if args.configure:
        run_setup_wizard()
        return

    creds = resolve_credentials(args)
    client = create_driver(
        vendor=creds.get("vendor", "huawei"),
        host=creds["host"],
        port=creds["port"],
        user=creds["username"],
        password=creds["password"]
    )

    try:
        if args.serve > 0:
            start_rest_daemon(client, port=args.serve)
            return

        if args.status:
            client.login()
            if args.json:
                st = client.get_full_wan_status()
                lat = measure_ping_tcp("1.1.1.1", 53)
                is_cgnat, cgnat_label, _ = check_cgnat(st["ip"])
                pool_name, _, _ = identify_ip_pool(st["ip"])
                print(json.dumps({
                    "ip": st["ip"],
                    "pool": pool_name,
                    "cgnat": is_cgnat,
                    "cgnat_label": cgnat_label,
                    "latency_ms": lat,
                    "gateway": st.get("gateway", "0.0.0.0"),
                    "bras": st.get("bras", "N/A"),
                    "driver": client.vendor_name
                }, indent=2))
            else:
                print_status_dashboard(client)
            client.logout()
            return

        target_prefixes = [p.strip() for p in args.pool.split(",") if p.strip()] if args.pool else []

        if args.rotate or args.until_different or args.unique_ever or args.max_ping > 0 or target_prefixes:
            client.login()
            t0 = time.time()
            old_ip, new_ip = perform_smart_rotation(
                client,
                until_different=args.until_different or bool(target_prefixes),
                unique_ever=args.unique_ever,
                target_pools=target_prefixes,
                max_ping_ms=args.max_ping,
                timeout=args.timeout,
                quiet=args.json
            )
            client.logout()
            if args.json:
                lat = measure_ping_tcp("1.1.1.1", 53)
                is_cgnat, cgnat_label, _ = check_cgnat(new_ip)
                pool_name, _, _ = identify_ip_pool(new_ip)
                print(json.dumps({
                    "success": bool(new_ip),
                    "old_ip": old_ip,
                    "new_ip": new_ip,
                    "duration_seconds": round(time.time() - t0, 2),
                    "latency_ms": lat,
                    "pool": pool_name,
                    "cgnat": is_cgnat,
                    "cgnat_label": cgnat_label
                }))
            return

        interactive_menu(client)

    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"\033[1;31m[Error] {e}\033[0m")
        sys.exit(1)
    finally:
        try:
            client.logout()
        except Exception:
            pass

if __name__ == "__main__":
    main()
