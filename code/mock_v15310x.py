# mock_vl53l0x.py — Fake ToF sensor for local testing
# ====================================================
# Returns simulated distance readings. You can configure
# what distances it returns to test different scenarios.

import random


class VL53L0X:
    """
    Fake VL53L0X sensor.
    
    By default returns random distances simulating an open room
    with a few towers. You can override this by setting
    VL53L0X.fake_distances to a list of values that will be
    returned in sequence (cycling).
    """
    
    # Set this to a list to control exactly what read() returns.
    # Example: VL53L0X.fake_distances = [800, 800, 2500, 2500, 1300]
    # If None, returns random values simulating towers in a room.
    fake_distances = None
    _read_index = 0
    
    # Simulated tower positions (used when fake_distances is None)
    # Format: (start_reading_index, end_reading_index, distance_mm)
    # These simulate 6 towers at different angles in a 200-reading scan
    _towers = [
        (15, 20, 800),     # close tower at ~27°
        (50, 55, 1800),    # far tower at ~90°
        (85, 90, 1300),    # middle tower at ~153°
        (115, 120, 800),   # close tower at ~207°
        (145, 150, 1300),  # middle tower at ~261°
        (175, 180, 1800),  # far tower at ~315°
    ]
    _scan_index = 0
    
    def __init__(self, i2c=None):
        self.i2c = i2c
        VL53L0X._scan_index = 0
        print("    [MOCK] VL53L0X sensor created (fake readings)")
    
    def read(self):
        """
        Return a fake distance reading in mm.
        """
        # If user provided explicit fake values, cycle through them
        if VL53L0X.fake_distances is not None:
            idx = VL53L0X._read_index % len(VL53L0X.fake_distances)
            VL53L0X._read_index += 1
            val = VL53L0X.fake_distances[idx]
            return val + random.randint(-10, 10)  # add slight noise
        
        # Otherwise, simulate a room with towers
        idx = VL53L0X._scan_index % 200
        VL53L0X._scan_index += 1
        
        # Check if current reading index falls within a tower
        for start, end, dist in VL53L0X._towers:
            if start <= idx <= end:
                return dist + random.randint(-15, 15)
        
        # Background — far wall
        return 2500 + random.randint(-50, 50)
