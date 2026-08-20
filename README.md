# ⚡ Jents VPN & Quantum Privacy Suite (v1.0.0)

[![Download Jents_VPN.exe](https://img.shields.io/badge/⚡_DOWNLOAD_JENTS_VPN.EXE-CLICK_HERE_TO_DOWNLOAD-00f0ff?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/Jents_VPN.exe)
[![Download DNS_Changer.exe](https://img.shields.io/badge/⚡_DOWNLOAD_DNS_CHANGER.EXE-CLICK_HERE_TO_DOWNLOAD-b026ff?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/DNS_Changer.exe)
[![Download IP_Detector.exe](https://img.shields.io/badge/🔍_DOWNLOAD_IP_DETECTOR.EXE-CLICK_HERE_TO_DOWNLOAD-00ff9d?style=for-the-badge&logo=windows&logoColor=black)](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/IP_Detector.exe)

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![Version: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-purple.svg)](https://github.com/sumitajsr79-eng/jents-vpn/releases/tag/v1.0.0)

> 💡 **HOW TO DOWNLOAD DIRECTLY:**
> * To download any executable with **1-click**, click the big download badges above or the direct links below!

---

## 📥 Direct 1-Click Downloads (`.exe`)

| Application | Description | Direct Download Link |
| :--- | :--- | :--- |
| ⚡ **Jents_VPN.exe** | Full Autonomous Quantum VPN Client (Aether God HUD) | [⬇️ **Download Jents_VPN.exe**](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/Jents_VPN.exe) |
| ⚡ **DNS_Changer.exe** | Intelligent DNS Optimizer, Speed Benchmark & 1-Click Changer | [⬇️ **Download DNS_Changer.exe**](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/DNS_Changer.exe) |
| 🔍 **IP_Detector.exe** | Standalone Live Public IP & Geolocation Security Scanner | [⬇️ **Download IP_Detector.exe**](https://github.com/sumitajsr79-eng/jents-vpn/releases/download/v1.0.0/IP_Detector.exe) |

---

## ⚡ DNS Changer — Best DNS For Every Need

| DNS Provider | Primary / Secondary | Category | ★ Best For What |
| :--- | :--- | :--- | :--- |
| **Cloudflare DNS** | `1.1.1.1` • `1.0.0.1` | ⚡ Speed & Gaming | 🎮 **Ultra-Low Latency Gaming** & Fastest Web Browsing (1ms lookup, zero-log) |
| **AdGuard DNS** | `94.140.14.14` • `94.140.15.15` | 🛑 Ad Blocking | 🚫 **Blocking System-Wide Ads, Trackers & Telemetry** across all apps |
| **Google Public DNS** | `8.8.8.8` • `8.8.4.4` | 🎬 4K Streaming | 📺 **4K Video Streaming (YouTube/Netflix)** & Global Anycast 99.99% Uptime |
| **Quad9 Security** | `9.9.9.9` • `149.112.112.112` | 🛡️ Threat Defense | 🔒 **Blocking Phishing, Ransomware & Cyber Threats** via Swiss GDPR non-profit |
| **Cloudflare Malware** | `1.1.1.2` • `1.0.0.2` | 🛡️ Cyber Defense | ⚡ **High Speed + Automatic Known Malware Blocking** |
| **Cisco OpenDNS** | `208.67.222.222` • `208.67.220.220` | 🏢 Enterprise | 🌐 **Enterprise Stability & Custom Web Content Filtering** |
| **Cloudflare Families** | `1.1.1.3` • `1.0.0.3` | 👨‍👩‍👧 Family Safety | 🏡 **Family Internet Safety: Blocks Malware + Adult Content** |
| **Control D Uncensored** | `76.76.2.0` • `76.76.10.0` | 🔓 Uncensored | 🔓 **Bypassing ISP Censorship & Pure Neutral Web Access** |
| **Automatic (DHCP)** | *Router Assigned* | 🔄 ISP Default | 🔄 **1-Click Reset to Original Wi-Fi / Router Settings** |

---

## 🌟 Key Features

* **⚡ Zero-Touch Autonomous Operation**: The only manual interaction required is clicking **`[ CONNECT ]`**.
* **🌐 Verified Global Remote Relays**: Masks and changes your public IP address through verified high-speed exit relays across Germany, US, Netherlands, France, Singapore, and Japan.
* **🛡️ Encrypted DNS-over-HTTPS (DoH)**: Built-in zero-leak resolver using Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`) DoH channels with memory caching.
* **🚀 Zero-Delay Kernel Sockets**: Full-duplex bidirectional streaming with `TCP_NODELAY` and 256KB buffer scaling for 4K streaming, gaming, and downloads.
* **🎨 Aether God-Tier Cyber HUD**: 60 FPS animated Quantum Arc Reactor core, 3D interactive holographic world map, real-time speedometers, and live terminal logging.
* **🔍 Integrated IP Detector**: Built-in real-time IP, ISP, country, and security scanner.
* **⚡ Standalone DNS Changer**: Benchmark and 1-click switch between top DNS providers with live speed rankings.

---

## 📦 Project Structure

```text
jents_vpn/
├── Jents_VPN.exe            # Standalone compiled executable (Windows)
├── DNS_Changer.exe          # Standalone compiled DNS optimizer (Windows)
├── IP_Detector.exe          # Standalone compiled IP detector (Windows)
├── jents.py                 # Main application entry point & UAC privilege manager
├── dns_changer.py           # DNS optimizer, benchmark & adapter manager
├── ip_detector.py           # Real-time public IP & geolocation detector
├── build.py                 # PyInstaller production build pipeline
├── core/
│   ├── auto_engine.py       # Master engine orchestrator & state machine
│   ├── fleet_manager.py     # Verified remote exit relay pool
│   ├── tunnel_gateway.py    # Self-healing local HTTP/HTTPS tunnel gateway
│   ├── doh_resolver.py      # Encrypted DNS-over-HTTPS (DoH) engine
│   ├── proxy_router.py      # Windows WinINet & WinHTTP system proxy manager
│   ├── stats_engine.py      # Live bandwidth telemetry & throughput tracking
│   └── crypto_session.py    # Ephemeral cryptographic session manager
└── ui_web/
    └── index.html           # Aether God-Tier Cyber HUD (HTML/CSS/JS)
```

---

## 📜 License
MIT License. Open-source for all security researchers and privacy enthusiasts.
