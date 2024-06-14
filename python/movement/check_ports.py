import RPi.GPIO as GPIO

# Definieer de GPIO-pin (bijvoorbeeld pin 18)
pin_nummer = 18

# GPIO initialisatie
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_nummer, GPIO.IN)

# Lees de status van de GPIO-poort
status = GPIO.input(pin_nummer)

# Print de status (optioneel)
print(f"Status van GPIO-poort {pin_nummer}: {status}")

# Optioneel: controleer of de GPIO 'open' is
if status == GPIO.HIGH:  # GPIO.HIGH komt overeen met een logische '1' of 'hoog'
    print("GPIO-poort is open (hoog).")
else:
    print("GPIO-poort is niet open (laag).")

# GPIO schoonmaak
GPIO.cleanup()
