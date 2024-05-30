import socket

def stuur_coordinaten(x, y):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.100', 65432))  # Pas het IP-adres aan

    try:
        commando = f"{x},{y}"
        client_socket.sendall(commando.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print(response)

    except Exception as e:
        print(f"Er trad een fout op: {str(e)}")
    finally:
        client_socket.close()

# Voorbeeldcoördinaten
x_coord = 10
y_coord = 20

# Stuur de coördinaten naar de server
stuur_coordinaten(x_coord, y_coord)
