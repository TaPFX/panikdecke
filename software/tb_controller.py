# testbench for the controller so we have not to wait
# and can debug the controller without the server/client
# and waiting time

from Controller import Controller
import numpy as np

from matplotlib import pyplot as plt

t_end = 60 #s
t_sum = 0

ctrlInst = Controller()
ctrlInst.dbg = True

speed = 0.5
stop_at = None

while(t_sum < t_end):
    t_sum += ctrlInst.update(speed, stop_at)

speed = 1
t_sum = 0

while(t_sum < t_end):
    t_sum += ctrlInst.update(speed, stop_at)

stop_at = 30
t_sum = 0

while(t_sum < t_end):
    t_sum += ctrlInst.update(speed, stop_at)

ctrlInst.dbg_plot()


