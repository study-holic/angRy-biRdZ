# mock_machine.py — Fake hardware layer for testing on your laptop
# =================================================================
# This pretends to be the Pico's `machine` module so you can run
# all your catapult code in VS Code without a Pico connected.
#
# HOW TO USE:
#   1. Put this file in the same folder as your catapult code
#   2. Run: python test_runner.py
#      (test_runner.py patches the imports before loading your code)
#
# Every hardware call is logged to the terminal so you can see
# exactly what the code WOULD do on real hardware.

import time as _time


class Pin:
    """Fake GPIO pin."""
    OUT = 1
    IN = 0
    
    def __init__(self, pin_number, mode=None):
        self.pin = pin_number
        self.mode = mode
        self._value = 0
    
    def value(self, v=None):
        if v is not None:
            self._value = v
            return None
        return self._value
    
    def __repr__(self):
        return f"Pin(GP{self.pin})"


class PWM:
    """Fake PWM output."""
    
    def __init__(self, pin):
        self.pin = pin
        self._freq = 0
        self._duty = 0
    
    def freq(self, f=None):
        if f is not None:
            self._freq = f
        return self._freq
    
    def duty_u16(self, d=None):
        if d is not None:
            old = self._duty
            self._duty = d
            # Only log meaningful changes (not every micro-step)
            if abs(d - old) > 100:
                # Decode what this means for a servo
                if self._freq == 50:
                    angle = max(0, min(180, (d - 1638) * 180 // (8192 - 1638)))
                    print(f"    [HW] {self.pin} PWM duty={d} (~{angle}° servo)")
        return self._duty
    
    def deinit(self):
        pass


class I2C:
    """Fake I2C bus that pretends sensors are connected."""
    
    def __init__(self, bus_id, sda=None, scl=None, freq=400000):
        self.bus_id = bus_id
        self.sda = sda
        self.scl = scl
        print(f"    [HW] I2C bus {bus_id} initialised (SDA={sda}, SCL={scl})")
    
    def scan(self):
        # Pretend both the ToF and OLED are connected
        devices = [0x29, 0x3C]
        print(f"    [HW] I2C scan: found {[hex(d) for d in devices]}")
        return devices
    
    def readfrom_mem(self, addr, reg, nbytes):
        return bytes(nbytes)
    
    def writeto_mem(self, addr, reg, data):
        pass
    
    def readfrom(self, addr, nbytes):
        return bytes(nbytes)
    
    def writeto(self, addr, data):
        pass


# time module functions that MicroPython has but CPython doesn't
def sleep_ms(ms):
    """MicroPython's time.sleep_ms — just use regular sleep."""
    _time.sleep(ms / 1000)

def sleep_us(us):
    """MicroPython's time.sleep_us — just use regular sleep."""
    _time.sleep(us / 1_000_000)
