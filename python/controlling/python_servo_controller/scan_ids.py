from pyax12.connection import Connection
import RPi.GPIO as GPIO
import time

# Schakel GPIO-waarschuwingen uit
GPIO.setwarnings(False)

# Maak verbinding met de seriële poort
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=1, waiting_time=0.1)

time.sleep(0.01)

# Ping de Dynamixel eenheden
ids_available = serial_connection.scan()

time.sleep(0.01)

# Print de gevonden IDs
for dynamixel_id in ids_available:
    print(dynamixel_id)

# Sluit de seriële verbinding
serial_connection.close()
