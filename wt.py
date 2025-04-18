import RPi.GPIO as GPIO
import time

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define pins for HX711
DOUT = 5  # Data output pin (DOUT) connected to GPIO 5
SCK = 6   # Clock pin (PD_SCK) connected to GPIO 6

# Set up GPIO pins
GPIO.setup(DOUT, GPIO.IN)   # DOUT pin as input
GPIO.setup(SCK, GPIO.OUT)   # SCK pin as output

# Function to read data from HX711
def read_hx711():
    count = 0
    # Wait for the DOUT pin to go low (ready to send data)
    while GPIO.input(DOUT) == 1:
        pass

    # Read 24 bits of data
    for i in range(24):
        # Pulse the clock pin to read the data
        GPIO.output(SCK, GPIO.HIGH)
        count = count << 1
        if GPIO.input(DOUT) == GPIO.HIGH:
            count += 1
        GPIO.output(SCK, GPIO.LOW)

    # Set the clock pin high for the last bit (to prepare for next read)
    GPIO.output(SCK, GPIO.HIGH)
    GPIO.output(SCK, GPIO.LOW)

    # Convert the 24-bit data to a signed integer (Two's complement)
    if count & 0x800000:  # If the 24th bit is 1, it's a negative number
        count -= 0x1000000  # Convert to negative
    return count

# Read and print data
try:
    while True:
        data = read_hx711()
        print(f"Data: {data}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program.")
    GPIO.cleanup()  # Clean up GPIO settings before exit
