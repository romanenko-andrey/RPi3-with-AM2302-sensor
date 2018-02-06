#config.txt
#core_freq=258
#enable_uart=1

import serial
from time import sleep

port = serial.Serial("/dev/ttyS0", baudrate=2400, stopbits=2, timeout=1)
req = bytearray([1, 4, 3, 0xE8, 0, 1, 0xB1, 0xBA])

req2 = bytearray([1,1,1,1,2,2,2,2])
#'hello'.encode('utf-8')

while True:
    port.write(req)
    rcv = port.read(7)
    print(list(rcv))
    sleep(1)


