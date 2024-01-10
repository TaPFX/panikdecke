
import numpy as np


STEP_PER_REVOLUTION = 3200 # set this by the 3 switches
LSB_ANGLE = 360 / STEP_PER_REVOLUTION
SPEED_THRESHOLD = LSB_ANGLE / 1 # 0.9° per second is the lower boundary
MAX_ACCELERATION = 0.05 # 1° per second**2

class Controller:
    def __init__(self) -> None:

        self.curr_pos = 0
        self.curr_speed = 0

        self.switch_state = False

        self.dbg = True
        self.dbg_speed = []
        self.dbg_pos = []
        self.dbg_trigger = []
        self.dbg_curr_speed = []

    def update(self, speed=0, stop_at=None):
        # checks if a switch activity was performed
        # trigger frequency
        if(stop_at is None):

            delta_speed = speed - self.curr_speed
            if( abs(delta_speed) > MAX_ACCELERATION):
                delta_speed = MAX_ACCELERATION*np.sign(delta_speed)    

            if (abs(speed) > SPEED_THRESHOLD):
                f_trigger = abs( speed / LSB_ANGLE )
                self.trigger_motor(speed)
                #print(f"Speed: {speed}, wait for {1/f_trigger:.3}s")
            else:
                # no trigger to motor
                f_trigger =  1/ 1.0 #if speed is zero, wait for 1s and try again

            new_speed = self.curr_speed + delta_speed
            self.curr_speed = new_speed
            #self.curr_speed = f_3db(f_trigger, self.curr_speed, new_speed) # evtl. rc filter implementieren (Achtung: variable sample frequenz!)
        else:
            # use curr_speed to calculate how to ramp down to achieve the desired location
            # TODO consider curr_speed sign for polarity for check how far is the curr_pos and stop_at away
            # delta_pos   = self.curr_pos - stop_at
            # delta_speed = self.curr_speed - 0
            # TODO calculate required acceleration when ramping down to stop_at
            # if acceleration is smaller than MAX_ACCELERATION, do a ramp down
            # otherwise add one turn (360) to the delta_pos, calculate required acceleration, and do a ramp down
            # consider rounding errors for reaching stop_at
            # ignore get_switch_state() if stop_at is not None (because of jitter of the switch)

            f_trigger = 1/ 1.0

        self.update_pos(f_trigger)

        if(self.dbg):
            self.dbg_speed.append(speed)
            self.dbg_curr_speed.append(self.curr_speed)
            self.dbg_pos.append(self.curr_pos)
            self.dbg_trigger.append(1/f_trigger)

        return 1/f_trigger
    
    def update_pos(self, f_trigger):
        new_state = self.get_switch_state()
        if(self.switch_state != new_state):
            self.switch_state = new_state
            if(new_state == True):
                self.curr_pos = 0
            else:
                self.curr_pos = 180
        else:
            self.curr_pos += self.curr_speed*f_trigger
            self.curr_pos = self.curr_pos % 360
            
    def get_switch_state(self):
        # TODO read Pin Polarity of switch from Raspi
        return False

    def trigger_motor(self, speed):
        # TODO trigger motor here and set direction pin polarity
        if(speed > 0):
            direction = True
        elif(speed < 0):
            direction = False
        pass