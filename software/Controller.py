
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime

import os

# don't know why, but theory and pratice does not match...
# +/- 10% accuracy in speed
corr_factor = 2.7842

STEP_PER_REVOLUTION = round(800*corr_factor) # set this by the 3 switches
LSB_ANGLE = 360 / STEP_PER_REVOLUTION
SPEED_THRESHOLD = LSB_ANGLE / 1 # 0.9° per second is the lower boundary
MAX_ACCELERATION = 0.1 # 1° per second**2
MAX_SECONDS_PER_TURNAROUND = 1.9/corr_factor

def get_datetime_str():
    return datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

class Controller:
    def __init__(self) -> None:

        self.curr_pos = 0
        self.curr_speed = 0
        self.stop_at_old = None
        self.speed_ramp_down_array = None

        self.switch_state = False
        self.out_en = False

        self.PANIC_OFF = False

        self.dbg = False
        self.dbg_speed = []
        self.dbg_pos = []
        self.dbg_trigger = []
        self.dbg_curr_speed = []

    def update(self, speed=0, stop_at=None):
        # checks if a switch activity was performed
        # trigger frequency
        if(stop_at is None):
            self.stop_at_old = stop_at
            self.speed_ramp_down_array = None

            speed_new = self.limit_acc(speed)
            #speed_new = speed

        else:
            if( stop_at != self.stop_at_old):

                self.stop_at_old = stop_at

                if(self.curr_speed > SPEED_THRESHOLD):
                    self.speed_ramp_down_array = list(np.arange(self.curr_speed, 0, - MAX_ACCELERATION))
                    self.speed_ramp_down_array.append(0)
                    delta_pos   = stop_at - self.curr_pos # positions to go
                elif(self.curr_speed < SPEED_THRESHOLD):
                    self.speed_ramp_down_array = list(np.arange(self.curr_speed, 0, MAX_ACCELERATION))
                    self.speed_ramp_down_array.append(0)
                    delta_pos   = self.curr_pos - stop_at # positions to go
                else:
                    self.print_out("Stop at routine was called, but curr_speed was zero or less than SPEED_THRESHOLD, ignoring stop_at command.")
                    self.speed_ramp_down_array = list(np.array([0]))
                    delta_pos = 0
                
                if(delta_pos < 0):
                    delta_pos += 360

                N = len(self.speed_ramp_down_array)
                braking_to_go = N*LSB_ANGLE

                if(braking_to_go > delta_pos): # cannot brake with MAX_ACCELERATION, do one turnaround more
                    delta_corr = round((braking_to_go - delta_pos)/LSB_ANGLE)
                    self.speed_ramp_down_array = list(np.insert(self.speed_ramp_down_array, 0, np.ones(STEP_PER_REVOLUTION - delta_corr)*self.curr_speed))
                else: # default, run with curr_speed until braking
                    N_to_go = round((delta_pos - braking_to_go)/LSB_ANGLE)
                    self.speed_ramp_down_array = list(np.insert(self.speed_ramp_down_array, 0, np.ones(N_to_go)*self.curr_speed))

                if(np.isclose(self.speed_ramp_down_array[-1], 0)):
                   self.speed_ramp_down_array[-1] = 0
                
                if( self.speed_ramp_down_array[-1] != 0 ):
                    last_acc = self.speed_ramp_down_array[-2] - self.speed_ramp_down_array[-1]
                    if(abs(last_acc) > MAX_ACCELERATION ):
                        self.PANIC_OFF = True
                        self.print_out("Controller: Something went terribly wrong at the stop_at routine, PANIC_OFF is triggered. Sanity check went wrong, consult software engineer.")

            if(self.speed_ramp_down_array != []):
                speed_new = self.speed_ramp_down_array.pop(0)
            else:
                speed_new = 0

        f_trigger = self.trigger_motor(speed_new)
        self.curr_speed = speed_new
        #self.curr_speed = f_3db(f_trigger, self.curr_speed, speed_new) # evtl. rc filter implementieren (Achtung: variable sample frequenz!)

        self.update_pos(f_trigger, stop_at)

        if(self.dbg):
            self.dbg_speed.append(speed)
            self.dbg_curr_speed.append(self.curr_speed)
            self.dbg_pos.append(self.curr_pos)
            self.dbg_trigger.append(1/f_trigger)

        if(f_trigger > STEP_PER_REVOLUTION / MAX_SECONDS_PER_TURNAROUND):
            self.PANIC_OFF = True
            self.out_en = False
            self.print_out("Controller: PANIC_OFF was triggered, MAX SPEED was commanded, but this shall be prevented by software!.")
            self.print_out(f"f_trigger: {f_trigger}, f_max : {STEP_PER_REVOLUTION / MAX_SECONDS_PER_TURNAROUND}")
            f_trigger = 1

        return 1/f_trigger, self.out_en
    
    def limit_acc(self, speed):
        delta_speed = speed - self.curr_speed
        # limit acceleration
        if( abs(delta_speed) > MAX_ACCELERATION):
            delta_speed = MAX_ACCELERATION*np.sign(delta_speed)
        speed_new = self.curr_speed + delta_speed
        return speed_new

    def update_pos(self, f_trigger, stop_at):
        new_state = self.get_switch_state()
        if(self.switch_state == new_state or stop_at is not None):
            self.curr_pos += self.curr_speed*1/f_trigger
            self.curr_pos = self.curr_pos % 360
        else:
            if(new_state == True):
                self.curr_pos = 0
            else:
                self.curr_pos = 180

        self.switch_state = new_state
                
    def get_switch_state(self):
        # TODO read Pin Polarity of switch from Raspi
        return False

    def trigger_motor(self, speed):
        # check if commanded speed is larger than threshold
        if (abs(speed) < SPEED_THRESHOLD):
            self.out_en = False
            return  1/ 1.0 # if speed is nearly zero, do not trigger and wait for 1s and try again
            # this prevents from waiting until infinity

        self.out_en = True
        f_trigger = abs( speed / LSB_ANGLE )

        # TODO trigger motor here and set direction pin polarity
        if(speed > 0):
            direction = True
        elif(speed < 0):
            direction = False
        
        if(not self.PANIC_OFF):
            pass #trigger here
        
        return f_trigger

    def dbg_plot(self):
        if(self.dbg):
            time = np.cumsum(self.dbg_trigger)
            fig, ax = plt.subplots()
            twin1 = ax.twinx()
            ax.plot(time, self.dbg_pos, 'x-', label='pos', color='b')
            ax.set_ylabel("position in °")
            twin1.plot(time, self.dbg_speed, 'x-', label='speed cmd', color='r')
            twin1.plot(time, self.dbg_curr_speed, 'x-', label='speed actual', color='k')
            twin1.set_ylabel("speed in °/s")
            ax.set_xlabel("time in s")
            fig.legend()
            plt.show()

    def print_out(self, str_in):
        str_format = f"{get_datetime_str()}: {str_in}"
        print(str_format)
        with open("Controller.log", "a") as myfile:
            myfile.write(str_format + "\r")
