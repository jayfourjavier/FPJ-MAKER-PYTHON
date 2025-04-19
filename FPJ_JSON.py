import json
import os
from typing import Any


class JsonHelper:
    def __init__(self, filename: str = "data.json") -> None:
        """
        Initializes the JsonHelper with a specified file.

        Args:
            filename (str): The name of the JSON file to read/write. Defaults to "data.json".
        """
        self.filename: str = filename
        self._ensure_file()

    def _ensure_file(self) -> None:
        """
        Ensures that the JSON file exists. If the file does not exist, it creates an empty file.
        """
        if not os.path.isfile(self.filename):
            try:
                print(f"[INFO] Creating new data file: {self.filename}")
                with open(self.filename, "w") as f:
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
            with open(self.filename, "r") as f:
                data: dict = json.load(f)
                return data
        except Exception as e:
            print(f"[ERROR] Failed to read data: {e}")
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
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[WRITE] {key} set to {value}")
        except Exception as e:
            print(f"[ERROR] Failed to write data: {e}")

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
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[WRITE] {key} set to {value}")
        except Exception as e:
            print(f"[ERROR] Failed to modify data: {e}")


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

class FpjStatus:
    def __init__(self) -> None:
        self.fpjson = FpjJson()

    def is_kakawate_enough(self) -> bool:
        weight = self.fpjson.get_kakawate_weight()
        print(f"[STATUS] KakawateWeight is {weight}g")
        return weight >= 1000

    def is_neem_enough(self) -> bool:
        weight = self.fpjson.get_neem_weight()
        print(f"[STATUS] NeemWeight is {weight}g")
        return weight >= 2000

    def is_molasses_enough(self) -> bool:
        weight = self.fpjson.get_molasses_weight()
        print(f"[STATUS] MolassesWeight is {weight}g")
        return weight >= 4000

    def is_water_enough(self) -> bool:
        weight = self.fpjson.get_water_weight()
        print(f"[STATUS] WaterWeight is {weight}g")
        return weight >= 6000

    def is_ingredients_enough(self) -> bool:
        return (
            self.is_kakawate_enough()
            and self.is_neem_enough()
            and self.is_molasses_enough()
            and self.is_water_enough()
        )

    def batch_done(self) -> bool:
        is_done = self.fpjson.is_already_fermenting()
        print(f"[STATUS] BatchDone is {is_done}")
        return is_done
    
    def is_mixing_done(self) -> bool: 
        return self.fpjson.get_mixing_status()


# Main execution
if __name__ == "__main__":
    try:
        fpj_json = FpjStatus()

        # Example of setting and getting slider position
        fpj_json.set_slider_position(1500)
        latest_position = fpj_json.get_slider_position()
        print(f"Latest position: {latest_position}")

        # Reset weights
        #fpj_json.reset_weights()

        # Example of setting mixer position and checking mixing status
        fpj_json.set_mixer_position(100)
        fpj_json.set_mixing_status(True)

        # Check and display status
        fpj_status = FpjStatus()
        fpj_status.check_status(fpj_json)
        fpj_status.display_status()

    except KeyboardInterrupt:
        print("\n[EXIT] Program interrupted by user.")
