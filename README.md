# Win11Checker

A sleek dark-themed Windows utility to verify the installation and basic system health of Windows 10/11.

## ✨ What's new in v2.0 "Aurora Edition"
- 🌌 **Animated aurora gradient header** — live color-wave banner drawn on canvas
- 🔵 **Live circular gauges** — real-time CPU load & memory usage with smooth animations
- 🃏 **Glassmorphism card layout** — report console + dashboard side panels
- 💡 **Neon buttons** with hover glow (Run Check / Copy Report)
- 🎨 **Color-coded report console** — green OK, amber warnings, red errors
- ⏳ **Non-blocking scans** — checks run on a background thread with a spinner (no more frozen window!)
- 🧠 **"Tip of the moment"** rotator with Windows troubleshooting tips
- 📋 One-click **Copy Report** to clipboard
- 🛡️ Graceful fallbacks: skips PowerShell steps off-Windows, works without `psutil`

## 🚀 Features

> ✅ Checks OS version, RAM, disk space, update status, and more  
> 🖥️ GUI built with `tkinter`  
> 📦 Single `.exe` via PyInstaller

## 🚀 Features
- Detects Windows 11/10 (build ≥ 22000)
- Verifies minimum requirements (4 GB RAM, 64 GB free disk)
- Generates Windows Update log (via PowerShell)
- Cross-compatible with Windows 10/11

## 📥 Download
Pre-built executable: [`Win11Checker.exe`](https://github.com/oloion/Win11Checker1.1/releases) 

## 🛠️ Build from source
```bash
pip install psutil
pyinstaller --onefile --windowed --icon=icon.ico python_source_code.py
```


(⚠️ Note on VirusTotal: Some antivirus engines flag this tool as suspicious due to its use of PowerShell and PyInstaller packaging. This is a known false positive. The source code is open and auditable. No network calls, no persistence, no data exfiltration. We will fix it soon. 
⚠️ The program may also freeze during log creation, which we will fix soon too)
