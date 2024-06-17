import socket
from robot_arm import RobotArm

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 65000))
    server_socket.listen(5)
    print("Server listening on port 65000...")
    robot = RobotArm()
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        try:
            command = receive_message(client_socket)
            if not command:
                break
            if command.strip().lower() == 'quit':
                break
            shoulder_angle, elbow_angle = map(float, command.split(","))
            robot.move_to_position(shoulder_angle, elbow_angle)
            print(f"Moved robot arm to: Shoulder angle={shoulder_angle}, Elbow angle={elbow_angle}")
        except ValueError as ve:
            print(f"ValueError: {ve}")
        except Exception as e:
            print(f"Error processing command: {e}")
        finally:
            client_socket.close()

def receive_message(sock):
    length_data = sock.recv(4)
    if not length_data:
        return None
    length = int.from_bytes(length_data, byteorder='big')
    return sock.recv(length).decode('utf-8')

def main():
    start_server()

if __name__ == "__main__":
    main()
