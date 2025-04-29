from time import sleep
from FPJ_SCALE import Scale
from FPJ_STEPPER import Steppers
from FPJ_RELAY import RelayController, OutputController
from FPJ_LIMITSWITCH import LimitStatus
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
button = LimitStatus()
DaysToFerment: int = 7
ReadyForHarvestDisplayed: bool = False
WaitingToFermentDisplayed: bool = False
MachineResetDone: bool = False
LoadAndPressStartDisplayed: bool = False


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
    global MachineResetDone
    print("[SYSTEM] Resetting slider and taring scale...")
    lcd.display_activity(1)
    controller.mixer_up()
    stepper.moveSliderToHome()
    scale.trigger_tare()
    MachineResetDone = True



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

    while True:
        weight = scale.get_weight()
        updated_weight = current_weight + weight
        
        print(f"[{name}] : {updated_weight}g / {target_weight}g")

        # ✅ Update LCD and JSON every loop
        display_weight_func(updated_weight)
        set_weight_func(updated_weight)



        # ✅ Read JSON again for decision making
        current_weight = get_weight_func()
        deficit = target_weight - current_weight

        if deficit <= 0:
            print(f"[{name}] Target achieved. Final JSON weight: {current_weight}g.")
            break

        dispense_func(step)
        sleep(0.3)




def add_kakawate():
    lcd.display_activity(2)
    dispense_ingredient(
        "KAKAWATE",
        json.get_kakawate_weight,
        json.update_kakawate_weight,
        controller.dispense_kakawate,
        lcd.display_kakawate_weight,
        step=5
    )


def add_neem():
    lcd.display_activity(3)
    dispense_ingredient(
        "NEEM",
        json.get_neem_weight,
        json.update_neem_weight,
        controller.dispense_neem,
        lcd.display_neem_weight,
        step=5
    )


def add_molasses():
    lcd.display_activity(4)
    dispense_ingredient(
        "MOLASSES",
        json.get_molasses_weight,
        json.update_molasses_weight,
        controller.add_molasses,
        lcd.display_molasses_weight,
        step=2
    )


def add_water():
    lcd.display_activity(5)
    dispense_ingredient(
        "WATER",
        json.get_water_weight,
        json.update_water_weight,
        controller.pump_water,
        lcd.display_water_weight,
        step=1.5
    )

def display_all_weights():
    #Display all existing weights
    print("Materials are complete and ready for mixing")
    lcd.display_kakawate_weight(json.get_kakawate_weight())
    lcd.display_neem_weight(json.get_neem_weight())
    lcd.display_molasses_weight(json.get_molasses_weight())
    lcd.display_water_weight(json.get_water_weight())


def mix():
    """Handles the mixing process by moving the mixer down, mixing, and then moving it back up."""
    print("[SYSTEM] Starting mix process...")
    lcd.display_activity(7)
    controller.mixer_down()
    lcd.display_activity(8)
    controller.mix(20)                                  #DITO BABAGUHIN KUNG GAANO KATAGAL ANG MIXING
    lcd.display_activity(9)
    controller.mixer_up()
    json.set_mixing_status(True)
    print("[SYSTEM] Mixing process completed.")

def mix_ingredients():
    if not status.is_mixing_done():
        print("[SYSTEM] Initiating mixing process...")
        lcd.display_activity(6)
        stepper.moveSliderToMixer()
        mix()
    else:
        stepper.moveSliderToMixer()
        print("[SSTEM] Mixing already completed.")

def seal():
    print("[ACTION] Proceeding to packaging...")
    stepper.lift_cover()
    lcd.display_activity(10) #MOVING SLIDER TO SEALER
    stepper.moveSliderToSealer()
    lcd.display_activity(11) #SEALING
    stepper.seal()
    LedIndicator.turn_off()
    lcd.display_activity(12)   #WAITING TO FERMENT
    json.set_fermenting(True)
    json.set_fermentation_start_date()

def add_ingredients():
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

def reset_flags():
    global ReadyForHarvestDisplayed
    global WaitingToFermentDisplayed
    global MachineResetDone
    global LoadAndPressStartDisplayed

    stepper.lift_cover()
    sleep(10)
    json.set_fermenting(False)
    json.reset_weights()
    json.set_mixing_status(False)
    json.set_loaded(False)
    print("RESET")
    ReadyForHarvestDisplayed = False
    WaitingToFermentDisplayed = False
    MachineResetDone = False
    LoadAndPressStartDisplayed = False

def main () -> None:
    global MachineResetDone
    global WaitingToFermentDisplayed
    global ReadyForHarvestDisplayed
    global LoadAndPressStartDisplayed

    try:
        lcd.welcome()
        controller.power_up()
        lcd.lcd2.clear()

        while True:
            if button.is_reset_btn_pressed():
                reset_flags()
                if not MachineResetDone:
                    reset_slider()
    
            if button.is_start_btn_pressed():
                json.set_loaded(True)
                print("START")

            if not status.is_batch_done(): 
                if not MachineResetDone:
                    reset_slider()

                if json.is_loaded():
                    if not status.is_ingredients_enough():                      # ingredients are not yet complete in the mixing container
                        print("[SYSTEM] Starting ingredient preparation...")
                        add_ingredients()     
                    else:                                                       # all ingredients is complete in the mixing container
                        display_all_weights()
                        mix_ingredients()
                        seal()
                else:
                    if not LoadAndPressStartDisplayed:
                        print("Not loaded yet.")
                        lcd.display_activity(14)
                        LoadAndPressStartDisplayed = True

            if status.is_batch_done() and status.is_ready_for_harvest(DaysToFerment):
                if not ReadyForHarvestDisplayed:
                    print("Ready for harvest")
                    lcd.display_activity(13)                                        # ready for harvest
                    LedIndicator.turn_on() 
                    ReadyForHarvestDisplayed = True

            if status.is_batch_done() and not status.is_ready_for_harvest(DaysToFerment):
                if not WaitingToFermentDisplayed:
                    print("[STATUS] Batch already fermenting. Skipping process.")
                    lcd.display_activity(12)                                        # waiting to ferment
                    LedIndicator.turn_off()
                    WaitingToFermentDisplayed = True

    except KeyboardInterrupt:
        print("\n[INTERRUPT] KeyboardInterrupt detected! Turning off all relays...")

    finally:
        controller.shutdown()
        print("[SYSTEM] System safely shut down.")



if __name__ == "__main__":
    main()