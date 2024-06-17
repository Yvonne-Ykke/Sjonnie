from pyax12.connection import Connection
from pyax12 import utils
import pyax12.packet as pk
import time

sc = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.1)


dyn = 88
params = 100


sc.write_data(dyn, pk.MAX_TORQUE, params)

sc.close()
