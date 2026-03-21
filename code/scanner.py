# scanner.py — Tower scanning and detection
# ===========================================
# Rotates turret 360°, samples ToF at each step,
# clusters readings into tower detections.
#
# Test independently:
#   from stepper import Stepper
#   from sensors import DistanceSensor
#   from display import Display
#   from scanner import Scanner
#   turret = Stepper()
#   tof = DistanceSensor()
#   screen = Display()
#   scan = Scanner(turret, tof, screen)
#   turret.enable()
#   towers = scan.full_scan()
#   scan.print_towers(towers)

import time
import config


class Scanner:
    """
    Handles tower detection by sweeping the ToF sensor around 360°.
    
    How it works:
    1. Rotate turret one full revolution in small steps
    2. At each step, read ToF distance
    3. Most readings will be "background" (far walls, >2200mm)
    4. Towers appear as clusters of closer readings
    5. Group consecutive close readings into clusters
    6. Each cluster = one tower, centered at its midpoint
    7. Classify by distance: close (~800mm), middle (~1300mm), far (~1800mm)
    """
    
    def __init__(self, stepper, distance_sensor, display=None):
        self.stepper = stepper
        self.tof = distance_sensor
        self.display = display
    
    def full_scan(self):
        """
        Perform a complete 360° scan and return detected towers.
        
        Returns:
            List of tower dicts, each containing:
            - 'step': stepper position (microsteps from scan start)
            - 'distance_mm': average distance to tower
            - 'category': 'close', 'middle', or 'far'
            - 'angle_deg': angle in degrees from scan start
            - 'width': number of scan samples (angular size)
        """
        if self.display:
            self.display.text("SCANNING...", "360 deg sweep")
        
        # Collect raw scan data
        readings = self._sweep_360()
        
        # Detect tower clusters
        towers = self._detect_towers(readings)
        
        # Return turret to start
        self.stepper.home()
        
        if self.display:
            self.display.text(
                "SCAN COMPLETE",
                f"Found {len(towers)} towers"
            )
        
        return towers
    
    def quick_verify(self, tower):
        """
        After aiming at a tower, re-read its distance for accuracy.
        Takes extra samples since we're pointed right at it.
        
        Args:
            tower: tower dict from full_scan
            
        Returns:
            Updated distance in mm
        """
        dist = self.tof.read(num_samples=7)  # more samples = more accurate
        tower['distance_mm'] = dist
        tower['category'] = self._classify_distance(dist)
        return dist
    
    def narrow_scan(self, center_step, half_width_steps=100):
        """
        Do a narrow re-scan around a known tower position for
        more precise centering.
        
        Args:
            center_step: approximate tower position from full_scan
            half_width_steps: how far to scan on each side
            
        Returns:
            Refined step position of tower center
        """
        start = center_step - half_width_steps
        end = center_step + half_width_steps
        
        self.stepper.goto(start)
        time.sleep_ms(100)
        
        best_dist = 9999
        best_step = center_step
        
        step_size = max(1, config.SCAN_STEP_SIZE // 4)  # finer resolution
        
        pos = start
        while pos <= end:
            dist = self.tof.read_fast()
            if dist < best_dist:
                best_dist = dist
                best_step = pos
            self.stepper.move(step_size)
            pos += step_size
            time.sleep_ms(5)
        
        return best_step
    
    def _sweep_360(self):
        """
        Rotate 360° and collect distance readings.
        
        Returns:
            List of (step_position, distance_mm) tuples
        """
        readings = []
        steps_per_rev = self.stepper.steps_per_rev()
        num_samples = steps_per_rev // config.SCAN_STEP_SIZE
        
        start_pos = self.stepper.position
        
        for i in range(num_samples):
            # Read distance (fast mode for scanning speed)
            dist = self.tof.read_fast()
            step_pos = start_pos + (i * config.SCAN_STEP_SIZE)
            readings.append((step_pos, dist))
            
            # Advance turret
            self.stepper.move(config.SCAN_STEP_SIZE, use_accel=False)
            time.sleep_ms(5)  # brief settling time
            
            # Update display with progress
            if self.display and i % 20 == 0:
                pct = (i * 100) // num_samples
                self.display.progress("Scanning", pct)
        
        return readings
    
    def _detect_towers(self, readings):
        """
        Process scan readings to identify individual towers.
        
        Algorithm:
        1. Walk through readings sequentially
        2. When distance drops below BACKGROUND_THRESHOLD → start of cluster
        3. When distance rises above threshold → end of cluster
        4. If cluster has enough samples (not noise) but not too many
           (not a wall), it's a tower
        5. Take the center sample's position as the tower's aim point
        6. Handle wraparound: if scan ends mid-cluster, check if it
           merges with a cluster at the start
        """
        towers = []
        in_cluster = False
        cluster = []
        first_cluster = None  # for wraparound detection
        
        for step_pos, dist in readings:
            if dist < config.BACKGROUND_THRESHOLD:
                if not in_cluster:
                    in_cluster = True
                    cluster = []
                cluster.append((step_pos, dist))
            else:
                if in_cluster:
                    tower = self._process_cluster(cluster)
                    if tower:
                        if first_cluster is None:
                            first_cluster = len(towers)
                        towers.append(tower)
                    in_cluster = False
                    cluster = []
        
        # Handle cluster that wraps around (ends at last reading,
        # might connect to first cluster)
        if in_cluster and cluster:
            tower = self._process_cluster(cluster)
            if tower:
                # Check if this merges with the first detected tower
                if (first_cluster is not None and 
                    first_cluster == 0 and 
                    len(towers) > 0):
                    # First tower started at the very beginning of scan
                    first_step = readings[0][1]
                    if first_step < config.BACKGROUND_THRESHOLD:
                        # Merge: take average of both clusters
                        t0 = towers[0]
                        avg_dist = (t0['distance_mm'] + tower['distance_mm']) // 2
                        towers[0]['distance_mm'] = avg_dist
                        towers[0]['category'] = self._classify_distance(avg_dist)
                        # Don't add the duplicate
                    else:
                        towers.append(tower)
                else:
                    towers.append(tower)
        
        return towers
    
    def _process_cluster(self, cluster):
        """
        Convert a cluster of readings into a tower detection.
        
        Returns:
            Tower dict, or None if cluster is invalid (too small/large).
        """
        width = len(cluster)
        
        # Filter: too few samples = noise, too many = wall
        if width < config.TOWER_MIN_WIDTH:
            return None
        if width > config.TOWER_MAX_WIDTH:
            return None
        
        # Center of cluster
        center_idx = width // 2
        center_step = cluster[center_idx][0]
        
        # Average distance
        avg_dist = sum(d for _, d in cluster) // width
        
        # Angle in degrees
        steps_per_rev = self.stepper.steps_per_rev()
        angle_deg = (center_step * 360) / steps_per_rev
        
        return {
            'step': center_step,
            'distance_mm': avg_dist,
            'category': self._classify_distance(avg_dist),
            'angle_deg': round(angle_deg, 1),
            'width': width,
        }
    
    def _classify_distance(self, dist_mm):
        """Classify a distance into close/middle/far category."""
        if dist_mm <= config.CLOSE_MAX:
            return 'close'
        elif dist_mm <= config.MIDDLE_MAX:
            return 'middle'
        else:
            return 'far'
    
    def prioritise_towers(self, towers):
        """
        Sort towers by scoring priority.
        Far targets first (6× multiplier), then middle (4×), then close (2×).
        
        Args:
            towers: list of tower dicts
            
        Returns:
            New sorted list (original not modified)
        """
        priority = {'far': 0, 'middle': 1, 'close': 2}
        return sorted(towers, key=lambda t: priority.get(t['category'], 3))
    
    @staticmethod
    def print_towers(towers):
        """Pretty-print detected towers to serial."""
        if not towers:
            print("[scanner] No towers detected")
            return
        
        print(f"[scanner] Detected {len(towers)} tower(s):")
        print(f"  {'#':>2}  {'Category':>8}  {'Dist':>6}  {'Angle':>7}  {'Width':>5}")
        print(f"  {'─'*2}  {'─'*8}  {'─'*6}  {'─'*7}  {'─'*5}")
        for i, t in enumerate(towers):
            mult = config.SCORE_MULTIPLIER.get(t['category'], '?')
            print(f"  {i+1:>2}  {t['category']:>8}  {t['distance_mm']:>5}m  "
                  f"{t['angle_deg']:>6.1f}°  {t['width']:>5}  (×{mult})")
