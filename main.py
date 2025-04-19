from time import sleep
from FPJ_SCALE import Scale
from FPJ_STEPPER import Steppers
from FPJ_RELAY import RelayController, OutputController
from FPJ_JSON import FpjJson, FpjStatus
from FPJ_LCD import FPJ_LCD

# python3 main.py

serial_port = '/dev/ttyUSB0'  # Serial port of the ESP32 connected to the HX711
scale = Scale(serial_port)
stepper = Steppers()
controller = RelayController()
status = FpjStatus()
json = FpjJson()
lcd = FPJ_LCD()

LedIndicator = OutputController(pin_number=8, name="Ready for harvest")
LedIndicator.turn_off()

TARGET_WEIGHTS = {
    'KAKAWATE': 1000,
    'NEEM': 1000,
    'MOLASSES': 2000,
    'WATER': 2000
}


def reset_slider() -> None:
    """Resets the mixer to its home position and tares the scale."""
    print("[SYSTEM] Resetting slider and taring scale...")
    lcd.display_activity(1)
    controller.mixer_up()
    stepper.moveSliderToHome()
    scale.trigger_tare()


def dispense_ingredient(
    name: str,
    get_weight_func,
    set_weight_func,
    dispense_func,
    display_weight_func,
    step: int = 5
) -> None:
    """
    Generic function to dispense ingredients based on weight deficit.

    :param name: Ingredient name (for log display)
    :param get_weight_func: Function to retrieve current json weight for the ingredient
    :param set_weight_func: Function to update the json weight for the ingredient
    :param dispense_func: Relay controller function to dispense the ingredient
    :param display_weight_func: Function to update LCD with the weight (e.g. fpj_lcd.display_kakawate_weight)
    :param step: Amount to dispense per loop (default is 5 grams)
    """
    current_weight = get_weight_func()
    target_weight = TARGET_WEIGHTS[name]
    deficit = target_weight - current_weight

    print(f"[{name}] Target: {target_weight}g | Current: {current_weight}g | Deficit: {deficit}g")

    if deficit <= 0:
        print(f"[{name}] No need to add. Already enough.")
        display_weight_func(current_weight)  # ✅ Show weight even if enough
        return

    scale.trigger_tare()
    sleep(0.5)  # Allow some settling time

    dispensed_weight = 0
    while (weight := scale.get_weight()) < deficit:
        print(f"[{name}] : {weight}g / {deficit}g")

        # ✅ Update LCD every loop
        display_weight_func(weight)

        dispense_func(step)
        sleep(0.3)
        dispensed_weight = weight

    final_weight = current_weight + dispensed_weight
    print(f"[{name}] Final JSON weight: {final_weight}g. Updating JSON.")
    set_weight_func(final_weight)

    # ✅ Final display update
    display_weight_func(final_weight)


def add_kakawate():
    lcd.display_activity(2)
    dispense_ingredient(
        "KAKAWATE",
        json.get_kakawate_weight,
        json.update_kakawate_weight,
        controller.dispense_kakawate,
        lcd.display_kakawate_weight,
        step=2
    )


def add_neem():
    lcd.display_activity(3)
    dispense_ingredient(
        "NEEM",
        json.get_neem_weight,
        json.update_neem_weight,
        controller.dispense_neem,
        lcd.display_neem_weight,
        step=2
    )


def add_molasses():
    lcd.display_activity(4)
    dispense_ingredient(
        "MOLASSES",
        json.get_molasses_weight,
        json.update_molasses_weight,
        controller.add_molasses,
        lcd.display_molasses_weight,
        step=5
    )


def add_water():
    lcd.display_activity(5)
    dispense_ingredient(
        "WATER",
        json.get_water_weight,
        json.update_water_weight,
        controller.pump_water,
        lcd.display_water_weight,
        step=1
    )


def mix():
    """Handles the mixing process by moving the mixer down, mixing, and then moving it back up."""
    print("[SYSTEM] Starting mix process...")
    lcd.display_activity(6)
    stepper.moveSliderToMixer()
    lcd.display_activity(7)
    controller.mixer_down()
    lcd.display_activity(8)
    controller.mix(20)
    lcd.display_activity(9)
    controller.mixer_up()
    json.set_mixing_status(True)
    print("[SYSTEM] Mixing process completed.")


if __name__ == "__main__":
    try:
        lcd.welcome()
        controller.power_up()
        lcd.lcd2.clear()

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
                    else:
                        lcd.display_kakawate_weight(json.get_kakawate_weight())

                    if not status.is_neem_enough():
                        print("[DISPENSE] Neem not enough. Dispensing...")
                        add_neem()
                    else:
                        lcd.display_neem_weight(json.get_neem_weight())

                    controller.turn_off_chopper()
                else:
                    lcd.display_kakawate_weight(json.get_kakawate_weight())
                    lcd.display_neem_weight(json.get_neem_weight())

                if not status.is_molasses_enough():
                    print("[CHECK] Molasses not enough. Adding...")
                    add_molasses()
                else:
                    lcd.display_molasses_weight(json.get_molasses_weight())

                if not status.is_water_enough():
                    print("[CHECK] Water not enough. Pumping...")
                    add_water()
                else:
                    lcd.display_water_weight(json.get_water_weight())
            else:
                print("Materials are complete and ready for mixing")
                # ✅ Display all existing weights
                lcd.display_kakawate_weight(json.get_kakawate_weight())
                lcd.display_neem_weight(json.get_neem_weight())
                lcd.display_molasses_weight(json.get_molasses_weight())
                lcd.display_water_weight(json.get_water_weight())

            if not status.is_mixing_done():
                print("[SYSTEM] Initiating mixing process...")
                mix()
            else:
                print("[SYSTEM] Mixing already completed.")

            print("[ACTION] Turning off chopper...")
            controller.turn_off_chopper()

            print("[ACTION] Proceeding to packaging...")
            stepper.lift_cover()
            
            lcd.display_activity(10)
            stepper.moveSliderToSealer()
            lcd.display_activity(11)
            stepper.seal()
            LedIndicator.turn_on()

        else:
            print("[STATUS] Batch already fermenting. Skipping process.")
            lcd.display_activity(12)
            LedIndicator.turn_on()

    except KeyboardInterrupt:
        print("\n[INTERRUPT] KeyboardInterrupt detected! Turning off all relays...")

    finally:
        controller.shutdown()
        print("[SYSTEM] System safely shut down.")
