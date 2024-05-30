from pyax12.connection import Connection
import time
# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True,timeout=1, waiting_time=0.1)

time.sleep(0.01)

# Ping the dynamixel unit(s)
ids_available = serial_connection.scan()

time.sleep(0.01)
for dynamixel_id in ids_available:
    print(dynamixel_id)

print (ids_available)
# Close the serial connection
serial_connection.close()
