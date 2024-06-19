import socket
import sys
import signal
from enum import Enum
from robot_arm import RobotArm

class RobotAction(Enum):
    MOVE = "move"
    GRIPPER_OPEN = "gripper_open"
    GRIPPER_CLOSE = "gripper_close"
    WRIST_ROTATE = "wrist_rotate"
    GRIPPER_UP = "gripper_up"
    GRIPPER_DOWN = "gripper_down"

def move_handler(parts):
    if len(parts) != 4:
        raise ValueError("Ongeldig 'move' commando formaat ontvangen.")
    shoulder, elbow, wrist = map(float, parts[1:])
    print(f"Robotarm bewegen naar: Schouder {shoulder}, Elleboog {elbow}, Pols {wrist}")
    RobotArm.move_to_position(shoulder, elbow, wrist)
    return "Positie ingesteld."

def gripper_open_handler(parts):
    if len(parts) != 1:
        raise ValueError("Ongeldig 'gripper_open' commando formaat ontvangen.")
    print("Gripper openen")
    # Methode aanroepen om gripper te openen
    RobotArm.gripper_open()
    return "Gripper geopend."

def gripper_close_handler(parts):
    if len(parts) != 1:
        raise ValueError("Ongeldig 'gripper_close' commando formaat ontvangen.")
    print("Gripper sluiten")
    # Methode aanroepen om gripper te sluiten
    RobotArm.gripper_close()
    return "Gripper gesloten."

def wrist_rotate_handler(parts):
    if len(parts) != 2:
        raise ValueError("Ongeldig 'wrist_rotate' commando formaat ontvangen.")
    wrist_rotation_angle = float(parts[1])
    print(f"Pols draaien naar: {wrist_rotation_angle} graden")
    # Methode aanroepen om pols te draaien naar specifieke hoek
    RobotArm.wrist_rotate(wrist_rotation_angle)
    return f"Pols gedraaid naar {wrist_rotation_angle} graden."

def gripper_up_handler(parts):
    if len(parts) != 1:
        raise ValueError("Ongeldig 'gripper_up' commando formaat ontvangen.")
    print("Gripper omhoog")
    # Methode aanroepen om gripper omhoog te bewegen
    RobotArm.gripper_up()
    return "Gripper omhoog bewogen."

def gripper_down_handler(parts):
    if len(parts) != 1:
        raise ValueError("Ongeldig 'gripper_down' commando formaat ontvangen.")
    print("Gripper omlaag")
    # Methode aanroepen om gripper omlaag te bewegen
    RobotArm.gripper_down()
    return "Gripper omlaag bewogen."

action_handlers = {
    RobotAction.MOVE: move_handler,
    RobotAction.GRIPPER_OPEN: gripper_open_handler,
    RobotAction.GRIPPER_CLOSE: gripper_close_handler,
    RobotAction.WRIST_ROTATE: wrist_rotate_handler,
    RobotAction.GRIPPER_UP: gripper_up_handler,
    RobotAction.GRIPPER_DOWN: gripper_down_handler,
}

def process_command(command):
    parts = command.split(",")
    action_str = parts[0].strip().lower()
    
    if action_str not in RobotAction.__members__:
        raise ValueError(f"Onbekende actie: {action_str}")
    
    action = RobotAction[action_str]

    handler = action_handlers.get(action)
    if handler:
        return handler(parts)
    else:
        raise ValueError(f"Onbekende actiehandler voor actie: {action}")

def handle_client_connection(client_socket, addr):
    print(f"Verbinding geaccepteerd van {addr}")
    
    try:
        while True:
            command = client_socket.recv(1024).decode('utf-8')
            print(f"Ontvangen commando: {command}")
            
            if command.lower() == "quit":
                break
            
            try:
                response = process_command(command)
                client_socket.sendall(response.encode('utf-8'))
            except ValueError as ve:
                print(f"Fout bij verwerken commando: {ve}")
                client_socket.sendall(f"Fout: {str(ve)}\n".encode('utf-8'))
    
    except Exception as e:
        print(f"Fout bij verwerken commando: {e}")
        client_socket.sendall(f"Fout: {str(e)}\n".encode('utf-8'))
    
    finally:
        client_socket.close()
        print("Verbinding met client gesloten.")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', 65001))  # Luister op alle netwerkinterfaces
        server_socket.listen(5)
        print("Server luistert op poort 65001...")
        
        def signal_handler(sig, frame):
            print('Je drukte op Ctrl+C!')
            server_socket.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            client_socket, addr = server_socket.accept()
            handle_client_connection(client_socket, addr)
            
    except Exception as e:
        print(f"Fout bij het binden van de socket: {e}")
        sys.exit(1)
        
    finally:
        server_socket.close()
        print("Server gesloten.")

if __name__ == "__main__":
    start_tcp_server()
