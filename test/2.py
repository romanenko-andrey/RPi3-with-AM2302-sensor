print "hello form script #2"
import sys
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
print 'time = ', float(sys.argv[1])

import RPi.GPIO as GPIO
GPIO.setwarnings(False)

pin = 40
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

print "Pin 40 status = ", GPIO.input(pin)