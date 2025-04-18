from time import sleep
from FPJ_SCALE import Scale
from FPJ_STEPPER import Steppers
from FPJ_RELAY import RelayController

# python3 main.py

serial_port = '/dev/ttyUSB0'  # Serial port of the ESP32 processing the HX711 weighing scale
scale = Scale(serial_port)    # Create instance of Scale Class
weight: int = 0

stepper = Steppers()
controller = RelayController()

# Main loop
if __name__ == "__main__":
    try:
        # Move stepper to home
        controller.mixer_up()
        stepper.moveSliderToHome()

        # Tare weight
        scale.trigger_tare()

        # Start chopper
        controller.turn_on_chopper()

        # Weigh and dispense Kakawate until 1000g
        weight = scale.get_weight()
        while weight < 1000:
            print(f"[KAKAWATE] Current weight: {weight}g")
            controller.dispense_kakawate(5)
            weight = scale.get_weight()

        # Weigh and dispense Neem until 2000g
        while weight < 2000:
            print(f"[NEEM] Current weight: {weight}g")
            controller.dispense_neem(5)
            weight = scale.get_weight()
        
        # Weigh and add Molasses until 4000g
        while weight < 4000:
            print(f"[MOLASSES] Current weight: {weight}g")
            controller.add_molasses(5)
            weight = scale.get_weight()

        # Weigh and pump Water until 6000g
        while weight < 6000:
            print(f"[WATER] Current weight: {weight}g")
            controller.pump_water(1)
            weight = scale.get_weight()

        # Move to mixer
        controller.turn_off_chopper()
        stepper.moveSliderToMixer()

        # Add molasses and water
        controller.add_molasses(5)

        # Mixing sequence
        controller.mixer_down()
        controller.mix(20)
        controller.mixer_up()

        # Packaging
        stepper.lift_cover()
        stepper.moveSliderToSealer()
        stepper.seal()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected! Turning off all relays...")

    finally:
        # Ensure all relays are off before exiting
        controller.shutdown()
        print("System safely shut down.")
