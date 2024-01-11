import RPi.GPIO as GPIO
import time

# GPIO-Pin-Nummer
gpio_pin = 2

# Frequenz (in Hertz)
frequency = 10

# Konfiguration der GPIO-Bibliothek
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

try:
    while True:
        # Den GPIO-Pin toggeln
        GPIO.output(gpio_pin, not GPIO.input(gpio_pin))
        
        # Eine Pause einfügen, um die gewünschte Frequenz zu erreichen
        time.sleep(1 / (2 * frequency))

except KeyboardInterrupt:
    # Programm beenden, wenn Strg+C gedrückt wird
    pass

finally:
    # GPIO zurücksetzen und aufräumen
    GPIO.cleanup()
