import socket
from robot_arm import RobotArm  # Assuming this is your robot arm control module

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 65000))
    server_socket.listen(5)
    print("Server listening on port 65000...")
    robot = RobotArm()  # Initialize your RobotArm object here
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        
        try:
            # Receive data length (4 bytes)
            length_data = client_socket.recv(4)
            if not length_data:
                break
            
            # Convert length bytes to integer
            length = int.from_bytes(length_data, byteorder='big')
            
            # Receive actual data based on length
            data = client_socket.recv(length).decode('utf-8')
            
            print(f"Received command: {data}")
            
            # Process received command
            if data.strip().lower() == 'quit':
                break
            
            # Split received data into two angles
            angles = data.split(",")
            if len(angles) != 2:
                raise ValueError("Invalid data format. Expected two angles separated by comma.")
            
            shoulder_angle = float(angles[0])
            elbow_angle = float(angles[1])
            
            # Move robot arm to the specified angles
            robot.move_to_position(shoulder_angle, elbow_angle)
            print(f"Moved robot arm to: Shoulder angle={shoulder_angle}, Elbow angle={elbow_angle}")
        
        except ValueError as ve:
            print(f"ValueError: {ve}")
        except Exception as e:
            print(f"Error processing command: {e}")
        
        client_socket.close()

    server_socket.close()
    print("Server closed.")

def main():
    start_server()

if __name__ == "__main__":
    main()
