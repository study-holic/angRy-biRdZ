# Hack-A-Bot Catapult — File Structure
# ======================================
#
# Upload ALL .py files to the root of your Pico 2.
# Also upload the two library files (download separately):
#   - vl53l0x.py  → https://github.com/kevinmcaleer/vl53lx0
#   - ssd1306.py  → https://github.com/stlehmann/micropython-ssd1306
#
#
# FILE MAP
# ────────────────────────────────────────────
#
#   config.py      Pins, constants, calibration table
#                  ↑ imported by everything else
#                  ↑ EDIT THIS FILE to tune your build
#
#   servo.py       Positional + 360° continuous servo classes
#                  ↑ imported by launcher.py, calibrate.py
#
#   stepper.py     NEMA 17 turret control with acceleration
#                  ↑ imported by scanner.py, calibrate.py, main.py
#
#   sensors.py     VL53L0X ToF distance with median filtering
#                  ↑ imported by scanner.py, calibrate.py, main.py
#
#   display.py     SSD1306 OLED (text, progress bar, radar)
#                  ↑ imported by scanner.py, calibrate.py, main.py
#
#   scanner.py     360° sweep scan and tower detection
#                  ↑ imported by calibrate.py, main.py
#
#   launcher.py    Arm, latch, magazine, fire sequence
#                  ↑ imported by calibrate.py, main.py
#
#   calibrate.py   Interactive calibration shell
#                  ↑ imported by main.py (mode 2)
#
#   main.py        Entry point — mode selection + autonomous mode
#                  ↑ runs on boot
#
#
# HOW TO TEST EACH MODULE INDEPENDENTLY
# ────────────────────────────────────────────
#
# Connect to your Pico via Thonny or mpremote, then in the REPL:
#
# 1. Test I2C wiring (are sensors detected?):
#      from sensors import DistanceSensor
#      tof = DistanceSensor()
#      tof.scan_i2c()
#
# 2. Test ToF sensor:
#      tof.continuous_print()       # live distance readout
#
# 3. Test OLED:
#      from display import Display
#      screen = Display()
#      screen.text("Hello", "World")
#
# 4. Test latch servo:
#      from servo import Positional
#      latch = Positional(2)        # pin GP2
#      latch.set_angle(90)          # closed
#      latch.set_angle(20)          # open
#
# 5. Test arm servo (360° continuous):
#      from servo import Continuous
#      arm = Continuous(3)           # pin GP3
#      arm.spin(speed=50, duration_ms=500)
#      arm.spin(speed=-50, duration_ms=500)
#
# 6. Test stepper:
#      from stepper import Stepper
#      turret = Stepper()
#      turret.enable()
#      turret.move(800)              # CW
#      turret.move(-800)             # CCW
#      turret.home()
#      turret.disable()
#
# 7. Full calibration (interactive):
#      from calibrate import run
#      run()
#
# 8. Full autonomous:
#      from main import run_autonomous
#      run_autonomous()
