# test_runner.py — Run catapult code on your laptop in VS Code
# =============================================================
#
# This patches the MicroPython-only imports with mock versions
# so every module can be tested without a Pico connected.
#
# USAGE:
#   1. Put ALL files in the same folder:
#      - Your catapult code (config.py, servo.py, stepper.py, etc.)
#      - The mock files (mock_machine.py, mock_vl53l0x.py, mock_ssd1306.py)
#      - This file (test_runner.py)
#
#   2. Open a terminal in VS Code (Ctrl+`) and run:
#        python test_runner.py
#
#   3. Or run individual tests:
#        python test_runner.py --test servo
#        python test_runner.py --test stepper
#        python test_runner.py --test sensors
#        python test_runner.py --test display
#        python test_runner.py --test scanner
#        python test_runner.py --test launcher
#        python test_runner.py --test calibration
#        python test_runner.py --test autonomous

import sys
import os
import time

# ═══════════════════════════════════════════
#  STEP 1: Patch MicroPython imports
# ═══════════════════════════════════════════
# This MUST happen before importing any catapult code.
# We replace the `machine`, `vl53l0x`, and `ssd1306` modules
# with our mock versions that work on a normal computer.

import mock_machine
import mock_vl53l0x
import mock_ssd1306

# Inject mocks into Python's module system
sys.modules['machine'] = mock_machine

# Patch time module to add MicroPython-specific functions
import time as _time_module
if not hasattr(_time_module, 'sleep_ms'):
    _time_module.sleep_ms = mock_machine.sleep_ms
if not hasattr(_time_module, 'sleep_us'):
    _time_module.sleep_us = mock_machine.sleep_us

sys.modules['vl53l0x'] = mock_vl53l0x
sys.modules['ssd1306'] = mock_ssd1306

print("=" * 60)
print("  MOCK HARDWARE LOADED — running on laptop, not Pico")
print("=" * 60)
print()

# Speed up delays for testing (override time.sleep_ms to be instant)
FAST_MODE = True
if FAST_MODE:
    _original_sleep_ms = mock_machine.sleep_ms
    _original_sleep_us = mock_machine.sleep_us
    _time_module.sleep_ms = lambda ms: None  # skip all delays
    _time_module.sleep_us = lambda us: None  # skip all delays
    _original_sleep = _time_module.sleep
    _time_module.sleep = lambda s: None
    print("[test] FAST MODE: all delays skipped\n")


# ═══════════════════════════════════════════
#  STEP 2: Import catapult modules
# ═══════════════════════════════════════════
# Now that machine/vl53l0x/ssd1306 are patched,
# we can safely import everything.

import config
from servo import Positional, Continuous
from stepper import Stepper
from sensors import DistanceSensor
from display import Display
from scanner import Scanner
from launcher import Launcher


# ═══════════════════════════════════════════
#  TEST FUNCTIONS
# ═══════════════════════════════════════════

def test_config():
    """Verify config.py loads and has sensible values."""
    print("─" * 50)
    print("TEST: config.py")
    print("─" * 50)
    
    checks = [
        ("LATCH_PIN", config.LATCH_PIN, 2),
        ("ARM_PIN", config.ARM_PIN, 3),
        ("STEP_PIN", config.STEP_PIN, 4),
        ("STEPS_PER_TURRET_REV", config.STEPS_PER_TURRET_REV, 3200),
        ("LATCH_CLOSED", config.LATCH_CLOSED, range(0, 181)),
        ("LATCH_OPEN", config.LATCH_OPEN, range(0, 181)),
        ("ARM_SPEED", config.ARM_SPEED, range(1, 101)),
        ("CALIBRATION_TABLE length", len(config.CALIBRATION_TABLE), range(2, 50)),
        ("MAX_SHOTS", config.MAX_SHOTS, 5),
    ]
    
    passed = 0
    for name, value, expected in checks:
        if isinstance(expected, range):
            ok = value in expected
        else:
            ok = value == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name} = {value}")
        if ok:
            passed += 1
    
    print(f"\n  {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_servo():
    """Test both servo classes with dummy hardware."""
    print("─" * 50)
    print("TEST: servo.py — Positional + Continuous")
    print("─" * 50)
    
    errors = []
    
    # Positional servo
    print("\n  Creating Positional servo on pin 2...")
    latch = Positional(2)
    
    print("  set_angle(0):")
    latch.set_angle(0)
    if latch.current_angle != 0:
        errors.append(f"Angle should be 0, got {latch.current_angle}")
    
    print("  set_angle(90):")
    latch.set_angle(90)
    if latch.current_angle != 90:
        errors.append(f"Angle should be 90, got {latch.current_angle}")
    
    print("  set_angle(180):")
    latch.set_angle(180)
    if latch.current_angle != 180:
        errors.append(f"Angle should be 180, got {latch.current_angle}")
    
    print("  Clamping test — set_angle(999):")
    latch.set_angle(999)
    if latch.current_angle != 180:
        errors.append(f"Should clamp to 180, got {latch.current_angle}")
    
    print("  sweep(0, 90):")
    latch.sweep(0, 90, step=30, delay_ms=1)
    
    print("  sweep_to(45):")
    latch.sweep_to(45, step=15, delay_ms=1)
    
    # Continuous servo
    print("\n  Creating Continuous servo on pin 3...")
    arm = Continuous(3)
    
    print("  spin(speed=50, duration_ms=500):")
    arm.spin(speed=50, duration_ms=500)
    
    print("  spin(speed=-50, duration_ms=500):")
    arm.spin(speed=-50, duration_ms=500)
    
    print("  spin(speed=0, duration_ms=100)  — should not move:")
    arm.spin(speed=0, duration_ms=100)
    
    print("  stop():")
    arm.stop()
    
    print("  off():")
    arm.off()
    
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("\n  [PASS] All servo tests passed\n")
    
    return len(errors) == 0


def test_stepper():
    """Test stepper motor control logic."""
    print("─" * 50)
    print("TEST: stepper.py — Turret control")
    print("─" * 50)
    
    errors = []
    
    turret = Stepper()
    
    print("  enable():")
    turret.enable()
    if not turret.enabled:
        errors.append("Should be enabled")
    
    print("  move(800)  — quarter turn CW:")
    turret.move(800)
    if turret.position != 800:
        errors.append(f"Position should be 800, got {turret.position}")
    else:
        print(f"    Position: {turret.position} (expected 800)")
    
    print("  move(-800) — quarter turn CCW:")
    turret.move(-800)
    if turret.position != 0:
        errors.append(f"Position should be 0, got {turret.position}")
    else:
        print(f"    Position: {turret.position} (expected 0)")
    
    print("  goto(1600) — half turn:")
    turret.goto(1600)
    if turret.position != 1600:
        errors.append(f"Position should be 1600, got {turret.position}")
    else:
        print(f"    Position: {turret.position} (expected 1600)")
    
    print("  goto_angle(90):")
    turret.goto_angle(90)
    expected = int(90 * config.STEPS_PER_TURRET_REV / 360)
    if turret.position != expected:
        errors.append(f"Position should be {expected}, got {turret.position}")
    else:
        print(f"    Position: {turret.position} (expected {expected})")
    
    print(f"  get_angle(): {turret.get_angle():.1f}°")
    
    print("  home():")
    turret.home()
    if turret.position != 0:
        errors.append(f"Position should be 0 after home, got {turret.position}")
    else:
        print(f"    Position: {turret.position} (expected 0)")
    
    print(f"  steps_per_rev(): {turret.steps_per_rev()}")
    if turret.steps_per_rev() != config.STEPS_PER_TURRET_REV:
        errors.append(f"steps_per_rev should be {config.STEPS_PER_TURRET_REV}")
    
    print("  reset_position():")
    turret.move(500)
    turret.reset_position()
    if turret.position != 0:
        errors.append(f"Position should be 0 after reset, got {turret.position}")
    else:
        print(f"    Position reset to: {turret.position}")
    
    print("  disable():")
    turret.disable()
    if turret.enabled:
        errors.append("Should be disabled")
    
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("\n  [PASS] All stepper tests passed\n")
    
    return len(errors) == 0


def test_sensors():
    """Test ToF sensor with mock readings."""
    print("─" * 50)
    print("TEST: sensors.py — Distance sensor (mock)")
    print("─" * 50)
    
    errors = []
    
    tof = DistanceSensor()
    
    print("  scan_i2c():")
    devices = tof.scan_i2c()
    if 0x29 not in devices:
        errors.append("0x29 (VL53L0X) not found in mock scan")
    
    print("  is_working():")
    working = tof.is_working()
    print(f"    Result: {working}")
    
    print("  read_raw():")
    raw = tof.read_raw()
    print(f"    Raw reading: {raw} mm")
    
    print("  read() — filtered (median of 5):")
    filtered = tof.read()
    print(f"    Filtered reading: {filtered} mm")
    
    print("  read_fast():")
    fast = tof.read_fast()
    print(f"    Fast reading: {fast} mm")
    
    # Test with specific fake values
    print("\n  Testing with controlled fake values [500, 500, 500, 9000, 100]:")
    mock_vl53l0x.VL53L0X.fake_distances = [500, 500, 500, 9000, 100]
    mock_vl53l0x.VL53L0X._read_index = 0
    
    # Recreate sensor to pick up new fake values
    tof2 = DistanceSensor()
    reading = tof2.read()
    print(f"    Median-filtered reading: {reading} mm (expect ~500)")
    
    # Reset fake distances
    mock_vl53l0x.VL53L0X.fake_distances = None
    mock_vl53l0x.VL53L0X._scan_index = 0
    
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("\n  [PASS] All sensor tests passed\n")
    
    return len(errors) == 0


def test_display():
    """Test OLED display wrapper."""
    print("─" * 50)
    print("TEST: display.py — OLED display (mock)")
    print("─" * 50)
    
    screen = Display()
    
    print("  text():")
    screen.text("Line 1", "Line 2", "Line 3", "Line 4")
    
    print("  progress():")
    screen.progress("Loading", 50)
    
    print("  splash():")
    screen.splash()
    
    print("  shot_info():")
    screen.shot_info(1, 5, "far", 1800, "FIRING")
    
    print("  clear():")
    screen.clear()
    
    print("  is_working():", screen.is_working())
    
    print("\n  [PASS] All display tests passed\n")
    return True


def test_scanner():
    """Test the scanning and tower detection algorithm."""
    print("─" * 50)
    print("TEST: scanner.py — Tower detection")
    print("─" * 50)
    
    errors = []
    
    # Reset mock sensor to simulate towers
    mock_vl53l0x.VL53L0X.fake_distances = None
    mock_vl53l0x.VL53L0X._scan_index = 0
    
    turret = Stepper()
    tof = DistanceSensor()
    screen = Display()
    scan = Scanner(turret, tof, screen)
    
    turret.enable()
    
    print("  Running full_scan()...")
    towers = scan.full_scan()
    
    print(f"\n  Detected {len(towers)} tower(s):")
    scan.print_towers(towers)
    
    if len(towers) == 0:
        errors.append("Should detect at least 1 tower from mock data")
    
    # Check classification
    for t in towers:
        if t['category'] not in ('close', 'middle', 'far'):
            errors.append(f"Invalid category: {t['category']}")
        if t['distance_mm'] < 30 or t['distance_mm'] > 8000:
            errors.append(f"Invalid distance: {t['distance_mm']}")
    
    # Test priority sorting
    print("\n  Priority sorting (far first):")
    prioritised = scan.prioritise_towers(towers)
    if len(prioritised) >= 2:
        cats = [t['category'] for t in prioritised]
        print(f"    Order: {cats}")
        # Far should come before close
        if 'far' in cats and 'close' in cats:
            if cats.index('far') > cats.index('close'):
                errors.append("Far towers should sort before close towers")
    
    turret.disable()
    
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("\n  [PASS] All scanner tests passed\n")
    
    return len(errors) == 0


def test_launcher():
    """Test the firing sequence logic."""
    print("─" * 50)
    print("TEST: launcher.py — Fire sequence")
    print("─" * 50)
    
    errors = []
    
    gun = Launcher()
    
    print("  initialise():")
    gun.initialise()
    
    print("  latch_close():")
    gun.latch_close()
    
    print("  latch_open():")
    gun.latch_open()
    
    print("  cock(duration_ms=500):")
    gun.latch_close()
    gun.cock(duration_ms=500)
    if not gun.is_cocked:
        errors.append("Should be cocked after cock()")
    
    print("  manual_fire():")
    gun.manual_fire()
    if gun.shots_fired != 1:
        errors.append(f"Shot count should be 1, got {gun.shots_fired}")
    else:
        print(f"    Shots fired: {gun.shots_fired}")
    
    print("  reload():")
    gun.reload()
    
    # Test calibration lookup
    print("\n  Calibration table lookup:")
    test_distances = [500, 800, 1000, 1300, 1800, 2500]
    for dist in test_distances:
        dur = gun.compute_cock_duration(dist)
        print(f"    {dist}mm → {dur}ms cock duration")
        if dur <= 0:
            errors.append(f"Duration for {dist}mm should be >0, got {dur}")
    
    print("\n  fire_at_distance(1300):")
    cock_dur = gun.fire_at_distance(1300)
    print(f"    Used cock duration: {cock_dur}ms")
    print(f"    Total shots fired: {gun.shots_fired}")
    if gun.shots_fired != 2:
        errors.append(f"Shot count should be 2, got {gun.shots_fired}")
    
    print("  emergency_stop():")
    gun.emergency_stop()
    
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("\n  [PASS] All launcher tests passed\n")
    
    return len(errors) == 0


def test_autonomous():
    """Run the full autonomous sequence with mock hardware."""
    print("─" * 50)
    print("TEST: Full autonomous sequence (mock hardware)")
    print("─" * 50)
    
    # Reset mock sensor
    mock_vl53l0x.VL53L0X.fake_distances = None
    mock_vl53l0x.VL53L0X._scan_index = 0
    
    print("  Importing and running autonomous mode...\n")
    
    try:
        from main import run_autonomous
        run_autonomous()
        print("\n  [PASS] Autonomous sequence completed without errors\n")
        return True
    except Exception as e:
        print(f"\n  [FAIL] Autonomous sequence crashed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


# ═══════════════════════════════════════════
#  RUN TESTS
# ═══════════════════════════════════════════

def run_all():
    """Run every test and print a summary."""
    tests = [
        ("config", test_config),
        ("servo", test_servo),
        ("stepper", test_stepper),
        ("sensors", test_sensors),
        ("display", test_display),
        ("scanner", test_scanner),
        ("launcher", test_launcher),
        ("autonomous", test_autonomous),
    ]
    
    results = {}
    for name, func in tests:
        try:
            results[name] = func()
        except Exception as e:
            print(f"\n  [CRASH] {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
        print()
    
    # Summary
    print("=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        icon = "✓" if ok else "✗"
        print(f"  {icon} {status}  {name}")
    
    print(f"\n  {passed}/{total} test suites passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    # Check for --test argument to run a specific test
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        test_map = {
            "config": test_config,
            "servo": test_servo,
            "stepper": test_stepper,
            "sensors": test_sensors,
            "display": test_display,
            "scanner": test_scanner,
            "launcher": test_launcher,
            "autonomous": test_autonomous,
            "calibration": test_launcher,  # alias
        }
        
        if test_name in test_map:
            test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {', '.join(test_map.keys())}")
    else:
        run_all()
