# main.py — Entry point for the Catapult
# It imports all modules and orchestrates the autonomous sequence.

import time
import config
from stepper import Stepper
from sensors import DistanceSensor
from display import Display
from scanner import Scanner
from launcher import Launcher

#  AUTONOMOUS MODE — the 50-point play

def run_autonomous():
    """
    Full autonomous sequence. Zero human input after pressing start.
    
    Steps:
    1. Initialise all hardware
    2. Scan 360° to find tower positions
    3. Sort towers by score priority (far first = highest multiplier)
    4. For each tower (up to 5 shots):
       a. Aim turret at tower
       b. Re-verify distance
       c. Compute launch power from calibration table
       d. Reload from magazine
       e. Fire
    5. Return to home position
    """
    # ── INIT ──
    screen = Display()
    tof = DistanceSensor()
    turret = Stepper()
    gun = Launcher()
    scan = Scanner(turret, tof, screen)
    
    screen.splash()
    time.sleep(1)
    
    # Safety check: are sensors working?
    if not tof.is_working():
        screen.text("ERROR!", "ToF sensor", "not found!", "Check wiring")
        print("[main] ABORT: ToF sensor not responding")
        return
    
    gun.initialise()
    turret.enable()
    
    # ── PHASE 1: SCAN ──
    print("\n[main] Phase 1: Scanning for towers...")
    towers = scan.full_scan()
    scan.print_towers(towers)
    
    if not towers:
        screen.text("NO TARGETS", "FOUND!", "Check sensor", "placement")
        print("[main] ABORT: No towers detected")
        turret.disable()
        return
    
    # ── PHASE 2: PRIORITISE ──
    print("\n[main] Phase 2: Prioritising targets...")
    towers = scan.prioritise_towers(towers)
    
    # Show radar view
    screen.radar(towers, turret.steps_per_rev())
    time.sleep(2)
    
    print("[main] Attack order:")
    for i, t in enumerate(towers):
        mult = config.SCORE_MULTIPLIER.get(t['category'], '?')
        print(f"  #{i+1}: {t['category']} at {t['distance_mm']}mm "
              f"(×{mult} multiplier)")
    
    # ── PHASE 3: ENGAGE TARGETS ──
    print(f"\n[main] Phase 3: Engaging targets (max {config.MAX_SHOTS} shots)...")
    
    for i, tower in enumerate(towers):
        if gun.shots_fired >= config.MAX_SHOTS:
            print(f"[main] Shot limit reached ({config.MAX_SHOTS})")
            break
        
        shot_num = gun.shots_fired + 1
        print(f"\n{'─'*40}")
        print(f"[main] Shot {shot_num}/{config.MAX_SHOTS}")
        print(f"[main] Target: {tower['category']} tower at "
              f"{tower['angle_deg']}° / {tower['distance_mm']}mm")
        
        # Show targeting info on OLED
        screen.shot_info(shot_num, config.MAX_SHOTS, 
                         tower['category'], tower['distance_mm'], 
                         status="AIMING")
        
        # Aim turret
        print(f"[main] Aiming turret to step {tower['step']}...")
        turret.goto(tower['step'])
        time.sleep_ms(500)
        
        # Re-verify distance after aiming (more accurate when pointed at target)
        actual_dist = scan.quick_verify(tower)
        print(f"[main] Verified distance: {actual_dist}mm "
              f"(was {tower['distance_mm']}mm)")
        
        screen.shot_info(shot_num, config.MAX_SHOTS,
                         tower['category'], actual_dist,
                         status="FIRING")
        
        # Fire at the verified distance
        cock_dur = gun.fire_at_distance(actual_dist)
        
        screen.shot_info(shot_num, config.MAX_SHOTS,
                         tower['category'], actual_dist,
                         status="DONE")
        
        print(f"[main] Shot {shot_num} complete "
              f"(cock={cock_dur}ms, dist={actual_dist}mm)")
        time.sleep(1)
    
    # ── PHASE 4: FINISH ──
    print(f"\n{'─'*40}")
    print(f"[main] Sequence complete! Fired {gun.shots_fired} shots.")
    
    turret.home()
    turret.disable()
    
    screen.text("COMPLETE!", f"{gun.shots_fired} shots", "fired", "")
    print("[main] Done.")

#  SENSOR TEST MODE
def run_sensor_test():
    """
    Minimal test: just read the ToF sensor and display on OLED.
    Use this first to verify your wiring is correct.
    """
    screen = Display()
    tof = DistanceSensor()
    
    # First, scan I2C to see what's connected
    tof.scan_i2c()
    
    if not tof.is_working():
        screen.text("ToF SENSOR", "NOT FOUND!", "", "Check wiring")
        return
    
    screen.text("SENSOR TEST", "Point at target", "", "Ctrl+C to stop")
    time.sleep(1)
    
    print("\n[test] Live sensor readings (Ctrl+C to stop)")
    try:
        while True:
            dist = tof.read()
            screen.text("SENSOR TEST", f"Dist: {dist}mm", "", "")
            time.sleep_ms(200)
    except KeyboardInterrupt:
        print("\n[test] Stopped")


#  STEPPER TEST MODE
def run_stepper_test():
    """
    Test turret rotation: quarter turns in each direction.
    Use this to verify stepper wiring and DRV8825 current limit.
    """
    screen = Display()
    turret = Stepper()
    
    screen.text("STEPPER TEST", "Starting...")
    turret.enable()
    time.sleep(1)
    
    steps = turret.steps_per_rev()
    quarter = steps // 4
    
    print(f"[test] Steps per revolution: {steps}")
    print(f"[test] Quarter turn: {quarter} steps")
    
    for direction, label in [(1, "CW"), (-1, "CCW")]:
        for i in range(4):
            angle = turret.get_angle()
            screen.text("STEPPER TEST", f"{label} quarter {i+1}", f"Angle: {angle:.0f}")
            print(f"[test] {label} quarter turn {i+1}/4 (angle: {angle:.0f}°)")
            turret.move(quarter * direction)
            time.sleep(1)
    
    turret.home()
    turret.disable()
    screen.text("STEPPER TEST", "Complete!")
    print("[test] Stepper test done")


# ═══════════════════════════════════════════
#  MODE SELECTION
# ═══════════════════════════════════════════

def main():
    """Startup menu — select operating mode."""
    print("\n" + "=" * 50)
    print("  HACK-A-BOT CATAPULT")
    print("=" * 50)
    print()
    print("  1 — AUTONOMOUS (competition mode)")
    print("  2 — CALIBRATION (build firing table)")
    print("  3 — SENSOR TEST (verify ToF + OLED)")
    print("  4 — STEPPER TEST (verify turret)")
    print()
    
    try:
        choice = input("Select mode [1-4]: ").strip()
    except:
        choice = "3"  # default to sensor test if input fails
    
    if choice == "1":
        run_autonomous()
    elif choice == "2":
        from calibrate import run as run_cal
        run_cal()
    elif choice == "3":
        run_sensor_test()
    elif choice == "4":
        run_stepper_test()
    else:
        print(f"Unknown option: {choice}")
        print("Defaulting to sensor test...")
        run_sensor_test()


# ── Auto-run on boot ──
if __name__ == "__main__":
    main()
