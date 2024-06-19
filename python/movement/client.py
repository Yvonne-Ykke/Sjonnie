import socket
import angle_calculator as ac
import time

class RobotAction:
    MOVE = "move"
    GRIPPER_OPEN = "gripper_open"
    GRIPPER_CLOSE = "gripper_close"
    WRIST_ROTATE = "wrist_rotate"
    GRIPPER_UP = "gripper_up"
    GRIPPER_DOWN = "gripper_down"

def send_command_to_robot(action, *args):
    try:
        with socket.create_connection(('141.252.29.70', 65001)) as client_socket:
            print("Connected to the server.")

            if len(args) == 1:
                command = f"{action.value},{args[0]}"
            else:
                command = f"{action.value},{','.join(map(str, args))}"

            send_message(client_socket, command)
            print(f"Sent command: {command}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def send_message(sock, message):
    try:
        message_bytes = message.encode('utf-8')
        sock.sendall(message_bytes)

        response = sock.recv(1024).decode('utf-8')
        print(f"Received response: {response}")

    except Exception as e:
        print(f"Error sending/receiving data: {e}")

# Voorbeelden van gebruik:
if __name__ == "__main__":
    POS_1_X, POS_1_Y = 0, 400
    shoulder_angle, elbow_angle = ac.main(POS_1_X, POS_1_Y)
    WRIST_ANGLE_1 = 45

    send_command_to_robot(RobotAction.GRIPPER_OPEN)
    send_command_to_robot(RobotAction.GRIPPER_UP)
    send_command_to_robot(RobotAction.MOVE, shoulder_angle, elbow_angle, WRIST_ANGLE_1)

    time.sleep(5)

    send_command_to_robot(RobotAction.GRIPPER_DOWN)
    time.sleep(5)

    send_command_to_robot(RobotAction.GRIPPER_CLOSE)
    send_command_to_robot(RobotAction.GRIPPER_UP)
    
    POS_2_X, POS_2_Y = 300, 100
    shoulder_angle, elbow_angle = ac.main(POS_2_X, POS_2_Y)
    WRIST_ANGLE_2 = 90

    send_command_to_robot(RobotAction.MOVE, shoulder_angle, elbow_angle, WRIST_ANGLE_2)

    time.sleep(3)
    send_command_to_robot(RobotAction.GRIPPER_DOWN)
    send_command_to_robot(RobotAction.GRIPPER_OPEN)

