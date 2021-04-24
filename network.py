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
NODE = 0 #ID 0 is reserved for new nodes

def init_radio(node, network):
	radio = RFM69.RFM69(RF69_915MHZ, node, network, True)
	radio.readAllRegs()
	radio.rcCalibration()
	radio.setHighPower(True)
	radio.encrypt("3141592653589793")
	return radio

# Initialize radio
print("Initializing radio module...")
radio = init_radio(NODE, NETWORK)

# Exit gracefully if SIGINT
def signal_handler(sig, frame):
	print("Captured SIGINT, shutting down")
	radio.shutdown()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

print(f"Checking for other modules on network {NETWORK}...")
radio.send(255) # Ping all modules. Since we're node 0 they'll ping us back
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

if not len(NET_NODES):
	print(f"No nodes found on network {NETWORK}.")
else:
	print(f"Found existing nodes: {NET_NODES}")

for i in NET_NODES:
	if i >= NODE: NODE = i + 1

if NODE >= 255:
	print(f"Too many nodes on network {NETWORK}! Shutting down.")
	radio.shutdown()
	sys.exit(0)

print("Reinitializing radio module...")
radio.shutdown()
radio = init_radio(NODE, NETWORK)
print(f"Broadcasting this node's ID ({NODE})")
radio.send(255)

# Just wait for other nodes to join
radio.receiveBegin()
while True:
	if radio.receiveDone():
		print(f"Message received from node {radio.SENDERID}.")
		if radio.SENDERID == 0:
			radio.send(radio.SENDERID) #don't need any ACK
		elif radio.SENDERID not in NET_NODES:
			NET_NODES.append(radio.SENDERID)
			print(f"Node {radio.SENDERID} has joined the network.")

		#We've received and responded to a message, now wait for another
		radio.receiveBegin()
	time.sleep(TOSLEEP)

print("shutting down")
radio.shutdown()
