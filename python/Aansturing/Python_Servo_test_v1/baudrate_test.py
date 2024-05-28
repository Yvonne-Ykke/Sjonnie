from pyax12.connection import Connection

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000)

dynamixel_id = 1

# Ping the third dynamixel unit
is_available = serial_connection.ping(dynamixel_id)

print(is_available)

# Ping the dynamixel unit(s)
ids_available = serial_connection.scan()

for dynamixel_id in ids_available:
    print(dynamixel_id)

# Close the serial connection
serial_connection.close()
