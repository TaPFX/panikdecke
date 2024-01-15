
from PanikDeckeClient import PanikDeckeClient

import time

clientInst = PanikDeckeClient()

clientInst.speed(0.2) # degree per second

time.sleep(5)

clientInst.speed(0.4) # degree per second

time.sleep(5)

clientInst.stop_at(6.5) # degree

time.sleep(15)

clientInst.shutdown()
