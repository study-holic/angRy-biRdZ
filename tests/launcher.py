# stubs/launcher.py — mock MG996R arm servo + MG90S latch servo
# Simulates state and timing without moving any hardware

import time
import config


class _MockServo:
    """Generic servo stub used for both arm and latch."""
    def __init__(self, name):
        self._name   = name
        self._angle  = 0
        self._speed  = 0

    def set_angle(self, angle):
        self._angle = angle
        print(f"  [SERVO:{self._name}] → {angle}°")

    def spin(self, speed=50, duration_ms=500):
        self._speed = speed
        print(f"  [SERVO:{self._name}] Spinning speed={speed} for {duration_ms}ms...", end="", flush=True)
        time.sleep(duration_ms / 1000)
        self._speed = 0
        print(" done")

    def stop(self):
        self._speed = 0
        print(f"  [SERVO:{self._name}] Stopped")

    def off(self):
        """Remove PWM signal — servo goes limp."""
        self._speed = 0
        print(f"  [SERVO:{self._name}] PWM off (limp)")


class Launcher:
    def __init__(self):
        print("  [LAUNCHER] Initialising (mock)")
        self.arm   = _MockServo("ARM")
        self.latch = _MockServo("LATCH")
        self.is_cocked = False
        self._cock_ms  = 0

    # ── lifecycle ───────────────────────────────────────────

    def initialise(self):
        self.latch_close()
        self.arm.stop()
        print("  [LAUNCHER] Ready")

    def emergency_stop(self):
        self.arm.stop()
        self.latch.set_angle(config.LATCH_OPEN_ANGLE)
        self.is_cocked = False
        print("  [LAUNCHER] *** EMERGENCY STOP ***")

    # ── latch ───────────────────────────────────────────────

    def latch_open(self):
        self.latch.set_angle(config.LATCH_OPEN_ANGLE)
        self.is_cocked = False

    def latch_close(self):
        self.latch.set_angle(config.LATCH_CLOSE_ANGLE)

    # ── arm ─────────────────────────────────────────────────

    def cock(self, duration_ms=500):
        """Pull the arm back (spin MG996R against latch)."""
        print(f"  [LAUNCHER] Cocking for {duration_ms}ms...")
        self.arm.spin(speed=80, duration_ms=duration_ms)
        self.arm.stop()
        self.is_cocked = True
        self._cock_ms  = duration_ms
        print(f"  [LAUNCHER] Armed! cock_ms={duration_ms}")

    def manual_fire(self):
        """Release the latch to fire."""
        if not self.is_cocked:
            print("  [LAUNCHER] Warning: arm not cocked — results will be weak")
        print("  [LAUNCHER] *** FIRE ***")
        self.latch_open()
        time.sleep(0.3)
        self.latch_close()
        self.is_cocked = False

    def reload(self):
        """Trigger magazine feed servo."""
        print("  [LAUNCHER] Reloading from magazine...")
        time.sleep(0.4)
        print("  [LAUNCHER] Ball loaded")
