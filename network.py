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
NODE = 2 #ID 0 is reserved for new nodes

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

print(f"Checking for other modules on network {NETWORK}...")
radio.send(1) # Ping all modules. Since we're node 0 they'll ping us back
radio.receiveBegin()
timedOut = 0
NET_NODES = []
NODE = 1
while timedOut < TIMEOUT:
	if radio.receiveDone():
		print(f"Response from node {radio.SENDERID}.")
		NET_NODES.append(radio.SENDERID)
		if radio.ACKRequested(): radio.sendACK(radio.SENDERID)
		radio.receiveBegin()

	timedOut+=TOSLEEP
	time.sleep(TOSLEEP)

if not len(NET_NODES):
	print(f"No nodes found on network {NETWORK}.")

print("shutting down")
radio.shutdown()
