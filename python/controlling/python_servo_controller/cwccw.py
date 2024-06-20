from pyax12.connection import Connection
from pyax12 import utils
import pyax12.packet as pk
import time

sc = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.1)

margin = False
slope = True

dyn = 88
params = 150


sc.set_cw_angle_limit(dyn, 0)
sc.set_ccw_angle_limit(dyn, 1023)


sc.close()
