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
        for _ in range(3):
            # Clear both LCDs first
            self.lcd1.clear()
            self.lcd2.clear()

            sleep(0.3)  # blank screen before flash

            # Display message on both LCDs
            self.lcd1.display(overwrite=True, 
                            line1="WELCOME TO FPJ MAKER",
                            line2="FABRICATED BY:",
                            line3="JAY FOUR JAVIER",
                            line4="JODIE JAVIER")
            sleep(0.5)
            self.lcd2.display(overwrite=True, 
                            line1="FABRICATED FOR:",
                            line2="JONASH MALLARI",
                            line3="JAYBERT MAGNAYE",
                            line4="ARVIE MANDAP")

            sleep(0.5)  # visible time

        # Final state: message stays visible
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

    def update_lcd_weight(self, material_name, weight, line):
        """
        Update the LCD with the material weight.
        Sets the cursor to specific positions as described:
        1. First cell for material name.
        2. 12th cell for ':'.
        3. 15th cell for weight.
        4. 20th cell for 'g'.
        """
        # Format the weight as a string (up to 4 digits)
        weight_str = f"{weight}"  # ensures weight has 4 digits, padding with spaces if necessary
        
        # Clear the target line first to avoid leftovers from previous data
        self.lcd2.lcd.cursor_pos = (line, 0)
        self.lcd2.lcd.write_string(" " * 20)  # Clear the entire line by writing spaces

        # Create the content for the line
        line_content = f"{material_name}"

        # Update the LCD for the specified line
        self.lcd2.lcd.cursor_pos = (line, 0)  # Move cursor to start of the line
        self.lcd2.lcd.write_string(line_content)  # Write the material name

        # Set cursor to the 12th cell and print ":"
        self.lcd2.lcd.cursor_pos = (line, 12)
        self.lcd2.lcd.write_string(":")

        # Set cursor to the 15th cell and print the weight (ensuring it's in the correct format)
        self.lcd2.lcd.cursor_pos = (line, 14)
        self.lcd2.lcd.write_string(weight_str)

        # Set cursor to the 20th cell and print "g"
        self.lcd2.lcd.cursor_pos = (line, 19)  # Adjusting to 0-index (column 19 is the 20th cell)
        self.lcd2.lcd.write_string("g")



    def display_kakawate_weight(self, weight):
        self.update_lcd_weight("Kakawate", weight, 0)

    def display_neem_weight(self, weight):
        self.update_lcd_weight("Neem", weight, 1)

    def display_molasses_weight(self, weight):
        self.update_lcd_weight("Molasses", weight, 2)

    def display_water_weight(self, weight):
        self.update_lcd_weight("Water", weight, 3)

    def display_activity(self, activity: int):
        """
        Display the current activity on self.lcd1 in the following format:
        
        LCD Layout:
        Line 1: [blank]
        Line 2: "CURRENT ACTIVITY" (centered)
        Line 3: Activity description (centered and in UPPERCASE)
        Line 4: [blank]

        Activity Map:
        0  - Waiting to load
        1  - Homing slider
        2  - Chopping Kakawate
        3  - Chopping Neem
        4  - Adding Molasses
        5  - Adding Water
        6  - Moving to Mixer
        7  - Moving Mixer Down
        8  - Mixing
        9  - Moving Mixer Up
        10 - Moving to Sealer
        11 - Sealing
        12 - Waiting to Ferment
        13 - Ready for Harvest
        """

        activity_map = {
            0: "Waiting to load",
            1: "Homing slider",
            2: "Chopping Kakawate",
            3: "Chopping Neem",
            4: "Adding Molasses",
            5: "Adding Water",
            6: "Moving to Mixer",
            7: "Moving Mixer Down",
            8: "Mixing",
            9: "Moving Mixer Up",
            10: "Moving to Sealer",
            11: "Sealing",
            12: "Waiting to Ferment",
            13: "Ready for Harvest"
        }

        message = activity_map.get(activity, "Unknown Activity").upper()

        self.lcd1.display(
            overwrite=True,
            line1="",
            line2="CURRENT ACTIVITY",
            line3=message,
            line4=""
        )










# Example usage
if __name__ == '__main__':
    print("FPJ_LCD.py TEST")
    lcd = FPJ_LCD()
    lcd.welcome()

    # Example weights for the materials
    kakawate_weight = 1020  # Example weight in grams
    neem_weight = 1010      # Example weight in grams
    water_weight = 2040     # Example weight in grams
    molasses_weight = 2020  # Example weight in grams

    # Display weights on the LCD
    lcd.display_kakawate_weight(kakawate_weight)
    lcd.display_neem_weight(neem_weight)
    lcd.display_water_weight(water_weight)
    lcd.display_molasses_weight(molasses_weight)
