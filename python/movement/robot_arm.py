import socket
from pyax12.connection import Connection
import sys
import signal

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

SERVO_1 = 61
SERVO_2 = 3

def move_to_position(shoulder_angle, elbow_angle):
    serial_connection.goto(SERVO_1, shoulder_angle, speed = 20, degrees = True)
    serial_connection.goto(SERVO_2, elbow_angle, speed = 20, degrees = True)
    print(f"Bewegen naar positie: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 65000))  # Listen on all networkinterfaces
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
        client_socket, addr = server_socket.accept()
        print(f"Verbinding geaccepteerd van {addr}")
        try:
            command = client_socket.recv(1024).decode('utf-8')
            print(f"Ontvangen commando: {command}")
            if command.lower() == "quit":
                break
            shoulder_angle, elbow_angle = map(float, command.split(","))
            move_to_position(shoulder_angle, elbow_angle)
            client_socket.sendall("Positie ingesteld.\n".encode('utf-8'))
        except Exception as e:
            print(f"Fout bij verwerken commando: {e}")
            client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
        finally:
            client_socket.close()
            print("Verbinding met client gesloten.")
    server_socket.close()
    serial_connection.close()
    print("Server gesloten.")

if __name__ == "__main__":
    start_tcp_server()
