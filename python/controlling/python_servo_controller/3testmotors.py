from pyax12.connection import Connection
import time

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

dynamixel_id1 = 61
dynamixel_id2 = 3
dynamixel_id3 = 10

time.sleep(0.01)

# Go to 0°
print("send1")
serial_connection.goto(dynamixel_id1, 0, speed=512, degrees=False)
time.sleep(0.01)
serial_connection.goto(dynamixel_id2, 0, speed=512, degrees=False)
time.sleep(0.01)
serial_connection.goto(dynamixel_id3, 0, speed=512, degrees=False)
print("ga naar 0")
time.sleep(5)    # Wait 1 second

#voor de motors moet de timing op 0.00010 en voor uitlezen 0.00005 in de library

# Go to -45° (45° CW)
print("send2")
serial_connection.goto(dynamixel_id1, 512, speed=512, degrees=False)
time.sleep(0.01)
print("2")
serial_connection.goto(dynamixel_id2, 512, speed=512, degrees=False)
time.sleep(0.01)
print("3")
serial_connection.goto(dynamixel_id3, 512, speed=512, degrees=False)
print("ga naar -149")
time.sleep(5)    # Wait 1 second

# Go to -90° (90° CW)
print("149")
serial_connection.goto(dynamixel_id1, 1023, speed=512, degrees=False)
time.sleep(0.01)
serial_connection.goto(dynamixel_id2, 1023, speed=512, degrees=False)
time.sleep(0.01)
serial_connection.goto(dynamixel_id3, 1023, speed=512, degrees=False)
time.sleep(3)    # Wait 1 second

# Go to -135° (135° CW)
#serial_connection.goto(dynamixel_id, -135, speed=512, degrees=True)
#time.sleep(3)    # Wait 1 second

# Go to -150° (150° CW)
#serial_connection.goto(dynamixel_id, -150, speed=512, degrees=True)
#time.sleep(3)    # Wait 1 second

# Go to +150° (150° CCW)
#serial_connection.goto(dynamixel_id, 150, speed=512, degrees=True)
#time.sleep(3)    # Wait 2 seconds

# Go to +135° (135° CCW)
#serial_connection.goto(dynamixel_id, 135, speed=512, degrees=True)
#time.sleep(3)    # Wait 1 second

# Go to +90° (90° CCW)
#serial_connection.goto(dynamixel_id, 90, speed=512, degrees=True)
#time.sleep(1)    # Wait 1 second

# Go to +45° (45° CCW)
#serial_connection.goto(dynamixel_id, 45, speed=512, degrees=True)
#time.sleep(1)    # Wait 1 second

# Go back to 0°
#serial_connection.goto(dynamixel_id, 0, speed=512, degrees=True)
print("eind")
# Close the serial connection
serial_connection.close()
