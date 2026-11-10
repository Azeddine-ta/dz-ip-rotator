# ⚡ DZ IP Rotator & Route Optimizer
### Algérie Télécom WAN Automation & Subnet Optimizer

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20Termux%20%7C%20macOS-lightgrey.svg)]()
[![ISP](https://img.shields.io/badge/ISP-Algérie%20Télécom%20(FTTH%20%2F%20VDSL)-orange.svg)]()
[![Telegram](https://img.shields.io/badge/Telegram-@x4D7217A7A6F-2CA5E0.svg?logo=telegram)](https://t.me/x4D7217A7A6F)

A lightweight, zero-dependency Python tool to rotate WAN IP addresses, hunt optimal gaming routes, and target specific IP subnets (`105.x`, `154.x`, `41.x`, `197.x`) on **Algérie Télécom** fibre and DSL connections.

> 📖 **[اضغط هنا لقراءة الدليل الكامل باللغة العربية (README_AR.md)](README_AR.md)**

---

```text
  ___  ____    ___ ____   ___  ___ _____ ___  ____  
 |   \/__  /  |_ _|  _ \ | _ \/ _ \_   _/ _ \| _ \ 
 | |) | / /    | ||  _/  |   / (_) || || (_) |   / 
 |___/ /_/    |___|_|    |_|_\___/ |_| \___/|_|_\ 
       ⚡ Algérie Télécom Optimizer v5.0 ⚡
      Dev: Azeddine  •  https://t.me/x4D7217A7A6F
```

---

## 🎯 Why this tool?

On Algérie Télécom (Idoom Fibre / VDSL / ADSL):
1. **Subnet Routing & Latency Variations:** Certain IP pools (e.g. `105.x` vs `154.x` vs `41.x`) have vastly different transit routes, some adding severe latency towards European game servers (Paris, Frankfurt, Madrid).
2. **Suboptimal Routing Paths:** Reconnecting automatically finds the fastest submarine cable route with minimal ping.
3. **Slow Router Reboots:** Restarting the optical network terminal (ONT) takes 2-3 minutes. This tool bounces the PPPoE session directly via web APIs in **under 3 seconds**.

---

## 🧪 Tested & Confirmed Hardware (Real-World Verified)

This utility was developed and **rigorously tested in real-world conditions on Algérie Télécom (Idoom Fibre)** on the following hardware:

| Brand / ONT Model | Firmware / Notes | Status |
| :--- | :--- | :---: |
| **Huawei EchoLife / OptiXstar** (HG8145V5, HG8245H, HG8145X6) | Tested with `telecomadmin` & `admin`. Instant WAN bounce. | ✅ **Verified & Working** |
| **FiberHome** (HG6145D2, HG6145F1) | Tested on HG6145D2 with custom AES-128 login encryption. | ✅ **Verified & Working** |

---

## 🚀 Features

* **Zero Dependencies:** Built entirely with Python's standard library (`urllib`, `socket`, `json`). No `pip install` required.
* **Multi-Vendor Router Support:**
  * **Huawei EchoLife / OptiXstar** (HG8145X6, HG8145V5, HG8245H, HG8245W5)
  * **FiberHome** (HG6145D2, HG6145F1, AN5506) — with built-in pure-Python AES-128-CBC auth cipher
* **Auto-Discovery:** Automatically detects gateway IP (`192.168.1.1`) and fingerprints router brand on first run.
* **Smart Gaming Route Hunter:** Automatically cycles IPs until ping to gaming / DNS benchmarks drops below your target threshold (e.g. `< 20ms` or `< 25ms`).
* **IP Pool Hunter:** Force rotation until you land on your preferred pool (`105`, `154`, `41`, `197`).
* **REST API Daemon:** Built-in lightweight HTTP server (`--serve 8080`) to trigger rotations from external bots or scripts.
* **Multi-Language TUI:** Interactive console interface supporting both English and French.

---

## 📦 Quick Start (Get Started in 10 Seconds)

### 📱 Android (Termux) — 1-Line Run:
Open Termux and paste:
```bash
pkg update && pkg install -y python curl && curl -sSL https://raw.githubusercontent.com/Azeddine-ta/dz-ip-rotator/main/change_ip.py -o change_ip.py && python change_ip.py
```

### 🐧 Linux / macOS — 1-Line Run:
```bash
curl -sSL https://raw.githubusercontent.com/Azeddine-ta/dz-ip-rotator/main/change_ip.py -o change_ip.py && python3 change_ip.py
```

### 🪟 Windows — 1-Click Run:
1. Download this repo as a ZIP (`Code` > `Download ZIP`) or `git clone`.
2. Extract the folder and double-click **`run.bat`**!

---

## 🎮 Interactive Menu (TUI)

```text
╭──────────────────────────────────────────────────────────╮
│  🌐 Algérie Télécom WAN & Route Optimizer v5.0
├──────────────────────────────────────────────────────────┤
│  Router Target: http://192.168.1.1:80
│  Hardware/OS  : FiberHome HG6145D2
│  Internet WAN : Connected (Uptime: 04h 12m)
├──────────────────────────────────────────────────────────┤
│  Current IP   : 105.106.12.34 [✓ Public 1:1]
│  Pool Subnet  : 41.x (Algiers/Centre) │ BRAS: FH_BRAS
│  Ping Latency : 17.4 ms (1.1.1.1)
╰──────────────────────────────────────────────────────────╯

  [1] ⚡ Fast IP Rotate (Instant Single Cycle)
  [2] 🎯 Target Specific IP Pool (105.x, 154.x, 41.x, 197.x)
  [3] 🎮 Smart Gaming Route Hunter (Target Ping < X ms)
  [4] 💎 Rotate Until Never-Seen IP (Permanent Unique)
  [5] ⏱️ Auto-Rotate Timer Loop
  [6] 📊 Multi-Server Latency Benchmark
  [7] 📜 View IP History
  [8] 📋 Copy Current IP to Clipboard
  [0] 🔑 Reconfigure Router Credentials
  [l] 🌐 Switch Language / Changer de langue (FR/EN)
  [r] 🔄 Refresh Dashboard   [q] 🚪 Quit
```

---

## 💻 CLI & Automation Examples

You can run the script non-interactively for headless servers, scheduled tasks (cron), or bots:

```bash
# Instant single rotation and exit
python3 change_ip.py -r

# Rotate until you get an IP different from current
python3 change_ip.py -r -u

# Force rotation into 105.x subnet
python3 change_ip.py -r -p 105

# Hunt for gaming route with ping under 20ms (Valorant, CS2, etc.)
python3 change_ip.py -r --max-ping 20

# Output status in JSON format (for scripts & bots)
python3 change_ip.py -s --json

# Run latency benchmark across Cloudflare, Google, Quad9
python3 change_ip.py --bench
```

### JSON Output Sample (`-s --json`)
```json
{
  "ip": "105.106.12.34",
  "status": "Connected",
  "uptime": "04h 12m",
  "ping_ms": 17.4,
  "is_cgnat": false,
  "pool": "105.x",
  "vendor": "fiberhome"
}
```

---

## 🌐 Built-in REST API Daemon

Launch background server on port `8080`:
```bash
python3 change_ip.py --serve 8080
```

Trigger actions via standard HTTP requests:
```bash
# Query current WAN status
curl http://127.0.0.1:8080/status

# Trigger instant rotation
curl http://127.0.0.1:8080/rotate

# Rotate with target pool and max ping threshold
curl "http://127.0.0.1:8080/rotate?pool=105&max_ping=25"
```

---

## 🔒 Security & Privacy

* Credentials entered during the setup wizard are saved locally at `~/.config/dz-ip-changer/config.json` with strict user-only permissions (`0600`).
* No telemetry, no third-party tracking, and no external servers contacted except standard public DNS ping probes (Cloudflare `1.1.1.1` and Google `8.8.8.8`).

---

## 👤 Author

* **Developer:** Azeddine
* **Telegram:** [@x4D7217A7A6F](https://t.me/x4D7217A7A6F)
* **GitHub:** [@Azeddine-ta](https://github.com/Azeddine-ta)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

