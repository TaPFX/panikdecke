import RPi.GPIO as GPIO
import time
import asyncio

# Frequenz (in Hertz)
frequency = 1200#*2.7842

async def main():
    time_last = time.time()
    while True:
        await asyncio.sleep(1 / (frequency))
        print(0, time.time() - time_last, 1/frequency )
        time_last = time.time()

asyncio.run(main())

