from time import sleep
import FPJ_PCF
from FPJ_RELAY import RelayController, OutputController
from FPJ_LIMITSWITCH import LimitStatus

# Pin definitions
SliderPulsePin: int = 15
SliderDirectionPin: int = 14
SliderPulseInterval: float = 0.0005
SealerPulsePin: int = 13
SealerDirectionPin: int = 12
SealerPulseInterval: float = 0.001

limit_status = LimitStatus()  # Create only one instance globally

# Optional direct pin instances (not used directly in StepperController)
SliderPulse = OutputController(pin_number=SliderPulsePin, name="Slider Pulse")
SliderDirection = OutputController(pin_number=SliderDirectionPin, name="Slider Direction")
SealerPulse = OutputController(pin_number=SealerPulsePin, name="Sealer Pulse")
SealerDirection = OutputController(pin_number=SealerDirectionPin, name="Sealer Direction")

class StepperController:
    controller = RelayController()
    motor_enabled = False  # Track motor power state

    def __init__(self, pulse_pin: int, direction_pin: int, pulse_interval: float):
        self.ready = FPJ_PCF.relay_ready
        self.pulse_interval = pulse_interval

        if self.ready:
            self.pulse_pin = OutputController(pulse_pin, "Pulse Pin")
            self.direction_pin = OutputController(direction_pin, "Direction Pin")
            print("StepperController initialized successfully.")
        else:
            print("PCF for relay not ready!")
            self.pulse_pin = None
            self.direction_pin = None

    def is_sealer_up(self) -> bool:
        return limit_status.is_cover_up()

    def is_sealer_down(self) -> bool:
        return limit_status.is_cover_down()

    def is_slider_at_home(self) -> bool:
        return limit_status.is_slider_home()

    def move_stepper(self, direction: bool = True, step: int = 200) -> None:
        if not self.ready or self.pulse_pin is None or self.direction_pin is None:
            print("StepperController not ready or pins not initialized.")
            return

        if not self.motor_enabled:
            self.enable()
        
        self.direction_pin.turn_on() if direction else self.direction_pin.turn_off()
        print(f"Moving stepper: direction={direction}, steps={step}")

        for current_step in range(step):
            self.pulse_pin.turn_off()
            sleep(self.pulse_interval)
            self.pulse_pin.turn_on()
            sleep(self.pulse_interval)
            #print(f"Step {current_step + 1} of {step}")

        print("Stepper movement complete.")

    def move_stepper_to_destination(self, direction: bool = True, max_step: int = 1000, destination_func=None) -> None:
        if not self.ready or self.pulse_pin is None or self.direction_pin is None:
            print("StepperController not ready or pins not initialized.")
            return

        if not self.motor_enabled:
            self.enable()
        
        self.direction_pin.turn_on() if direction else self.direction_pin.turn_off()
        print(f"Moving stepper toward destination, direction={direction}")

        for current_step in range(max_step):
            if destination_func and destination_func():
                break

            self.pulse_pin.turn_off()
            sleep(self.pulse_interval)
            self.pulse_pin.turn_on()
            sleep(self.pulse_interval)

        print("Stepper destination movement complete.")

    def enable(self) -> None:
        if not self.motor_enabled:
            self.controller.enable_stepper()
            self.motor_enabled = True
            print("Stepper motor enabled.")

    def disable(self) -> None:
        if self.motor_enabled:
            self.controller.disable_stepper()
            self.motor_enabled = False
            print("Stepper motor disabled.")


class Steppers:
    def __init__(self):
        self.sealer = StepperController(
            pulse_pin=SealerPulsePin,
            direction_pin=SealerDirectionPin,
            pulse_interval=SealerPulseInterval
        )

        self.slider = StepperController(
            pulse_pin=SliderPulsePin,
            direction_pin=SliderDirectionPin,
            pulse_interval=SliderPulseInterval
        )

    def lift_cover(self) -> None:
        print("Lifting cover...")
        self.sealer.move_stepper_to_destination(
            direction=True,
            max_step=1000,
            destination_func=limit_status.is_cover_up
        )

    def seal(self) -> None:
        print("Sealing...")
        self.sealer.move_stepper_to_destination(
            direction=False,
            max_step=1000,
            destination_func=limit_status.is_cover_down
        )

    def moveSliderToHome(self) -> None:
        print("Moving slider to home...")
        self.slider.enable()
        self.lift_cover()
        self.slider.move_stepper_to_destination(
            direction=True,
            max_step=100000,  # Safety max steps to prevent endless loop
            destination_func=limit_status.is_slider_home
        )

    def moveSliderToMixer(self) -> None:
        print("Moving slider to mixer...")
        self.slider.enable()
        self.lift_cover()
        self.slider.move_stepper(False, step=21000)

    def moveSliderToSealer(self) -> None:
        print("Moving slider to sealer...")
        self.slider.enable()
        self.lift_cover()
        self.slider.move_stepper(False, step=37000)

    def disableSealer(self) -> None:
        print("Disabling sealer...")
        self.sealer.disable()

    def disableSlider(self) -> None:
        print("Disabling slider...")
        self.slider.disable()


stepper = Steppers()

# === MAIN ===
if __name__ == "__main__":
    if not FPJ_PCF.relay_ready:
        print("PCF8575 (Relay) not ready!")
    else:
        print("PCF8575 (Relay) ready. Starting stepper test...")

    stepper.moveSliderToHome()
    stepper.moveSliderToMixer()
    stepper.moveSliderToSealer()

    try:
        while True:
            stepper.lift_cover()
            stepper.seal()

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        stepper.disableSealer()
