import socket

def send_arm_angles_to_robot(shoulder_angle, elbow_angle):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('141.252.29.70', 65000))
        print("Verbinding met de server succesvol.")

        commando = f"{shoulder_angle},{elbow_angle}"
        _send_message(client_socket, commando)
        print(f"Verzonden commando: {commando}")

        response = _recv_message(client_socket)
        print(f"Ontvangen antwoord: {response}")

    except Exception as e:
        print(f"Er trad een fout op: {str(e)}")
    finally:
        client_socket.close()
        print("Verbinding gesloten.")

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

# Voorbeeld van functieaanroep
send_arm_angles_to_robot(45, 90)
