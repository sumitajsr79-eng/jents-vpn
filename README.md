# ⚡ Jents VPN (v1.0.0) — Autonomous Quantum Privacy & Network Tunnel

[![Download Jents_VPN.exe](https://img.shields.io/badge/⚡_DOWNLOAD_JENTS_VPN.EXE-CLICK_HERE_TO_DOWNLOAD-00f0ff?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/Jents_VPN.exe)
[![Download IP_Detector.exe](https://img.shields.io/badge/🔍_DOWNLOAD_IP_DETECTOR.EXE-CLICK_HERE_TO_DOWNLOAD-00ff9d?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/IP_Detector.exe)

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![Version: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-purple.svg)](https://github.com/sumitajsr79-eng/jents-vpn/releases/tag/v1.0.0)

> 💡 **HOW TO DOWNLOAD DIRECTLY:**
> * When you click a file name in the GitHub file list above, GitHub opens its code/preview page.
> * To download the executable directly with **1-click**, **click the big blue download button above** or click the direct links below!

---

## 📥 Direct 1-Click Downloads (`.exe`)

| Application | Description | Direct Download Link |
| :--- | :--- | :--- |
| ⚡ **Jents_VPN.exe** | Full Autonomous Quantum VPN Client (Aether God HUD) | [⬇️ **Download Jents_VPN.exe**](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/Jents_VPN.exe) |
| 🔍 **IP_Detector.exe** | Standalone Live Public IP & Geolocation Security Scanner | [⬇️ **Download IP_Detector.exe**](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/IP_Detector.exe) |

*(Alternative Raw Mirrors: [Jents_VPN.exe Mirror](https://github.com/sumitajsr79-eng/jents-vpn/raw/main/Jents_VPN.exe) • [IP_Detector.exe Mirror](https://github.com/sumitajsr79-eng/jents-vpn/raw/main/IP_Detector.exe))*

---

## 🌟 Key Features

* **⚡ Zero-Touch Autonomous Operation**: The only manual interaction required is clicking the **`[ CONNECT ]`** button.
* **🌐 Verified Global Remote Relays**: Masks and changes your public IP address through verified high-speed exit relays across Europe, France, Germany, US, and Asia.
* **🛡️ Encrypted DNS-over-HTTPS (DoH)**: Built-in zero-leak resolver using Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`) DoH channels with memory caching.
* **🚀 Zero-Delay Kernel Sockets**: Full-duplex bidirectional streaming with `TCP_NODELAY` and 256KB buffer scaling for 4K streaming, gaming, and downloads.
* **🎨 Aether God-Tier Cyber HUD**: 60 FPS animated Quantum Arc Reactor core, 3D interactive holographic world map, real-time speedometers, and live terminal logging.
* **🔍 Integrated IP Detector**: Built-in real-time IP, ISP, country, and security scanner.

---

## 📦 Project Structure

```text
jents_vpn/
├── Jents_VPN.exe            # Standalone compiled executable (Windows)
├── IP_Detector.exe          # Standalone compiled IP detector (Windows)
├── jents.py                 # Main application entry point & UAC privilege manager
├── ip_detector.py           # Standalone IP & Geolocation security scanner
├── build.py                 # Standalone PyInstaller executable compiler
├── config/
│   ├── config_manager.py    # Local settings manager
│   └── default_nodes.json   # Seed gateway profiles
├── core/
│   ├── auto_engine.py       # Master orchestration state machine & self-test
│   ├── api_bridge.py        # Local REST/WebSocket bridge for Aether God UI
│   ├── fleet_manager.py     # Live remote exit node discovery & testing
│   ├── tunnel_gateway.py    # Full-duplex proxy & streaming engine
│   ├── doh_resolver.py      # DNS-over-HTTPS in-memory cached resolver
│   ├── proxy_router.py      # Dual-layer WinINet + WinHTTP proxy manager
│   ├── crypto_session.py    # Ephemeral session key negotiation
│   ├── stats_engine.py      # Real-time telemetry & bandwidth sampler
│   ├── dns_guard.py         # Adapter DNS safety guard
│   └── kill_switch.py       # Loopback & tunnel whitelisting
├── ui_web/
│   └── index.html           # Aether God-Tier Cybernetic HUD interface
├── ui/
│   └── jents_window.py      # Standalone native Tkinter canvas UI
├── tests/                   # Complete automated test suite
├── LICENSE                  # MIT Open Source License
└── README.md                # Project documentation
```

---

## 🚀 Quick Start from Source

```bash
# Clone repository
git clone https://github.com/sumitajsr79-eng/jents-vpn.git
cd jents-vpn

# Run Jents VPN
python jents.py

# Run IP Detector
python ip_detector.py
```

---

## ⚖️ License & Legal

This project is open-source and licensed under the **[MIT License](LICENSE)**.

> **Educational & Research Notice**: Jents VPN is an open-source educational networking client developed for privacy research and secure proxy experimentation. It is 100% free and open-source.
