# Win11Checker v1.0
# A simple utility to verify Windows 10/11 installation and system health

import tkinter as tk
from tkinter import scrolledtext, messagebox
import io
import sys
import platform
import subprocess
import psutil
import shutil
import os

# --- System checks ---
def check_os():
    print("=== OS Check ===")
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    print(f"System: {os_name}")
    print(f"Version: {os_version}")
    print(f"Release: {os_release}")

    if os_name == "Windows":
        try:
            parts = os_version.split('.')
            if len(parts) >= 3:
                major, minor, build = map(int, parts[:3])
                if major >= 10 and build >= 22000:
                    print("✓ Windows 11 detected")
                elif major == 10 and build < 22000:
                    print("⚠ Windows 10 detected")
                else:
                    print("⚠ Unknown Windows version")
            else:
                print("⚠ Could not parse OS version")
        except ValueError:
            print("⚠ Failed to parse OS version string")
    else:
        print("⚠ Not a Windows system")

def check_system_resources():
    print("\n=== System Resources Check ===")
    try:
        ram_total = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        disk_total, _, disk_free = shutil.disk_usage("C:\\")
        disk_total_gb = round(disk_total / (1024 ** 3), 2)
        disk_free_gb = round(disk_free / (1024 ** 3), 2)

        print(f"Total RAM: {ram_total} GB")
        print(f"C:\\ Drive (total): {disk_total_gb} GB")
        print(f"C:\\ Drive (free): {disk_free_gb} GB")

        # Windows 11 minimum requirements
        if ram_total >= 4 and disk_free_gb >= 64:
            print("✓ Meets Windows 11 minimum requirements")
        else:
            print("⚠ May not meet Windows 11 requirements")
    except Exception as e:
        print(f"⚠ Error checking resources: {e}")

def check_updates():
    print("\n=== Windows Update Log Check (PowerShell) ===")
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-WindowsUpdateLog"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            print("✓ Update log generated in C:\\Windows\\Logs\\WindowsUpdate\\")
        else:
            print("⚠ Failed to generate update log")
            stderr = result.stderr.strip()
            print(stderr[:200] + ("..." if len(stderr) > 200 else ""))
    except Exception as e:
        print(f"⚠ PowerShell error: {e}")

def run_full_check():
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        print("Windows 10/11 Installation Checker")
        print("=" * 45)
        check_os()
        check_system_resources()
        check_updates()
        print("\nCheck completed.")
    except Exception as e:
        print(f"❌ Critical error: {e}")
    finally:
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, output)

# --- GUI Setup ---
root = tk.Tk()
root.title("Win11Checker — Windows Installation Verifier")
root.geometry("720x500")
root.resizable(True, True)

# Header
header = tk.Label(root, text="Win11Checker", font=("Segoe UI", 16, "bold"))
header.pack(pady=10)

desc = tk.Label(root, text="Verify Windows 10/11 installation and system health", fg="gray")
desc.pack(pady=5)

# Run button
btn = tk.Button(
    root,
    text="▶ Run Check",
    command=run_full_check,
    font=("Segoe UI", 10),
    width=20,
    height=2,
    bg="#007ACC",
    fg="white",
    activebackground="#005A9E"
)
btn.pack(pady=10)

# Output area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 9))
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Status bar
status = tk.Label(root, text="Ready", anchor="w", fg="green")
status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

# --- Entry point ---
if __name__ == "__main__":
    root.mainloop()
