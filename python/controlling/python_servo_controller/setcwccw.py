from pyax12.connection import Connection
from pyax12 import utils
import pyax12.packet as pk
import time

sc = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.1)


dyn = 10
angle_limit = 4

time.sleep(0.01)
params = utils.int_to_little_endian_bytes(angle_limit)
time.sleep(0.01)
sc.write_data(dyn, pk.CW_COMPLIENCE_Margin, params)
time.sleep(0.01)
sc.close()


