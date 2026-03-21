# stubs/config.py — mock constants (mirrors real config.py)

SERVO_PIN       = 15
LATCH_PIN       = 14
STEPPER_STEP    = 2
STEPPER_DIR     = 3
STEPPER_EN      = 4
I2C_SDA         = 4
I2C_SCL         = 5
OLED_ADDR       = 0x3C
TOF_ADDR        = 0x29

STEPS_PER_DEGREE = 5.6
SCAN_RANGE_DEG   = 180
VALID_RANGE_MM   = (600, 2000)

LATCH_OPEN_ANGLE  = 0
LATCH_CLOSE_ANGLE = 90

LAUNCH_PROFILES = {
    "close": 400,
    "mid":   560,
    "far":   720,
}

CALIBRATION_TABLE = [
    (400, 800),
    (560, 1300),
    (720, 1800),
]
