import RPi.GPIO as GPIO
import time

pin = 29
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

for i in range(0, 5):
	GPIO.output(pin, GPIO.HIGH)
	time.sleep(2)
	GPIO.output(pin, GPIO.LOW)
	time.sleep(1)

GPIO.cleanup()