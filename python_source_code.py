# Win11Checker v2.0 "Aurora Edition"
# A sleek dark-themed utility to verify Windows 10/11 installation and system health
# New: animated gradient header, live CPU/RAM gauges, glassmorphism cards,
#      color-coded report console with syntax highlighting, run progress animation

import tkinter as tk
from tkinter import scrolledtext
import io
import sys
import math
import time
import platform
import subprocess
import threading
import shutil

try:
    import psutil
except ImportError:
    psutil = None

# ----------------------------- Theme / palette -----------------------------
BG          = "#0b0f1a"   # deep space background
BG_CARD     = "#141a2e"   # card surface
BG_CARD_2   = "#1b2340"   # hover / accent surface
FG          = "#e6ecff"   # main text
FG_DIM      = "#8b95b3"   # dimmed text
ACCENT_1    = "#7c4dff"   # violet
ACCENT_2    = "#00d4ff"   # cyan
ACCENT_3    = "#ff2e97"   # magenta
OK          = "#3ddc84"
WARN        = "#ffb020"
ERR         = "#ff5566"
GRID        = "#232c4a"

FONT_UI     = "Segoe UI"
FONT_MONO   = "Consolas"

VERSION     = "v2.0 Aurora"


# ----------------------------- System checks -------------------------------
def check_os(out):
    out("=== OS Check ===", "dim")
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    out(f"System:   {os_name}")
    out(f"Version:  {os_version}")
    out(f"Release:  {os_release}")

    if os_name == "Windows":
        try:
            parts = os_version.split(".")
            if len(parts) >= 3:
                major, minor, build = map(int, parts[:3])
                if major >= 10 and build >= 22000:
                    out("OK Windows 11 detected (build >= 22000)", "ok")
                elif major == 10:
                    out(f"WARN Windows 10 detected (build {build})", "warn")
                else:
                    out("WARN Unknown Windows version", "warn")
            else:
                out("WARN Could not parse OS version", "warn")
        except ValueError:
            out("WARN Failed to parse OS version string", "warn")
    else:
        out(f"INFO Running on non-Windows system ({os_name}) — some checks skipped", "info")


def check_system_resources(out):
    out("", None)
    out("=== System Resources Check ===", "dim")
    if psutil is None:
        out("WARN psutil not installed — resource check skipped", "warn")
        return
    try:
        ram_total = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        disk_total, _, disk_free = shutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
        disk_total_gb = round(disk_total / (1024 ** 3), 2)
        disk_free_gb = round(disk_free / (1024 ** 3), 2)

        out(f"Total RAM:        {ram_total} GB")
        out(f"Drive (total):    {disk_total_gb} GB")
        out(f"Drive (free):     {disk_free_gb} GB")

        if ram_total >= 4 and disk_free_gb >= 64:
            out("OK Meets Windows 11 minimum requirements", "ok")
        else:
            out("WARN May not meet Windows 11 requirements (4 GB RAM / 64 GB free)", "warn")
    except Exception as e:
        out(f"WARN Error checking resources: {e}", "warn")


def check_updates(out):
    out("", None)
    out("=== Windows Update Log Check (PowerShell) ===", "dim")
    if platform.system() != "Windows":
        out("INFO Not a Windows system — skipping PowerShell update log", "info")
        return
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-WindowsUpdateLog"],
            capture_output=True, text=True, shell=True, timeout=60
        )
        if result.returncode == 0:
            out("OK Update log generated in C:\\Windows\\Logs\\WindowsUpdate\\", "ok")
        else:
            out("WARN Failed to generate update log", "warn")
            stderr = result.stderr.strip()
            out(stderr[:200] + ("..." if len(stderr) > 200 else ""), "dim")
    except Exception as e:
        out(f"WARN PowerShell error: {e}", "warn")


# ----------------------------- GUI helpers ---------------------------------
class GradientHeader(tk.Canvas):
    """Animated aurora-style gradient banner drawn on a canvas."""

    def __init__(self, master, height=90):
        super().__init__(master, height=height, bg=BG, highlightthickness=0, bd=0)
        self.height = height
        self.phase = 0.0
        self._job = None
        self.bind("<Configure>", lambda e: self.redraw())
        self.animate()

    @staticmethod
    def _mix(c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    def redraw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.height
        if w <= 1:
            return
        cols = [tuple(int(x[i:i+2], 16) for i in (1, 3, 5)) for x in
                (ACCENT_1, ACCENT_2, ACCENT_3, ACCENT_1)]
        bands = max(w // 3, 1)
        n = len(cols) - 1
        for i in range(bands):
            p = i / (bands - 1)
            seg = min(int(p * n), n - 1)
            t = (p * n) - seg
            wave = 0.5 + 0.5 * math.sin(self.phase + p * math.tau)
            rgb = self._mix(cols[seg], cols[seg + 1], t)
            rgb = tuple(int(v * (0.35 + 0.65 * wave)) for v in rgb)
            x0 = int(i * w / bands)
            x1 = int((i + 1) * w / bands) + 1
            self.create_rectangle(x0, 0, x1, h, fill="#%02x%02x%02x" % rgb, outline="")
        # title over the gradient
        self.create_text(20, h // 2 - 10, text="Win11Checker", anchor="w",
                         fill="#ffffff", font=(FONT_UI, 20, "bold"))
        self.create_text(20, h // 2 + 14, text="Verify Windows 10/11 installation & system health",
                         anchor="w", fill="#dbe4ff", font=(FONT_UI, 9))
        self.create_text(w - 16, 12, text=VERSION, anchor="ne",
                         fill="#ffffff", font=(FONT_UI, 9, "bold"))

    def animate(self):
        self.phase += 0.035
        self.redraw()
        self._job = self.after(50, self.animate)


class Gauge(tk.Canvas):
    """Circular progress gauge with smooth animated value transitions."""

    def __init__(self, master, label, color, size=110):
        super().__init__(master, width=size, height=size, bg=BG_CARD,
                         highlightthickness=0, bd=0)
        self.label = label
        self.color = color
        self.size = size
        self.value = 0.0          # current displayed value 0..1
        self.target = 0.0         # target value 0..1
        self._anim = None
        self._draw()

    def set(self, frac, text=None):
        self.target = max(0.0, min(1.0, frac))
        self.custom_text = text
        self._animate()

    def _animate(self):
        d = self.target - self.value
        if abs(d) < 0.005:
            self.value = self.target
            self._draw()
            self._anim = None
            return
        self.value += d * 0.15
        self._draw()
        self._anim = self.after(25, self._animate)

    def _arc_points(self, r, start_deg, sweep_deg):
        cx = cy = self.size / 2
        pts = []
        steps = max(int(abs(sweep_deg) / 3), 1)
        for i in range(steps + 1):
            a = math.radians(start_deg + sweep_deg * i / steps)
            pts.append(cx + r * math.cos(a))
            pts.append(cy - r * math.sin(a))
        return pts

    def _draw(self):
        self.delete("all")
        s, cx = self.size, self.size / 2
        r = s / 2 - 10
        start, full = 90, -300  # gap at bottom
        # track
        self.create_line(*self._arc_points(r, start, full), width=9, capstyle="round", fill=GRID)
        # value arc
        if self.value > 0.01:
            self.create_line(*self._arc_points(r, start, full * self.value),
                             width=9, capstyle="round", fill=self.color)
        pct = int(round(self.value * 100))
        txt = getattr(self, "custom_text", None) or f"{pct}%"
        self.create_text(cx, cx - 6, text=txt, fill=FG, font=(FONT_UI, 14, "bold"))
        self.create_text(cx, cx + 16, text=self.label, fill=FG_DIM, font=(FONT_UI, 8))


class Card(tk.Frame):
    """Rounded-corner 'glass' card built from a canvas backdrop."""

    def __init__(self, master, title):
        super().__init__(master, bg=BG_CARD, highlightbackground=GRID,
                         highlightcolor=ACCENT_2, highlightthickness=1)
        tk.Label(self, text=title, bg=BG_CARD, fg=ACCENT_2,
                 font=(FONT_UI, 10, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
        self.body = tk.Frame(self, bg=BG_CARD)
        self.body.pack(fill="both", expand=True, padx=12, pady=6)


class NeonButton(tk.Canvas):
    """Flat neon button with glow-on-hover."""

    def __init__(self, master, text, command, width=190, height=44, color=ACCENT_2):
        super().__init__(master, width=width, height=height, bg=BG,
                         highlightthickness=0, bd=0)
        self.command = command
        self.color = color
        self.text = text
        self.state = "normal"
        self._hover = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        w, h = int(self["width"]), int(self["height"])
        if self.state == "disabled":
            bg_, fg_, outline = BG_CARD_2, FG_DIM, GRID
        elif self._hover:
            bg_, fg_, outline = self.color, "#04101c", self.color
        else:
            bg_, fg_, outline = BG_CARD, self.color, self.color
        self.create_rectangle(2, 2, w - 2, h - 2, fill=bg_, outline=outline, width=2)
        self.create_text(w // 2, h // 2, text=self.text, fill=fg_, font=(FONT_UI, 11, "bold"))

    def _on_enter(self, _):
        self._hover = True
        self._draw()

    def _on_leave(self, _):
        self._hover = False
        self._draw()

    def _on_click(self, _):
        if self.state != "disabled":
            self.command()

    def set_state(self, state):
        self.state = state
        self.itemconfigure("all", state="normal" if state != "disabled" else "disabled")
        self._draw()


# ----------------------------- Main window ---------------------------------
root = tk.Tk()
root.title("Win11Checker — Windows Installation Verifier")
root.geometry("860x620")
root.configure(bg=BG)
root.minsize(720, 540)

TAG_COLORS = {"ok": OK, "warn": WARN, "err": ERR, "info": ACCENT_2, "dim": FG_DIM, None: FG}

header = GradientHeader(root)
header.pack(fill="x")

# --- Left column: report console ---
left = tk.Frame(root, bg=BG)
left.pack(side="left", fill="both", expand=True, padx=(14, 7), pady=12)

console_card = Card(left, "REPORT CONSOLE")
console_card.pack(fill="both", expand=True)

text_area = scrolledtext.ScrolledText(
    console_card.body, wrap=tk.WORD, font=(FONT_MONO, 10),
    bg="#0d1226", fg=FG, insertbackground=FG, relief="flat",
    highlightthickness=0, padx=10, pady=8
)
text_area.pack(fill="both", expand=True)
for tag, col in TAG_COLORS.items():
    if tag:
        text_area.tag_configure(tag, foreground=col)

btn_row = tk.Frame(left, bg=BG)
btn_row.pack(fill="x", pady=(10, 0))

spinner_label = tk.Label(btn_row, text="", bg=BG, fg=ACCENT_2, font=(FONT_MONO, 11, "bold"), width=3)


def out(line="", tag=None):
    text_area.insert(tk.END, line + "\n", tag or "none")
    text_area.see(tk.END)


SPIN = "|/-\\"


def _spin():
    if not run_btn.state == "disabled":
        spinner_label.config(text="")
        return
    global _spin_i
    _spin_i = (_spin_i + 1) % len(SPIN)
    spinner_label.config(text=SPIN[_spin_i])
    root.after(90, _spin)


_spin_i = 0


def update_gauges():
    """Refresh live CPU / RAM gauges periodically."""
    if psutil is not None:
        try:
            cpu = psutil.cpu_percent(interval=None)
            vm = psutil.virtual_memory()
            gauge_cpu.set(cpu / 100.0, f"{cpu:.0f}%")
            gauge_ram.set(vm.percent / 100.0, f"{vm.percent:.0f}%")
            ram_sub.config(text=f"{round(vm.used / 2**30, 1)} / {round(vm.total / 2**30, 1)} GB")
            disk_sub.config(text=f"{round(shutil.disk_usage('/').free / 2**30)} GB free")
        except Exception:
            pass
    root.after(1500, update_gauges)


def run_full_check():
    def worker():
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            run_btn.set_state("disabled")
            status.config(text="Running diagnostics…", fg=ACCENT_2)

            def emit(line="", tag=None):
                print(line)
                root.after(0, out, line, tag)

            emit("Windows 10/11 Installation Checker")
            emit("=" * 45, "dim")
            check_os(emit)
            check_system_resources(emit)
            check_updates(emit)
            emit("", None)
            emit("Check completed.", "ok")
        except Exception as e:
            root.after(0, out, f"CRITICAL error: {e}", "err")
        finally:
            sys.stdout = old_stdout
            root.after(0, finish)

    def finish():
        run_btn.set_state("normal")
        status.config(text=f"Done — {time.strftime('%H:%M:%S')}", fg=OK)

    threading.Thread(target=worker, daemon=True).start()


run_btn = NeonButton(btn_row, "▶  RUN CHECK", run_full_check)
run_btn.pack(side="left")
spinner_label.pack(side="left", padx=8)
root.after(90, _spin)

copy_btn = NeonButton(btn_row, "⧉  COPY REPORT", width=140, color=ACCENT_1,
                      command=lambda: (root.clipboard_clear(),
                                       root.clipboard_append(text_area.get("1.0", tk.END)),
                                       status.config(text="Report copied to clipboard", fg=OK)))
copy_btn.pack(side="left", padx=(10, 0))

# --- Right column: live dashboard ---
right = tk.Frame(root, bg=BG, width=250)
right.pack(side="right", fill="y", padx=(7, 14), pady=12)

perf_card = Card(right, "LIVE SYSTEM")
perf_card.pack(fill="x")

gauge_cpu = Gauge(perf_card.body, "CPU LOAD", ACCENT_2)
gauge_cpu.pack(pady=(4, 0))
gauge_ram = Gauge(perf_card.body, "MEMORY", ACCENT_3)
gauge_ram.pack(pady=4)

req_card = Card(right, "WIN11 REQUIREMENTS")
req_card.pack(fill="x", pady=(12, 0))

def req_row(parent, name, sub):
    f = tk.Frame(parent, bg=BG_CARD_2)
    f.pack(fill="x", pady=3, padx=2)
    tk.Label(f, text=name, bg=BG_CARD_2, fg=FG, font=(FONT_UI, 9, "bold")).pack(anchor="w", padx=8, pady=(4, 0))
    l = tk.Label(f, text=sub, bg=BG_CARD_2, fg=FG_DIM, font=(FONT_UI, 8))
    l.pack(anchor="w", padx=8, pady=(0, 4))
    return l

ram_sub = req_row(req_card.body, "RAM ≥ 4 GB", "")
disk_sub = req_row(req_card.body, "Free disk ≥ 64 GB", "")
req_row(req_card.body, "OS Build ≥ 22000", "detected during scan")

tip_card = Card(right, "TIP OF THE MOMENT")
tip_card.pack(fill="x", pady=(12, 0))
tips = [
    "TPM 2.0 is required for a clean Windows 11 install.",
    "Run Get-WindowsUpdateLog as Administrator for full logs.",
    "sfc /scannow repairs corrupted system files.",
    "DISM /Online /Cleanup-Image /RestoreHealth fixes the component store.",
    "Check Event Viewer → Windows Logs for update failures.",
]
tip_lbl = tk.Label(tip_card.body, text=tips[0], bg=BG_CARD, fg=FG_DIM,
                   font=(FONT_UI, 9), wraplength=210, justify="left")
tip_lbl.pack(anchor="w")


def cycle_tip():
    tips.append(tips.pop(0))
    tip_lbl.config(text=tips[0])
    root.after(6000, cycle_tip)


cycle_tip()

# --- Status bar ---
status = tk.Label(root, text="Ready", anchor="w", bg="#0d1226", fg=OK,
                  font=(FONT_UI, 9), padx=12, pady=4)
status.pack(side="bottom", fill="x")

# prime gauges so they show something before first scan
if psutil is not None:
    try:
        psutil.cpu_percent(interval=None)  # prime
    except Exception:
        pass
update_gauges()

# --- Entry point ---
if __name__ == "__main__":
    root.mainloop()
