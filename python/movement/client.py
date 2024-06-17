import socket

def send_arm_angles_to_robot(shoulder_angle, elbow_angle):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('141.252.29.70', 65000))
        print("Connected to the server.")

        command = f"{shoulder_angle},{elbow_angle}"
        send_message(client_socket, command)
        print(f"Sent command: {command}")

        response = receive_message(client_socket)
        print(f"Received response: {response}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client_socket.close()
        print("Connection closed.")

def send_message(sock, message):
    message_bytes = message.encode('utf-8')
    length = len(message_bytes)
    sock.sendall(length.to_bytes(4, byteorder='big'))  # Send the length as a 4-byte integer
    sock.sendall(message_bytes)  # Send the actual message

def receive_message(sock):
    length_data = sock.recv(4)
    if not length_data:
        return None  # Connection closed
    length = int.from_bytes(length_data, byteorder='big')
    message = b''
    while len(message) < length:
        message += sock.recv(length - len(message))
    return message.decode('utf-8')