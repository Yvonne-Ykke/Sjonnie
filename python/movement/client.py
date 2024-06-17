import socket

def send_arm_angles_to_robot(shoulder_angle, elbow_angle):
    try:
        with socket.create_connection(('141.252.29.70', 65000)) as client_socket:
            print("Connected to the server.")

            command = f"{shoulder_angle},{elbow_angle}"
            send_message(client_socket, command)
            print(f"Sent command: {command}")

            response = receive_message(client_socket)
            if response:
                print(f"Received response: {response}")
            else:
                print("No response received from the server.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def send_message(sock, message):
    message_bytes = message.encode('utf-8')
    sock.sendall(message_bytes)

def receive_message(sock):
    try:
        message = sock.recv(1024)  # Assuming maximum message size of 1024 bytes
        return message.decode('utf-8')
    except Exception as e:
        print(f"Error receiving message: {str(e)}")
        return None
