print "hello form script #3"

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

GPIO.output(pin, GPIO.LOW)
