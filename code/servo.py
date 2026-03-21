# servo.py — Servo motor control
# ================================
# Handles both POSITIONAL servos (MG90S latch, magazine)
# and 360° CONTINUOUS ROTATION servos (MG996R arm).
#
# Test independently:
#   from servo import Positional, Continuous
#   latch = Positional(2)
#   latch.set_angle(90)
#   arm = Continuous(3)
#   arm.spin(speed=70, duration_ms=500)

from machine import Pin, PWM
import time


# PWM duty cycle constants (at 50Hz = 20ms period)
# Standard servo pulse: 0.5ms (0°) to 2.5ms (180°)
_MIN_DUTY = 1638     # 0.5ms / 20ms * 65535
_MAX_DUTY = 8192     # 2.5ms / 20ms * 65535
_CENTER_DUTY = (_MIN_DUTY + _MAX_DUTY) // 2  # ~1.5ms = center/stop


def _angle_to_duty(angle):
    """Convert angle (0-180) to PWM duty_u16 value."""
    angle = max(0, min(180, angle))
    return int(_MIN_DUTY + (_MAX_DUTY - _MIN_DUTY) * angle / 180)


class Positional:
    """
    Standard positional servo (e.g. MG90S, SG90).
    You tell it an angle, it goes there and holds.
    
    Usage:
        latch = Positional(pin=2)
        latch.set_angle(90)           # go to 90°
        latch.sweep(from_a=90, to_a=20, delay_ms=15)  # smooth move
    """
    
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.current_angle = 90  # assume middle at startup
    
    def set_angle(self, angle):
        """Jump to a specific angle (0-180)."""
        angle = max(0, min(180, angle))
        self.pwm.duty_u16(_angle_to_duty(angle))
        self.current_angle = angle
    
    def sweep(self, from_angle, to_angle, step=1, delay_ms=15):
        """
        Smoothly move from one angle to another.
        Prevents mechanical shock and current spikes.
        """
        if from_angle < to_angle:
            for a in range(from_angle, to_angle + 1, step):
                self.set_angle(a)
                time.sleep_ms(delay_ms)
        else:
            for a in range(from_angle, to_angle - 1, -step):
                self.set_angle(a)
                time.sleep_ms(delay_ms)
    
    def sweep_to(self, target_angle, step=1, delay_ms=15):
        """Sweep from current position to target."""
        self.sweep(self.current_angle, target_angle, step, delay_ms)
    
    def off(self):
        """Stop sending pulses (servo goes limp)."""
        self.pwm.duty_u16(0)


class Continuous:
    """
    360° continuous rotation servo (e.g. MG996R 360).
    You control SPEED and DIRECTION, not position.
    
    Pulse width meaning:
        ~1.5ms = stopped
        < 1.5ms = spin direction A
        > 1.5ms = spin direction B
    
    We control launch power by spin DURATION (how long
    the servo pulls the arm back), not angle.
    
    Usage:
        arm = Continuous(pin=3)
        arm.spin(speed=70, duration_ms=500)   # pull back for 500ms
        arm.spin(speed=-50, duration_ms=300)  # reverse for 300ms
        arm.stop()
    """
    
    def __init__(self, pin, gear_ratio=1.0):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.gear_ratio = gear_ratio
        self.stop()
    
    def spin(self, speed, duration_ms):
        """
        Spin the servo at a given speed for a given duration.
        
        Args:
            speed: -100 to +100
                   0 = stop
                   positive = pull arm back (cock)
                   negative = release arm forward
            duration_ms: how long to spin (controls how far arm moves)
                         This is adjusted by gear_ratio automatically.
        """
        speed = max(-100, min(100, speed))
        
        # Map speed (-100..+100) to duty cycle
        range_duty = (_MAX_DUTY - _MIN_DUTY) // 2
        duty = int(_CENTER_DUTY + (range_duty * speed / 100))
        
        # Adjust duration for gear ratio
        # Higher gear ratio = servo needs to spin longer for same arm movement
        adjusted_duration = int(duration_ms * self.gear_ratio)
        
        self.pwm.duty_u16(duty)
        time.sleep_ms(adjusted_duration)
        self.stop()
    
    def spin_start(self, speed):
        """Start spinning without auto-stop. Call stop() manually."""
        speed = max(-100, min(100, speed))
        range_duty = (_MAX_DUTY - _MIN_DUTY) // 2
        duty = int(_CENTER_DUTY + (range_duty * speed / 100))
        self.pwm.duty_u16(duty)
    
    def stop(self):
        """Stop the servo (send center pulse)."""
        self.pwm.duty_u16(_CENTER_DUTY)
    
    def off(self):
        """Stop sending pulses entirely (servo goes limp)."""
        self.pwm.duty_u16(0)
