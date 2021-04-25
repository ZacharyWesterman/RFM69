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
		self.outgoing = {}
		self.incoming = {}

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
		self.radio.send(255, '', True) # Ping all modules, and request ACK
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
		self.radio.send(255) # Ping with new ID, don't need an ACK

		# Be ready to receive
		self.radio.receiveBegin()

	def logout(self):
		# TODO: let other nodes know you're not there anymore
		self.radio.shutdown()

	#handle messages
	def handle(self):
		if self.radio.receiveDone():
			#Cache last message from radio
			senderid = self.radio.SENDERID
			self.incoming[senderid] = self.radio.DATA

			if self.radio.ACKRequested():
				self.radio.sendACK(senderid) #Send ACK if requested
				print("sent ACK")

			if senderid == 0: # New node requesting my ID
				pass
				# self.radio.send(senderid)
			elif senderid not in self.nodes: #Update list of nodes
				self.nodes.append(senderid)
				self.nodes.sort()
				print(f"Node {senderid} has joined the network.")


			#We've received and responded to a message, now wait for another
			self.radio.receiveBegin()
		time.sleep(TOSLEEP)

	def send(self, dest, msg):
		self.radio.send(dest, msg, True) # Send message to a specific module, request ACK

		#wait 1 second for ACK
		timedOut = 0
		while timedOut < 2:
			#We got a response, log the node ID
			if self.radio.ACKReceived(dest):
				print("Ack received")
				return True

			timedOut += TOSLEEP
			time.sleep(TOSLEEP)

		print("Message not sent.")
		return False



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
		print("sending... ", end='')
		if net.send(1, "hello"):
			print("ack received")
		else:
			print("no ack")

print("shutting down")
net.logout()
