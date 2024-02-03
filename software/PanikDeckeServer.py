
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

import numpy as np

import os

from Controller import Controller, SPEED_THRESHOLD

from datetime import datetime

import time


def get_datetime_str():
    return datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

if(os.name != 'nt'): # can be tested on windows shell without RPi
    IS_RASPI = True
    import RPi.GPIO as GPIO
    # GPIO-Pin-Nummer
    gpio_pin = 2
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.OUT)

class PanikDeckeServer:
    def __init__(self, ip = "127.0.0.1", port = 1337) -> None:

        self.dispatcher = Dispatcher()
        self.dispatcher.map("/shutdown", self.shutdown_now)
        self.dispatcher.map("/speed", self.set_speed)
        self.dispatcher.map("/stop", self.stop_immediately)
        self.dispatcher.map("/stop_at", self.set_stop)

        self.ip = ip
        self.port = port

        self.shutdown = False
        self.speed = 0
        self.stop_at = None

        self.logging = True
        self.logging_filename = "PanikDeckeServer.log"

        self.print_out("\r\r============================================================================\r\r")

        asyncio.run(self.init_server())

    async def init_server(self):
        self.server = AsyncIOOSCUDPServer((self.ip, self.port), self.dispatcher, asyncio.get_event_loop())
        self.transport, self.protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        self.print_out(f"Create Server on {self.ip}:{self.port}")
        await self.server_func()
        if(os.name != 'nt'):
            GPIO.cleanup()
        self.transport.close()  # Clean up serve endpoint

    async def accurate_sleep(wait_time):
        start = time.perf_counter()
        while True:
            if (time.perf_counter() - start) >= wait_time:
                break
            await asyncio.sleep(0)

    async def server_func(self):
        ctrlInst = Controller()
        if(os.name != 'nt'):
            ctrlInst.dbg = False # set later to False when running on raspi
        else:
            ctrlInst.dbg = True
        self.print_out("server_func(): Server started.")
        last_time = time.time()
        while(not self.shutdown):
            t_wait, out_en = ctrlInst.update(self.speed, self.stop_at)
            t_wait = np.clip(t_wait - (time.time() - last_time), 0, 1)
            if(os.name != 'nt' and out_en):
                GPIO.output(gpio_pin, not GPIO.input(gpio_pin))
            await self.accurate_sleep(t_wait/2)
            if(os.name != 'nt' and out_en):
                GPIO.output(gpio_pin, not GPIO.input(gpio_pin))
            await  self.accurate_sleep(t_wait/2)
            last_time = time.time()
        ctrlInst.dbg_plot()

    def shutdown_now(self, address, *args):
        self.shutdown = args[0]
        self.print_out("shutodwn_now(): Shutdown received.")

    def set_speed(self, address, *args):
        self.stop_at = None
        self.speed = args[0]
        self.print_out(f"set_speed(): Speed set to {self.speed}.")
        if(abs(self.speed) < SPEED_THRESHOLD):
            self.print_out(f"Warning: Speed too low, ignoring.")

    def set_stop(self, address, *args):
        self.stop_at = args[0]
        self.print_out(f"set_stop(): Stop at {self.stop_at}°.")

    def stop_immediately(self, address, *args):
        self.speed = 0
        self.print_out(f"set_stop(): Stop immediatley.")

    def print_out(self, str_in):
        str_format = f"{get_datetime_str()}: {str_in}"
        print(str_format)
        if(self.logging):
            with open(self.logging_filename, "a") as myfile:
                myfile.write(str_format + "\r")
