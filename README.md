# 🚦 Smart Traffic Signal Simulator

A **density-based adaptive traffic signal system** built with Python and Tkinter — inspired by my embedded systems project using Arduino and IR sensors.

## 📌 About

This simulator replicates the logic of a real-world smart traffic control system:
- Each lane has a **vehicle density** (0–100%)
- Green signal duration is **dynamically calculated** based on density
- Higher density → longer green time (up to 20s)
- Lower density → shorter green time (minimum 5s)
- Signals cycle through all 4 lanes automatically

## 🖥️ Features

- 🔴🟡🟢 Real-time signal state visualization (Red / Yellow / Green)
- 📊 Live density bars with Low / Medium / High indicators
- 🎛️ Manual density override sliders for each lane
- 🔁 Auto density drift — simulates changing traffic conditions
- ⏱️ Countdown timer showing remaining green/yellow time
- 📍 Intersection view with animated directional arrow
- 🔢 Cycle counter and active lane stats

## 🧠 Algorithm

```
green_time = MIN_GREEN + (density / 100) × (MAX_GREEN - MIN_GREEN)

Where:
  MIN_GREEN = 5 seconds
  MAX_GREEN = 20 seconds
  YELLOW    = 2 seconds (fixed)
```

## 🚀 How to Run

**Requirements:** Python 3.x (Tkinter is built-in — no install needed!)

```bash
# Clone the repo
git clone https://github.com/simman06/traffic-signal-simulator
cd traffic-signal-simulator

# Run the simulator
python traffic_simulator.py
```

## 🎮 Controls

| Control | Action |
|---|---|
| ▶ START | Begin the simulation |
| ⏹ STOP | Pause the simulation |
| ↺ RESET | Reset all densities and counters |
| Sliders | Manually set vehicle density per lane |

## 🔗 Related

- 🔌 Hardware version: Arduino + IR sensors (Proteus simulation)
- 📄 [My Resume](https://simman06.github.io/github-portfolio/)
- 💼 [LinkedIn](https://linkedin.com/in/narasimman-venkatesan-995a0929b)

## 👨‍💻 Author

**Narasimman V** — ECE Student, Anna University  
Passionate about Embedded Systems, IoT, and Python Development.
