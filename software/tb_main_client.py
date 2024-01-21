
from PanikDeckeClient import PanikDeckeClient

import time
import os

test_on_pc = False # set to true if talk to localhost server

if(not test_on_pc):
    clientInst = PanikDeckeClient(ip='Panikdecke')
else:
    clientInst = PanikDeckeClient()

#clientInst.speed(0.2) # degree per second

#time.sleep(5)

#clientInst.speed(0.4) # degree per second

#time.sleep(5)

#clientInst.stop_at(6.5) # degree

#time.sleep(15)

clientInst.shutdown()
