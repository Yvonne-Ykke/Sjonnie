from pyax12.connection import Connection
import time

# Connect to the serial port
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

pos1 = 80 #als degrees false is dan is het van 0 tot 1023 en als het true is dan ist het van -150 tot 150
pos2 = 920
posm = 512

gopen = 300
gdicht = 30

beneden = 1023
boven = 0

spdt = 300
spda = 20
spdg = 500
dynatrans = 69
dynamixelgrip = 2
dynamixel_id1 = 10
dyn2 = 3

time.sleep(0.1)

while(True):
    serial_connection.goto(dynamixel_id1, pos1, speed=spda, degrees=False)
    time.sleep(0.05)
    serial_connection.goto(dyn2, pos2, speed=spda, degrees=False)
    time.sleep(10)
    serial_connection.goto(dynatrans, beneden, speed=spdt, degrees=False)
    time.sleep(2)
    serial_connection.goto(dynamixelgrip, gdicht, speed=spdg, degrees=False)
    time.sleep(0.1)
    serial_connection.goto(dynatrans, boven, speed=spdt, degrees=False)
    time.sleep(2)
    serial_connection.goto(dynamixel_id1, posm, speed=spda, degrees=False)
    time.sleep(0.05)
    serial_connection.goto(dyn2, posm, speed=spda, degrees=False)
    time.sleep(10)
    serial_connection.goto(dynatrans, beneden, speed=spdt, degrees=False)
    time.sleep(2)
    serial_connection.goto(dynamixelgrip, gopen, speed=spdg, degrees=False)
    time.sleep(2)
    serial_connection.goto(dynatrans, boven, speed=spdt, degrees=False)
    time.sleep(2)

while(False):
    serial_connection.goto(dynatrans, beneden, speed=spdt, degrees=False)
    time.sleep(5)
    serial_connection.goto(dynatrans, boven, speed=spdt, degrees=False)
    time.sleep(5)


time.sleep(0.01)
#serial_connection.set_ccw_angle_limit(dynamixelgrip, 1023, degrees=False)
#serial_connection.pretty_print_control_table(dynamixelgrip)
#serial_connection.goto(dynamixelgrip, gopen, speed=spd, degrees=False)
#time.sleep(1)
#serial_connection.goto(dynamixelgrip, gdicht, speed=spd, degrees=False)
#time.sleep(1)
#serial_connection.goto(dynamixelgrip, gopen, speed=spd, degrees=False)
#time.sleep(1)
#serial_connection.goto(dynamixelgrip, gdicht, speed=spd, degrees=False)



print("eind")
# Close the serial connection
serial_connection.close()
