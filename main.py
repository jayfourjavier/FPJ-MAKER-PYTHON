from time import sleep
from FPJ_SCALE import Scale
from FPJ_STEPPER import Steppers
from FPJ_RELAY import RelayController, OutputController
from FPJ_JSON import FpjJson, FpjStatus

# python3 main.py

serial_port = '/dev/ttyUSB0'  # Serial port of the ESP32 connected to the HX711
scale = Scale(serial_port)
stepper = Steppers()
controller = RelayController()
status = FpjStatus()
json = FpjJson()

LedIndicator = OutputController(pin_number=8, name="Ready for harvest")
LedIndicator.turn_off()

TARGET_WEIGHTS = {
    'kakawate': 1000,
    'neem': 1000,
    'molasses': 2000,
    'water': 2000
}


def reset_slider() -> None:
    """Resets the mixer to its home position and tares the scale."""
    print("[SYSTEM] Resetting slider and taring scale...")
    controller.mixer_up()
    stepper.moveSliderToHome()
    scale.trigger_tare()


def dispense_ingredient(name: str, get_weight_func, dispense_func, step: int = 5) -> None:
    """
    Generic function to dispense ingredients based on weight deficit.
    :param name: Ingredient name (for log display)
    :param get_weight_func: Function to retrieve current json weight for the ingredient
    :param dispense_func: Relay controller function to dispense the ingredient
    :param step: Amount to dispense per loop (default is 5 grams)
    """
    current_weight = get_weight_func()
    target_weight = TARGET_WEIGHTS[name]
    deficit = target_weight - current_weight

    print(f"[{name.upper()}] Target: {target_weight}g | Current: {current_weight}g | Deficit: {deficit}g")

    if deficit <= 0:
        print(f"[{name.upper()}] No need to add. Already enough.")
        return

    scale.trigger_tare()
    sleep(0.5)  # Allow some settling time

    while (weight := scale.get_weight()) < deficit:
        print(f"[{name.upper()}] : {weight}g / {deficit}g")
        dispense_func(step)
        sleep(0.3)


def add_kakawate():
    dispense_ingredient("kakawate", json.get_kakawate_weight, controller.dispense_kakawate)


def add_neem():
    dispense_ingredient("neem", json.get_neem_weight, controller.dispense_neem)


def add_molasses():
    dispense_ingredient("molasses", json.get_molasses_weight, controller.add_molasses)


def add_water():
    dispense_ingredient("water", json.get_water_weight, controller.pump_water, step=1)


def mix():
    """Handles the mixing process by moving the mixer down, mixing, and then moving it back up."""
    print("[SYSTEM] Starting mix process...")
    controller.mixer_down()
    controller.mix()
    controller.mixer_up()
    status.set_mixing_done(True)
    print("[SYSTEM] Mixing process completed.")


if __name__ == "__main__":
    try:
        #controller.power_up()


        if not status.batch_done():
            reset_slider()

            if not status.is_ingredients_enough():
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
            else:
                print("Materials are complete and ready for mixing")

            # Proceed to mixing if not done yet
            if not status.is_mixing_done():
                print("[SYSTEM] Initiating mixing process...")
                mix()
            else:
                print("[SYSTEM] Mixing already completed.")

            print("[ACTION] Turning off chopper...")
            controller.turn_off_chopper()

            print("[ACTION] Proceeding to packaging...")
            stepper.lift_cover()
            stepper.moveSliderToSealer()
            stepper.seal()
            LedIndicator.turn_on()

        else:
            print("[STATUS] Batch already fermenting. Skipping process.")
            LedIndicator.turn_on()

    except KeyboardInterrupt:
        print("\n[INTERRUPT] KeyboardInterrupt detected! Turning off all relays...")

    finally:
        controller.shutdown()
        #LedIndicator.turn_off()
        print("[SYSTEM] System safely shut down.")
