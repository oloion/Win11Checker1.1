# Win11Checker

A simple Windows utility to verify the installation and basic system health of Windows 10/11.

> ✅ Checks OS version, RAM, disk space, update status, and more  
> 🖥️ GUI built with `tkinter`  
> 📦 Single `.exe` via PyInstaller

## 🚀 Features
- Detects Windows 11 (build ≥ 22000)
- Verifies minimum requirements (4 GB RAM, 64 GB free disk)
- Generates Windows Update log (via PowerShell)
- Cross-compatible with Windows 10/11

## 📥 Download
Pre-built executable: [`Win11Checker.exe`](https://github.com/olioin/Win11Checker/releases) 

## 🛠️ Build from source
```bash
pip install psutil
pyinstaller --onefile --windowed --icon=icon.ico gui.py
