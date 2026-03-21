# sensors.py — VL53L0X Time-of-Flight distance sensor
# =====================================================
# Reads distance with median filtering for reliability.
#
# Test independently:
#   from sensors import DistanceSensor
#   tof = DistanceSensor()
#   print(tof.read())          # single filtered reading
#   print(tof.read_raw())      # single unfiltered reading
#   tof.continuous_print()     # live distance readout (Ctrl+C to stop)

import time
import config

# Import the VL53L0X library
# Download from: https://github.com/kevinmcaleer/vl53lx0
# Upload vl53l0x.py to your Pico
try:
    from vl53l0x import VL53L0X
    TOF_AVAILABLE = True
except ImportError:
    print("[sensors] WARNING: vl53l0x library not found!")
    print("  Download from: https://github.com/kevinmcaleer/vl53lx0")
    print("  Upload vl53l0x.py to the Pico.")
    TOF_AVAILABLE = False


class DistanceSensor:
    """
    Wrapper around VL53L0X with median filtering.
    
    Why median instead of mean?
    If 4 readings say 800mm and 1 says 3000mm (sensor glitch),
    the mean is 1240mm (wrong). The median is 800mm (correct).
    Median rejects outliers naturally.
    """
    
    def __init__(self):
        if TOF_AVAILABLE:
            try:
                self.sensor = VL53L0X(config.i2c)
                self._working = True
                print("[sensors] VL53L0X initialised OK")
            except Exception as e:
                print(f"[sensors] VL53L0X init failed: {e}")
                print("  Check wiring: SDA→GP0, SCL→GP1, VCC→3.3V, GND→GND")
                self._working = False
        else:
            self._working = False
    
    def read_raw(self):
        """
        Single raw reading from the sensor (no filtering).
        Returns distance in mm, or -1 on error.
        """
        if not self._working:
            return -1
        try:
            d = self.sensor.read()
            if config.TOF_MIN_VALID < d < config.TOF_MAX_VALID:
                return d
            return -1
        except Exception:
            return -1
    
    def read(self, num_samples=None):
        """
        Filtered distance reading using median of multiple samples.
        
        Args:
            num_samples: override config.TOF_SAMPLES if needed
            
        Returns:
            Distance in mm, or 9999 if sensor fails.
        """
        if not self._working:
            return 9999
        
        n = num_samples or config.TOF_SAMPLES
        readings = []
        
        for _ in range(n):
            d = self.read_raw()
            if d > 0:
                readings.append(d)
            time.sleep_ms(config.TOF_SAMPLE_DELAY_MS)
        
        if not readings:
            return 9999
        
        # Median filter
        readings.sort()
        return readings[len(readings) // 2]
    
    def read_fast(self):
        """
        Quick single-sample read (for scanning where speed matters).
        Still validates range, but no multi-sample filtering.
        """
        d = self.read_raw()
        return d if d > 0 else 9999
    
    def is_working(self):
        """Check if sensor is responding."""
        return self._working and self.read_raw() > 0
    
    def continuous_print(self, interval_ms=200):
        """
        Print live distance readings. Useful for testing sensor
        placement and verifying it can see the towers.
        Press Ctrl+C to stop.
        """
        print("[sensors] Live distance readout (Ctrl+C to stop)")
        print("-" * 40)
        try:
            while True:
                d = self.read()
                bar = "#" * min(d // 50, 40)  # visual bar
                print(f"  {d:5d} mm  {bar}")
                time.sleep_ms(interval_ms)
        except KeyboardInterrupt:
            print("\n[sensors] Stopped")
    
    def scan_i2c(self):
        """
        Scan the I2C bus and report what's connected.
        Useful for debugging wiring issues.
        
        Expected devices:
          0x29 = VL53L0X
          0x3C = SSD1306 OLED
        """
        devices = config.i2c.scan()
        print(f"[sensors] I2C scan found {len(devices)} device(s):")
        known = {0x29: "VL53L0X (ToF)", 0x3C: "SSD1306 (OLED)"}
        for addr in devices:
            name = known.get(addr, "unknown")
            print(f"  0x{addr:02X} = {name}")
        if 0x29 not in devices:
            print("  WARNING: VL53L0X not found! Check wiring.")
        if 0x3C not in devices:
            print("  WARNING: SSD1306 not found! Check wiring.")
        return devices
