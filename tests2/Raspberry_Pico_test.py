# Confirm MicroPython version
import sys
print(sys.version)

# Confirm it's a Pico 2
import sys
print(sys.implementation)

# Test the onboard LED (GP25)
from machine import Pin
led = Pin(25, Pin.OUT)
led.on()   # should light up
led.off()


# Blink it
import time
led = Pin(25, Pin.OUT)
for i in range(10):
    led.toggle()
    time.sleep(0.3)
print ("LED ok")

# Test PWM works (needed for servos)
from machine import Pin, PWM
pwm = PWM(Pin(15))
pwm.freq(50)
print("PWM ok")

# Copy config.py across and test it loads
import config
print(config.LAUNCH_PROFILES)
