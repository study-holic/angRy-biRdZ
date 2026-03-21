# stubs/sensors.py — mock VL53L0X distance sensor
# Returns realistic fake distances with slight noise

import random
import time
import config

_FAKE_TOWERS = [800, 1300, 1800]   # simulated tower distances

class DistanceSensor:
    def __init__(self):
        print("  [SENSOR] VL53L0X initialised (mock)")
        self._base_distance = random.choice(_FAKE_TOWERS)

    def scan_i2c(self):
        """Simulate an I2C bus scan."""
        print("  [I2C] Scanning bus...")
        print(f"  [I2C] Found device at 0x{config.TOF_ADDR:02X} (VL53L0X)")
        print(f"  [I2C] Found device at 0x{config.OLED_ADDR:02X} (SSD1306 OLED)")
        print("  [I2C] Scan complete — 2 devices found")

    def read(self):
        """Return a distance reading with ±20mm noise."""
        noise = random.randint(-20, 20)
        raw = self._base_distance + noise
        # clamp to valid range
        lo, hi = config.VALID_RANGE_MM
        return max(lo, min(hi, raw))

    def read_filtered(self, samples=5):
        """Average N readings to reduce noise."""
        readings = [self.read() for _ in range(samples)]
        return sum(readings) // len(readings)

    def set_fake_distance(self, mm):
        """Test helper: point the fake sensor at a specific distance."""
        self._base_distance = mm
        print(f"  [SENSOR] Fake target set to {mm}mm")

    def continuous_print(self):
        """Stream readings until Ctrl+C."""
        print("  [SENSOR] Continuous mode — press Ctrl+C to stop")
        try:
            while True:
                dist = self.read()
                print(f"  {dist:>6} mm")
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n  [SENSOR] Stopped")
