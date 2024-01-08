
import numpy as np

STEP_PER_REVOLUTION = 400 # set this by the 3 switches
LSB_ANGLE = 360 / STEP_PER_REVOLUTION
SPEED_THRESHOLD = LSB_ANGLE / 1 # 0.9° per second is the lower boundary

class Controller:
    def __init__(self) -> None:

        self.curr_pos = 0
        self.curr_speed = 0

        self.switch_state = False

        self.dbg = True
        self.dbg_speed = []
        self.dbg_pos = []

    def update(self, speed=0, stop_at=None):
        # checks if a switch activity was performed
        # trigger frequency
        if(stop_at is None):
            self.curr_speed = speed # TODO smooth control of self.curr_speed - speed
            if (abs(speed) > SPEED_THRESHOLD):
                f_trigger = abs( speed / LSB_ANGLE )
                self.trigger_motor(speed)
                print(f"Speed: {speed}, wait for {1/f_trigger:.3}s")
            else:
                f_trigger =  1/ 1.0 #if speed is zero, wait for 100ms and try again
        else:
            #TODO ramp down speed to zero smoothly
            f_trigger = 1/ 1.0

        self.update_pos(f_trigger)

        if(self.dbg):
            self.dbg_speed.append(speed)
            self.dbg_pos.append(self.curr_pos)

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
            print(self.curr_pos)
            
    def get_switch_state(self):
        # TODO read Pin Polarity from Raspi
        return False

    def trigger_motor(self, speed):
        # TODO trigger motor here and set direction
        if(speed > 0):
            direction = True
        elif(speed < 0):
            direction = False
        pass