# display.py — SSD1306 OLED display (128×64)
# =============================================
# Shows status text, radar view, and progress bars.
#
# Test independently:
#   from display import Display
#   screen = Display()
#   screen.text("Hello", "World")
#   screen.progress("Scanning", 50)

import math
import config

# Import the SSD1306 library
# Download from: https://github.com/stlehmann/micropython-ssd1306
# Upload ssd1306.py to your Pico
try:
    import ssd1306
    OLED_AVAILABLE = True
except ImportError:
    print("[display] WARNING: ssd1306 library not found!")
    print("  Download from: https://github.com/stlehmann/micropython-ssd1306")
    OLED_AVAILABLE = False


class Display:
    """
    OLED display wrapper. All methods are safe to call even
    if the OLED is not connected — they just print to serial instead.
    This means you can test everything over USB without an OLED.
    """
    
    def __init__(self):
        if OLED_AVAILABLE:
            try:
                self.oled = ssd1306.SSD1306_I2C(128, 64, config.i2c)
                self._working = True
                print("[display] OLED initialised OK")
            except Exception as e:
                print(f"[display] OLED init failed: {e}")
                self._working = False
                self.oled = None
        else:
            self._working = False
            self.oled = None
    
    def text(self, line1="", line2="", line3="", line4=""):
        """
        Display up to 4 lines of text.
        Each line is max ~16 characters at default font.
        Also prints to serial for debugging without OLED.
        """
        lines = [str(line1), str(line2), str(line3), str(line4)]
        
        # Always print to serial (useful when debugging via USB)
        for line in lines:
            if line:
                print(f"  [OLED] {line}")
        
        if not self._working:
            return
        
        self.oled.fill(0)
        for i, line in enumerate(lines):
            if line:
                self.oled.text(line[:16], 0, i * 16)
        self.oled.show()
    
    def progress(self, label, percent):
        """
        Show a label with a progress bar underneath.
        
        Args:
            label: text to show above the bar
            percent: 0-100
        """
        percent = max(0, min(100, percent))
        
        print(f"  [OLED] {label}: {percent}%")
        
        if not self._working:
            return
        
        self.oled.fill(0)
        self.oled.text(label[:16], 0, 8)
        
        # Progress bar
        bar_y = 32
        bar_w = 120
        bar_h = 12
        self.oled.rect(4, bar_y, bar_w, bar_h, 1)       # outline
        fill_w = int((bar_w - 4) * percent / 100)
        self.oled.fill_rect(6, bar_y + 2, fill_w, bar_h - 4, 1)  # fill
        
        # Percentage text
        self.oled.text(f"{percent}%", 48, 52)
        self.oled.show()
    
    def radar(self, towers, steps_per_rev, current_target_idx=-1):
        """
        Draw a radar-style view of detected towers.
        Center dot = catapult. Dots around = towers.
        Current target is highlighted with a larger marker.
        
        Args:
            towers: list of tower dicts with 'step', 'category'
            steps_per_rev: total steps in one full rotation
            current_target_idx: index of tower being targeted (-1 = none)
        """
        if not self._working:
            # Print text version to serial
            for i, t in enumerate(towers):
                marker = " >>>" if i == current_target_idx else ""
                print(f"  [RADAR] {t['category']:6s} {t['distance_mm']:5d}mm{marker}")
            return
        
        self.oled.fill(0)
        cx, cy = 64, 32  # center of display
        radius = 28
        
        # Draw circle outline (every 10°)
        for angle_deg in range(0, 360, 10):
            a = math.radians(angle_deg)
            x = int(cx + radius * math.cos(a))
            y = int(cy + radius * math.sin(a))
            self.oled.pixel(x, y, 1)
        
        # Center crosshair
        self.oled.hline(cx - 2, cy, 5, 1)
        self.oled.vline(cx, cy - 2, 5, 1)
        
        # Draw tower dots
        for i, tower in enumerate(towers):
            angle_rad = 2 * math.pi * tower['step'] / steps_per_rev
            
            # Distance category determines radius on radar
            if tower['category'] == 'close':
                r = 8
            elif tower['category'] == 'middle':
                r = 16
            else:
                r = 24
            
            x = int(cx + r * math.cos(angle_rad))
            y = int(cy + r * math.sin(angle_rad))
            
            if i == current_target_idx:
                # Highlighted: larger filled square
                self.oled.fill_rect(x - 3, y - 3, 7, 7, 1)
            else:
                # Normal: small dot
                self.oled.fill_rect(x - 1, y - 1, 3, 3, 1)
        
        # Tower count in corner
        self.oled.text(f"{len(towers)}T", 100, 0)
        self.oled.show()
    
    def shot_info(self, shot_num, total_shots, category, distance_mm, status="READY"):
        """
        Show shot information before/during firing.
        
        Args:
            shot_num: current shot number
            total_shots: max shots
            category: 'close', 'middle', or 'far'
            distance_mm: measured distance
            status: 'READY', 'AIMING', 'FIRING', 'HIT?'
        """
        self.text(
            f"Shot {shot_num}/{total_shots}",
            f"{category.upper()} {distance_mm}mm",
            f"Status: {status}",
            ""
        )
    
    def splash(self, title="HACK-A-BOT", subtitle="CATAPULT v2.0"):
        """Show startup splash screen."""
        self.text(title, subtitle, "", "Initialising...")
    
    def clear(self):
        """Clear the display."""
        if self._working:
            self.oled.fill(0)
            self.oled.show()
    
    def is_working(self):
        return self._working
