
from PanikDeckeClient import PanikDeckeClient

import time

clientInst = PanikDeckeClient()

clientInst.speed(1) # degree per second

time.sleep(5)

clientInst.speed(0.5) # degree per second

time.sleep(5)

clientInst.stop()

#clientInst.stop_at(11) # degree

#time.sleep(2)

clientInst.shutdown()
