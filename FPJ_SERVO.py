#!/usr/bin/env python3

from gpiozero import AngularServo
from time import sleep


class ServoController:
    def __init__(self, gpio_pin=18, min_pulse=0.0005, max_pulse=0.0025):
        self.servo = AngularServo(
            gpio_pin,
            min_pulse_width=min_pulse,
            max_pulse_width=max_pulse
        )

    def move_to(self, angle, wait=0.5):
        """Move servo to specified angle and hold briefly (optional)"""
        self.servo.angle = angle
        sleep(wait)  # Give it time to reach position

    def open(self):
        """Open by moving to 0 degrees"""
        print("Opening...")
        sleep(1)
        self.move_to(90)

    def close(self):
        """Close by moving to -45 degrees"""
        print("Closing...")
        sleep(1)
        self.move_to(0)

if __name__ == "__main__":
    servo = ServoController()

    try:
        while True:
            servo.open()
            sleep(1)
            servo.close()
            sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user.")
        
