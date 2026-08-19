# ⚡ Jents VPN (v1.0.0) — Autonomous Quantum Privacy & Network Tunnel

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![Version: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-purple.svg)](https://github.com/sumitajsr79-eng/jents-vpn/releases)

**Jents VPN** is an open-source, zero-configuration autonomous VPN client and network proxy built for ultra-fast speeds, zero-leak DNS protection, and 1-click global traffic masking.

---

## 📥 Direct Downloads (`.exe`)

You can run Jents VPN directly without installing Python:

* 🚀 **[Download Jents_VPN.exe (Standalone Application)](Jents_VPN.exe)**
* 🔍 **[Download IP_Detector.exe (Live IP & Geolocation Scanner)](IP_Detector.exe)**

---

## 🌟 Key Features

* **⚡ Zero-Touch Autonomous Operation**: The only manual interaction required is clicking the **`[ CONNECT ]`** button.
* **🌐 Verified Global Remote Relays**: Masks and changes your public IP address through verified high-speed exit relays across Europe, France, Germany, US, and Asia.
* **🛡️ Encrypted DNS-over-HTTPS (DoH)**: Built-in zero-leak resolver using Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`) DoH channels with memory caching.
* **🚀 Zero-Delay Kernel Sockets**: Full-duplex bidirectional streaming with `TCP_NODELAY` and 256KB buffer scaling for 4K streaming, gaming, and downloads.
* **🎨 Cyberpunk Quantum HUD**: 60 FPS animated Quantum Arc Reactor core, floating background particle fields, real-time speedometers, and live terminal logging.
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
│   ├── fleet_manager.py     # Live remote exit node discovery & testing
│   ├── tunnel_gateway.py    # Full-duplex proxy & streaming engine
│   ├── doh_resolver.py      # DNS-over-HTTPS in-memory cached resolver
│   ├── proxy_router.py      # Dual-layer WinINet + WinHTTP proxy manager
│   ├── crypto_session.py    # Ephemeral session key negotiation
│   ├── stats_engine.py      # Real-time telemetry & bandwidth sampler
│   ├── dns_guard.py         # Adapter DNS safety guard
│   └── kill_switch.py       # Loopback & tunnel whitelisting
├── ui/
│   └── jents_window.py      # Cyberpunk 60 FPS animated Tkinter canvas UI
├── tests/                   # Complete automated test suite
├── LICENSE                  # MIT Open Source License
└── README.md                # Project documentation
```

---

## 🚀 Quick Start

### 1. Run from Source:
```bash
# Clone repository
git clone https://github.com/sumitajsr79-eng/jents-vpn.git
cd jents-vpn

# Run Jents VPN
python jents.py

# Run IP Detector
python ip_detector.py
```

### 2. Build Standalone Executable (`.exe`):
```bash
python build.py
```
The compiled single-file executable will be saved in `dist/Jents_VPN.exe`.

---

## ⚖️ License & Legal

This project is open-source and licensed under the **[MIT License](LICENSE)**.

> **Educational & Research Notice**: Jents VPN is an open-source educational networking client developed for privacy research and secure proxy experimentation. It is 100% free and open-source.
