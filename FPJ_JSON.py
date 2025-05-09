import json
import os
from datetime import datetime
from typing import Any
from FPJ_CONSTANTS import TARGET_WEIGHTS

class JsonHelper:
    def __init__(self, filename: str = "FPJ_DATA.json") -> None:
        """
        Initializes the JsonHelper with a specified file.

        Args:
            filename (str): The name of the JSON file to read/write. Defaults to "FPJ_DATA.json".
        """
        self.filename: str = filename
        self._ensure_file()

    def _ensure_file(self) -> None:
        """
        Ensures that the JSON file exists. If the file does not exist, it creates an empty file.
        """
        # Absolute path to the file
        abs_path = os.path.abspath(self.filename)
        if not os.path.isfile(abs_path):
            try:
                print(f"[INFO] Creating new data file at: {abs_path}")
                with open(abs_path, "w") as f:
                    json.dump({}, f, indent=4)
            except Exception as e:
                print(f"[ERROR] Failed to create data file: {e}")

    def get_all(self) -> dict:
        """
        Loads and returns the entire JSON data from the file.

        Returns:
            dict: The loaded JSON data.
        """
        try:
            abs_path = os.path.abspath(self.filename)
            with open(abs_path, "r") as f:
                data: dict = json.load(f)
                return data
        except Exception as e:
            print(f"[ERROR] Failed to read data from {abs_path}: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Gets the value for the given key from the JSON data.

        Args:
            key (str): The key to search for.
            default (Any): The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key.
        """
        data: dict = self.get_all()
        value: Any = data.get(key, default)
        print(f"[FETCH] {key} is {value}.")
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Sets a key-value pair in the JSON file.

        Args:
            key (str): The key to set.
            value (Any): The value to associate with the key.
        """
        try:
            data: dict = self.get_all()
            data[key] = value
            abs_path = os.path.abspath(self.filename)
            with open(abs_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[WRITE] {key} set to {value}")
        except Exception as e:
            print(f"[ERROR] Failed to write data to {abs_path}: {e}")

    def modify(self, key: str, value: Any) -> None:
        """
        Modifies an existing key-value pair or adds a new key-value pair if it doesn't exist.

        Args:
            key (str): The key to modify or add.
            value (Any): The new value to associate with the key.
        """
        try:
            data: dict = self.get_all()
            if key in data:
                print(f"[MODIFY] {key} exists, modifying value.")
            else:
                print(f"[ADD] {key} does not exist, adding new entry.")
            data[key] = value
            abs_path = os.path.abspath(self.filename)
            with open(abs_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[WRITE] {key} set to {value}")
        except Exception as e:
            print(f"[ERROR] Failed to modify data in {abs_path}: {e}")


class FpjJson:
    def __init__(self) -> None:
        """
        Initializes the FPJ_JSON class, which manages the interaction with the FPJ_DATA.json file.
        """
        self.json_helper: JsonHelper = JsonHelper("FPJ_DATA.json")

    def is_at_home(self) -> bool:
        """
        Checks if the person is at home based on the 'IsAtHome' value in the JSON.

        Returns:
            bool: The status of whether the person is at home.
        """
        return self.json_helper.get("IsAtHome", False)

    def set_weight(self, key: str, value: int = 0) -> None:
        """
        Sets the weight for a given key.

        Args:
            key (str): The key representing the weight (e.g., 'NeemWeight').
            value (int): The weight value to set.
        """
        if value < 0:
            print(f"[WARNING] {key} cannot be negative. Value not set.")
            return
        self.json_helper.set(key, value)

    def get_weight(self, key: str) -> int:
        """
        Retrieves the weight for a given key.

        Args:
            key (str): The key representing the weight (e.g., 'NeemWeight').

        Returns:
            int: The weight value associated with the key.
        """
        return self.json_helper.get(key, 0)

    def update_kakawate_weight(self, value: int) -> None:
        """Updates the Kakawate weight."""
        self.set_weight("KakawateWeight", value)

    def update_neem_weight(self, value: int) -> None:
        """Updates the Neem weight."""
        self.set_weight("NeemWeight", value)

    def update_molasses_weight(self, value: int) -> None:
        """Updates the Molasses weight."""
        self.set_weight("MolassesWeight", value)

    def update_water_weight(self, value: int) -> None:
        """Updates the Water weight."""
        self.set_weight("WaterWeight", value)

    def get_neem_weight(self) -> int:
        """Retrieves the Neem weight."""
        return self.get_weight("NeemWeight")

    def get_kakawate_weight(self) -> int:
        """Retrieves the Kakawate weight."""
        return self.get_weight("KakawateWeight")

    def get_molasses_weight(self) -> int:
        """Retrieves the Molasses weight."""
        return self.get_weight("MolassesWeight")

    def get_water_weight(self) -> int:
        """Retrieves the Water weight."""
        return self.get_weight("WaterWeight")

    def reset_weights(self) -> None:
        """Resets all weights to 0."""
        self.update_neem_weight(0)
        self.update_kakawate_weight(0)
        self.update_molasses_weight(0)
        self.update_water_weight(0)
        print("[INFO] All weights have been reset to 0.")

    def is_already_fermenting(self) -> bool:
        """Checks if the fermentation process has already started."""
        return self.json_helper.get("IsFermenting", False)

    def set_fermenting(self, status: bool) -> None:
        """Sets the fermentation status."""
        self.json_helper.set("IsFermenting", status)

    def get_slider_position(self) -> int:
        """Retrieves the latest slider position."""
        return self.json_helper.get("SliderLatestPosition", 0)

    def set_slider_position(self, position: int) -> None:
        """Sets the slider position."""
        self.json_helper.set("SliderLatestPosition", position)

    def set_mixer_position(self, position: int) -> None:
        """Sets the mixer motor position."""
        self.json_helper.set("MixerLatestPosition", position)

    def get_mixer_position(self) -> int:
        """Gets the mixer motor position."""
        return self.json_helper.get("MixerLatestPosition", 0)

    def set_mixing_status(self, status: bool) -> None:
        """Sets the mixing status."""
        self.json_helper.set("IsMixingDone", status)

    def get_mixing_status(self) -> bool:
        """Gets the mixing status."""
        return self.json_helper.get("IsMixingDone", False)
    

    def set_fermentation_start_date(self) -> None:
        """Sets the current date as the fermentation start date."""
        fermentation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.json_helper.set("FermentationDate", fermentation_date)
        print(f"[INFO] Fermentation start date set to {fermentation_date}")
    
    def get_fermentation_start_date(self) -> str:
        """Retrieves the fermentation start date from the JSON."""
        return self.json_helper.get("FermentationDate", "")
    
    def set_loaded(self, status: bool = True) -> None:
        """Sets the IsLoaded flag to indicate if the system has been loaded."""
        self.json_helper.set("IsLoaded", status)
        print(f"[STATUS] IsLoaded set to {status}")

    def is_loaded(self) -> bool:
        """Checks if the system is marked as loaded."""
        return self.json_helper.get("IsLoaded", False)

class FpjStatus:
    def __init__(self) -> None:
        self.fpjson = FpjJson()

    def is_kakawate_enough(self) -> bool:
        weight = self.fpjson.get_kakawate_weight()
        print(f"[STATUS] KakawateWeight is {weight}g")
        return weight >= TARGET_WEIGHTS["KAKAWATE"]

    def is_neem_enough(self) -> bool:
        weight = self.fpjson.get_neem_weight()
        print(f"[STATUS] NeemWeight is {weight}g")
        return weight >= TARGET_WEIGHTS["NEEM"]

    def is_molasses_enough(self) -> bool:
        weight = self.fpjson.get_molasses_weight()
        print(f"[STATUS] MolassesWeight is {weight}g")
        return weight >= TARGET_WEIGHTS["MOLASSES"]

    def is_water_enough(self) -> bool:
        weight = self.fpjson.get_water_weight()
        print(f"[STATUS] WaterWeight is {weight}g")
        return weight >= TARGET_WEIGHTS["WATER"]

    def is_ingredients_enough(self) -> bool:
        return (
            self.is_kakawate_enough()
            and self.is_neem_enough()
            and self.is_molasses_enough()
            and self.is_water_enough()
        )

    def is_batch_done(self) -> bool:
        is_done = self.fpjson.is_already_fermenting()
        print(f"[STATUS] BatchDone is {is_done}")
        return is_done
    
    def is_mixing_done(self) -> bool: 
        return self.fpjson.get_mixing_status()

    def is_ready_for_harvest(self, duration_in_days: int) -> bool:
        """Checks if the fermentation duration has exceeded the given days."""
        fermentation_date_str = self.fpjson.get_fermentation_start_date()
        if not fermentation_date_str:
            print("[ERROR] Fermentation date is not set.")
            return False

        fermentation_date = datetime.strptime(fermentation_date_str, '%Y-%m-%d %H:%M:%S')
        current_date = datetime.now()
        duration = (current_date - fermentation_date).days

        print(f"[STATUS] Fermentation started on {fermentation_date_str}, current date is {current_date.strftime('%Y-%m-%d %H:%M:%S')}. Duration: {duration} days")

        if duration >= duration_in_days:
            print(f"[INFO] Ready for harvest!")
            return True
        else:
            print(f"[INFO] Not yet ready for harvest. {duration_in_days - duration} days to go.")
            return False


# Main execution
if __name__ == "__main__":
    # Initialize the FPJ JSON and status helper objects
    fpj_json = FpjJson()
    fpj_status = FpjStatus()

    # Test JSON helper methods
    print("[TEST] Fetching all data:")
    print(fpj_json.json_helper.get_all())

    print("[TEST] Fetching NeemWeight:")
    print(fpj_json.get_neem_weight())

    # Update some weights for testing purposes
    fpj_json.update_neem_weight(1500)
    fpj_json.update_kakawate_weight(1200)
    fpj_json.update_molasses_weight(600)
    fpj_json.update_water_weight(700)

    print("[TEST] After updating weights:")
    print(f"NeemWeight: {fpj_json.get_neem_weight()}g")
    print(f"KakawateWeight: {fpj_json.get_kakawate_weight()}g")
    print(f"MolassesWeight: {fpj_json.get_molasses_weight()}g")
    print(f"WaterWeight: {fpj_json.get_water_weight()}g")

    # Test status checks
    print("[TEST] Checking if Kakawate is enough:")
    print(f"Is Kakawate enough? {fpj_status.is_kakawate_enough()}")

    print("[TEST] Checking if Neem is enough:")
    print(f"Is Neem enough? {fpj_status.is_neem_enough()}")

    print("[TEST] Checking if Molasses is enough:")
    print(f"Is Molasses enough? {fpj_status.is_molasses_enough()}")

    print("[TEST] Checking if Water is enough:")
    print(f"Is Water enough? {fpj_status.is_water_enough()}")

    # Reset all weights for testing
    fpj_status.reset()

    print("[TEST] After resetting weights:")
    print(f"NeemWeight: {fpj_json.get_neem_weight()}g")
    print(f"KakawateWeight: {fpj_json.get_kakawate_weight()}g")
    print(f"MolassesWeight: {fpj_json.get_molasses_weight()}g")
    print(f"WaterWeight: {fpj_json.get_water_weight()}g")

    # Set the system as loaded
    fpj_json.set_loaded(True)

    # Test fermentation process status
    fpj_json.set_fermentation_start_date()
    print(f"Fermentation start date: {fpj_json.get_fermentation_start_date()}")
    print(f"Is system loaded? {fpj_json.is_loaded()}")
