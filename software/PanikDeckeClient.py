
import argparse
import random
import time

from pythonosc import udp_client


class PanikDeckeClient:
  
    def __init__(self, ip="127.0.0.1", port=1337) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--ip", default=ip,
            help="The ip of the OSC server")
        self.parser.add_argument("--port", type=int, default=port,
            help="The port the OSC server is listening on")
        self.args = self.parser.parse_args()

        self.client = udp_client.SimpleUDPClient(self.args.ip, self.args.port)
        print(f"Created Client at {self.args.ip}:{self.args.port}")

    def shutdown(self):
        self.client.send_message("/shutdown", True)

    def speed(self, speed_val):
        self.client.send_message("/speed", speed_val)

    def stop_at(self, stop_at_val):
        self.client.send_message("/stop_at", stop_at_val)

    def stop(self):
        self.client.send_message("/stop", True)