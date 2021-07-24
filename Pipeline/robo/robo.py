#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import zmq
import socket as s

HOST = "robo"
#address = os.environ.get('SERVER_CONNECT_URI')
PORTC = "50012"
ip= s.gethostbyname(HOST)

pC = "tcp://" + ip + ":" + PORTC
context = zmq.Context()
# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind(pC)

print("Fiz o bind")
# Wait for start of batch
s = receiver.recv()
# Start our clock now
tstart = time.time()
# Process 100 confirmations
for task_nbr in range(100):
    s = receiver.recv()
    if task_nbr % 10 == 0:
        sys.stdout.write(':')
    else:
        sys.stdout.write('.')
    sys.stdout.flush()
# Calculate and report duration of batch
tend = time.time()
print("\nTotal elapsed time: %d msec" % ((tend-tstart)*1000))