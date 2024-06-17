import socket
import sys
import signal
from robot_arm import RobotArm
import RPi.GPIO as GPIO

# Disable GPIO warnings globally
GPIO.setwarnings(False)

def _start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 65000))  # Listen on all network interfaces
        server_socket.listen(5)
        print("Server luistert op poort 65000...")
    except Exception as e:
        print(f"Fout bij het binden van de socket: {e}")
        server_socket.close()
        sys.exit(1)

    def signal_handler(sig, frame):
        print('Je drukte op Ctrl+C!')
        server_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal

    robot = RobotArm()

    while True:
        client_socket = _accept_tcp_connection(server_socket)
        if client_socket is None:
            continue
        try:
            with client_socket:
                command = _get_command(client_socket)
                if command == 'quit':
                    break
                shoulder_angle, elbow_angle = _get_angles_from_command(command)
                robot.move_to_position(shoulder_angle, elbow_angle)
                _send_feedback_to_client(client_socket, shoulder_angle, elbow_angle)
        except Exception as e:
            print(f"Fout bij verwerken commando: {e}")
            try:
                client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
            except Exception as e_send:
                print(f"Fout bij verzenden foutmelding naar client: {e_send}")
        finally:
            print("Verbinding met client gesloten.")

    server_socket.close()
    print("Server gesloten.")

def _send_feedback_to_client(client_socket, shoulder_angle, elbow_angle):
    feedback = f"Positie ingesteld: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}\n"
    _send_message(client_socket, feedback)

def _get_angles_from_command(command):
    shoulder_angle, elbow_angle = map(float, command.split(","))
    return shoulder_angle, elbow_angle

def _get_command(client_socket):
    message = _recv_message(client_socket)
    print(f"Ontvangen commando: {message}")
    return message.lower()

def _send_message(client_socket, message):
    message = message.encode('utf-8')
    length = len(message)
    client_socket.sendall(length.to_bytes(4, byteorder='big'))  # Verstuur de lengte als een 4-byte integer
    client_socket.sendall(message)  # Verstuur het eigenlijke bericht

def _recv_message(client_socket):
    length_data = client_socket.recv(4)
    if not length_data:
        return None  # Verbinding is gesloten
    length = int.from_bytes(length_data, byteorder='big')
    message = b''
    while len(message) < length:
        to_read = min(length - len(message), 1024)
        message += client_socket.recv(to_read)
    return message.decode('utf-8')

def _accept_tcp_connection(server_socket):
    try:
        client_socket, addr = server_socket.accept()
        print(f"Verbinding geaccepteerd van {addr}")
        return client_socket
    except Exception as e:
        print(f"Fout bij het accepteren van de verbinding: {e}")
        return None

def main():
    _start_server()

if __name__ == "__main__":
    main()
