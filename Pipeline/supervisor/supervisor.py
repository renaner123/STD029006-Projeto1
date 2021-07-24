#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import zmq
import socket as s
#PUB para broadcast
#SUB pra receber broadcast
#address = os.environ.get('SERVER_CONNECT_URI')

HOSTD = "auditor"
HOSTC = "robo"
PORTD = "50011"
PORTC = "50012"
pD = "tcp://" + s.gethostbyname(HOSTD) + ":" + PORTD
pC = "tcp://" + s.gethostbyname(HOSTC) + ":" + PORTC
context = zmq.Context()
# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect(pD)
# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect(pC)
print("Worker ready...")
# Process tasks forever
while True:
    s = receiver.recv()
    # Simple progress indicator for the viewer
    sys.stdout.write('.')
    sys.stdout.flush()
    # Do the work
    time.sleep(int(s)*0.001)
    # Send results to coletor
    sender.send(b'')