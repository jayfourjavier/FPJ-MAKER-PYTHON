import board
import digitalio
import time
from adafruit_pcf8575 import PCF8575
import FPJ_PCF

pcf = FPJ_PCF.pcf_limitswitch
pcf_ready = FPJ_PCF.limit_switch_ready

# === Limit Switch Class ===
class LimitSwitch:
    def __init__(self, pin_number: int, name: str) -> None:
        self.name = name
        self.available = pcf_ready
        self.pcf = pcf

        if self.available and pcf is not None:
            try:
                self.pin = pcf.get_pin(pin_number)
                self.pin.switch_to_input(pull=digitalio.Pull.UP)
            except Exception as e:
                print(f"Error setting up pin {pin_number} for {name}: {e}")
                self.available = False

    def is_triggered(self) -> bool:
        if not self.available:
            return False
        try:
            triggered = not self.pin.value  # Active LOW
            if triggered:
                print(f"{self.name} Triggered")
            return triggered
        except Exception as e:
            print(f"Error reading {self.name}: {e}")
            return False


# === Pin assignments ===
CoverLowerLimitSwitchPin = 4
CoverUpperLimitSwitchPin = 5
MixerUpperLimitSwitchPin = 6
MixerLowerLimitSwitchPin = 7
SliderHomeLimitSwitchPin = 11
ResetPin: int = 9
StartPin: int = 10
LedPin: int = 8


# === Instantiate limit switches ===
MixerUp = LimitSwitch(MixerUpperLimitSwitchPin, "Mixer Up")
MixerDown = LimitSwitch(MixerLowerLimitSwitchPin, "Mixer Down")
CoverUp = LimitSwitch(CoverUpperLimitSwitchPin, "Cover Up")
CoverDown = LimitSwitch(CoverLowerLimitSwitchPin, "Cover Down")
Slider = LimitSwitch(SliderHomeLimitSwitchPin, "Slider")
Reset = LimitSwitch(ResetPin, "Reset")
Start = LimitSwitch(StartPin, "Start")


# === Limit Status Class ===
class LimitStatus:
    def __init__(self):
        self.ready = pcf_ready

    def is_mixer_up(self) -> bool:
        return MixerUp.is_triggered()

    def is_mixer_down(self) -> bool:
        return MixerDown.is_triggered()

    def is_slider_home(self) -> bool:
        return Slider.is_triggered()

    def is_cover_up(self) -> bool:
        return CoverUp.is_triggered()

    def is_cover_down(self) -> bool:
        return CoverDown.is_triggered()
    
    def is_reset_btn_pressed(self) -> bool:
        return Reset.is_triggered()
    
    def is_start_btn_pressed(self) -> bool:
        return Start.is_triggered()

if __name__ == "__main__":
    limit_status = LimitStatus()
    
    try:
        print("Starting Limit Switch Test (Ctrl+C to stop)...")
        while True:
            if limit_status.is_reset_btn_pressed():
                print("limit_status.is_reset_btn_pressed()")

            if limit_status.is_loaded_btn_pressed():
                print("limit_status.is_loaded_btn_pressed()")


    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")

    
