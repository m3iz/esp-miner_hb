import logging
import time
from smbus2 import SMBus


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

        self.i2c_bus = self.config['i2c_bus']
        self.i2c_multiplexor_addr = self.config['i2c_multiplexor_addr']
        self.i2c_temperature_sensor_channel = self.config['i2c_temperature_sensor_channel']
        self.temp_ambient_addr = self.config['temp_ambient_addr']
        self.temp_dcdc_addr = self.config['temp_dcdc_addr']
        self.temp_hashboard_1_addr = self.config['temp_hashboard_1_addr']
        self.temp_hashboard_2_addr = self.config['temp_hashboard_2_addr']
        self.temp_hashboard_3_addr = self.config['temp_hashboard_3_addr']
        self.temp_hashboard_4_addr = self.config['temp_hashboard_4_addr']

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

    def select_i2c_channel(self, channel):
        with SMBus(self.i2c_bus) as bus:
            bus.write_byte(self.i2c_multiplexor_addr, 1 << channel)

    def read_temp(self, channel, addr):
        try:
            self.select_i2c_channel(channel)
            with SMBus(self.i2c_bus) as bus:
                data = bus.read_i2c_block_data(addr, 0x00, 2)
                temp_raw = (data[0] << 8) | data[1]
                temperature = temp_raw / 256.0
                return round(temperature, 2)
        except Exception as e:
            print(f"Error on channel {channel}: {e}")
            return None

    def read_temperature_and_voltage(self):
        return {
            "ambient_temp": self.read_temp(self.i2c_temperature_sensor_channel, self.temp_ambient_addr),
            "dcdc_temp": self.read_temp(self.i2c_temperature_sensor_channel, self.temp_dcdc_addr),
            "temp": [
                self.read_temp(self.i2c_temperature_sensor_channel, self.temp_hashboard_1_addr),
                self.read_temp(self.i2c_temperature_sensor_channel, self.temp_hashboard_2_addr),
                self.read_temp(self.i2c_temperature_sensor_channel, self.temp_hashboard_3_addr),
                self.read_temp(self.i2c_temperature_sensor_channel, self.temp_hashboard_4_addr),
            ],
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
