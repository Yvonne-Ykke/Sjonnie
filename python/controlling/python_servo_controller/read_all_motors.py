from pyax12.connection import Connection
import time

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

dynamixel_id1 = 23
dynamixel_id2 = 3
dynamixel_id3 = 11
dynamixel_id4 = 88
dynamixel_id5 = 2

SHOULDER = 23
ELBOW = 3
TRANS = 11
WRIST = 88
GRIPPER = 2


#ids_available = serial_connection.scan()
motors = []
time.sleep(0.01)
#for dynamixel_id in ids_available:
#    motors.append[dynamixel_id]



#simpel uitlezen in hexadecimalen
#serial_connection.print_control_table(dynamixel_id2)
#serial_connection.print_control_table(dynamixel_id)
time.sleep(0.01)

try:
    print("--------------------------------------------------------------------------------------")
    serial_connection.pretty_print_control_table(dynamixel_id1)
except (Exception) as ex:
    print("Motor 1 uitlezen error. " + str(ex))
print("--------------------------------------------------------------------------------------")
time.sleep(0.1)

try:
    serial_connection.pretty_print_control_table(dynamixel_id2)
except (Exception) as ex:
    print("Motor 2 uitlezen error. " + str(ex))
print("--------------------------------------------------------------------------------------")
time.sleep(0.01)

try:
    serial_connection.pretty_print_control_table(dynamixel_id3)
except (Exception) as ex:
    print("Motor 3 uitlezen error. " + str(ex))
print("--------------------------------------------------------------------------------------")
time.sleep(0.1)

try:
    serial_connection.pretty_print_control_table(dynamixel_id4)
except (Exception) as ex:
    print("Motor 4 uitlezen error. " + str(ex))
print("--------------------------------------------------------------------------------------")
time.sleep(0.1)

try:
    serial_connection.pretty_print_control_table(dynamixel_id5)
except (Exception) as ex:
    print("Motor 5 uitlezen error. " + str(ex))
print("--------------------------------------------------------------------------------------")
time.sleep(0.1)


#print(serial_connection.get_present_position(3, degrees=True))

serial_connection.close()
