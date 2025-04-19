from RPLCD.i2c import CharLCD
from smbus2 import SMBus
from time import sleep

class LCD_CONTROLLER:
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
                    centered = str(text).strip().center(20)[:20]  # Center-align and trim if needed
                    self.lcd.cursor_pos = (i, 0)
                    self.lcd.write_string(centered)
                except Exception as e:
                    print(f"❌ Error writing to line {i+1} on LCD at 0x{self.address:02X}: {e}")

                
class FPJ_LCD:
    def __init__(self):
        self.lcd1 = LCD_CONTROLLER(0x25)
        self.lcd2 = LCD_CONTROLLER(0x24)

    def welcome(self) -> None:
        self.lcd1.display(overwrite=True, 
                          line1="WELCOME TO FPJ MAKER",
                          line2="FABRICATED BY:",
                          line3="JAY FOUR JAVIER",
                          line4="JODIE JAVIER")
        self.lcd2.display(overwrite=True, 
                          line1="FABRICATED FOR:",
                          line2="JONASH MALLARI",
                          line3="JAYBERT MAGNAYE",
                          line4="ARVIE MANDAP")


# Example usage
if __name__ == '__main__':
    print("FPJ_LCD.py TEST")
    lcd = FPJ_LCD()
    lcd.welcome()


