import socket
from pyax12.connection import Connection
import sys
import signal

serial_connection = Connection(port="/dev/ttyS0", baudrate=1000000, rpi_gpio=True, timeout=0.5, waiting_time=0.01)

servo_1 = 61
servo_2 = 3

def move_to_position(shoulder_angle, elbow_angle):
    serial_connection.goto_position(servo_1, shoulder_angle, 100)
    serial_connection.goto_position(servo_2, elbow_angle, 100)
    print(f"Bewegen naar positie: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('141.252.29.47', 65000))
    server_socket.listen(5)
    print("Server luistert op poort 65000...")

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        server_socket.close()
        serial_connection.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Verbinding geaccepteerd van {addr}")
        try:
            command = client_socket.recv(1024).decode('utf-8')
            if command.lower() == "quit":
                break
            shoulder_angle, elbow_angle = map(float, command.split(","))
            move_to_position(shoulder_angle, elbow_angle)
            client_socket.sendall("Positie ingesteld.\n".encode('utf-8'))
        except Exception as e:
            client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
        finally:
            client_socket.close()
    server_socket.close()
    serial_connection.close()

if __name__ == "__main__":
    start_tcp_server()
