# Win11Checker

A simple Windows utility to verify the installation and basic system health of Windows 10/11.

> ✅ Checks OS version, RAM, disk space, update status, and more  
> 🖥️ GUI built with `tkinter`  
> 📦 Single `.exe` via PyInstaller

## 🚀 Features
- Detects Windows 11/10 (build ≥ 22000)
- Verifies minimum requirements (4 GB RAM, 64 GB free disk)
- Generates Windows Update log (via PowerShell)
- Cross-compatible with Windows 10/11

## 📥 Download
Pre-built executable: [`Win11Checker.exe`](https://github.com/olioin/Win11Checker1.1/releases) *(SOON)*

## 🛠️ Build from source
```bash
pip install psutil
pyinstaller --onefile --windowed --icon=icon.ico python_source_code.py



(⚠️ Note on VirusTotal: Some antivirus engines flag this tool as suspicious due to its use of PowerShell and PyInstaller packaging. This is a known false positive. The source code is open and auditable. No network calls, no persistence, no data exfiltration. We will fix it sooner)
