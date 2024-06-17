from pyax12.connection import Connection

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True,timeout=1, waiting_time=0.1)

#
serial_connection.is_torque_enable(3)
serial_connection.set_(10, 88)

serial_connection.close()
