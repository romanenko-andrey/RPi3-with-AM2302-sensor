print "hello form script #4"

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

pin = 31
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

print "Pin 31 status = ", GPIO.input(pin)