import socket

def move_servos(shoulder_angle, elbow_angle):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('141.252.29.70', 65000))
        print("Verbinding met de server succesvol.")

        commando = f"{shoulder_angle},{elbow_angle}"
        client_socket.sendall(commando.encode('utf-8'))
        print(f"Verzonden commando: {commando}")

        response = client_socket.recv(1024).decode('utf-8')
        print(f"Ontvangen antwoord: {response}")

    except Exception as e:
        print(f"Er trad een fout op: {str(e)}")
    finally:
        client_socket.close()
        print("Verbinding gesloten.")

