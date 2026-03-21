#!/usr/bin/env python3
"""
run_local.py — run calibrate.py on your laptop without a Pico

Usage:
    python run_local.py

What it does:
  1. Inserts stubs/ at the front of sys.path so every hardware
     import (sensors, stepper, launcher, display, config, scanner)
     resolves to the mock versions instead of the real ones.
  2. Patches time.sleep_ms onto the stdlib time module so
     MicroPython-style calls don't crash.
  3. Imports and runs calibrate.run() exactly as it would on the Pico.
"""

import sys
import os
import time

# ── 1. Point imports at stubs/ ───────────────────────────────────────────────

STUBS_DIR = os.path.join(os.path.dirname(__file__), "tests")
sys.path.insert(0, STUBS_DIR)

# ── 2. Patch MicroPython-only time calls ─────────────────────────────────────

def _sleep_ms(ms):
    time.sleep(ms / 1000)

def _ticks_ms():
    return int(time.monotonic() * 1000)

def _ticks_diff(a, b):
    return a - b

time.sleep_ms  = _sleep_ms
time.ticks_ms  = _ticks_ms
time.ticks_diff = _ticks_diff

# ── 3. Launch calibration shell ───────────────────────────────────────────────

if __name__ == "__main__":
    # calibrate.py lives one level up (alongside this script)
    sys.path.insert(0, os.path.dirname(__file__))

    print("\n  Running in LOCAL SIMULATION mode")
    print("  All hardware calls are mocked — no Pico required\n")

    from calibrate import run
    run()
