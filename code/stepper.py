# stepper.py — NEMA 17 stepper motor control via DRV8825
# ========================================================
# Handles turret rotation with acceleration ramping.
#
# Test independently:
#   from stepper import Stepper
#   turret = Stepper()
#   turret.enable()
#   turret.move(800)          # 800 steps clockwise
#   turret.move(-400)         # 400 steps counter-clockwise
#   turret.goto(0)            # return to start position
#   turret.disable()

from machine import Pin
import time
import config


class Stepper:
    """
    Controls NEMA 17 stepper via DRV8825 driver.
    
    Tracks absolute position in microsteps from the startup position.
    Supports acceleration ramping to prevent missed steps.
    """
    
    def __init__(self):
        self.step_pin = Pin(config.STEP_PIN, Pin.OUT)
        self.dir_pin = Pin(config.DIR_PIN, Pin.OUT)
        self.enable_pin = Pin(config.ENABLE_PIN, Pin.OUT)
        
        self.enable_pin.value(1)  # disabled at startup (active LOW)
        self.position = 0          # current position in microsteps
        self.enabled = False
    
    def enable(self):
        """Enable the motor driver (holds position)."""
        self.enable_pin.value(0)  # active LOW
        self.enabled = True
        time.sleep_ms(10)
    
    def disable(self):
        """Disable the motor driver (saves power, loses holding torque)."""
        self.enable_pin.value(1)
        self.enabled = False
    
    def move(self, steps, use_accel=True):
        """
        Move by a relative number of steps.
        Positive = clockwise, negative = counter-clockwise.
        
        Args:
            steps: number of microsteps (negative for CCW)
            use_accel: whether to ramp speed up/down (recommended)
        """
        if steps == 0:
            return
        
        if not self.enabled:
            self.enable()
        
        direction = 1 if steps > 0 else 0
        num_steps = abs(steps)
        
        self.dir_pin.value(direction)
        time.sleep_us(5)  # direction setup time for DRV8825
        
        if use_accel:
            self._move_with_accel(num_steps)
        else:
            self._move_constant(num_steps, config.STEP_DELAY_US)
        
        self.position += steps
    
    def goto(self, target_position):
        """
        Move to an absolute position (in microsteps from home).
        
        Args:
            target_position: target step count
        """
        diff = target_position - self.position
        if diff != 0:
            self.move(diff)
    
    def goto_angle(self, degrees):
        """
        Move turret to an absolute angle in degrees.
        
        Args:
            degrees: 0-360 target angle
        """
        steps = int(degrees * config.STEPS_PER_TURRET_REV / 360)
        self.goto(steps)
    
    def home(self):
        """Return to position 0."""
        self.goto(0)
    
    def reset_position(self):
        """Call this to define current position as home (0)."""
        self.position = 0
    
    def get_angle(self):
        """Return current turret angle in degrees."""
        return (self.position * 360) / config.STEPS_PER_TURRET_REV
    
    def _move_constant(self, num_steps, delay_us):
        """Move at constant speed."""
        for _ in range(num_steps):
            self.step_pin.value(1)
            time.sleep_us(delay_us)
            self.step_pin.value(0)
            time.sleep_us(delay_us)
    
    def _move_with_accel(self, num_steps):
        """
        Move with trapezoidal acceleration profile.
        Ramps up speed at start, cruises in the middle,
        ramps down at end. Prevents missed steps.
        """
        accel_steps = min(config.ACCEL_STEPS, num_steps // 2)
        max_d = config.STEP_DELAY_MAX_US
        min_d = config.STEP_DELAY_MIN_US
        
        for i in range(num_steps):
            # Acceleration phase
            if i < accel_steps:
                t = i / accel_steps
                delay = int(max_d - (max_d - min_d) * t)
            # Deceleration phase
            elif i >= num_steps - accel_steps:
                remaining = num_steps - i
                t = remaining / accel_steps
                delay = int(max_d - (max_d - min_d) * t)
            # Cruise phase
            else:
                delay = min_d
            
            self.step_pin.value(1)
            time.sleep_us(delay)
            self.step_pin.value(0)
            time.sleep_us(delay)
    
    def steps_per_rev(self):
        """Return total microsteps for one full turret revolution."""
        return config.STEPS_PER_TURRET_REV
