# Hack-A-Bot Catapult — Test Log & Checklist

> Print this out or keep it open on your laptop during the build.
> Tick boxes as you go. Write results directly into this file.
> If a test fails, note the fix in the "Notes" column before moving on.

---

## Phase 0: Pre-Build Checks

### 0.1 Software Setup

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 0.1.1 | MicroPython firmware flashed to Pico 2 (hold BOOTSEL → drag .uf2) | ☐ | Firmware version: ________ |
| 0.1.2 | Thonny IDE or mpremote connects to Pico over USB | ☐ | |
| 0.1.3 | REPL responds to `print("hello")` | ☐ | |
| 0.1.4 | `vl53l0x.py` library uploaded to Pico root | ☐ | Source: github.com/kevinmcaleer/vl53lx0 |
| 0.1.5 | `ssd1306.py` library uploaded to Pico root | ☐ | Source: github.com/stlehmann/micropython-ssd1306 |
| 0.1.6 | All 9 project files uploaded to Pico root | ☐ | config, servo, stepper, sensors, display, scanner, launcher, calibrate, main |
| 0.1.7 | `import config` runs without errors in REPL | ☐ | |
| 0.1.8 | `import servo` runs without errors | ☐ | |
| 0.1.9 | `import stepper` runs without errors | ☐ | |
| 0.1.10 | `import sensors` runs without errors | ☐ | |
| 0.1.11 | `import display` runs without errors | ☐ | |
| 0.1.12 | `import scanner` runs without errors | ☐ | |
| 0.1.13 | `import launcher` runs without errors | ☐ | |
| 0.1.14 | `import calibrate` runs without errors | ☐ | |

### 0.2 Component Inventory

| # | Component | Qty | Have it? | Condition |
|---|-----------|-----|----------|-----------|
| 0.2.1 | Raspberry Pi Pico 2 | 1 | ☐ | |
| 0.2.2 | VL53L0X V2 ToF sensor | 1 | ☐ | |
| 0.2.3 | SSD1306 0.96" OLED | 1 | ☐ | |
| 0.2.4 | MG996R 360° servo | 1 | ☐ | |
| 0.2.5 | MG90S micro servo | 1 | ☐ | |
| 0.2.6 | NEMA 17 stepper motor | 1 | ☐ | |
| 0.2.7 | DRV8825 stepper driver + heatsink | 1 | ☐ | |
| 0.2.8 | LM2596S buck converter | 1 | ☐ | |
| 0.2.9 | 12V 6A power supply | 1 | ☐ | |
| 0.2.10 | USB-A to Micro-USB cable | 1 | ☐ | |
| 0.2.11 | Perfboard 7×9 cm | 1 | ☐ | |
| 0.2.12 | 22AWG wire (2m) | 1 | ☐ | |
| 0.2.13 | M3×10mm screws | ≥10 | ☐ | |
| 0.2.14 | Capacitor kit | 1 | ☐ | |
| 0.2.15 | 30mm 3D-printed balls | ≥3 | ☐ | Count: ________ |
| 0.2.16 | Rubber bands / springs (for arm energy) | — | ☐ | Type: ________ |
| 0.2.17 | Screwdriver set | 1 | ☐ | |
| 0.2.18 | Multimeter | 1 | ☐ | |

---

## Phase 1: Power & Wiring

### 1.1 Buck Converter Setup

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1.1.1 | 12V PSU powered on, multimeter reads 12V ±0.5V across output terminals | ☐ | Measured: ________ V |
| 1.1.2 | PSU positive → LM2596S IN+, PSU negative → LM2596S IN- | ☐ | Double-checked polarity |
| 1.1.3 | Multimeter red probe on OUT+, black on OUT- | ☐ | |
| 1.1.4 | Turned pot until output reads 5.0V ±0.1V (NO LOAD connected yet) | ☐ | Measured: ________ V |
| 1.1.5 | Output stays stable at 5.0V for 30 seconds | ☐ | |
| 1.1.6 | Connected Pico VSYS to OUT+, Pico GND to OUT- | ☐ | |
| 1.1.7 | Pico powers on from buck converter (onboard LED or REPL responds) | ☐ | |
| 1.1.8 | Re-checked voltage with Pico connected (still 5.0V ±0.2V) | ☐ | Measured: ________ V |

### 1.2 Common Ground

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1.2.1 | PSU GND, buck converter GND, Pico GND all connected together | ☐ | |
| 1.2.2 | DRV8825 GND connected to common ground | ☐ | |
| 1.2.3 | Servo GND wires connected to common ground | ☐ | |
| 1.2.4 | Sensor GND wires connected to common ground | ☐ | |
| 1.2.5 | OLED GND connected to common ground | ☐ | |
| 1.2.6 | Continuity test: multimeter beeps between any two GND points | ☐ | |

### 1.3 DRV8825 Setup

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1.3.1 | Heatsink attached to DRV8825 chip | ☐ | |
| 1.3.2 | VMOT connected to 12V (direct from PSU, NOT from buck converter) | ☐ | |
| 1.3.3 | GND connected to common ground | ☐ | |
| 1.3.4 | Vref measured with multimeter (red on pot, black on GND) | ☐ | Vref: ________ V |
| 1.3.5 | Vref adjusted to ~0.7V for 1A current limit (formula: I = Vref × 2) | ☐ | Target current: ________ A |
| 1.3.6 | STEP → GP4, DIR → GP5, ENABLE → GP6 wired | ☐ | |
| 1.3.7 | Motor coil wires connected to correct A1/A2/B1/B2 terminals | ☐ | |
| 1.3.8 | 100µF capacitor across VMOT and GND (close to DRV8825) | ☐ | |

### 1.4 I2C Bus

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1.4.1 | OLED SDA → GP0 (pin 1), OLED SCL → GP1 (pin 2) | ☐ | |
| 1.4.2 | OLED VCC → 3.3V (pin 36), OLED GND → GND | ☐ | |
| 1.4.3 | VL53L0X SDA → GP0 (same bus), VL53L0X SCL → GP1 | ☐ | |
| 1.4.4 | VL53L0X VIN → 3.3V, VL53L0X GND → GND | ☐ | |
| 1.4.5 | I2C scan detects both devices: | ☐ | |
| | `from sensors import DistanceSensor` | | |
| | `tof = DistanceSensor()` | | |
| | `tof.scan_i2c()` | | |
| 1.4.6 | 0x29 (VL53L0X) appears in scan | ☐ | |
| 1.4.7 | 0x3C (SSD1306) appears in scan | ☐ | |

### 1.5 Servo Power

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 1.5.1 | MG90S VCC → 5V rail, GND → common GND, signal → GP2 | ☐ | |
| 1.5.2 | MG996R VCC → dedicated 5-6V supply, GND → common GND, signal → GP3 | ☐ | Power source: ________ |
| 1.5.3 | Magazine servo VCC → 5V rail, GND → GND, signal → GP7 | ☐ | |
| 1.5.4 | MG996R does NOT cause Pico to reset when it moves (power is sufficient) | ☐ | |
| 1.5.5 | Checked voltage on 5V rail while MG996R spins (should stay >4.5V) | ☐ | Measured under load: ________ V |

---

## Phase 2: Individual Component Tests

### 2.1 OLED Display (display.py)

```python
from display import Display
screen = Display()
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.1.1 | Display initialises | `screen = Display()` | Prints "OLED initialised OK" | ☐ | |
| 2.1.2 | Show text | `screen.text("Line1","Line2","Line3","Line4")` | All 4 lines visible | ☐ | |
| 2.1.3 | Long text truncation | `screen.text("This is a very long line")` | Truncated at 16 chars, no crash | ☐ | |
| 2.1.4 | Progress bar | `screen.progress("Loading", 50)` | Bar fills to halfway | ☐ | |
| 2.1.5 | Progress 0% | `screen.progress("Empty", 0)` | Empty bar outline | ☐ | |
| 2.1.6 | Progress 100% | `screen.progress("Full", 100)` | Fully filled bar | ☐ | |
| 2.1.7 | Clear display | `screen.clear()` | Screen goes blank | ☐ | |
| 2.1.8 | Splash screen | `screen.splash()` | Shows title and version | ☐ | |
| 2.1.9 | Serial fallback | Disconnect OLED, repeat 2.1.2 | Text appears in serial, no crash | ☐ | |

### 2.2 ToF Sensor (sensors.py)

```python
from sensors import DistanceSensor
tof = DistanceSensor()
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.2.1 | Sensor initialises | `tof = DistanceSensor()` | Prints "VL53L0X initialised OK" | ☐ | |
| 2.2.2 | Single reading | `tof.read_raw()` | Returns number 30-8000 | ☐ | Value: ________ mm |
| 2.2.3 | Filtered reading | `tof.read()` | Stable number (median of 5) | ☐ | Value: ________ mm |
| 2.2.4 | Hand at 10cm | Hold hand 10cm from sensor | Reads ~100mm ±20mm | ☐ | Value: ________ mm |
| 2.2.5 | Hand at 50cm | Hold hand 50cm from sensor | Reads ~500mm ±30mm | ☐ | Value: ________ mm |
| 2.2.6 | Wall at 1m | Point at wall 1m away | Reads ~1000mm ±50mm | ☐ | Value: ________ mm |
| 2.2.7 | Wall at 2m | Point at wall 2m away | Reads ~2000mm ±100mm | ☐ | Value: ________ mm |
| 2.2.8 | Open space (no target) | Point at ceiling/far wall >3m | Reads 9999 or >2500 | ☐ | Value: ________ mm |
| 2.2.9 | Consistency check | Take 10 readings at fixed target | All within ±30mm of each other | ☐ | Range: ________ to ________ mm |
| 2.2.10 | Continuous readout | `tof.continuous_print()` | Live values, Ctrl+C stops cleanly | ☐ | |
| 2.2.11 | Sensor blocked/covered | Cover sensor with hand | Returns 9999 or very small number | ☐ | |
| 2.2.12 | Fast read | `tof.read_fast()` | Returns quickly (<50ms) | ☐ | |

### 2.3 Latch Servo — MG90S Positional (servo.py)

```python
from servo import Positional
latch = Positional(2)
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.3.1 | Create servo object | `latch = Positional(2)` | No error | ☐ | |
| 2.3.2 | Move to 0° | `latch.set_angle(0)` | Servo moves to one extreme | ☐ | |
| 2.3.3 | Move to 90° | `latch.set_angle(90)` | Servo moves to middle | ☐ | |
| 2.3.4 | Move to 180° | `latch.set_angle(180)` | Servo moves to other extreme | ☐ | |
| 2.3.5 | Smooth sweep | `latch.sweep(0, 180, delay_ms=20)` | Smooth motion, no jerks | ☐ | |
| 2.3.6 | Reverse sweep | `latch.sweep(180, 0, delay_ms=20)` | Smooth reverse | ☐ | |
| 2.3.7 | Latch closed position | `latch.set_angle(90)` | Mechanism actually holds arm | ☐ | Adjust LATCH_CLOSED in config if needed |
| 2.3.8 | Latch open position | `latch.set_angle(20)` | Mechanism actually releases arm | ☐ | Adjust LATCH_OPEN in config if needed |
| 2.3.9 | No Pico reset during movement | Move rapidly 0→180→0 | Pico stays connected | ☐ | If resets, power issue |
| 2.3.10 | Off command | `latch.off()` | Servo goes limp (no holding torque) | ☐ | |

### 2.4 Arm Servo — MG996R 360° Continuous (servo.py)

```python
from servo import Continuous
arm = Continuous(3)
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.4.1 | Create servo object | `arm = Continuous(3)` | No error, servo stationary | ☐ | |
| 2.4.2 | Spin forward slowly | `arm.spin(speed=30, duration_ms=1000)` | Spins one direction for 1s, stops | ☐ | |
| 2.4.3 | Spin forward fast | `arm.spin(speed=100, duration_ms=500)` | Spins faster in same direction | ☐ | |
| 2.4.4 | Spin reverse slowly | `arm.spin(speed=-30, duration_ms=1000)` | Spins opposite direction | ☐ | |
| 2.4.5 | Spin reverse fast | `arm.spin(speed=-100, duration_ms=500)` | Spins faster opposite | ☐ | |
| 2.4.6 | Speed zero = stop | `arm.spin(speed=0, duration_ms=1000)` | Does not move | ☐ | |
| 2.4.7 | Stop command | `arm.spin_start(50)` then `arm.stop()` | Starts spinning, then stops | ☐ | |
| 2.4.8 | Off command | `arm.off()` | Servo goes limp | ☐ | |
| 2.4.9 | Determine cocking direction | Try +speed and -speed | Which direction pulls arm back? | ☐ | Cock direction: positive / negative |
| 2.4.10 | No Pico brownout | Spin at full speed | Pico stays on, voltage >4.5V | ☐ | |

### 2.5 Stepper Motor — NEMA 17 via DRV8825 (stepper.py)

```python
from stepper import Stepper
turret = Stepper()
turret.enable()
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.5.1 | Enable motor | `turret.enable()` | Motor locks in place (holding torque) | ☐ | |
| 2.5.2 | Small CW move | `turret.move(100)` | Slight clockwise rotation | ☐ | |
| 2.5.3 | Small CCW move | `turret.move(-100)` | Returns to approximately starting pos | ☐ | |
| 2.5.4 | Quarter turn CW | `turret.move(turret.steps_per_rev()//4)` | Exactly 90° rotation | ☐ | |
| 2.5.5 | Full revolution | `turret.move(turret.steps_per_rev())` | Exactly 360°, returns to same spot | ☐ | Mark starting position with tape |
| 2.5.6 | Position tracking | `print(turret.position)` after moves | Matches expected cumulative steps | ☐ | |
| 2.5.7 | Goto absolute | `turret.goto(800)` then `turret.goto(0)` | Goes to position, then back to start | ☐ | |
| 2.5.8 | Goto angle | `turret.goto_angle(90)` | Turret faces 90° | ☐ | |
| 2.5.9 | Home | `turret.home()` | Returns to step 0 | ☐ | |
| 2.5.10 | Acceleration (no missed steps) | `turret.move(1600)` with accel | Smooth ramp up/down, no stuttering | ☐ | |
| 2.5.11 | Full revolution accuracy | Mark start pos with tape, do full rev | Returns to exact same position | ☐ | Overshoot/undershoot: ________ |
| 2.5.12 | Disable | `turret.disable()` | Motor shaft spins freely by hand | ☐ | |
| 2.5.13 | No overheating | Run motor for 2 minutes | DRV8825 warm but not burning hot | ☐ | Approx temp: ________ |
| 2.5.14 | Motor direction matches code | `turret.move(800)` | CW in real life = positive in code | ☐ | If reversed, swap motor coil wires |

### 2.6 Magazine Servo (if built)

```python
from servo import Positional
mag = Positional(7)
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.6.1 | Gate closed | `mag.set_angle(90)` | Blocks ball from dropping | ☐ | |
| 2.6.2 | Gate open | `mag.set_angle(45)` | Ball drops into cup | ☐ | |
| 2.6.3 | Only 1 ball drops | Open and close gate once | Exactly 1 ball falls through | ☐ | Adjust timing/angles if 0 or 2 |
| 2.6.4 | Multiple reloads | Open/close 5 times with balls loaded | 1 ball each time, no jams | ☐ | |
| 2.6.5 | Empty magazine | Open gate with no balls | No crash, no jam | ☐ | |

### 2.7 Buzzer (optional)

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 2.7.1 | Buzzer beeps | In launcher: `gun._beep(1000, 200)` | Audible tone | ☐ | |
| 2.7.2 | Different frequencies | Try 500Hz, 1000Hz, 2000Hz | Pitch changes | ☐ | |
| 2.7.3 | No buzzer = no crash | Disconnect buzzer, run code | Code runs normally, no errors | ☐ | |

---

## Phase 3: Module Integration Tests

### 3.1 Launcher Module (launcher.py)

```python
from launcher import Launcher
gun = Launcher()
gun.initialise()
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 3.1.1 | Initialise | `gun.initialise()` | Latch closes, arm stops, mag closes | ☐ | |
| 3.1.2 | Latch cycle | `gun.latch_close()` then `gun.latch_open()` | Holds then releases | ☐ | |
| 3.1.3 | Arm cock short | `gun.latch_close(); gun.cock(200)` | Small arm pullback, latch holds | ☐ | |
| 3.1.4 | Arm cock long | `gun.latch_close(); gun.cock(1000)` | Large arm pullback, latch holds | ☐ | |
| 3.1.5 | Manual fire | `gun.manual_fire()` | Beeps, latch opens, arm returns | ☐ | |
| 3.1.6 | Full fire sequence | `gun.fire_at_distance(1000)` | Reload→cock→countdown→fire→reset | ☐ | |
| 3.1.7 | Calibration lookup | `gun.compute_cock_duration(800)` | Returns reasonable ms value | ☐ | Value: ________ ms |
| 3.1.8 | Calibration lookup (min) | `gun.compute_cock_duration(100)` | Returns table minimum | ☐ | Value: ________ ms |
| 3.1.9 | Calibration lookup (max) | `gun.compute_cock_duration(3000)` | Returns table maximum | ☐ | Value: ________ ms |
| 3.1.10 | Emergency stop | `gun.emergency_stop()` | All servos stop immediately | ☐ | |
| 3.1.11 | Reload works | `gun.reload()` | Ball drops into cup | ☐ | |
| 3.1.12 | Shot counter | Fire 3 times, check `gun.shots_fired` | Returns 3 | ☐ | |

### 3.2 Scanner Module (scanner.py)

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
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 3.2.1 | Full 360° scan (empty room) | `towers = scan.full_scan()` | Completes without error, turret returns home | ☐ | Time taken: ________ s |
| 3.2.2 | No towers in empty room | `scan.print_towers(towers)` | "No towers detected" or very few | ☐ | |
| 3.2.3 | Single target detection | Place 1 object at ~1m, rescan | Detects 1 tower at ~1000mm | ☐ | Reported: ________ mm |
| 3.2.4 | Distance accuracy | Measure real distance with tape | Sensor reading within ±100mm | ☐ | Real: ________ mm, Sensor: ________ mm |
| 3.2.5 | Angle accuracy | Place target at known angle | Reported angle within ±5° | ☐ | Real: ________ °, Reported: ________ ° |
| 3.2.6 | Multiple targets | Place 3 objects at different angles | Detects 3 separate towers | ☐ | |
| 3.2.7 | Distance classification | Objects at ~0.8m, ~1.3m, ~1.8m | Correctly classified close/middle/far | ☐ | |
| 3.2.8 | Wall rejection | Large wall/flat surface in scan range | Not detected as a tower (too wide) | ☐ | Adjust TOWER_MAX_WIDTH if needed |
| 3.2.9 | Priority sorting | `sorted = scan.prioritise_towers(towers)` | Far targets first, close last | ☐ | |
| 3.2.10 | Quick verify | Aim at tower, `scan.quick_verify(tower)` | Updated distance more accurate | ☐ | |
| 3.2.11 | Narrow re-scan | `scan.narrow_scan(tower['step'])` | Returns refined step position | ☐ | |
| 3.2.12 | OLED progress bar | Watch OLED during scan | Shows "Scanning" with progress % | ☐ | |
| 3.2.13 | Radar display | `screen.radar(towers, turret.steps_per_rev())` | Dots visible at correct positions | ☐ | |
| 3.2.14 | Scan repeatability | Run full_scan 3 times, same setup | Same towers detected each time (±1 sample) | ☐ | |

### 3.3 Calibration Shell (calibrate.py)

```python
from calibrate import run
run()
```

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 3.3.1 | Shell starts | `run()` | Prints help, shows prompt `cal>` | ☐ | |
| 3.3.2 | Help command | `help` | Prints all available commands | ☐ | |
| 3.3.3 | I2C scan | `i2c` | Shows connected devices | ☐ | |
| 3.3.4 | Distance reading | `dist` | Shows distance on screen + serial | ☐ | |
| 3.3.5 | Live readout | `live` | Continuous readings, Ctrl+C stops | ☐ | |
| 3.3.6 | Latch control | `latch open` then `latch close` | Servo moves correctly | ☐ | |
| 3.3.7 | Arm control | `arm 50 500` | Spins at speed 50 for 500ms | ☐ | |
| 3.3.8 | Stepper control | `step 200` then `step -200` | Turns CW then CCW | ☐ | |
| 3.3.9 | Angle control | `angle 90` | Turret faces 90° | ☐ | |
| 3.3.10 | Cock command | `cock 500` | Arm pulls back, latch holds | ☐ | |
| 3.3.11 | Fire command | `fire` | Arm releases, prompts for measurement | ☐ | |
| 3.3.12 | Test shot with log | `testshot 600` | Cocks, fires, logs result | ☐ | |
| 3.3.13 | View shot log | `log` | Shows all logged shots | ☐ | |
| 3.3.14 | Generate table | `table` (after 3+ test shots) | Prints calibration table for config.py | ☐ | |
| 3.3.15 | Clear log | `clear` | Empties shot log | ☐ | |
| 3.3.16 | Scan from cal mode | `scan` | Runs full 360° scan | ☐ | |
| 3.3.17 | Emergency stop | `estop` | All motors stop | ☐ | |
| 3.3.18 | Quit | `quit` | Exits cleanly, disables motors | ☐ | |
| 3.3.19 | Invalid command | `asdfgh` | "Unknown command" message, no crash | ☐ | |
| 3.3.20 | Magazine reload | `mag` | Ball drops into cup | ☐ | |

---

## Phase 4: Calibration Test Shots

> Fire test shots at different cock durations. Measure where each ball lands.
> Use `testshot <ms>` in calibration mode — it logs results automatically.

### 4.1 Calibration Data Collection

| Shot # | Cock Duration (ms) | Measured Landing Distance (mm) | Notes |
|--------|-------------------|-------------------------------|-------|
| 1 | 200 | | |
| 2 | 200 | | |
| 3 | 200 | | |
| 4 | 400 | | |
| 5 | 400 | | |
| 6 | 400 | | |
| 7 | 600 | | |
| 8 | 600 | | |
| 9 | 600 | | |
| 10 | 800 | | |
| 11 | 800 | | |
| 12 | 800 | | |
| 13 | 1000 | | |
| 14 | 1000 | | |
| 15 | 1000 | | |
| 16 | 1200 | | |
| 17 | 1200 | | |
| 18 | 1200 | | |
| 19 | | | |
| 20 | | | |

### 4.2 Calibration Validation

| # | Test | Pass? | Notes |
|---|------|-------|-------|
| 4.2.1 | Generated calibration table from `table` command | ☐ | |
| 4.2.2 | Pasted table into config.py → CALIBRATION_TABLE | ☐ | |
| 4.2.3 | Saved and rebooted Pico | ☐ | |
| 4.2.4 | Test: `gun.compute_cock_duration(800)` returns sensible value | ☐ | Value: ________ ms |
| 4.2.5 | Test: `gun.compute_cock_duration(1300)` returns sensible value | ☐ | Value: ________ ms |
| 4.2.6 | Test: `gun.compute_cock_duration(1800)` returns sensible value | ☐ | Value: ________ ms |
| 4.2.7 | Validation shot at ~800mm target | ☐ | Hit within 15cm? Y/N |
| 4.2.8 | Validation shot at ~1300mm target | ☐ | Hit within 15cm? Y/N |
| 4.2.9 | Validation shot at ~1800mm target | ☐ | Hit within 15cm? Y/N |
| 4.2.10 | Consistency: 3 shots at same distance land within 10cm of each other | ☐ | Spread: ________ cm |

### 4.3 Config Values Record

> After calibration, record your final config values here for backup.

| Parameter | Value |
|-----------|-------|
| LATCH_CLOSED | |
| LATCH_OPEN | |
| ARM_SPEED | |
| ARM_RELEASE_SPEED | |
| ARM_COCK_DURATION_MIN | |
| ARM_COCK_DURATION_MAX | |
| ARM_RELEASE_DURATION | |
| BACKGROUND_THRESHOLD | |
| CLOSE_MAX | |
| MIDDLE_MAX | |
| TOWER_MIN_WIDTH | |
| TOWER_MAX_WIDTH | |
| CALIBRATION_TABLE | (see config.py) |

---

## Phase 5: Full Autonomous Integration

### 5.1 Mode Selection

| # | Test | Command | Expected | Pass? | Notes |
|---|------|---------|----------|-------|-------|
| 5.1.1 | Main menu appears | `from main import main; main()` | Shows 4 options | ☐ | |
| 5.1.2 | Sensor test mode | Select option 3 | Reads sensor, shows on OLED | ☐ | |
| 5.1.3 | Stepper test mode | Select option 4 | Quarter turns both directions | ☐ | |
| 5.1.4 | Calibration mode | Select option 2 | Opens calibration shell | ☐ | |

### 5.2 Autonomous Sequence — Controlled Environment

> Set up 1-3 test targets at known positions before running.

| # | Test | Setup | Expected | Pass? | Notes |
|---|------|-------|----------|-------|-------|
| 5.2.1 | Auto mode starts | Select option 1 | Splash screen, initialisation | ☐ | |
| 5.2.2 | Scan phase | — | Turret rotates 360°, returns home | ☐ | |
| 5.2.3 | Detection phase | 1 target at 1m | Detects 1 tower, correct distance | ☐ | |
| 5.2.4 | Aiming phase | — | Turret rotates to face target | ☐ | |
| 5.2.5 | Distance verification | — | Re-reads distance after aiming | ☐ | |
| 5.2.6 | Reload | — | Ball drops into cup | ☐ | |
| 5.2.7 | Fire | — | Ball launches toward target | ☐ | |
| 5.2.8 | Arm reset | — | Arm returns to rest after firing | ☐ | |
| 5.2.9 | Complete sequence | 1 target | Full auto: scan→aim→reload→fire→reset | ☐ | |
| 5.2.10 | Multi-target sequence | 3 targets at different angles | Fires at each one in priority order | ☐ | |
| 5.2.11 | Priority order correct | Far + middle + close targets | Far hit first, then middle, then close | ☐ | |
| 5.2.12 | Shot limit respected | 6+ targets but MAX_SHOTS=5 | Stops after 5 shots | ☐ | |
| 5.2.13 | OLED updates throughout | Watch screen during sequence | Shows scan progress, targeting, shot info | ☐ | |
| 5.2.14 | Serial log complete | Read serial output after run | All phases logged with distances and decisions | ☐ | |
| 5.2.15 | Finish state | After sequence completes | Turret home, motors disabled, "COMPLETE" shown | ☐ | |

### 5.3 Autonomous — Edge Cases

| # | Test | Setup | Expected | Pass? | Notes |
|---|------|-------|----------|-------|-------|
| 5.3.1 | No targets found | Empty room, nothing in range | Shows "NO TARGETS FOUND", exits cleanly | ☐ | |
| 5.3.2 | Sensor disconnected | Unplug VL53L0X before running | Shows error message, doesn't crash | ☐ | |
| 5.3.3 | Target very close (<0.5m) | Place object at 40cm | Fires with minimum power | ☐ | |
| 5.3.4 | Target at max range | Object at ~2m | Fires with maximum power | ☐ | |
| 5.3.5 | Magazine empty mid-sequence | Load 2 balls, set up 4 targets | Fires 2, attempts 3rd (fails gracefully?) | ☐ | |
| 5.3.6 | Power interruption recovery | Unplug/replug during scan | Pico reboots to main menu | ☐ | |
| 5.3.7 | Multiple runs without reboot | Run autonomous twice in a row | Second run works correctly | ☐ | |

---

## Phase 6: Competition Simulation

### 6.1 Arena Setup

> Replicate the actual competition layout:
> - Catapult in center
> - 6 columns of 3 stacked blocks
> - 2 close (0.8m), 2 middle (1.3m), 2 far (1.8m)
> - Arranged in a circle around the catapult

| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| 6.1.1 | 6 block towers placed at correct distances | ☐ | |
| 6.1.2 | Towers are 3 blocks high | ☐ | |
| 6.1.3 | 30mm balls loaded in magazine (at least 5) | ☐ | |
| 6.1.4 | Catapult centered in arena | ☐ | |
| 6.1.5 | Power supply connected and stable | ☐ | |
| 6.1.6 | USB disconnected (running on external power only) | ☐ | |

### 6.2 Dress Rehearsal Runs

| Run # | Towers Detected | Shots Fired | Blocks Knocked | Estimated Score | Issues |
|-------|----------------|-------------|----------------|-----------------|--------|
| 1 | /6 | /5 | /12 | /100 | |
| 2 | /6 | /5 | /12 | /100 | |
| 3 | /6 | /5 | /12 | /100 | |
| 4 | /6 | /5 | /12 | /100 | |
| 5 | /6 | /5 | /12 | /100 | |

### 6.3 Score Calculation Worksheet

> For each run, calculate the accuracy score:
> Only top 2 blocks per column count. Bottom block never counts.
>
> Formula: (blocks knocked from top 2 of column) × distance_multiplier
> Close=×2, Middle=×4, Far=×6

| Column | Distance | Multiplier | Top Blocks Knocked (0-2) | Points |
|--------|----------|------------|--------------------------|--------|
| Close 1 | 0.8m | ×2 | /2 | |
| Close 2 | 0.8m | ×2 | /2 | |
| Middle 1 | 1.3m | ×4 | /2 | |
| Middle 2 | 1.3m | ×4 | /2 | |
| Far 1 | 1.8m | ×6 | /2 | |
| Far 2 | 1.8m | ×6 | /2 | |
| | | | **Accuracy Total** | **/40** |

| Category | Points |
|----------|--------|
| Automation (fully autonomous) | /50 |
| Accuracy (from table above) | /40 |
| Engineering & design | /5 |
| Innovation & creativity | /5 |
| **TOTAL** | **/100** |

---

## Phase 7: Competition Day Checklist

### 7.1 Before Leaving

| # | Check | Done? |
|---|-------|-------|
| 7.1.1 | All code saved and tested | ☐ |
| 7.1.2 | Backup of all .py files on USB stick / laptop | ☐ |
| 7.1.3 | config.py has FINAL calibration table | ☐ |
| 7.1.4 | Spare 30mm balls printed (at least 5 extra) | ☐ |
| 7.1.5 | Spare rubber bands / springs packed | ☐ |
| 7.1.6 | Spare wire, screws, tape packed | ☐ |
| 7.1.7 | Multimeter packed | ☐ |
| 7.1.8 | Screwdriver set packed | ☐ |
| 7.1.9 | Laptop + USB cable packed (for emergency reflash) | ☐ |
| 7.1.10 | Power supply + power cable packed | ☐ |

### 7.2 At the Venue — Setup

| # | Check | Done? |
|---|-------|-------|
| 7.2.1 | Catapult placed in arena center | ☐ |
| 7.2.2 | Power supply connected, 5V rail confirmed | ☐ |
| 7.2.3 | Pico boots to main menu | ☐ |
| 7.2.4 | Quick sensor test (mode 3) — distance reads correctly | ☐ |
| 7.2.5 | Quick stepper test (mode 4) — turret rotates smoothly | ☐ |
| 7.2.6 | Loaded 5+ balls in magazine | ☐ |
| 7.2.7 | One test fire to confirm mechanism works | ☐ |
| 7.2.8 | USB cable disconnected for competition run | ☐ |

### 7.3 Competition Run

| # | Step | Done? | Notes |
|---|------|-------|-------|
| 7.3.1 | Confirm targets are set up | ☐ | |
| 7.3.2 | Confirm balls are loaded | ☐ | |
| 7.3.3 | Select mode 1 (AUTONOMOUS) | ☐ | |
| 7.3.4 | Step back — hands off | ☐ | |
| 7.3.5 | Watch OLED for scan progress | ☐ | |
| 7.3.6 | Observe each shot | ☐ | |
| 7.3.7 | Sequence completes | ☐ | |
| 7.3.8 | Record blocks knocked per column | ☐ | See 6.3 worksheet |

### 7.4 If Something Goes Wrong

| Problem | Quick Fix |
|---------|-----------|
| Pico doesn't boot | Check USB cable, check 5V rail with multimeter |
| ToF sensor not found | Reseat I2C wires, check 3.3V, run `tof.scan_i2c()` |
| OLED blank | Check I2C wiring, code still works via serial output |
| Stepper not moving | Check ENABLE pin (should be LOW), check Vref, check 12V to VMOT |
| Servo jittering | Power issue — check 5V rail voltage under load |
| Arm doesn't cock | Check MG996R direction (positive vs negative speed in config) |
| Latch doesn't hold | Adjust LATCH_CLOSED angle in config (±10° increments) |
| Latch doesn't release | Adjust LATCH_OPEN angle in config |
| Balls not feeding | Check magazine servo angles, check tube alignment |
| Scan finds 0 towers | Lower BACKGROUND_THRESHOLD in config, check sensor height/angle |
| Scan finds too many towers | Raise BACKGROUND_THRESHOLD, raise TOWER_MIN_WIDTH |
| Shots all fall short | Increase cock durations in calibration table |
| Shots all overshoot | Decrease cock durations in calibration table |
| Pico resets during fire | Power brownout — add capacitor on 5V rail, or separate servo power |
| Code crash mid-run | Connect USB, check serial for error traceback, fix and reflash |

---

## Troubleshooting Reference

### I2C Issues

```
No devices found:
  → Check SDA/SCL wiring (GP0/GP1)
  → Check power to sensors (3.3V not 5V for VL53L0X)
  → Check for loose connections
  → Try lower I2C frequency: change freq=400000 to freq=100000 in config.py

Only one device found:
  → The missing device has a wiring issue
  → Check its VCC and GND independently
  → Try disconnecting the working device to test the broken one alone
```

### Motor Issues

```
Servo jitters/buzzes but doesn't move:
  → Insufficient power (need >1A for MG996R)
  → Add capacitor across servo power pins
  → Check signal wire connection

Stepper vibrates but doesn't rotate:
  → Coil wires swapped (A1/A2 vs B1/B2)
  → Swap one coil pair and retry
  → Current limit too low (increase Vref)

Stepper skips steps:
  → Speed too high (increase STEP_DELAY_US)
  → Current limit too low
  → Mechanical binding/friction
  → Enable acceleration ramp
```

### Software Issues

```
ImportError: no module named 'xxx':
  → File not uploaded to Pico root
  → Filename typo (case-sensitive!)

MemoryError:
  → Pico running low on RAM
  → Reduce TOF_SAMPLES or SCAN_STEP_SIZE
  → Remove unused imports

OSError: [Errno 5] EIO:
  → I2C communication error
  → Check wiring, reduce bus speed
  → Power cycle the sensor
```
