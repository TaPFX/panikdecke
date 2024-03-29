
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime

import os

if(os.name != 'nt'): # can be tested on windows shell without RPi
    IS_RASPI = True
    import RPi.GPIO as GPIO
    # GPIO-Pin-Nummer
    sw_gpio_pin = 17
    sw_gpio_dir_pin = 27
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sw_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(sw_gpio_dir_pin, GPIO.OUT)

# wait x ticks without changing polarity, then accept event
SW_DEBOUNCE_TICKS = 5

# Gear Ratio
GEAR_TEETH_SMALL = 18
GEAR_TEETH_LARGE = 56
#GEAR_TEETH_LARGE = 180 # final
GEAR_TEETH_RATIO = GEAR_TEETH_LARGE / GEAR_TEETH_SMALL

# Offset calibration of the switch in degree
SWITCH_OFFSET_DEG = 5
#SWITCH_OFFSET_DEG = ? # for final

STEP_PER_REVOLUTION = round(GEAR_TEETH_RATIO*800) # set this by the 3 switches
# error is small as we reset the position by the switches

LSB_ANGLE = 360 / STEP_PER_REVOLUTION
SPEED_THRESHOLD = LSB_ANGLE / 1 # 0.9° per second is the lower boundary
MAX_ACCELERATION = 0.3 # 1° per second**2, TODO adjust
MAX_SECONDS_PER_TURNAROUND = 5.9 # only for safety checks, 360 / 5.9 = 61 deg per second so 60 is max
# choose a slightly below value

def get_datetime_str():
    return datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

class Controller:
    def __init__(self) -> None:

        self.curr_pos = 0
        self.curr_speed = 0
        self.stop_at_old = None
        self.speed_ramp_down_array = None

        self.sw_offset = SWITCH_OFFSET_DEG

        self.switch_state = self.get_switch_state()
        self.out_en = False

        self.PANIC_OFF = False

        self.dbg = False
        self.dbg_speed = []
        self.dbg_pos = []
        self.dbg_trigger = []
        self.dbg_curr_speed = []

        self.switch_lock = 0 # switch debouncer

    def update(self, speed=0, stop_at=None):
        # checks if a switch activity was performed
        # trigger frequency

        if(stop_at is None):
            self.stop_at_old = stop_at
            self.speed_ramp_down_array = None

            speed_new = self.limit_acc(speed)
            #speed_new = speed

        else:
            stop_at = stop_at % 360 # accepts all input angles

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
                    self.speed_ramp_down_array = list(np.insert(self.speed_ramp_down_array, 0, np.ones(round(STEP_PER_REVOLUTION - delta_corr))*self.curr_speed))
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
            self.switch_lock = 0
        else:
            self.switch_lock +=1 # wait SW_DEBOUNCE_TICKS ticks for stable inputs
            if(self.switch_lock > SW_DEBOUNCE_TICKS):
                self.switch_state = new_state
                if(new_state == True):
                    self.curr_pos = 0 + self.sw_offset
                    self.print_out("Switch detecting 0°.")
                else:
                    self.curr_pos = 180 + self.sw_offset
                    self.print_out("Switch detecting 180°.")
                
    def get_switch_state(self):
        if(os.name != 'nt'):
            if(GPIO.input(sw_gpio_pin) == GPIO.LOW):
                return True
            else:
                return False
        else:
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
            if(os.name != 'nt'):
                GPIO.output(sw_gpio_dir_pin, 0)
        elif(speed < 0):
            direction = False
            if(os.name != 'nt'):
                GPIO.output(sw_gpio_dir_pin, 1)
        
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
