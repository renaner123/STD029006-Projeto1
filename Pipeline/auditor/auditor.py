#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zmq, time, random
import socket as s

try:
    raw_input
except NameError:
# Python 3
    raw_input = input

HOST = "auditor"
HOSTC= "supervisor"
PORTD = "50011"
PORTC = "50012"

#address = os.environ.get('SERVER_CONNECT_URI')
pD = "tcp://" + s.gethostbyname(HOST) + ":" + PORTD
pC = "tcp://" + s.gethostbyname(HOSTC) + ":" + PORTC

context = zmq.Context()
# socket para distribuir tarefas
distribuidor = context.socket(zmq.PUSH)
distribuidor.bind(pD)
# socket para coletar respostas
coletor = context.socket(zmq.PUSH)
coletor.connect(pC)
print("Press Enter when the workers are ready: ")
_ = raw_input()
print("Sending tasks to workers...")
# The first message is "0" and signals start of batch
coletor.send(b'0')
# Initialize random number generator
random.seed()
# Send 100 tasks
total_msec = 0

for task_nbr in range(100):
    # Random workload from 1 to 100 msecs
    workload = random.randint(1, 100)
    total_msec += workload
    distribuidor.send_string(u'%i' % workload)
print("Total expected cost: %s msec" % total_msec)
# Give 0MQ time to deliver
time.sleep(1)
