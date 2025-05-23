import board
import digitalio
from time import sleep  # Importing only sleep
from adafruit_pcf8575 import PCF8575
from FPJ_LIMITSWITCH import LimitStatus
from FPJ_SERVO import ServoController
import FPJ_PCF

pcf = FPJ_PCF.pcf_relay

LimitSwitch = LimitStatus()

class Relay:
    PcfRelay = pcf
    used_pins = []

    def __init__(self, pin_number: int, name: str) -> None:
        self.name = name
        self.pin_number = pin_number
        self.pin = self.PcfRelay.get_pin(pin_number)
        self.pin.switch_to_output(value=True)  # Default OFF state
        
        # Add the pin to the used_pins list
        Relay.used_pins.append(pin_number)

    @classmethod
    def turn_off_unused_relays(cls):
        """Turn off all unused relays by setting them to True."""
        for pin_number in range(16):  # Assuming the PCF8575 has 16 pins (adjust if necessary)
            if pin_number not in cls.used_pins:
                pin = cls.PcfRelay.get_pin(pin_number)
                pin.switch_to_output(value=True)  # Set to OFF (active low logic)
                print(f"Relay on pin {pin_number} is OFF (unused).")

    def turn_on(self) -> None:
        """Turn on the relay (set pin to LOW, since it's active low)."""
        self.pin.value = False  # Active low logic

    def turn_off(self) -> None:
        """Turn off the relay (set pin to HIGH)."""
        self.pin.value = True  # Active high logic

    def run(self, on_time: float) -> None:
        """Turn on and off the relay with specified times."""
        self.turn_on()
        print(f"{self.name} is turned ON.")
        sleep(on_time)

        self.turn_off()
        print(f"{self.name} is turned OFF.")
        sleep(3)

        

class RelayController:
    # Relay instances for each device
    WaterPumpRelay = Relay(pin_number=6, name="Water Pump")
    KakawateRelay = Relay(pin_number=7, name="Kakawate Dispenser")
    NeemRelay = Relay(pin_number=9, name="Neem Dispenser")
    MixerRelay = Relay(pin_number=10, name="Mixer Motor")
    StepperPowerRelay = Relay(pin_number=5, name="Stepper Motor Power Supply")
    MixerDownRelay = Relay(pin_number=3, name="Mixer Down Relay")
    MixerUpRelay = Relay(pin_number=12, name="Mixer Up Relay")
    MolassesDispenser = ServoController()
    ServoPowerRelay = Relay(pin_number=2, name="Servo Power Supply")
    ChopperRelay = Relay(pin_number=1, name="Chopper Motor")


    def __init__(self):
        # Ensure unused relays are turned off
        Relay.turn_off_unused_relays()
        sleep(5)

    def pump_water(self, duration: float) -> None:
        """Activate water pump for a specific duration."""
        self.WaterPumpRelay.run(duration)

    def dispense_neem(self, duration: float) -> None:
        """Activate neem dispenser for a specific duration."""
        self.NeemRelay.run(duration)

    def dispense_kakawate(self, duration: float) -> None:
        """Activate kakawate dispenser for a specific duration."""
        self.KakawateRelay.run(duration)

    def enable_stepper(self) -> None:
        """Enable the stepper motor power supply."""
        self.StepperPowerRelay.turn_on()
        print("Stepper motor power supply is turned ON.")
        sleep(3)


    def disable_stepper(self) -> None:
        """Disable the stepper motor power supply."""
        self.StepperPowerRelay.turn_off()
        print("Stepper motor power supply is turned OFF.")
        sleep(3)


    def enable_servo(self) -> None:
        """Enable the servo motor power supply."""
        self.ServoPowerRelay.turn_on()
        print("Servo motor power supply is turned ON.")
        sleep(3)


    def disable_servo(self) -> None:
        """Disable the servo motor power supply."""
        self.ServoPowerRelay.turn_off()
        print("Servo motor power supply is turned OFF.")
        sleep(3)

    def mix(self, duration: float) -> None:
        """Activate the mixer motor for a specific duration."""
        self.MixerRelay.run(duration)
    
    def mixer_down(self) -> None:
        """Move the mixer down."""
        print("Moving mixer down...")
        self.MixerDownRelay.turn_on()
        while not LimitSwitch.is_mixer_down():
            print("Waiting to reach down position...")
            sleep(1)
        self.MixerDownRelay.turn_off()
        print("Mixer reached down position.")
        sleep(3)

    def mixer_up(self) -> None:
        """Move the mixer up."""
        print("Moving mixer up...")
        self.MixerUpRelay.turn_on()
        while not LimitSwitch.is_mixer_up():
            print("Waiting to reach up position...")
            sleep(1)
        self.MixerUpRelay.turn_off()
        print("Mixer reached up position.")
        sleep(3)

    def add_molasses(self, duration: int = 5) -> None:
        """Dispense molasses for a given duration (default is 5 seconds)."""
        self.enable_servo()
        print(f"Starting to dispense molasses for {duration} seconds...")
        self.MolassesDispenser.open()
        sleep(duration)
        self.MolassesDispenser.close()
        self.disable_servo()
        print("Finished dispensing molasses.")

    def turn_on_chopper(self) -> None:
        """
        Turn on the chopper via the relay.
        """
        print("Turning on the chopper...")
        self.ChopperRelay.turn_on()
        print("Chopper is now ON.")

    def turn_off_chopper(self) -> None:
        """
        Turn off the chopper via the relay.
        """
        print("Turning off the chopper...")
        self.ChopperRelay.turn_off()
        print("Chopper is now OFF.")

    def shutdown(self) -> None:
        self.ChopperRelay.turn_off()
        self.MixerRelay.turn_off()
        self.WaterPumpRelay.turn_off()
        self.ServoPowerRelay.turn_off()
        self.NeemRelay.turn_off()
        self.KakawateRelay.turn_off()
        self.StepperPowerRelay.turn_off()
        self.MixerDownRelay.turn_off()
        self.MixerUpRelay.turn_off()

# Test function (not in production)
def test_all_relays():
    print("Testing all relays (0 to 15)...")
    for pin_number in range(16):
        print(f"Testing relay on pin {pin_number}")
        pin = Relay.PcfRelay.get_pin(pin_number)
        pin.switch_to_output(value=True)
        sleep(5)
        pin.value = False
        print(f"Relay on pin {pin_number} is ON")
        sleep(5)
        pin.value = True
        print(f"Relay on pin {pin_number} is OFF")

# Main loop
def test_loop() -> None:
    controller = RelayController()

    controller.mixer_down()
    controller.add_molasses(5)
    controller.pump_water(5)
    controller.mix(10)
    controller.mixer_up()

class OutputController:
    def __init__(self, pin_number: int, name: str) -> None:
        self.name = name
        self.available = FPJ_PCF.limit_switch_ready
        self.pcf = FPJ_PCF.pcf_limitswitch

        if self.available and self.pcf is not None:
            try:
                self.pin = self.pcf.get_pin(pin_number)
                self.pin.switch_to_output(value=True)
            except Exception as e:
                print(f"Error setting up pin {pin_number} for {name}: {e}")
                self.available = False

    def turn_on(self) -> None:
        if self.available:
            print(f"Turning ON {self.name}")
            self.pin.value = False

    def turn_off(self) -> None:
        if self.available:
            print(f"Turning OFF {self.name}")
            self.pin.value = True



controller = RelayController()






# Main test execution
if __name__ == "__main__":

    try:
        # Continuously get weight and tare in a loop
        while True:
            #sleep(1)  # Wait for 1 second before getting the weight again
            #test_output_controller()
            controller.turn_on_chopper()
            sleep(5)

            print("Loop")
    except KeyboardInterrupt:
        print("\n\n Program terminated by user.")
    finally:
        # Close the serial connection when exiting
        controller.turn_off_chopper()
        sleep(5)
        print("\nProgram closed.")
        
