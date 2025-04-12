import logging
import time


try:
    import serial # type: ignore
    import OPi.GPIO as GPIO
    from orangepi import zero2
except:
    print('Unable to import something')
    pass

from . import board

class EmberoneHardware(board.Board):

    def __init__(self, config):
        # Setup GPIO
        GPIO.setmode(zero2.BOARD)  # Use Physical pin numbering

        self.config = config
        self.nrst_pin = self.config['nrst_pin']
        self.sdn_pin = self.config['sdn_pin']
        logging.debug(f'nrst_pin = {self.nrst_pin}, sdn_pin={self.sdn_pin}')
        GPIO.setup(self.sdn_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.nrst_pin, GPIO.OUT, initial=GPIO.HIGH)

        # Initialize serial communication
        self._serial_port_asic = serial.Serial(
            port=self.config['serial_port_asic'],  # For ASIC serial communication use usbmodemb310cc523
            baudrate=115200,    # Set baud rate to 115200
            bytesize=serial.EIGHTBITS,     # Number of data bits
            parity=serial.PARITY_NONE,     # No parity
            stopbits=serial.STOPBITS_ONE,  # Number of stop bits
            timeout=1                      # Set a read timeout
        )

        GPIO.output(self.sdn_pin, GPIO.HIGH)
        GPIO.output(self.nrst_pin, GPIO.HIGH)

        logging.debug('Wait for init...')
        time.sleep(10)

    def gpio_set(self, pin, value):
        # Construct the command to set the GPIO pin
        print(f'gpio_set {pin}={value}')

    def set_fan_speed(self, channel, percent):
        pass

    def read_temperature_and_voltage(self):
        return {
            "temp": [None, None, None, None],
            "voltage": [None, None, None, None],
        }

    def set_led(self, state):
        pass

    def reset_func(self):
        GPIO.output(self.nrst_pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(self.nrst_pin, GPIO.HIGH)
        time.sleep(0.5)

    def shutdown(self):
        # disable buck converter
        logging.info("shutdown miner ...")
        GPIO.output(self.sdn_pin, False)

    def serial_port(self):
        return self._serial_port_asic
