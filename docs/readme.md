# Hack-A-Bot Autonomous Catapult

A fully autonomous catapult system built on the Raspberry Pi Pico 2 for the Hack-A-Bot Live competition. The system scans 360° to detect block towers using a laser distance sensor, calculates launch parameters from a calibration table, aims a stepper-driven turret, and fires projectiles with zero human input.

**Target score: 100/100** — fully autonomous (50pts), calibrated accuracy (40pts), clean engineering (5pts), auto-reload magazine + OLED HUD (5pts).

---

## Hardware

| Component | Role |
|-----------|------|
| Raspberry Pi Pico 2 | Main controller (MicroPython) |
| VL53L0X V2 ToF sensor | Laser distance measurement (I2C, 0x29) |
| SSD1306 0.96" OLED | Status display (I2C, 0x3C) |
| MG90S micro servo | Latch — holds and releases the cocked arm |
| MG996R 360° servo | Arm — pulls the catapult arm back against rubber bands |
| NEMA 17 stepper | Turret — rotates the entire catapult to aim at targets |
| DRV8825 driver | Stepper motor driver with 1/16 microstepping |
| LM2596S buck converter | Steps 12V down to 5V for logic and servos |
| 12V 6A PSU | Main power supply |

### Pin Map

| Pico Pin | GPIO | Component | Signal |
|----------|------|-----------|--------|
| 1 | GP0 | OLED + ToF | I2C SDA |
| 2 | GP1 | OLED + ToF | I2C SCL |
| 4 | GP2 | MG90S latch | PWM |
| 5 | GP3 | MG996R arm | PWM |
| 6 | GP4 | DRV8825 | STEP |
| 7 | GP5 | DRV8825 | DIR |
| 9 | GP6 | DRV8825 | ENABLE (active LOW) |
| 10 | GP7 | Magazine servo | PWM |
| 11 | GP8 | Piezo buzzer | PWM (optional) |

---

## Repository Structure

```
├── main.py           Entry point — mode selection + autonomous sequence
├── config.py         All pin assignments, constants, and calibration table
├── servo.py          Positional servo + 360° continuous rotation servo classes
├── stepper.py        NEMA 17 turret control with trapezoidal acceleration
├── sensors.py        VL53L0X ToF distance sensor with median filtering
├── display.py        SSD1306 OLED wrapper (text, progress bar, radar view)
├── scanner.py        360° sweep scan and tower detection algorithm
├── launcher.py       Arm cocking, latch release, magazine reload, fire sequence
├── calibrate.py      Interactive calibration shell for building the firing table
├── catapult_plan.md  Full hardware build guide (wiring, assembly, troubleshooting)
└── test_log.md       180-item test checklist covering every phase of the build
```

### Dependency Graph

```
main.py
 ├── stepper.py ──────┐
 ├── sensors.py ──────┤
 ├── display.py ──────┤── all import config.py
 ├── scanner.py ──────┤   (shared constants)
 │    ├── stepper      │
 │    ├── sensors      │
 │    └── display      │
 ├── launcher.py ─────┤
 │    └── servo.py ───┘
 └── calibrate.py
      └── uses all of the above
```

### External Libraries (upload to Pico root alongside the project files)

| Library | Source | I2C Address |
|---------|--------|-------------|
| `vl53l0x.py` | [kevinmcaleer/vl53lx0](https://github.com/kevinmcaleer/vl53lx0) | 0x29 |
| `ssd1306.py` | [stlehmann/micropython-ssd1306](https://github.com/stlehmann/micropython-ssd1306) | 0x3C |

---

## Getting Started

### 1. Flash MicroPython to the Pico 2

1. Download the latest `.uf2` from [micropython.org/download/RPI_PICO2](https://micropython.org/download/RPI_PICO2/).
2. Hold the **BOOTSEL** button on the Pico while plugging it into USB.
3. A drive called `RPI-RP2` appears. Drag the `.uf2` file onto it.
4. The Pico reboots into MicroPython.

### 2. Upload Files

Using [Thonny IDE](https://thonny.org/) or `mpremote`:

```bash
# With mpremote (install: pip install mpremote)
mpremote cp config.py servo.py stepper.py sensors.py display.py scanner.py launcher.py calibrate.py main.py :
mpremote cp vl53l0x.py ssd1306.py :
```

Or in Thonny: open each file → File → Save copy → select "Raspberry Pi Pico" → save to root `/`.

### 3. Verify Wiring

Connect to the Pico REPL (Thonny or `mpremote repl`) and run:

```python
from sensors import DistanceSensor
tof = DistanceSensor()
tof.scan_i2c()
```

Expected output:

```
[sensors] I2C scan found 2 device(s):
  0x29 = VL53L0X (ToF)
  0x3C = SSD1306 (OLED)
```

### 4. Run

```python
import main
main.main()
```

Select a mode:

| Mode | Use |
|------|-----|
| 1 — AUTONOMOUS | Competition run. Scan → detect → aim → fire × 5. Zero human input. |
| 2 — CALIBRATION | Interactive shell. Fire test shots, build the calibration table. |
| 3 — SENSOR TEST | Read ToF distance and display on OLED. Verify wiring. |
| 4 — STEPPER TEST | Quarter turns in both directions. Verify turret rotation. |

---

## Testing Each Module

Every file can be imported and tested independently in the REPL. Work bottom-up — verify hardware layers before running integrated modes.

### I2C Bus (are devices connected?)

```python
from sensors import DistanceSensor
tof = DistanceSensor()
tof.scan_i2c()
```

### ToF Distance Sensor

```python
tof.read()                # single filtered reading (median of 5)
tof.continuous_print()    # live readout — Ctrl+C to stop
```

### OLED Display

```python
from display import Display
screen = Display()
screen.text("Line 1", "Line 2", "Line 3", "Line 4")
screen.progress("Loading", 75)
```

If the OLED is not connected, all methods still work — they print to serial instead.

### Latch Servo (MG90S — positional)

```python
from servo import Positional
latch = Positional(2)       # GP2
latch.set_angle(90)         # closed position
latch.set_angle(20)         # open position (fires the arm)
latch.sweep(20, 90)         # smooth motion back to closed
```

### Arm Servo (MG996R — 360° continuous)

```python
from servo import Continuous
arm = Continuous(3)          # GP3
arm.spin(speed=50, duration_ms=1000)    # spin forward 1s
arm.spin(speed=-50, duration_ms=1000)   # spin reverse 1s
arm.stop()                              # halt
```

Speed ranges from -100 (full reverse) to +100 (full forward). Duration controls how far the arm pulls back, which controls launch power.

### Stepper Motor (NEMA 17 turret)

```python
from stepper import Stepper
turret = Stepper()
turret.enable()              # lock motor in place
turret.move(800)             # ~90° clockwise
turret.move(-800)            # ~90° counter-clockwise
turret.goto_angle(180)       # absolute: face 180°
turret.home()                # return to 0°
turret.disable()             # release motor (saves power)
```

3200 microsteps = one full revolution (200 native steps × 16 microstepping).

### Magazine Servo (positional)

```python
from servo import Positional
mag = Positional(7)          # GP7
mag.set_angle(90)            # gate closed
mag.set_angle(45)            # gate open — drops 1 ball
mag.set_angle(90)            # gate closed
```

### Full Scan (tower detection)

```python
from stepper import Stepper
from sensors import DistanceSensor
from display import Display
from scanner import Scanner

turret = Stepper()
tof = DistanceSensor()
screen = Display()
scan = Scanner(turret, tof, screen)

turret.enable()
towers = scan.full_scan()
scan.print_towers(towers)
turret.disable()
```

### Launcher (fire sequence)

```python
from launcher import Launcher
gun = Launcher()
gun.initialise()

gun.reload()                          # drop ball from magazine
gun.latch_close()                     # ensure latch holds
gun.cock(duration_ms=600)             # pull arm back 600ms
gun.manual_fire()                     # release latch → FIRE

gun.fire_at_distance(1300)            # full auto: reload → cock → fire for 1300mm target
gun.emergency_stop()                  # kill all servos immediately
```

---

## Calibration

The calibration table maps arm cock duration (ms) to launch distance (mm). Without real calibration data, every shot misses.

### Procedure

```bash
# Boot the Pico, select mode 2
cal> testshot 200       # fire at 200ms cock duration, enter measured distance
cal> testshot 200       # repeat 2 more times for averaging
cal> testshot 200
cal> testshot 400       # increase duration, repeat 3×
cal> testshot 400
cal> testshot 400
# ... continue for 600, 800, 1000, 1200
cal> table              # generates the table — copy into config.py
```

The `table` command outputs a ready-to-paste Python list:

```python
CALIBRATION_TABLE = [
    (  200,   503),
    (  400,   780),
    (  600,  1050),
    (  800,  1310),
    ( 1000,  1580),
    ( 1200,  1870),
]
```

Paste this into `config.py`, save, and reboot.

### Other Calibration Commands

| Command | Action |
|---------|--------|
| `dist` | Read current ToF distance |
| `live` | Continuous distance readout (Ctrl+C to stop) |
| `latch open` / `latch close` | Test latch mechanism |
| `arm <speed> <ms>` | Spin arm servo manually |
| `cock <ms>` | Pull arm back for N ms |
| `fire` | Release latch (fire current load) |
| `step <N>` | Rotate turret N steps (+CW, -CCW) |
| `angle <deg>` | Rotate turret to absolute angle |
| `mag` | Trigger magazine reload |
| `scan` | Run full 360° tower scan |
| `log` | Show all logged test shots |
| `table` | Generate calibration table from logged shots |
| `clear` | Clear shot log |
| `estop` | Emergency stop all motors |
| `help` | Print all commands |
| `quit` | Exit calibration mode |

---

## Autonomous Sequence

When mode 1 is selected, the system runs this sequence with zero human input:

1. **Initialise** — all servos to safe positions, enable stepper, check sensor
2. **Scan** — 360° turret rotation, 200 ToF readings (one every 1.8°)
3. **Detect** — cluster consecutive close readings into tower positions
4. **Prioritise** — sort towers: far first (×6), middle (×4), close (×2)
5. **Engage** (up to 5 shots) — for each tower:
   - Aim turret → re-verify distance → lookup calibration table
   - Reload from magazine → cock arm → countdown beeps → fire
   - Reset arm to rest position
6. **Finish** — return turret home, disable stepper, display results

---

## Configuration Reference

All tuneable parameters live in `config.py`. The most commonly adjusted values during a build:

| Parameter | Default | What It Controls |
|-----------|---------|-----------------|
| `LATCH_CLOSED` | 90 | Servo angle that holds the arm (tune to your mechanism) |
| `LATCH_OPEN` | 20 | Servo angle that releases the arm |
| `ARM_SPEED` | 70 | MG996R cocking speed (0–100) |
| `ARM_RELEASE_SPEED` | -50 | MG996R return speed (negative = reverse) |
| `ARM_COCK_DURATION_MIN` | 200 | Shortest cock duration in ms (close targets) |
| `ARM_COCK_DURATION_MAX` | 1200 | Longest cock duration in ms (far targets) |
| `MICROSTEP_MODE` | 16 | DRV8825 microstepping (must match M0/M1/M2 wiring) |
| `BACKGROUND_THRESHOLD` | 2200 | mm — ToF readings above this are ignored during scan |
| `CLOSE_MAX` | 1050 | mm — towers closer than this are classified "close" |
| `MIDDLE_MAX` | 1550 | mm — towers closer than this are classified "middle" |
| `TOWER_MIN_WIDTH` | 2 | Minimum scan samples to count as a tower (noise filter) |
| `TOWER_MAX_WIDTH` | 30 | Maximum scan samples (rejects walls) |
| `CALIBRATION_TABLE` | placeholder | **(must replace with real test data)** |

---

## Documentation

| Document | Contents |
|----------|----------|
| [`catapult_plan.md`](catapult_plan.md) | Full build guide: component explanations, power architecture, step-by-step wiring with test checkpoints, mechanical assembly, calibration walkthrough, day-by-day schedule |
| [`test.md`](test_log.md) | 180-item checklist covering pre-build inventory, power setup, individual component tests, module integration, calibration data collection, competition simulation, and competition day prep |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pico resets when servo moves | MG996R brownout | Dedicated 5V supply for MG996R |
| Stepper vibrates, won't rotate | Motor coil wires crossed | Swap one wire between A and B coil pairs |
| Stepper skips steps | DRV8825 current too low | Increase Vref (quarter turn CW on pot) |
| ToF not found on I2C scan | Wrong voltage or wiring | VIN must be 3.3V not 5V. Check SDA/SCL |
| Scan detects 0 towers | Threshold too high or sensor tilted | Lower `BACKGROUND_THRESHOLD`. Level sensor |
| Shots inconsistent | Loose pivot or ball placement | Tighten arm bolt. Check cup holds ball firmly |
| `ImportError` on boot | Library file missing | Upload `vl53l0x.py` and `ssd1306.py` to Pico root |

See [`catapult_plan.md`](catapult_plan.md) for the full troubleshooting guide.

---

## License

Built for Hack-A-Bot Live. Inspired by [Arduino Robot Catapult](https://www.instructables.com/Arduino-Robot-Catapult/) by avi_o (used as high-level reference only — different hardware, original code).
