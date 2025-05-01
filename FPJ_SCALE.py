import serial
import time
import math

class Scale:
    def __init__(self, port: str, baud_rate: int = 115200) -> None:
        self.serial_connection = serial.Serial(port, baud_rate)
        time.sleep(2)  # Wait for the connection to be established

    def trigger_tare(self) -> bool:
        """
        Sends 'TARE' to the ESP32 and waits for the 'TARED' response.
        Returns True if tare is successful, False otherwise.
        """
        self.serial_connection.write(b"TARE\n")
        print("Sent TARE command to ESP32.")
        
        # Wait for the "TARED" response
        while True:
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                print("ESP32 Response:", response)
                if response == "TARED":
                    return True
        return False  # If the "TARED" response is never received, return False

    def get_weight(self) -> int:
        """
        Sends 'WEIGHT' to the ESP32 and waits for the weight value (format: 'WT,value').
        Returns the rounded weight value (rounded to nearest 10) as an integer.
        """
        self.serial_connection.write(b"WEIGHT\n")
        print("Sent WEIGHT command to ESP32.")
        
        # Wait for the weight response (e.g., "WT, value")
        while True:
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.readline().decode('utf-8').strip()
                
                if response.startswith("WT,"):
                    # Extract the weight value from the response
                    weight_value = response.split(",")[1]
                    try:
                        weight = float(weight_value)
                        
                        # Round to the nearest 10 and return as an integer
                        rounded_weight = math.ceil(weight / 10.0) * 10
                        corrected_weight = rounded_weight / 2
                        return int(corrected_weight)
                    except ValueError:
                        print("Error: Invalid weight value received.")
                        return 0  # Return 0 if the weight value is invalid

    def close(self) -> None:
        """Close the serial connection."""
        self.serial_connection.close()


# Usage example:
if __name__ == "__main__":
    # Replace with the correct port for your ESP32
    serial_port = '/dev/ttyUSB0'  
    
    # Create an instance of the Scale class
    scale = Scale(serial_port)
    
    # Trigger tare and wait for response
    if scale.trigger_tare():
        print("Tare successful.")
    else:
        print("Tare failed.")
    
    # Continuously get weight every 1 second
    try:
        while True:
            weight = scale.get_weight()
            print(f"Rounded Weight: {weight} g")
            time.sleep(1)  # Wait for 1 second before getting the weight again
    except KeyboardInterrupt:
        print("\nProgram terminated.")
    finally:
        # Close the serial connection
        scale.close()
