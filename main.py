from time import sleep
from FPJ_SCALE import Scale
from FPJ_STEPPER import Steppers
from FPJ_RELAY import RelayController
from FPJ_JSON import FpjJson, FpjStatus

# python3 main.py

serial_port = '/dev/ttyUSB0'  # Serial port of the ESP32 connected to the HX711
scale = Scale(serial_port)
stepper = Steppers()
controller = RelayController()
status = FpjStatus()
json = FpjJson()


def reset_slider() -> None:
    """Resets the mixer to its home position and tares the scale."""
    print("[SYSTEM] Resetting slider and taring scale...")
    controller.mixer_up()
    stepper.moveSliderToHome()
    scale.trigger_tare()


def add_kakawate() -> None:
    
    while (weight := scale.get_weight()) < 1000:
        print(f"[KAKAWATE] Current weight: {weight}g")
        controller.dispense_kakawate(5)


def add_neem() -> None:
    while (weight := scale.get_weight()) < 2000:
        print(f"[NEEM] Current weight: {weight}g")
        controller.dispense_neem(5)




def add_molasses() -> None:
    while (weight := scale.get_weight()) < 4000:
        print(f"[MOLASSES] Current weight: {weight}g")
        controller.add_molasses(5)


def add_water() -> None:
    while (weight := scale.get_weight()) < 6000:
        print(f"[WATER] Current weight: {weight}g")
        controller.pump_water(1)


if __name__ == "__main__":
    try:
        if not status.batch_done():
            reset_slider()

            if not status.is_ingredients_complete():
                print("[SYSTEM] Starting ingredient preparation...")

                if not status.is_kakawate_enough() or not status.is_neem_enough():
                    print("[CHECK] Kakawate or Neem not enough. Preparing chopper...")

                    controller.turn_on_chopper()
                    
                    if not status.is_kakawate_enough():
                        print("[DISPENSE] Kakawate not enough. Dispensing...")
                        add_kakawate()

                    if not status.is_neem_enough():
                        print("[DISPENSE] Neem not enough. Dispensing...")
                        add_neem()

                    controller.turn_off_chopper()



                if not status.is_molasses_enough():
                    print("[CHECK] Molasses not enough. Adding...")
                    add_molasses()

                if not status.is_water_enough():
                    print("[CHECK] Water not enough. Pumping...")
                    add_water()

            print("[ACTION] Turning off chopper...")
            controller.turn_off_chopper()

            print("[ACTION] Moving to mixer and adding molasses...")
            stepper.moveSliderToMixer()
            controller.add_molasses(5)

            print("[ACTION] Mixing sequence started...")
            controller.mixer_down()
            controller.mix(20)
            controller.mixer_up()

            print("[ACTION] Proceeding to packaging...")
            stepper.lift_cover()
            stepper.moveSliderToSealer()
            stepper.seal()

        else:
            print("[STATUS] Batch already fermenting. Skipping process.")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] KeyboardInterrupt detected! Turning off all relays...")

    finally:
        controller.shutdown()
        print("[SYSTEM] System safely shut down.")
