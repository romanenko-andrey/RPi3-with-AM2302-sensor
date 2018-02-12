print "hello form script #4"

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

print "Pin 40 status = ", GPIO.input(pin)