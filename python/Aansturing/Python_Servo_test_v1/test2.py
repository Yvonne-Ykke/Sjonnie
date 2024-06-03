from pyax12.connection import Connection
import time

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

dynamixel_id1 = 61
dynamixel_id2 = 3
dynamixel_id3 = 10

#simpel uitlezen in hexadecimalen
#serial_connection.print_control_table(dynamixel_id2)
#serial_connection.print_control_table(dynamixel_id)
time.sleep(0.01)

try:
	serial_connection.pretty_print_control_table(dynamixel_id1)
except:
    print("Motor 1 uitlezen error.")
print("--------------------------------------------------------------------------------------")
time.sleep(0.1)

try:
    serial_connection.pretty_print_control_table(dynamixel_id2)
except:
    print("Motor 2 uitlezen error")
print("--------------------------------------------------------------------------------------")
time.sleep(0.01)

try:
    serial_connection.pretty_print_control_table(dynamixel_id3)
except:
    print("Motor 3 uitlezen error")

time.sleep(0.1)

print(serial_connection.get_present_position(3, degrees=True))

serial_connection.close()
