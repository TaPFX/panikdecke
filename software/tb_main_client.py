
from PanikDeckeClient import PanikDeckeClient

import time

clientInst = PanikDeckeClient()

clientInst.speed(5) # degree per second

time.sleep(3)

clientInst.stop_at(11) # degree

time.sleep(2)

clientInst.shutdown()
