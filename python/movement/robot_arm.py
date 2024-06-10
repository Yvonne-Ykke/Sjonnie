import socket
from pyax12.connection import Connection
import sys
import signal

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3

def move_to_position(shoulder_angle, elbow_angle):
    serial_connection.goto(servo_1, shoulder_angle, speed = 20, degrees = True)
    serial_connection.goto(servo_2, elbow_angle, speed = 20, degrees = True)
    print(f"Bewegen naar positie: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 65000))  # Luister op alle netwerkinterfaces
        server_socket.listen(5)
        print("Server luistert op poort 65000...")
    except Exception as e:
        print(f"Fout bij het binden van de socket: {e}")
        sys.exit(1)

    def signal_handler(sig, frame):
        print('Je drukte op Ctrl+C!')
        server_socket.close()
        serial_connection.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        client_socket = accept_tcp_connection(server_socket)
        if client_socket is None: continue
        try:
            command = get_command(client_socket)
            if command == 'quit': break
            shoulder_angle, elbow_angle = get_angles_from_command(command)
            move_to_position(shoulder_angle, elbow_angle)
            send_feedback_to_client(client_socket, shoulder_angle, elbow_angle)
        except Exception as e:
            print(f"Fout bij verwerken commando: {e}")
            client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
        finally:
            client_socket.close()
            print("Verbinding met client gesloten.")

    server_socket.close()
    serial_connection.close()
    print("Server gesloten.")

def send_feedback_to_client(client_socket, shoulder_angle, elbow_angle):
    feedback = f"Positie ingesteld: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}\n"
    client_socket.sendall(feedback.encode('utf-8'))

def get_angles_from_command(command):
    shoulder_angle, elbow_angle = map(float, command.split(","))
    return shoulder_angle, elbow_angle

def get_command(client_socket):
    command = client_socket.recv(1024).decode('utf-8')
    print(f"Ontvangen commando: {command}")
    command = command.lower()
    return command
 
def accept_tcp_connection(server_socket):
        client_socket, addr = server_socket.accept()
        print(f"Verbinding geaccepteerd van {addr}")
        return client_socket

if __name__ == "__main__":
    start_tcp_server()
