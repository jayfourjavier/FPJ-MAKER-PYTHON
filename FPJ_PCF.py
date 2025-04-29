# pcf_controller.py
from adafruit_pcf8575 import PCF8575
import board

# === PCF8575 Instances ===
pcf_limitswitch = None
pcf_relay = None

# === Ready Flags ===
limit_switch_ready = False
relay_ready = False

# === I2C Setup ===
try:
    i2c = board.I2C()
except Exception as e:
    print(f"❌ Failed to initialize I2C bus: {e}")
    i2c = None

# === Initialize PCF8575 for Limit Switches ===
if i2c:
    try:
        pcf_limitswitch = PCF8575(i2c, address=0x20)
        limit_switch_ready = True
        print("✅ PCF8575 for Limit Switches initialized at 0x20.")
    except Exception as e:
        print(f"❌ Failed to initialize Limit Switch PCF8575 at 0x20: {e}")

# === Initialize PCF8575 for Relays ===
if i2c:
    try:
        pcf_relay = PCF8575(i2c, address=0x26)
        relay_ready = True
        print("✅ PCF8575 for Relays initialized at 0x26.")
    except Exception as e:
        print(f"❌ Failed to initialize Relay PCF8575 at 0x26: {e}")
