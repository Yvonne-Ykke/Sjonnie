from pyax12.connection import Connection
import moving
import paramiko

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3

# Functie om de robotarm te bewegen naar de opgegeven coördinaten
def move_to_position(x, y):
    shoulder_angle, elbow_angle = moving.main(x, y)
    serial_connection.goto_position(servo_1, shoulder_angle, 100)
    serial_connection.goto_position(servo_2, elbow_angle, 100)
    print(f"Bewegen naar positie ({x}, {y}): Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")

# Functie om de SSH-server te starten en commando's te verwerken
def start_ssh_server():
    server = paramiko.SSHClient()
    server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    server.connect('localhost', username='jouw_gebruikersnaam', password='jouw_wachtwoord')
    
    transport = server.get_transport()
    while True:
        channel = transport.accept(20)
        if channel is None:
            continue
        command = channel.recv(1024).decode("utf-8")
        if command.lower() == "quit":
            break
        try:
            x, y = map(float, command.split(","))
            move_to_position(x, y)
            channel.send("Positie ingesteld.\n".encode("utf-8"))
        except Exception as e:
            channel.send(f"Fout: {str(e)}\n".encode("utf-8"))
        channel.close()

    server.close()

# Start de SSH-server
start_ssh_server()
