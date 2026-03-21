# stubs/stepper.py — mock NEMA 17 stepper + DRV8825
# Tracks position internally, prints what the motor would do

import config

class Stepper:
    def __init__(self):
        print("  [STEPPER] NEMA 17 + DRV8825 initialised (mock)")
        self.position  = 0        # current step count (absolute)
        self._enabled  = False
        self._home_pos = 0

    # ── power ──────────────────────────────────────────────

    def enable(self):
        self._enabled = True
        print("  [STEPPER] Enabled (EN pin LOW)")

    def disable(self):
        self._enabled = False
        print("  [STEPPER] Disabled (EN pin HIGH — motor free)")

    # ── motion ─────────────────────────────────────────────

    def move(self, steps):
        """Move N steps. Positive = CW, negative = CCW."""
        self._check_enabled()
        direction = "CW" if steps >= 0 else "CCW"
        self.position += steps
        angle = self.get_angle()
        print(f"  [STEPPER] {direction} {abs(steps)} steps → pos={self.position} ({angle:.1f}°)")

    def goto(self, target_step):
        """Move to an absolute step position."""
        delta = target_step - self.position
        self.move(delta)

    def goto_angle(self, degrees):
        """Rotate turret to a target angle in degrees."""
        target_step = int(degrees * config.STEPS_PER_DEGREE)
        self.goto(target_step)

    def home(self):
        """Return to home position (step 0)."""
        print(f"  [STEPPER] Homing from step {self.position}")
        self.position = 0
        print(f"  [STEPPER] Home reached")

    # ── telemetry ───────────────────────────────────────────

    def get_angle(self):
        """Return current angle in degrees."""
        return self.position / config.STEPS_PER_DEGREE

    # ── internal ────────────────────────────────────────────

    def _check_enabled(self):
        if not self._enabled:
            print("  [STEPPER] Warning: motor not enabled — call turret.enable() first")
