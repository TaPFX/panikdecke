
from PanikDeckeClient import PanikDeckeClient

import time
import os, socket

def sleep(wait_time):
    try:
        time.sleep(wait_time)

    except KeyboardInterrupt:
        # Programm beenden, wenn Strg+C gedrückt wird
        pass

Raspi_IP = "192.168.178.90"

clientInst = PanikDeckeClient(ip=Raspi_IP)
# or on localhost:
#clientInst = PanikDeckeClient()

clientInst.speed(180) # degree per second
sleep(20)
clientInst.stop_at(0) # degree
sleep(20)
clientInst.speed(180) # degree per second
sleep(20)
clientInst.stop_at(0) # degree
sleep(20)
clientInst.shutdown()
