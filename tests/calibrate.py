# calibrate.py — Interactive calibration mode
# =============================================
# Use this to:
#   1. Test individual components
#   2. Fire test shots at different power levels
#   3. Build your calibration table
#   4. Verify sensor readings
#
# Run from REPL:
#   from calibrate import run
#   run()

import time
import config
from stepper import Stepper
from sensors import DistanceSensor
from display import Display
from launcher import Launcher


def run():
    """
    Interactive calibration shell.
    Type commands at the prompt to test components.
    """
    print("\n" + "=" * 50)
    print("  CALIBRATION MODE")
    print("=" * 50)
    
    # Initialise hardware
    screen = Display()
    tof = DistanceSensor()
    turret = Stepper()
    gun = Launcher()
    
    screen.text("CALIBRATION", "MODE", "", "Type 'help'")
    gun.initialise()
    turret.enable()
    
    # Log of test shots for building calibration table
    shot_log = []
    
    _print_help()
    
    while True:
        try:
            cmd = input("\ncal> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not cmd:
            continue
        
        parts = cmd.split()
        action = parts[0]
        args = parts[1:]
        
        try:
            # ── COMPONENT TESTS ──
            
            if action == "help":
                _print_help()
            
            elif action == "i2c":
                tof.scan_i2c()
            
            elif action == "dist" or action == "d":
                dist = tof.read()
                print(f"  Distance: {dist} mm")
                screen.text("DISTANCE:", f"{dist} mm")
            
            elif action == "live":
                tof.continuous_print()
            
            elif action == "latch":
                if args and args[0] == "open":
                    gun.latch_open()
                    print("  Latch: OPEN")
                elif args and args[0] == "close":
                    gun.latch_close()
                    print("  Latch: CLOSED")
                else:
                    angle = int(args[0]) if args else 90
                    gun.latch.set_angle(angle)
                    print(f"  Latch: {angle}°")
            
            elif action == "arm":
                if args and args[0] == "stop":
                    gun.arm.stop()
                    print("  Arm: STOPPED")
                elif args and args[0] == "off":
                    gun.arm.off()
                    print("  Arm: OFF (limp)")
                else:
                    speed = int(args[0]) if args else 50
                    dur = int(args[1]) if len(args) > 1 else 500
                    print(f"  Arm: speed={speed}, duration={dur}ms")
                    gun.arm.spin(speed=speed, duration_ms=dur)
                    print("  Arm: done")
            
            elif action == "mag":
                gun.reload()
            
            elif action == "step" or action == "s":
                steps = int(args[0]) if args else 100
                turret.move(steps)
                angle = turret.get_angle()
                print(f"  Stepper: moved {steps} steps → {angle:.1f}°")
            
            elif action == "goto":
                if args[0] == "home":
                    turret.home()
                    print("  Stepper: home")
                else:
                    target = int(args[0])
                    turret.goto(target)
                    print(f"  Stepper: position {turret.position}")
            
            elif action == "angle":
                deg = float(args[0]) if args else 0
                turret.goto_angle(deg)
                print(f"  Turret: {deg}° → step {turret.position}")
            
            # ── FIRING ──
            
            elif action == "cock":
                dur = int(args[0]) if args else 500
                gun.latch_close()
                gun.cock(duration_ms=dur)
                print(f"  Armed! Cock duration: {dur}ms")
                screen.text("ARMED!", f"cock: {dur}ms")
            
            elif action == "fire" or action == "f":
                gun.manual_fire()
                print("  FIRED!")
                
                # Prompt for measurement
                print("\n  Measure where the ball landed.")
                try:
                    dist_input = input("  Measured distance (mm), or skip: ").strip()
                    if dist_input and dist_input.isdigit():
                        measured = int(dist_input)
                        # Log the shot
                        if gun.is_cocked:
                            print("  (No cock duration recorded — cock first next time)")
                        shot_log.append({
                            'measured_mm': measured,
                        })
                        print(f"  Logged! ({len(shot_log)} shots total)")
                except:
                    pass
            
            elif action == "testshot":
                # Quick: cock + fire in one command
                dur = int(args[0]) if args else 500
                gun.latch_close()
                gun.cock(duration_ms=dur)
                time.sleep_ms(300)
                gun.manual_fire()
                
                print(f"\n  Shot with cock_duration={dur}ms")
                try:
                    dist_input = input("  Measured landing distance (mm): ").strip()
                    if dist_input and dist_input.isdigit():
                        measured = int(dist_input)
                        shot_log.append({
                            'cock_ms': dur,
                            'measured_mm': measured,
                        })
                        print(f"  Logged: {dur}ms → {measured}mm")
                        print(f"  ({len(shot_log)} shots total)")
                except:
                    pass
            
            # ── CALIBRATION TABLE ──
            
            elif action == "log":
                if not shot_log:
                    print("  No shots logged yet. Use 'testshot <ms>' to fire and log.")
                else:
                    print(f"\n  Shot log ({len(shot_log)} entries):")
                    print(f"  {'#':>3}  {'Cock(ms)':>8}  {'Distance(mm)':>12}")
                    for i, entry in enumerate(shot_log):
                        cock = entry.get('cock_ms', '?')
                        dist = entry.get('measured_mm', '?')
                        print(f"  {i+1:>3}  {cock:>8}  {dist:>12}")
            
            elif action == "table":
                _generate_table(shot_log)
            
            elif action == "clear":
                shot_log.clear()
                print("  Shot log cleared")
            
            # ── UTILITY ──
            
            elif action == "scan":
                from scanner import Scanner
                scan = Scanner(turret, tof, screen)
                towers = scan.full_scan()
                scan.print_towers(towers)
            
            elif action == "estop":
                gun.emergency_stop()
                turret.disable()
            
            elif action in ("quit", "q", "exit"):
                break
            
            else:
                print(f"  Unknown command: {action}")
                print("  Type 'help' for commands")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Cleanup
    gun.emergency_stop()
    turret.disable()
    screen.text("CALIBRATION", "ENDED")
    print("\n[calibrate] Done.")


def _print_help():
    print("""
  ── SENSOR ──────────────────────────────────
    i2c             Scan I2C bus for devices
    dist / d        Read ToF distance (filtered)
    live            Continuous distance readout (Ctrl+C)

  ── SERVOS ──────────────────────────────────
    latch open      Open latch (release arm)
    latch close     Close latch (hold arm)
    latch <angle>   Set latch to specific angle
    arm <spd> <ms>  Spin arm at speed for duration
    arm stop        Stop arm motor
    mag             Reload from magazine

  ── STEPPER ─────────────────────────────────
    step <N>        Move N steps (+CW, -CCW)
    goto <step>     Go to absolute step position
    goto home       Return to start
    angle <deg>     Rotate turret to degree angle

  ── FIRING ──────────────────────────────────
    cock <ms>       Pull arm back for N ms
    fire / f        Release latch (fire!)
    testshot <ms>   Cock + fire + log result

  ── CALIBRATION ─────────────────────────────
    log             Show all logged shots
    table           Generate calibration table
    clear           Clear shot log
    scan            Run full 360° tower scan

  ── OTHER ───────────────────────────────────
    estop           Emergency stop all motors
    quit / q        Exit calibration mode
    """)


def _generate_table(shot_log):
    """Generate a calibration table from logged test shots."""
    # Filter entries that have both cock_ms and measured_mm
    valid = [e for e in shot_log if 'cock_ms' in e and 'measured_mm' in e]
    
    if len(valid) < 2:
        print("  Need at least 2 valid shots (use 'testshot <ms>')")
        return
    
    # Sort by cock duration
    valid.sort(key=lambda e: e['cock_ms'])
    
    # Group by cock_ms and average the distances
    groups = {}
    for entry in valid:
        key = entry['cock_ms']
        if key not in groups:
            groups[key] = []
        groups[key].append(entry['measured_mm'])
    
    table = []
    for cock_ms in sorted(groups.keys()):
        dists = groups[cock_ms]
        avg_dist = sum(dists) // len(dists)
        table.append((cock_ms, avg_dist))
    
    print("\n  ── CALIBRATION TABLE ──")
    print(f"  {'Cock(ms)':>8}  {'Avg Dist(mm)':>12}  {'Samples':>7}")
    for cock_ms, avg_dist in table:
        n = len(groups[cock_ms])
        print(f"  {cock_ms:>8}  {avg_dist:>12}  {n:>7}")
    
    print("\n  Copy this into config.py → CALIBRATION_TABLE:")
    print("  CALIBRATION_TABLE = [")
    for cock_ms, avg_dist in table:
        print(f"      ({cock_ms:>5}, {avg_dist:>5}),")
    print("  ]")
