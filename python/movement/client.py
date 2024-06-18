import socket

def send_arm_angles_to_robot(shoulder_angle, elbow_angle, wrist_angle):
    try:
        with socket.create_connection(('141.252.29.70', 65000)) as client_socket:
            print("Connected to the server.")

            command = f"{shoulder_angle},{elbow_angle},{wrist_angle}"
            send_message(client_socket, command)
            print(f"Sent command: {command}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def send_message(sock, message):
    message_bytes = message.encode('utf-8')
    sock.sendall(message_bytes)