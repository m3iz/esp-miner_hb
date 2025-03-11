import logging
import time


try:
    import serial # type: ignore
    import OPi.GPIO as GPIO
    from orangepi import zero2
except:
    print('Unable to import something')
    pass

# Setup GPIO
GPIO.setmode(zero2.BOARD)  # Use Physical pin numbering

nrst_pin = 15
sdn_pin = 11
print(f'nrst_pin = {nrst_pin}, sdn_pin={sdn_pin}')
GPIO.setup(sdn_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(nrst_pin, GPIO.OUT, initial=GPIO.HIGH)

nrst_value = False
sdn_value = True
while True:
    print(nrst_value, sdn_value)
    GPIO.output(nrst_pin, nrst_value)
    GPIO.output(sdn_pin, sdn_value)
    nrst_value = not nrst_value
    sdn_value = not sdn_value
    time.sleep(1)


