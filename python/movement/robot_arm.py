from pyax12.connection import Connection
import time
import moving

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3
# dynamixel_id3 = 10

import paramiko
import moving

# Verbind met de robotarm via SSH
def ssh_server():
    ssh_server = paramiko.Transport(("localhost", 22))
    ssh_server.load_system_host_keys()
    ssh_server.listen(0)
    conn = ssh_server.accept(20)
    return conn

# Functie om de robotarm te bewegen naar de opgegeven coördinaten
def move_to_position(x, y):
    shoulder_angle, elbow_angle = moving.main(x, y)
    Connection.goto_position(servo_1, shoulder_angle, 100)
    Connection.goto_position(servo_2, elbow_angle, 100)

    # Voer hier je eigen code uit om de servo's te bewegen naar de berekende hoeken
    print(f"Bewegen naar positie ({x}, {y}): Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")

# Luister naar SSH-opdrachten
while True:
    conn = ssh_server()
    command = conn.recv(1024).decode("utf-8")
    if command.lower() == "quit":
        break
    try:
        # Commando verwacht in de vorm "x,y"
        x, y = map(float, command.split(","))
        move_to_position(x, y)
        conn.send("Positie ingesteld.\n".encode("utf-8"))
    except Exception as e:
        conn.send(f"Fout: {str(e)}\n".encode("utf-8"))
    conn.close()
