"""
Smart Traffic Signal Simulator
Author: Narasimman V
Description: Density-based adaptive traffic signal system using Python & Tkinter.
             Simulates real-time vehicle density detection and dynamic signal timing.
"""

import tkinter as tk
from tkinter import ttk
import random
import time
import threading

# ── Constants ──────────────────────────────────────────────────────────────────
LANES = ["North", "East", "South", "West"]
COLORS = {
    "bg":        "#0D1117",
    "panel":     "#161B22",
    "border":    "#30363D",
    "red":       "#FF4444",
    "yellow":    "#FFD700",
    "green":     "#00CC66",
    "off":       "#1A1A1A",
    "text":      "#E6EDF3",
    "subtext":   "#8B949E",
    "accent":    "#58A6FF",
    "lane_bg":   "#21262D",
    "bar_bg":    "#30363D",
}

MIN_GREEN = 5    # seconds
MAX_GREEN = 20   # seconds
YELLOW_TIME = 2  # seconds
DENSITY_UPDATE_INTERVAL = 3  # seconds


def density_to_green_time(density: int) -> int:
    """Convert vehicle density (0–100) to green signal duration in seconds."""
    return int(MIN_GREEN + (density / 100) * (MAX_GREEN - MIN_GREEN))


def density_label(density: int) -> str:
    if density < 30:
        return "Low"
    elif density < 65:
        return "Medium"
    else:
        return "High"


# ── Simulator Logic ─────────────────────────────────────────────────────────────
class TrafficSimulator:
    def __init__(self):
        self.densities = {lane: random.randint(10, 90) for lane in LANES}
        self.active_lane = LANES[0]
        self.phase = "green"   # green | yellow | red
        self.timer = 0
        self.running = False
        self.cycle_count = 0
        self.total_wait = {lane: 0 for lane in LANES}
        self.callbacks = []

    def register_callback(self, fn):
        self.callbacks.append(fn)

    def _notify(self):
        for fn in self.callbacks:
            fn()

    def update_density(self, lane, value):
        self.densities[lane] = int(value)

    def _simulate_density_drift(self):
        """Randomly adjust densities over time to simulate real traffic."""
        while self.running:
            time.sleep(DENSITY_UPDATE_INTERVAL)
            for lane in LANES:
                delta = random.randint(-15, 15)
                self.densities[lane] = max(5, min(95, self.densities[lane] + delta))
            self._notify()

    def start(self):
        self.running = True
        threading.Thread(target=self._run_cycle, daemon=True).start()
        threading.Thread(target=self._simulate_density_drift, daemon=True).start()

    def stop(self):
        self.running = False

    def _run_cycle(self):
        lane_index = 0
        while self.running:
            lane = LANES[lane_index % len(LANES)]
            self.active_lane = lane
            green_time = density_to_green_time(self.densities[lane])

            # GREEN phase
            self.phase = "green"
            for t in range(green_time, 0, -1):
                if not self.running:
                    return
                self.timer = t
                # Accumulate wait time for other lanes
                for other in LANES:
                    if other != lane:
                        self.total_wait[other] += 1
                self._notify()
                time.sleep(1)

            # YELLOW phase
            self.phase = "yellow"
            for t in range(YELLOW_TIME, 0, -1):
                if not self.running:
                    return
                self.timer = t
                self._notify()
                time.sleep(1)

            lane_index += 1
            self.cycle_count += 1


# ── GUI ─────────────────────────────────────────────────────────────────────────
class TrafficGUI:
    def __init__(self, root: tk.Tk, sim: TrafficSimulator):
        self.root = root
        self.sim = sim
        self.sim.register_callback(self._schedule_update)

        root.title("Smart Traffic Signal Simulator — Narasimman V")
        root.configure(bg=COLORS["bg"])
        root.resizable(False, False)

        self._build_ui()

    def _schedule_update(self):
        self.root.after(0, self._update_ui)

    # ── Build ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS["bg"])
        title_frame.pack(fill="x", padx=20, pady=(18, 4))

        tk.Label(title_frame, text="🚦 Smart Traffic Signal Simulator",
                 font=("Courier New", 18, "bold"), bg=COLORS["bg"],
                 fg=COLORS["accent"]).pack(side="left")

        tk.Label(title_frame, text="Density-Based Adaptive Control",
                 font=("Courier New", 10), bg=COLORS["bg"],
                 fg=COLORS["subtext"]).pack(side="left", padx=12)

        # Main content
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(padx=20, pady=8)

        # Left: intersection view
        left = tk.Frame(main, bg=COLORS["bg"])
        left.pack(side="left", padx=(0, 16))
        self._build_intersection(left)

        # Right: lane panels
        right = tk.Frame(main, bg=COLORS["bg"])
        right.pack(side="left")
        self.lane_frames = {}
        for lane in LANES:
            self._build_lane_panel(right, lane)

        # Bottom: controls + stats
        bottom = tk.Frame(self.root, bg=COLORS["bg"])
        bottom.pack(fill="x", padx=20, pady=(4, 16))
        self._build_controls(bottom)
        self._build_stats(bottom)

    def _build_intersection(self, parent):
        tk.Label(parent, text="INTERSECTION VIEW",
                 font=("Courier New", 9, "bold"), bg=COLORS["bg"],
                 fg=COLORS["subtext"]).pack(pady=(0, 6))

        self.canvas = tk.Canvas(parent, width=280, height=280,
                                bg=COLORS["panel"], highlightthickness=1,
                                highlightbackground=COLORS["border"])
        self.canvas.pack()
        self._draw_intersection()

    def _draw_intersection(self):
        c = self.canvas
        c.delete("all")
        w, h = 280, 280
        cx, cy = w // 2, h // 2
        road_w = 60

        # Road background
        c.create_rectangle(0, 0, w, h, fill=COLORS["panel"], outline="")
        # Roads
        c.create_rectangle(cx - road_w//2, 0, cx + road_w//2, h, fill="#1C1C1C", outline="")
        c.create_rectangle(0, cy - road_w//2, w, cy + road_w//2, fill="#1C1C1C", outline="")
        # Intersection box
        c.create_rectangle(cx-road_w//2, cy-road_w//2, cx+road_w//2, cy+road_w//2,
                            fill="#252525", outline="")

        # Lane markings (dashed center lines)
        for i in range(0, cy - road_w//2, 20):
            c.create_line(cx, i, cx, i+10, fill="#555", width=2, dash=(4, 4))
        for i in range(cy + road_w//2, h, 20):
            c.create_line(cx, i, cx, i+10, fill="#555", width=2, dash=(4, 4))
        for i in range(0, cx - road_w//2, 20):
            c.create_line(i, cy, i+10, cy, fill="#555", width=2, dash=(4, 4))
        for i in range(cx + road_w//2, w, 20):
            c.create_line(i, cy, i+10, cy, fill="#555", width=2, dash=(4, 4))

        # Traffic lights for each direction
        positions = {
            "North": (cx - road_w//2 - 22, cy - road_w//2 - 22),
            "South": (cx + road_w//2 + 4,  cy + road_w//2 + 4),
            "East":  (cx + road_w//2 + 4,  cy - road_w//2 - 22),
            "West":  (cx - road_w//2 - 22, cy + road_w//2 + 4),
        }
        self.signal_ovals = {}
        for lane, (lx, ly) in positions.items():
            color = self._signal_color(lane)
            oval = c.create_oval(lx, ly, lx+18, ly+18, fill=color,
                                 outline=COLORS["border"], width=1)
            self.signal_ovals[lane] = oval
            c.create_text(lx+9, ly+24, text=lane[0], fill=COLORS["subtext"],
                          font=("Courier New", 7, "bold"))

        # Active lane arrow
        active = self.sim.active_lane
        arrows = {
            "North": (cx, cy - road_w//2 - 35, cx, cy - road_w//2 - 10),
            "South": (cx, cy + road_w//2 + 35, cx, cy + road_w//2 + 10),
            "East":  (cx + road_w//2 + 35, cy, cx + road_w//2 + 10, cy),
            "West":  (cx - road_w//2 - 35, cy, cx - road_w//2 - 10, cy),
        }
        if active in arrows:
            x1, y1, x2, y2 = arrows[active]
            c.create_line(x1, y1, x2, y2, fill=COLORS["green"],
                          width=3, arrow=tk.LAST, arrowshape=(10, 12, 4))

        # Timer in center
        phase_color = {"green": COLORS["green"], "yellow": COLORS["yellow"],
                       "red": COLORS["red"]}.get(self.sim.phase, COLORS["text"])
        c.create_text(cx, cy, text=str(self.sim.timer),
                      fill=phase_color, font=("Courier New", 22, "bold"))

    def _signal_color(self, lane):
        if lane == self.sim.active_lane:
            return COLORS[self.sim.phase] if self.sim.phase in ("green", "yellow") else COLORS["red"]
        return COLORS["red"]

    def _build_lane_panel(self, parent, lane):
        frame = tk.Frame(parent, bg=COLORS["lane_bg"], relief="flat",
                         highlightthickness=1, highlightbackground=COLORS["border"])
        frame.pack(fill="x", pady=4)

        top = tk.Frame(frame, bg=COLORS["lane_bg"])
        top.pack(fill="x", padx=12, pady=(8, 2))

        signal_dot = tk.Label(top, text="●", font=("Arial", 14),
                              bg=COLORS["lane_bg"], fg=COLORS["red"])
        signal_dot.pack(side="left")

        tk.Label(top, text=f"  {lane.upper()} LANE",
                 font=("Courier New", 11, "bold"), bg=COLORS["lane_bg"],
                 fg=COLORS["text"]).pack(side="left")

        density_lbl = tk.Label(top, text="●●● HIGH",
                               font=("Courier New", 9), bg=COLORS["lane_bg"],
                               fg=COLORS["subtext"])
        density_lbl.pack(side="right")

        # Density bar
        bar_frame = tk.Frame(frame, bg=COLORS["lane_bg"])
        bar_frame.pack(fill="x", padx=12, pady=2)

        tk.Label(bar_frame, text="Density:", font=("Courier New", 8),
                 bg=COLORS["lane_bg"], fg=COLORS["subtext"]).pack(side="left")

        bar_bg = tk.Frame(bar_frame, bg=COLORS["bar_bg"], height=8, width=160)
        bar_bg.pack(side="left", padx=6)
        bar_bg.pack_propagate(False)

        bar_fill = tk.Frame(bar_bg, bg=COLORS["green"], height=8, width=80)
        bar_fill.place(x=0, y=0, relheight=1)

        green_lbl = tk.Label(bar_frame, text="Green: 12s",
                             font=("Courier New", 8), bg=COLORS["lane_bg"],
                             fg=COLORS["subtext"])
        green_lbl.pack(side="right")

        # Manual density slider
        slider_frame = tk.Frame(frame, bg=COLORS["lane_bg"])
        slider_frame.pack(fill="x", padx=12, pady=(2, 8))

        tk.Label(slider_frame, text="Manual Override:",
                 font=("Courier New", 8), bg=COLORS["lane_bg"],
                 fg=COLORS["subtext"]).pack(side="left")

        slider = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal",
                          bg=COLORS["lane_bg"], fg=COLORS["text"],
                          troughcolor=COLORS["bar_bg"], highlightthickness=0,
                          sliderlength=12, length=140, showvalue=False,
                          command=lambda v, l=lane: self.sim.update_density(l, v))
        slider.set(self.sim.densities[lane])
        slider.pack(side="left", padx=6)

        self.lane_frames[lane] = {
            "signal_dot": signal_dot,
            "density_lbl": density_lbl,
            "bar_fill": bar_fill,
            "green_lbl": green_lbl,
            "slider": slider,
        }

    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=COLORS["bg"])
        ctrl.pack(side="left")

        self.btn_start = tk.Button(ctrl, text="▶  START",
                                   font=("Courier New", 11, "bold"),
                                   bg=COLORS["green"], fg="#000",
                                   relief="flat", padx=16, pady=6,
                                   cursor="hand2", command=self._toggle)
        self.btn_start.pack(side="left", padx=(0, 8))

        tk.Button(ctrl, text="↺  RESET",
                  font=("Courier New", 11, "bold"),
                  bg=COLORS["border"], fg=COLORS["text"],
                  relief="flat", padx=16, pady=6,
                  cursor="hand2", command=self._reset).pack(side="left")

        self.status_lbl = tk.Label(ctrl, text="  ⏸ Stopped",
                                   font=("Courier New", 10), bg=COLORS["bg"],
                                   fg=COLORS["subtext"])
        self.status_lbl.pack(side="left", padx=12)

    def _build_stats(self, parent):
        stats = tk.Frame(parent, bg=COLORS["panel"], relief="flat",
                         highlightthickness=1, highlightbackground=COLORS["border"])
        stats.pack(side="right", padx=(0, 0), pady=4)

        tk.Label(stats, text="CYCLE STATS",
                 font=("Courier New", 8, "bold"), bg=COLORS["panel"],
                 fg=COLORS["subtext"]).pack(padx=12, pady=(6, 2))

        self.cycle_lbl = tk.Label(stats, text="Cycles: 0",
                                   font=("Courier New", 10), bg=COLORS["panel"],
                                   fg=COLORS["text"])
        self.cycle_lbl.pack(padx=12)

        self.active_lbl = tk.Label(stats, text="Active: —",
                                    font=("Courier New", 10), bg=COLORS["panel"],
                                    fg=COLORS["accent"])
        self.active_lbl.pack(padx=12, pady=(0, 6))

    # ── Update ─────────────────────────────────────────────────────────────────
    def _update_ui(self):
        self._draw_intersection()
        for lane in LANES:
            w = self.lane_frames[lane]
            density = self.sim.densities[lane]
            is_active = (lane == self.sim.active_lane)
            phase = self.sim.phase

            # Signal dot color
            if is_active:
                dot_color = COLORS.get(phase, COLORS["green"])
            else:
                dot_color = COLORS["red"]
            w["signal_dot"].config(fg=dot_color)

            # Density label & color
            dlabel = density_label(density)
            d_color = COLORS["green"] if density < 30 else (COLORS["yellow"] if density < 65 else COLORS["red"])
            w["density_lbl"].config(text=f"{'●' * (density // 33 + 1)} {dlabel}", fg=d_color)

            # Bar fill
            bar_width = int(160 * density / 100)
            w["bar_fill"].place(x=0, y=0, relheight=1, width=max(2, bar_width))
            w["bar_fill"].config(bg=d_color)

            # Green time
            gt = density_to_green_time(density)
            w["green_lbl"].config(text=f"Green: {gt}s")

            # Sync slider
            w["slider"].set(density)

        # Stats
        self.cycle_lbl.config(text=f"Cycles: {self.sim.cycle_count}")
        self.active_lbl.config(text=f"Active: {self.sim.active_lane} ({self.sim.phase.upper()})")

    def _toggle(self):
        if self.sim.running:
            self.sim.stop()
            self.btn_start.config(text="▶  START", bg=COLORS["green"], fg="#000")
            self.status_lbl.config(text="  ⏸ Stopped", fg=COLORS["subtext"])
        else:
            self.sim.start()
            self.btn_start.config(text="⏹  STOP", bg=COLORS["red"], fg="#fff")
            self.status_lbl.config(text="  ▶ Running", fg=COLORS["green"])

    def _reset(self):
        self.sim.stop()
        time.sleep(0.2)
        self.sim.densities = {lane: random.randint(10, 90) for lane in LANES}
        self.sim.cycle_count = 0
        self.sim.total_wait = {lane: 0 for lane in LANES}
        self.sim.timer = 0
        self.sim.phase = "green"
        self.sim.active_lane = LANES[0]
        self.btn_start.config(text="▶  START", bg=COLORS["green"], fg="#000")
        self.status_lbl.config(text="  ⏸ Stopped", fg=COLORS["subtext"])
        self._update_ui()


# ── Entry point ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    sim = TrafficSimulator()
    app = TrafficGUI(root, sim)
    root.mainloop()
