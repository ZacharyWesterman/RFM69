#!/usr/bin/env python3

import RFM69
from RFM69registers import *
import datetime
import time

# Handle exit signal gracefully
import signal
import sys

TOSLEEP=0.01
NETWORK=1
NODE = 0 #ID 0 is reserved for new nodes
ENCRYPTION_KEY = "3141592653589793"

class network(object):
	def __init__(self, network = 1):
		self.network = network
		self.nodes = []
		self.name = ""

	def init_radio(self, node, network):
		global ENCRYPTION_KEY
		self.radio = RFM69.RFM69(RF69_915MHZ, node, network, True)
		self.radio.readAllRegs()
		self.radio.rcCalibration()
		self.radio.setHighPower(True)
		self.radio.encrypt(ENCRYPTION_KEY)

	def login(self, name = "unkn"):
		global TOSLEEP
		self.init_radio(0, self.network)
		self.radio.send(255) # Ping all modules. Since we're node 0 they'll ping us back
		self.radio.receiveBegin()
		timedOut = 0
		self.nodes = []
		while timedOut < 1:
			#We got a response, log the node ID
			if self.radio.receiveDone():
				self.nodes.append(self.radio.SENDERID)
				self.radio.receiveBegin()

			timedOut += TOSLEEP
			time.sleep(TOSLEEP)
		self.nodes.sort()

		# Find the first free ID, and take that.
		newID = 1
		for i in self.nodes:
			if i > newID: break
			newID += 1

		# Throw exception if network is over-saturated
		if newID >= 255:
			self.radio.shutdown()
			raise f"Too many nodes on network {self.network}!"

		# Reinitialize radio module and broadcast new ID
		self.radio.shutdown()
		self.init_radio(newID, self.network)
		self.radio.send(255)

		# Be ready to receive
		self.radio.receiveBegin()

	def logout(self):
		# TODO: let other nodes know you're not there anymore
		self.radio.shutdown()

	#handle messages
	def handle(self):
		if self.radio.receiveDone():
			#get info from radio
			senderid = self.radio.SENDERID

			#Send ACK ASAP, we got the message
			if self.radio.ACKRequested():
				self.radio.sendACK(senderid)
				print(f"Ack sent to {senderid}")

			#Update list of nodes
			if (senderid != 0) and (senderid not in self.nodes):
				self.nodes.append(senderid)
				self.nodes.sort()
				print(f"Node {senderid} has joined the network.")

			#We've received and responded to a message, now wait for another
			self.radio.receiveBegin()
		time.sleep(TOSLEEP)


print("Connecting to network...")
net = network()
net.login()
print(f"Connected with ID {net.radio.address}")

# Exit gracefully if SIGINT
def signal_handler(sig, frame):
	print("Captured SIGINT, shutting down")
	net.logout()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
	net.handle()
	if net.radio.address != 1:
		if net.radio.sendWithRetry(1, "hello"):
			print("ack received")
		else:
			print("no ack")

print("shutting down")
net.logout()
