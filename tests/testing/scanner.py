# stubs/scanner.py — mock full-arc tower scanner
# Simulates a sweep and returns fake tower candidates

import random
import config

_FAKE_TOWER_ANGLES  = [-60, 0, 45]     # degrees where "towers" appear
_FAKE_TOWER_DISTS   = [800, 1300, 1800] # matching distances


class Scanner:
    def __init__(self, stepper, sensor, display):
        self._stepper = stepper
        self._sensor  = sensor
        self._display = display

    def full_scan(self):
        """
        Sweep the full arc, sample sensor at each step, return tower list.
        Returns: list of dicts {angle, distance, label}
        """
        print("\n  [SCANNER] Starting full scan...")
        self._display.text("SCANNING", "0%")

        towers = []
        step_deg = 10
        half    = config.SCAN_RANGE_DEG // 2

        for deg in range(-half, half + 1, step_deg):
            self._stepper.goto_angle(deg)
            dist = self._sensor.read()

            # Simulate a tower detection at our fake angles
            for fa, fd in zip(_FAKE_TOWER_ANGLES, _FAKE_TOWER_DISTS):
                if abs(deg - fa) <= step_deg // 2:
                    dist = fd + random.randint(-15, 15)

            lo, hi = config.VALID_RANGE_MM
            if lo <= dist <= hi:
                # Simple peak detection: record if notably closer than neighbours
                if not towers or abs(deg - towers[-1]['angle']) > step_deg * 2:
                    label = _classify(dist)
                    if label:
                        towers.append({'angle': deg, 'distance': dist, 'label': label})

            pct = int((deg + half) / config.SCAN_RANGE_DEG * 100)
            self._display.text("SCANNING", f"{pct}%")

        self._stepper.home()
        print(f"  [SCANNER] Scan complete — {len(towers)} towers found")
        return towers

    def print_towers(self, towers):
        if not towers:
            print("  [SCANNER] No towers detected")
            return
        print(f"\n  {'#':>2}  {'Angle':>6}  {'Distance':>10}  {'Label':>6}")
        for i, t in enumerate(towers):
            print(f"  {i+1:>2}  {t['angle']:>5}°  {t['distance']:>8}mm  {t['label']:>6}")


def _classify(dist_mm):
    if   dist_mm < 1050:  return "close"
    elif dist_mm < 1550:  return "mid"
    elif dist_mm <= 2000: return "far"
    return None
