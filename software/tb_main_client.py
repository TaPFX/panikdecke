
from PanikDeckeClient import PanikDeckeClient

import time
import os, socket

Raspi_IP = "192.168.178.90"

clientInst = PanikDeckeClient(ip=Raspi_IP)
# or on localhost:
#clientInst = PanikDeckeClient()

clientInst.speed(200) # degree per second

time.sleep(10)

#clientInst.speed(0.4) # degree per second

#time.sleep(5)

#clientInst.stop_at(6.5) # degree

#time.sleep(15)

clientInst.shutdown()
