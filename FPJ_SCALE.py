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
        Clears serial buffer, then reads 5 weight values from the ESP32 (format: 'WT,value'),
        prints each, averages them, and returns as int.
        """
        self.serial_connection.reset_input_buffer()  # 🔄 Clear any old data in the buffer
        weights = []
        print("Collecting 5 weight readings...")

        while len(weights) < 5:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line.startswith("WT,"):
                    try:
                        value = float(line.split(",")[1])
                        weights.append(value)
                        print(f"Reading {len(weights)}: {value:.2f}g")
                    except ValueError:
                        print("Skipped invalid reading:", line)

        avg_weight = sum(weights) / len(weights)
        print(f"Averaged: {avg_weight:.2f}g")

        return int(avg_weight)



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
