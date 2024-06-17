import socket
import sys
import signal
from robot_arm import RobotArm
import RPi.GPIO as GPIO

# Disable GPIO warnings globally
GPIO.setwarnings(False)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 65000))  # Listen on all network interfaces
        server_socket.listen(5)
        print("Server listening on port 65000...")
    except Exception as e:
        print(f"Error binding socket: {e}")
        server_socket.close()
        sys.exit(1)

    def handle_signal(sig, frame):
        print('Ctrl+C pressed!')
        server_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)  # Handle termination signal

    robot = RobotArm()

    while True:
        client_socket = accept_tcp_connection(server_socket)
        if client_socket is None:
            continue
        try:
            with client_socket:
                command = get_command(client_socket)
                if command == 'quit':
                    break
                shoulder_angle, elbow_angle = parse_command(command)
                robot.move_to_position(shoulder_angle, elbow_angle)
                send_feedback(client_socket, shoulder_angle, elbow_angle)
        except Exception as e:
            print(f"Error processing command: {e}")
            if client_socket.fileno() != -1:
                try:
                    client_socket.sendall(f"Error: {str(e)}\n".encode('utf-8'))
                except Exception as send_error:
                    print(f"Error sending error message to client: {send_error}")
        finally:
            print("Client connection closed.")

    server_socket.close()
    print("Server closed.")

def send_feedback(sock, shoulder_angle, elbow_angle):
    feedback = f"Position set: Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}\n"
    send_message(sock, feedback)

def parse_command(command):
    try:
        shoulder_angle, elbow_angle = map(float, command.split(","))
        return shoulder_angle, elbow_angle
    except ValueError as e:
        raise ValueError(f"Incomplete or invalid command: {command}") from e

def get_command(sock):
    message = receive_message(sock)
    if message:
        print(f"Received command: {message}")
        return message.lower()
    else:
        return ''

def send_message(sock, message):
    message_bytes = message.encode('utf-8')
    length = len(message_bytes)
    sock.sendall(length.to_bytes(4, byteorder='big'))  # Send the length as a 4-byte integer
    sock.sendall(message_bytes)  # Send the actual message

def receive_message(sock):
    try:
        length_data = sock.recv(4)
        if not length_data:
            return None  # Connection closed
        length = int.from_bytes(length_data, byteorder='big')
        message = b''
        while len(message) < length:
            part = sock.recv(length - len(message))
            if not part:
                break  # Connection closed
            message += part
        return message.decode('utf-8')
    except Exception as e:
        print(f"Error receiving message: {str(e)}")
        return None

def accept_tcp_connection(server_socket):
    try:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        return client_socket
    except Exception as e:
        print(f"Error accepting connection: {e}")
        return None

def main():
    start_server()

if __name__ == "__main__":
    main()
