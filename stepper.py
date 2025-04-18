from time import sleep
import board
import adafruit_pcf8575

print("🔌 Initializing I2C...")
try:
    i2c = board.I2C()
except Exception as e:
    print(f"❌ I2C init failed: {e}")
    exit(1)

# I2C addresses
i2c_io_address = 0x27
# i2c_relay_address = 0x26  # unused for now

# Attempt to connect to PCF8575
try:
    print(f"🔍 Connecting to PCF8575 at {hex(i2c_io_address)}...")
    pcf_io = adafruit_pcf8575.PCF8575(i2c, i2c_io_address)
except Exception as e:
    print(f"❌ Could not connect to PCF8575 at {hex(i2c_io_address)}: {e}")
    exit(1)

class StepperMotor:
    def __init__(self, pul_pin_id: int, dir_pin_id: int, io_expander):
        try:
            self.pul = io_expander.get_pin(pul_pin_id)
            self.dir = io_expander.get_pin(dir_pin_id)

            self.pul.switch_to_output(value=True)  # Default HIGH (off)
            self.dir.switch_to_output(value=True)

            print(f"✅ Stepper initialized: PUL={pul_pin_id}, DIR={dir_pin_id}")
        except Exception as e:
            print(f"❌ Stepper pin setup failed: {e}")
            raise

    def run(self, direction: bool, steps: int = 200, delay: float = 0.0005):
        try:
            print(f"➡️ Stepper run: {'FORWARD' if direction else 'REVERSE'} | Steps: {steps}")
            self.dir.value = not direction  # active-low logic

            for _ in range(steps):
                self.pul.value = False
                sleep(delay)
                self.pul.value = True
                sleep(delay)

            print("✅ Stepper run complete")
        except Exception as e:
            print(f"❌ Error during stepper run: {e}")

# Initialize steppers
try:
    horizontal_stepper = StepperMotor(pul_pin_id=0, dir_pin_id=1, io_expander=pcf_io)
    vertical_stepper   = StepperMotor(pul_pin_id=2, dir_pin_id=3, io_expander=pcf_io)
except Exception:
    exit(1)

def test_stepper(stepper: StepperMotor, label="Stepper"):
    try:
        print(f"🔄 Testing {label}")

        total_steps = 0
        while total_steps < 55000:
            stepper.run(direction=False, steps=1000)
            total_steps += 1000
            print(f"  - Forward steps: {total_steps:,}")

        total_steps = 0
        while total_steps < 55000:
            stepper.run(direction=True, steps=1000)
            total_steps += 1000
            print(f"  - Backward steps: {total_steps:,}")

    except Exception as e:
        print(f"❌ {label} test failed: {e}")

# Main loop
try:
    while True:
        test_stepper(horizontal_stepper, label="Horizontal Stepper")
        # test_stepper(vertical_stepper, label="Vertical Stepper")  # Optional
        sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Interrupted by user. Exiting...")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
