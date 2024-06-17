from pyax12.connection import Connection
from pyax12 import utils
import pyax12.packet as pk
import time

sc = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.1)

margin = True
slope = False

dyn = 88
params = 5

if slope:
    sc.write_data(dyn, pk.CW_COMPLIENCE_SLOPE, params)
    sc.write_data(dyn, pk.CCW_COMPLIENCE_SLOPE, params)


if margin:
    sc.write_data(dyn, pk.CW_COMPLIENCE_MARGIN, params)
    sc.write_data(dyn, pk.CCW_COMPLIENCE_MARGIN, params)
sc.close()
