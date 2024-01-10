
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

import numpy as np

from Controller import Controller, SPEED_THRESHOLD

from matplotlib import pyplot as plt

from datetime import datetime  

def get_datetime_str():
    return datetime.now().strftime("%d-%m-%Y, %H:%M:%S")

def print_out(str_in):
    print(f"{get_datetime_str()}: {str_in}")

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

        asyncio.run(self.init_server())

    async def init_server(self):
        self.server = AsyncIOOSCUDPServer((self.ip, self.port), self.dispatcher, asyncio.get_event_loop())
        self.transport, self.protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        await self.server_func()
        self.transport.close()  # Clean up serve endpoint

    async def server_func(self):
        ctrlInst = Controller()
        print_out("Server started.")
        while(not self.shutdown):
            await asyncio.sleep(ctrlInst.update(self.speed, self.stop_at))
        if(ctrlInst.dbg):
            time = np.cumsum(ctrlInst.dbg_trigger)
            fig, ax = plt.subplots()
            twin1 = ax.twinx()
            ax.plot(time, ctrlInst.dbg_pos, 'x-', label='pos', color='b')
            ax.set_ylabel("position in °")
            twin1.plot(time, ctrlInst.dbg_speed, 'x-', label='speed cmd', color='r')
            twin1.plot(time, ctrlInst.dbg_curr_speed, 'x-', label='speed actual', color='k')
            twin1.set_ylabel("speed in °/s")
            ax.set_xlabel("time in s")
            fig.legend()
            plt.show()

    def shutdown_now(self, address, *args):
        self.shutdown = args[0]
        print_out("Shutdown received.")

    def set_speed(self, address, *args):
        self.stop_at = None
        self.speed = args[0]
        print_out(f"Speed set to {self.speed}.")
        if(abs(self.speed) < SPEED_THRESHOLD):
            print_out(f"Warning: Speed too low, ignoring.")

    def set_stop(self, address, *args):
        self.stop_at = args[0]
        print_out(f"Stop at {self.stop_at}")

    def stop_immediately(self, address, *args):
        self.speed = 0
        print_out(f"Stop immediatley.")