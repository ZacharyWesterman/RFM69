#!/usr/bin/env python3

import RFM69
from RFM69registers import *
import datetime
import time

# Handle exit signal gracefully
import signal
import sys

TIMEOUT=1
TOSLEEP=0.01
NETWORK=1
NODE = 1

# Initialize radio
print("Initializing radio module...")
radio = RFM69.RFM69(RF69_915MHZ, NODE, NETWORK, True)
radio.readAllRegs()
radio.rcCalibration()
radio.setHighPower(True)
radio.encrypt("3141592653589793")

# Exit gracefully if SIGINT
def signal_handler(sig, frame):
	print("Captured SIGINT, shutting down")
	radio.shutdown()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

print("Waiting for new nodes to identify themselves...")
radio.receiveBegin()
while True:
	if radio.receiveDone():
		if radio.SENDERID == 0:
			print(f"Message received from node {radio.SENDERID}, responding with a ping.")
			radio.send(radio.SENDERID) #don't need any ACK

		#We've received and responded to a message, now wait for another
		radio.receiveBegin()
	time.sleep(TOSLEEP)

print("shutting down")
radio.shutdown()
