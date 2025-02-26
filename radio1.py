#!/usr/bin/env python3

import RFM69
from RFM69registers import *
import datetime
import time

NODE=1
NET=1
KEY="1234567891011121"
TIMEOUT=3
TOSLEEP=0.1

radio = RFM69.RFM69(RF69_915MHZ, NODE, NET, True)
print("class initialized")

print("reading all registers")
results = radio.readAllRegs()
#for result in results:
#    print(result)

print("Performing rcCalibration")
radio.rcCalibration()

print("setting high power")
radio.setHighPower(True)

print("Checking temperature")
print(radio.readTemperature(0))

print("setting encryption")
radio.encrypt(KEY)

print("starting loop...")
sequence = 0
while True:

    msg = "I'm radio %d: %d" % (NODE, sequence)
    sequence = sequence + 1

    print("tx to radio 2: " + msg)
    if radio.sendWithRetry(2, msg, 3, 20):
        print("ack recieved")

    print("start recv...")
    radio.receiveBegin()
    timedOut=0
    while not radio.receiveDone():
        timedOut+=TOSLEEP
        time.sleep(TOSLEEP)
        if timedOut > TIMEOUT:
            print("timed out waiting for recv")
            break

    print("end recv...")
    print(" *** %s from %s RSSI:%s" % ("".join([chr(letter) for letter in radio.DATA]), radio.SENDERID, radio.RSSI))

    if radio.ACKRequested():
        print("sending ack...")
        radio.sendACK()
    else:
        print("ack not requested...")

print("shutting down")
radio.shutdown()
