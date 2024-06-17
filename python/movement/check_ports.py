import RPi.GPIO as GPIO
import time

# GPIO initialisatie
GPIO.setmode(GPIO.BCM)

# Loop door pinnen 10 tot 21 (range stopt exclusief 21)
for pin_nummer in range(10, 21):
    GPIO.setup(pin_nummer, GPIO.IN)
    status = GPIO.input(pin_nummer)
    print(f"Status van GPIO-poort {pin_nummer}: {status}")

    # Optioneel: controleer of de GPIO 'open' is (hoog)
    if status == GPIO.HIGH:  # GPIO.HIGH komt overeen met een logische '1' of 'hoog'
        print(f"GPIO-poort {pin_nummer} is open (hoog). Je mag schrijven")
    else:
        print(f"GPIO-poort {pin_nummer} is niet open (laag).")

# GPIO schoonmaak
GPIO.cleanup()
