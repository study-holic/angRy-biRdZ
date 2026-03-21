# mock_ssd1306.py — Fake OLED display for local testing
# ======================================================
# Instead of drawing pixels, prints text to the terminal.


class SSD1306_I2C:
    """Fake OLED that prints to stdout instead of a screen."""
    
    def __init__(self, width, height, i2c):
        self.width = width
        self.height = height
        self._buffer = {}
        print(f"    [MOCK] SSD1306 OLED created ({width}x{height})")
    
    def fill(self, colour):
        self._buffer = {}
    
    def text(self, string, x, y, colour=1):
        self._buffer[(x, y)] = string
    
    def show(self):
        if self._buffer:
            lines = sorted(self._buffer.items(), key=lambda item: item[0][1])
            for (x, y), text in lines:
                print(f"    [OLED] {text}")
    
    def pixel(self, x, y, colour):
        pass
    
    def hline(self, x, y, w, colour):
        pass
    
    def vline(self, x, y, h, colour):
        pass
    
    def rect(self, x, y, w, h, colour):
        pass
    
    def fill_rect(self, x, y, w, h, colour):
        pass
