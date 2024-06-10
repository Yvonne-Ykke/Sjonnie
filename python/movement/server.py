import socket
import sys
import signal
import robot_arm


def _start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 65000))  # Listen on all networkinterfaces
        server_socket.listen(5)
        print("Server luistert op poort 65000...")
    except Exception as e:
        print(f"Fout bij het binden van de socket: {e}")
        sys.exit(1)

    def signal_handler():
        print('Je drukte op Ctrl+C!')
        server_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        client_socket = _accept_tcp_connection(server_socket)
        if client_socket is None: continue
        try:
            command = _get_command(client_socket)
            if command == 'quit': break
            shoulder_angle, elbow_angle = _get_angles_from_command(command)
            robot_arm.move_to_position(shoulder_angle, elbow_angle)
            _send_feedback_to_client(client_socket, shoulder_angle, elbow_angle)
        except Exception as e:
            print(f"Fout bij verwerken commando: {e}")
            client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
        finally:
            client_socket.close()
            print("Verbinding met client gesloten.")

    server_socket.close()
    print("Server gesloten.")

def _send_feedback_to_client(client_socket, shoulder_angle, elbow_angle):
    feedback = f"Positie ingesteld: Schouder hoek: {shoulder_angle}, Elleboog hoek: {elbow_angle}\n"
    client_socket.sendall(feedback.encode('utf-8'))

def _get_angles_from_command(command):
    shoulder_angle, elbow_angle = map(float, command.split(","))
    return shoulder_angle, elbow_angle

def _get_command(client_socket):
    command = client_socket.recv(1024).decode('utf-8')
    print(f"Ontvangen commando: {command}")
    command = command.lower()
    return command
 
def _accept_tcp_connection(server_socket):
        client_socket, addr = server_socket.accept()
        print(f"Verbinding geaccepteerd van {addr}")
        return client_socket

def main():
    _start_server()

if __name__ == "__main__":
    main()