from pyax12 import packet as pk
from pyax12.connection import Connection
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True,timeout=1, waiting_time=0.1)



on_off = 0
SHOULDER = 23
ELBOW = 3
TRANS = 11
WRIST = 88
GRIPPER = 2



serial_connection.write_data(SHOULDER, pk.TORQUE_ENABLE, on_off)
serial_connection.write_data(ELBOW, pk.TORQUE_ENABLE, on_off)
serial_connection.write_data(TRANS, pk.TORQUE_ENABLE, on_off)
serial_connection.write_data(WRIST, pk.TORQUE_ENABLE, on_off)
serial_connection.write_data(GRIPPER, pk.TORQUE_ENABLE, on_off)

serial_connection.close()

