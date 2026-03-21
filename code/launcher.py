# launcher.py — Catapult firing and calibration
# ===============================================
# Controls the arm, latch, and magazine to fire projectiles.
# Handles calibration table lookup for different distances.
#
# Test independently:
#   from launcher import Launcher
#   gun = Launcher()
#   gun.latch_close()
#   gun.cock(duration_ms=500)
#   gun.fire()
#   gun.reload()

import time
import config
from servo import Positional, Continuous


class Launcher:
    """
    Controls the catapult firing mechanism.
    
    Physical setup:
    - MG996R (360° continuous) pulls the arm back against rubber bands
    - MG90S (positional) acts as a latch holding the cocked arm
    - Releasing the latch fires the projectile
    - A second positional servo opens the magazine gate to reload
    
    Launch power is controlled by how long the MG996R spins
    (how far back the arm is pulled). This is mapped to
    target distance via the calibration table.
    """
    
    def __init__(self):
        # Latch servo (positional — holds/releases arm)
        self.latch = Positional(config.LATCH_PIN)
        
        # Arm servo (360° continuous — cocks the arm)
        self.arm = Continuous(config.ARM_PIN)
        
        # Magazine servo (positional — drops balls)
        self.magazine = Positional(config.MAGAZINE_PIN)
        
        # Optional buzzer
        self._init_buzzer()
        
        # State tracking
        self.is_cocked = False
        self.shots_fired = 0
    
    def _init_buzzer(self):
        """Try to set up the piezo buzzer (optional component)."""
        try:
            from machine import PWM, Pin
            self.buzzer = PWM(Pin(config.BUZZER_PIN))
            self.buzzer.duty_u16(0)
            self.has_buzzer = True
        except:
            self.has_buzzer = False
    
    def initialise(self):
        """
        Set all servos to safe starting positions.
        Call this once at startup before doing anything else.
        """
        print("[launcher] Initialising servos...")
        self.latch.set_angle(config.LATCH_CLOSED)
        self.arm.stop()
        self.magazine.set_angle(config.MAGAZINE_CLOSED)
        time.sleep_ms(500)
        self.is_cocked = False
        print("[launcher] Ready")
    
    # ── LATCH CONTROL ──
    
    def latch_close(self):
        """Close the latch (holds the arm in place)."""
        self.latch.set_angle(config.LATCH_CLOSED)
        time.sleep_ms(200)
    
    def latch_open(self):
        """Open the latch (releases the arm — this fires!)."""
        self.latch.set_angle(config.LATCH_OPEN)
        time.sleep_ms(100)
    
    # ── ARM CONTROL ──
    
    def cock(self, duration_ms):
        """
        Pull the arm back by spinning the MG996R for a set duration.
        Longer duration = further pull-back = more energy = longer shot.
        
        The latch MUST be closed before cocking, or the arm
        will just spring back immediately.
        
        Args:
            duration_ms: how long to spin the arm motor
        """
        if not self.is_cocked:
            self.latch_close()
        
        print(f"[launcher] Cocking arm for {duration_ms}ms")
        self.arm.spin(speed=config.ARM_SPEED, duration_ms=duration_ms)
        time.sleep_ms(300)  # settle
        self.is_cocked = True
    
    def release_arm(self):
        """Return arm to resting position (after firing)."""
        self.arm.spin(speed=config.ARM_RELEASE_SPEED, 
                      duration_ms=config.ARM_RELEASE_DURATION)
        time.sleep_ms(200)
        self.is_cocked = False
    
    # ── MAGAZINE ──
    
    def reload(self):
        """Drop one ball from the magazine into the cup."""
        print("[launcher] Reloading...")
        self.magazine.set_angle(config.MAGAZINE_OPEN)
        time.sleep_ms(config.MAGAZINE_DROP_TIME_MS)
        self.magazine.set_angle(config.MAGAZINE_CLOSED)
        time.sleep_ms(300)  # let ball settle in cup
        print("[launcher] Ball loaded")
    
    # ── FIRING SEQUENCE ──
    
    def fire_at_distance(self, distance_mm):
        """
        Complete firing sequence for a given target distance.
        
        1. Calculate required cock duration from calibration table
        2. Reload (drop ball from magazine)
        3. Cock arm
        4. Countdown
        5. Release latch → FIRE
        6. Return arm to rest
        
        Args:
            distance_mm: target distance in millimeters
            
        Returns:
            The cock_duration_ms used (useful for logging)
        """
        # Calculate arm cock duration
        cock_duration = self.compute_cock_duration(distance_mm)
        print(f"[launcher] Target: {distance_mm}mm → cock: {cock_duration}ms")
        
        # Reload
        self.reload()
        
        # Cock the arm
        self.latch_close()
        self.cock(cock_duration)
        time.sleep_ms(500)  # stabilise before firing
        
        # Countdown beeps
        self._countdown()
        
        # FIRE!
        print("[launcher] *** FIRE ***")
        self.latch_open()
        time.sleep_ms(500)  # let projectile clear
        
        # Reset
        self.latch_close()
        self.release_arm()
        
        self.shots_fired += 1
        return cock_duration
    
    def manual_fire(self):
        """
        Fire with whatever cock state the arm is currently in.
        Used in calibration mode.
        """
        if not self.is_cocked:
            print("[launcher] WARNING: Arm not cocked!")
        
        self._countdown()
        print("[launcher] *** FIRE ***")
        self.latch_open()
        time.sleep_ms(500)
        
        self.latch_close()
        self.release_arm()
        self.shots_fired += 1
    
    # ── CALIBRATION TABLE ──
    
    def compute_cock_duration(self, target_distance_mm):
        """
        Interpolate the calibration table to find the required
        arm cock duration for a given target distance.
        
        The calibration table maps:
            cock_duration_ms → launch_distance_mm
        
        We invert this: given a desired distance, find the duration.
        Linear interpolation between table entries.
        
        Args:
            target_distance_mm: desired launch distance
            
        Returns:
            Duration in ms to spin the arm motor
        """
        table = config.CALIBRATION_TABLE
        
        if not table:
            print("[launcher] WARNING: Empty calibration table!")
            return 500  # fallback
        
        # Below minimum range
        if target_distance_mm <= table[0][1]:
            return table[0][0]
        
        # Above maximum range
        if target_distance_mm >= table[-1][1]:
            return table[-1][0]
        
        # Linear interpolation between bracketing entries
        for i in range(len(table) - 1):
            dur1, dist1 = table[i]
            dur2, dist2 = table[i + 1]
            
            if dist1 <= target_distance_mm <= dist2:
                # How far between the two points (0.0 to 1.0)
                t = (target_distance_mm - dist1) / (dist2 - dist1)
                return int(dur1 + t * (dur2 - dur1))
        
        return table[-1][0]
    
    # ── HELPERS ──
    
    def _countdown(self):
        """Beep countdown before firing."""
        self._beep(800, 100)
        time.sleep_ms(200)
        self._beep(800, 100)
        time.sleep_ms(200)
        self._beep(1200, 300)
        time.sleep_ms(100)
    
    def _beep(self, freq=1000, duration_ms=100):
        """Short beep on the piezo buzzer."""
        if self.has_buzzer:
            self.buzzer.freq(freq)
            self.buzzer.duty_u16(3000)
            time.sleep_ms(duration_ms)
            self.buzzer.duty_u16(0)
    
    def emergency_stop(self):
        """Immediately stop all servos."""
        self.arm.stop()
        self.latch.set_angle(config.LATCH_CLOSED)
        self.magazine.set_angle(config.MAGAZINE_CLOSED)
        print("[launcher] EMERGENCY STOP")
