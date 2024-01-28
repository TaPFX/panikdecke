import RPi.GPIO as GPIO
import time
import asyncio

# GPIO-Pin-Nummer
gpio_pin = 2

# Frequenz (in Hertz)
frequency = 400

# Konfiguration der GPIO-Bibliothek
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

async def main():
    time_last = time.time()
    try:
        while True:
            # Den GPIO-Pin toggeln
            GPIO.output(gpio_pin, not GPIO.input(gpio_pin))
            
            # Eine Pause einfgen, um diedd genschte Frequenz zu erreichen
            time.sleep(1 / (2 * frequency))
            #await asyncio.sleep(1 / ( 2 * frequency ) )
            #print(0, time.time() - time_last, 1/(2*frequency) )
            time_last = time.time()

    except KeyboardInterrupt:
        # Programm beenden, wenn Strg+C gedrckt wird
        pass

asyncio.run(main())

def time_run():
    time_last = time.time()
    try:
        while True:
            # Den GPIO-Pin toggeln
            GPIO.output(gpio_pin, not GPIO.input(gpio_pin))
            
            # Eine Pause einfgen, um diedd genschte Frequenz zu erreichen
            time.sleep(1 / (2 * frequency))
            #await asyncio.sleep(1 / ( 2 * frequency ) )
            #print(1, time.time() - time_last, 1/(2*frequency) )
            #time_last = time.time()

    except KeyboardInterrupt:
        # Programm beenden, wenn Strg+C gedrckt wird
        pass

    finally:
        # GPIO zurcksetzen und aufrumen
        GPIO.cleanup()


time_run()
