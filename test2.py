import RPi.GPIO as GPIO
import time
import asyncio

# Frequenz (in Hertz)
frequency = 200#*2.7842

async def main():
    time_last = time.time()
    try:
        while True:
            await asyncio.sleep(1 / (frequency))
            print(0, time.time() - time_last, 1/frequency )
            time_last = time.time()

    except KeyboardInterrupt:
        # Programm beenden, wenn Strg+C gedrckt wird
        pass

asyncio.run(main())

