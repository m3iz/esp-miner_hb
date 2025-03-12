import os
import threading
import time
import serial # type: ignore
import OPi.GPIO as GPIO
from orangepi import zero2
from piaxe.bm1362 import BM1362, CMD_READ, GROUP_ALL, TYPE_CMD
import logging
import atexit

debug = True

nrst_pin = 15
sdn_pin = 11

chip_count = 48
chip_frequency = 300

receive_thread = None
_read_index = 0
_write_index = 0
_buffer = bytearray([0] * 64)

serial_lock = threading.Lock()
serial_port = serial.Serial(
    port="/dev/ttyUSB0",  # For ASIC serial communication use usbmodemb310cc523
    baudrate=115200,    # Set baud rate to 115200
    bytesize=serial.EIGHTBITS,     # Number of data bits
    parity=serial.PARITY_NONE,     # No parity
    stopbits=serial.STOPBITS_ONE,  # Number of stop bits
    timeout=1                      # Set a read timeout
)

def _serial_tx_func(data):
    with serial_lock:
        total_sent = 0
        while total_sent < len(data):
            sent = serial_port.write(data[total_sent:])
            if sent == 0:
                raise RuntimeError("Serial connection broken")
            total_sent += sent
        if debug:
            logging.info("-> %s", bytearray(data).hex())

def _serial_rx_func(size, timeout_ms):
    serial_port.timeout = timeout_ms / 1000.0

    data = serial_port.read(size)
    bytes_read = len(data)

    if debug and bytes_read > 0:
        logging.info("serial_rx: %d", bytes_read)
        logging.info("<- %s", data.hex())

    return data if bytes_read > 0 else None

def reset_func():
    GPIO.output(nrst_pin, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(nrst_pin, GPIO.HIGH)
    time.sleep(0.5)

def _receive_thread():
    logging.info('receiving thread started ...')
    mask_nonce = 0x00000000
    mask_version = 0x00000000

    global _buffer, _write_index, _read_index

    while True:
        byte = _serial_rx_func(11, 100)

        if not byte:
            continue

        logging.info('got some bytes')

        for i in range(0, len(byte)):
            _buffer[_write_index % 64] = byte[i]
            _write_index += 1

        if _write_index - _read_index >= 11 and _buffer[_read_index % 64] == 0xaa and _buffer[(_read_index + 1) % 64] == 0x55:
            data = bytearray([0] * 11)
            for i in range(0, 11):
                data[i] = _buffer[_read_index % 64]
                _read_index += 1

            logging.warning(data)

    logging.info('receiving thread ended ...')

def main():
    # Setup GPIO
    GPIO.setmode(zero2.BOARD)  # Use Physical pin numbering

    print(f'nrst_pin = {nrst_pin}, sdn_pin={sdn_pin}')
    GPIO.setup(sdn_pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(nrst_pin, GPIO.OUT, initial=GPIO.HIGH)

    GPIO.output(sdn_pin, GPIO.HIGH)
    GPIO.output(nrst_pin, GPIO.HIGH)

    print('Wait for init')
    time.sleep(3)

    print('Initing chips')

    asics = BM1362()

    asics.ll_init(
        _serial_tx_func,
        _serial_rx_func,
        reset_func
    )

    max_retries = 5  # Maximum number of attempts

    # currently the qaxe+ needs this loop :see-no-evil:
    for attempt in range(max_retries):
        print(f'Counting chips. Attempt {attempt}')
        try:
            chip_counter = asics.init(chip_frequency, chip_count, None)
            print("Initialization successful.")
            break
        except Exception as e:
            logging.error("Attempt %d: Not enough chips found: %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before the next attempt
            else:
                logging.error("Max retries reached. Initialization failed.")
                raise

    # set dificulty here

    print(chip_counter)


    logging.info(f'Starting receive thread...')
    receive_thread = threading.Thread(target=_receive_thread)
    receive_thread.start()

    # logging.info('Requesting hash rate ALL')
    # asics.request_hashrate_all()

    # logging.info('Requesting hash rate')
    # # for id in range(0, chip_counter):
    # logging.info(f'Request hashrate from chip {8 * 2}')
    # asics.request_hashrate(8 * 2)

    logging.info('Requesting nonce offset')
    asics.send(TYPE_CMD | GROUP_ALL | CMD_READ, [0x00, 0x0c])

    while True:
        time.sleep(1)

    GPIO.output(sdn_pin, GPIO.LOW)
    GPIO.output(nrst_pin, GPIO.LOW)



def setup_logging(log_level, log_filename):
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # If a log filename is provided, also log to a file
    if log_filename:
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def sigint_handler(signal_received=None, frame=None):
    print('SIGINT (Ctrl+C) captured, exiting gracefully')
    GPIO.output(sdn_pin, GPIO.LOW)
    GPIO.output(nrst_pin, GPIO.LOW)
    os._exit(0)

if __name__ == '__main__':

    log_level = logging.DEBUG

    setup_logging(log_level, None)
    atexit.register(sigint_handler)
    main()