print "hello form script #1"

import RPi.GPIO as GPIO
GPIO.setwarnings(True)

pin = 31
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

GPIO.output(pin, GPIO.HIGH)

