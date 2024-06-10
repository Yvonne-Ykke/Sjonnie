from pyax12.connection import Connection
import time
import curses
import socket

# Serial connection setup
serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

# Motor positions and speeds
pos1, pos2, posm = 80, 920, 512
gopen, gdicht = 300, 30
beneden, boven = 1023, 0
spdt, spda, spdg = 300, 20, 500
dynatrans, dynamixelgrip = 69, 2
dynamixel_id1, dyn2 = 10, 3

# Flag for position tracking
flag = 0

# Function for sending motor commands
def send(dyn_id=None, position=None, spd=None):
    cpos = serial_connection.get_present_position(dyn_id, degrees=False)
    spd = spda if dyn_id == dynamixelgrip else spdg if dyn_id == dynatrans else spdt
    time.sleep(0.05)
    dist = abs(position - cpos)
    serial_connection.goto(dyn_id, position, speed=spd, degrees=False)
    time.sleep(0.05)

# Function for smooth motor movement
def smooth_send(dyn_id, position):
    cpos, spd = 0, spda if dyn_id == dynamixelgrip else spdg if dyn_id == dynatrans else spdt
    time.sleep(0.05)
    if not serial_connection.is_moving(dyn_id):
        cpos = serial_connection.get_present_position(dyn_id, degrees=False)
    if abs(position - cpos) > 350:
        time.sleep(0.01)
        serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.2), degrees=False)
        time.sleep(3)
        serial_connection.goto(dyn_id, position, speed=int(abs((position-cpos)*0.5)*0.1), degrees=False)
    if abs(position - cpos) < 350:
        serial_connection.goto(dyn_id, position, speed=int(abs(position-cpos)*0.1), degrees=False)
        time.sleep(5)
        serial_connection.goto(dyn_id, position, speed=int(abs(position-cpos)*0.01), degrees=False)

# Define key-action mappings
key_actions = {
    'w': (smooth_send, (dyn2, 512)),
    'a': (smooth_send, (dynamixel_id1, 200)),
    's': (smooth_send, (dyn2, 200)),
    'd': (smooth_send, (dynamixel_id1, 900)),
    'k': (send, (dynatrans, beneden if flag == 0 else boven)),
    'q': (None, ()),  # Quit action
}

# Keyboard input loop
stdscr = curses.initscr()
while True:
    key_pressed = stdscr.getch()
    if key_pressed == ord('q'): break
    action = key_actions.get(chr(key_pressed), (None, ()))
    function_to_call, arguments = action
    if function_to_call:
        function_to_call(*arguments)

# TCP server setup and loop
HOST, PORT = '0.0.0.0', 65432
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

def test():
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if data:
            print(f'Recieved: {data.decode()}')
        conn.sendall(data)

if __name__ == "__main__":
    test()

s.shutdown(socket.SHUT_RDWR)
s.close()
