#!/usr/bin/env python3

import RFM69
from RFM69registers import *
import datetime
import time

# Handle exit signal gracefully
import signal
import sys

TIMEOUT=3
TOSLEEP=0.01

# Initialize radio
print("Initializing radio module...")
radio = RFM69.RFM69(RF69_915MHZ, 0, 1, True)
radio.readAllRegs()
radio.rcCalibration()
radio.setHighPower(True)
radio.encrypt("3141592653589793")

print("Checking for other modules on the network...")
radio.send(255)
radio.receiveBegin()
timedOut = 0
NET_NODES = []
NODE = 1
while timedOut < TIMEOUT:
	if radio.receiveDone():
		print(f"Response from node {radio.SENDERID}.")
		NET_NODES.append(radio.SENDERID)
		radio.receiveBegin()

	timedOut+=TOSLEEP
	time.sleep(TOSLEEP)

print(NET_NODES)

print("shutting down")
radio.shutdown()
