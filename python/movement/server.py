import socket
from robot_arm import RobotArm

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 65000))
    server_socket.listen(5)
    print("Server listening on port 65000...")
    robot = RobotArm()
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        command = receive_message(client_socket)
        print(f"Ontvangen command: {command}")

        if not command or command.strip().lower() == 'quit':
            client_socket.close()
            break

        shoulder_angle, elbow_angle = map(float, command.split(","))
        
        robot.move_to_position(shoulder_angle, elbow_angle)

        client_socket.close()

def receive_message(sock):
    length_data = sock.recv(4)
    print(f"data ontvangen: ")
    if not length_data:
        return None
    length = int.from_bytes(length_data, byteorder='big')
    data = sock.recv(length).decode('utf-8')
    print(f"omgezette data: {data}")
    return data

def main():
    start_server()

if __name__ == "__main__":
    main()
