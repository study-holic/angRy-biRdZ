# config.py — All pin assignments, constants, and calibration values
from machine import Pin, PWM, I2C


#  PIN ASSIGNMENTS
# Physical pin numbers noted in comments for wiring reference

I2C_SDA = 0          # GP0 = physical pin 1
I2C_SCL = 1          # GP1 = physical pin 2

LATCH_PIN = 2        # GP2 = physical pin 4  (MG90S — positional servo)
ARM_PIN = 3          # GP3 = physical pin 5  (MG996R — 360° continuous servo)
MAGAZINE_PIN = 7     # GP7 = physical pin 10 (ball feeder servo)

STEP_PIN = 4         # GP4 = physical pin 6  (DRV8825 STEP)
DIR_PIN = 5          # GP5 = physical pin 7  (DRV8825 DIR)
ENABLE_PIN = 6       # GP6 = physical pin 9  (DRV8825 ENABLE, active LOW)

BUZZER_PIN = 8       # GP8 = physical pin 11 (optional piezo)

#  I2C BUS (shared by OLED + ToF)
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

#  STEPPER — NEMA 17 via DRV8825
STEPPER_STEPS_PER_REV = 200      # native steps (1.8° per step)
MICROSTEP_MODE = 16              # DRV8825 microstepping (1, 2, 4, 8, 16, or 32)

# Derived: total microsteps for one full turret revolution
STEPS_PER_TURRET_REV = STEPPER_STEPS_PER_REV * MICROSTEP_MODE  # 200 × 16 = 3200

SCAN_STEP_SIZE = 16              # microsteps between ToF readings during scan
STEP_DELAY_US = 600              # microseconds per pulse (lower = faster)

# Acceleration ramp
STEP_DELAY_MAX_US = 2000         # starting speed (slow)
STEP_DELAY_MIN_US = 400          # cruising speed (fast)
ACCEL_STEPS = 80                 # steps to ramp up/down

#  LATCH SERVO (MG90S — positional)
LATCH_CLOSED = 90                # degrees — holds arm in cocked position
LATCH_OPEN = 20                  # degrees — releases arm to fire

#  ARM SERVO (MG996R — 360° continuous)
# 360° servos don't go to angles — they spin at a speed.
# Pulse width controls speed+direction:
#   ~1.5ms = stop
#   <1.5ms = spin one way (pulling arm back)
#   >1.5ms = spin other way (releasing arm)
ARM_SPEED = 70                   # speed for cocking (0-100, higher = faster pull)
ARM_RELEASE_SPEED = -50          # speed for returning to rest (negative = reverse)

# Timing-based arm positions (milliseconds of spin at ARM_SPEED)
ARM_COCK_DURATION_MIN = 200      # ms — minimum pull-back (close targets)
ARM_COCK_DURATION_MAX = 1200     # ms — maximum pull-back (far targets)
ARM_RELEASE_DURATION = 800       # ms — time to return arm to rest

#  MAGAZINE SERVO (positional)
MAGAZINE_CLOSED = 90             # blocks next ball
MAGAZINE_OPEN = 45               # drops one ball into cup
MAGAZINE_DROP_TIME_MS = 500      # how long gate stays open

#  ToF SENSOR (VL53L0X)
TOF_SAMPLES = 5                  # readings per measurement
TOF_SAMPLE_DELAY_MS = 15         # ms between samples
TOF_MIN_VALID = 30               # mm — below this is noise
TOF_MAX_VALID = 8000             # mm — above this is out of range

#  TOWER DETECTION
BACKGROUND_THRESHOLD = 2200      # mm — readings above this = no target
CLOSE_MAX = 1050                 # mm — tower at ~800mm
MIDDLE_MAX = 1550                # mm — tower at ~1300mm
                                  # above MIDDLE_MAX = far tower at ~1800mm

TOWER_MIN_WIDTH = 2              # minimum scan samples to count as a tower
TOWER_MAX_WIDTH = 30             # maximum samples — wider = probably a wall

#  CALIBRATION TABLE
# Format: (arm_cock_duration_ms, resulting_launch_distance_mm)
# *** FILL THIS IN FROM TEST SHOTS AFTER***
# Use calibration mode: run main.py → option 2
# Fire test shots at different durations, measure where they land.

CALIBRATION_TABLE = [
    (200,   500),
    (400,   750),
    (600,  1000),
    (800,  1300),
    (1000, 1600),
    (1200, 1900),
]

#  SCORING / GAME RULES
MAX_SHOTS = 5

# Score multipliers by distance category
SCORE_MULTIPLIER = {
    'far': 6,
    'middle': 4,
    'close': 2,
}
