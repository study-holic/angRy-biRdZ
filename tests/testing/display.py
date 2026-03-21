# stubs/display.py — mock OLED display
# Prints to terminal instead of rendering on hardware

class Display:
    def __init__(self):
        print("  [DISPLAY] OLED initialised (mock)")
        self._lines = []

    def text(self, *lines):
        """Render up to 4 lines on the OLED (mocked as terminal output)."""
        non_empty = [l for l in lines if l]
        self._lines = non_empty
        width = 28
        border = "+" + "-" * width + "+"
        print(f"\n  {border}")
        for line in non_empty[:4]:
            padded = str(line)[:width].center(width)
            print(f"  |{padded}|")
        print(f"  {border}\n")

    def clear(self):
        self._lines = []
        print("  [DISPLAY] Screen cleared")

    def show(self):
        pass  # no-op — hardware calls show() to flush buffer
