# testbench for the controller so we have not to wait
# and can debug the controller without the server/client
# and waiting time

from Controller import Controller
import numpy as np

from matplotlib import pyplot as plt

VERIF_SPEED_DELTA_THRES = 0.01
VERIF_POS_DELTA_THRES = 1 # auf 1° genau

ctrlInst = Controller()
ctrlInst.dbg = True
ctrlInst.sw_offset = 0 # remove offset for verification

def run_simulation(speed, stop_at, t_end):
    t_sum = 0
    while(t_sum < t_end):
        tmp, _ = ctrlInst.update(speed, stop_at)
        t_sum += tmp
    if ( stop_at is None and abs(ctrlInst.curr_speed - speed ) > VERIF_SPEED_DELTA_THRES):
        raise Exception("Speed not correctly verified")
    if( stop_at is not None and abs(ctrlInst.curr_pos - stop_at) > VERIF_POS_DELTA_THRES):
        if( abs(ctrlInst.curr_pos - stop_at - 360) > VERIF_POS_DELTA_THRES):
            raise Exception("Position not correctly verified")

# test speed
run_simulation(speed = 180, stop_at = None, t_end = 60)

# test stop_at
run_simulation(speed = 30, stop_at = 0, t_end = 60)

# increase speed again
run_simulation(speed = 180, stop_at = None, t_end = 30)

# test stop_at with one more turnaround
if(ctrlInst.curr_speed > 0):
    stop_at = ctrlInst.curr_pos + 0.1
elif(ctrlInst.curr_speed < 0):
    stop_at = ctrlInst.curr_pos - 0.1

run_simulation(speed = 30, stop_at = stop_at, t_end = 120)
print(f"Curr_pos: {ctrlInst.curr_pos}")

if(ctrlInst.PANIC_OFF):
    raise Exception("PANIC OFF WAS TRIGGERED")

ctrlInst.dbg_plot()


