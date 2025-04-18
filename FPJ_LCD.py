from RPLCD.i2c import CharLCD
from smbus2 import SMBus
from time import sleep

class FPJ_LCD:
    def __init__(self, address, cols=20, rows=4):
        self.address = address
        self.lcd = None
        try:
            # Check if the device at address responds
            with SMBus(1) as bus:
                bus.read_byte(address)  # will raise IOError if no device

            self.lcd = CharLCD(i2c_expander='PCF8574', address=address,
                               port=1, cols=cols, rows=rows,
                               charmap='A00', auto_linebreaks=True)
            self.clear()
            print(f"✅ LCD initialized at 0x{address:02X}")

        except Exception as e:
            print(f"❌ Error initializing LCD at 0x{address:02X}: {e}")

    def clear(self):
        if self.lcd:
            try:
                self.lcd.clear()
            except Exception as e:
                print(f"❌ Error clearing LCD at 0x{self.address:02X}: {e}")

    def display(self, overwrite=True, line1="", line2="", line3="", line4=""):
        if not self.lcd:
            print(f"⚠️ Cannot display: LCD at 0x{self.address:02X} not initialized.")
            return

        if overwrite:
            self.clear()

        lines = [line1, line2, line3, line4]
        for i, text in enumerate(lines):
            if text:
                try:
                    self.lcd.cursor_pos = (i, 0)
                    self.lcd.write_string(str(text).ljust(20)[:20])
                except Exception as e:
                    print(f"❌ Error writing to line {i+1} on LCD at 0x{self.address:02X}: {e}")

# Example usage
if __name__ == '__main__':
    lcd1 = FPJ_LCD(0x25)
    lcd2 = FPJ_LCD(0x24)

    lcd1.display(
        overwrite=True,
        line1="LCD 1 LINE 1",
        line2="LCD 1 LINE 2",
        line3="LCD 1 LINE 3",
        line4="LCD 1 LINE 4"
    )

    lcd2.display(
        overwrite=True,
        line1="LCD 2 LINE 1",
        line2="LCD 2 LINE 2",
        line3="LCD 2 LINE 3",
        line4="LCD 2 LINE 4"
    )
