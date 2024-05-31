import socket

def move_servos(shoulder_angle, elbow_angle):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('141.252.29.47', 65000))  # Pas het IP-adres aan

    try:
        commando = f"{shoulder_angle},{elbow_angle}"
        client_socket.sendall(commando.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print(response)

    except Exception as e:
        print(f"Er trad een fout op: {str(e)}")
    finally:
        client_socket.close()

