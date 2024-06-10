import time
import RPi.GPIO as GPIO
import serial

# Constants
AX_MODEL_NUMBER_L           = 0
AX_MODEL_NUMBER_H           = 1
AX_VERSION                  = 2
AX_ID                       = 3
AX_BAUD_RATE                = 4
AX_RETURN_DELAY_TIME        = 5
AX_CW_ANGLE_LIMIT_L         = 6
AX_CW_ANGLE_LIMIT_H         = 7
AX_CCW_ANGLE_LIMIT_L        = 8
AX_CCW_ANGLE_LIMIT_H        = 9
AX_SYSTEM_DATA2             = 10
AX_LIMIT_TEMPERATURE        = 11
AX_DOWN_LIMIT_VOLTAGE       = 12
AX_UP_LIMIT_VOLTAGE         = 13
AX_MAX_TORQUE_L             = 14
AX_MAX_TORQUE_H             = 15
AX_RETURN_LEVEL             = 16
AX_ALARM_LED                = 17
AX_ALARM_SHUTDOWN           = 18
AX_OPERATING_MODE           = 19
AX_DOWN_CALIBRATION_L       = 20
AX_DOWN_CALIBRATION_H       = 21
AX_UP_CALIBRATION_L         = 22
AX_UP_CALIBRATION_H         = 23

# RAM AREA
AX_TORQUE_ENABLE            = 24
AX_LED                      = 25
AX_CW_COMPLIANCE_MARGIN     = 26
AX_CCW_COMPLIANCE_MARGIN    = 27
AX_CW_COMPLIANCE_SLOPE      = 28
AX_CCW_COMPLIANCE_SLOPE     = 29
AX_GOAL_POSITION_L          = 30
AX_GOAL_POSITION_H          = 31
AX_GOAL_SPEED_L             = 32
AX_GOAL_SPEED_H             = 33
AX_TORQUE_LIMIT_L           = 34
AX_TORQUE_LIMIT_H           = 35
AX_PRESENT_POSITION_L       = 36
AX_PRESENT_POSITION_H       = 37
AX_PRESENT_SPEED_L          = 38
AX_PRESENT_SPEED_H          = 39
AX_PRESENT_LOAD_L           = 40
AX_PRESENT_LOAD_H           = 41
AX_PRESENT_VOLTAGE          = 42
AX_PRESENT_TEMPERATURE      = 43
AX_REGISTERED_INSTRUCTION   = 44
AX_PAUSE_TIME               = 45
AX_MOVING                   = 46
AX_LOCK                     = 47
AX_PUNCH_L                  = 48
AX_PUNCH_H                  = 49

# Status Return Levels
AX_RETURN_NONE              = 0
AX_RETURN_READ              = 1
AX_RETURN_ALL               = 2

# Instruction Set
AX_PING                     = 1
AX_READ_DATA                = 2
AX_WRITE_DATA               = 3
AX_REG_WRITE                = 4
AX_ACTION                   = 5
AX_RESET                    = 6
AX_SYNC_WRITE               = 131

# Specials
OFF                         = 0
ON                          = 1
LEFT                        = 0
RIGHT                       = 1
AX_BYTE_READ                = 1
AX_BYTE_READ_POS            = 2
AX_RESET_LENGTH             = 2
AX_ACTION_LENGTH            = 2
AX_ID_LENGTH                = 4
AX_LR_LENGTH                = 4
AX_SRL_LENGTH               = 4
AX_RDT_LENGTH               = 4
AX_LEDALARM_LENGTH          = 4
AX_SALARM_LENGTH            = 4
AX_TL_LENGTH                = 4
AX_VL_LENGTH                = 6
AX_CM_LENGTH                = 6
AX_CS_LENGTH                = 6
AX_CCW_CW_LENGTH            = 8
AX_BD_LENGTH                = 4
AX_TEM_LENGTH               = 4
AX_MOVING_LENGTH            = 4
AX_RWS_LENGTH               = 4
AX_VOLT_LENGTH              = 4
AX_LED_LENGTH               = 4
AX_TORQUE_LENGTH            = 4
AX_POS_LENGTH               = 4
AX_GOAL_LENGTH              = 5
AX_MT_LENGTH                = 5
AX_PUNCH_LENGTH             = 5
AX_SPEED_LENGTH             = 5
AX_GOAL_SP_LENGTH           = 7
AX_ACTION_CHECKSUM          = 250
BROADCAST_ID                = 254
AX_START                    = 255
AX_CCW_AL_L                 = 255
AX_CCW_AL_H                 = 3
TIME_OUT                    = 10

# Utility Functions
def delay_us(microseconds):
    time.sleep(microseconds / 1000000.0)

# AX12A Class
class AX12A:
    def __init__(self, direction_pin_tx, direction_pin_rx, direction_pin_tr, serial_instance):
        self.direction_pin_tx = direction_pin_tx
        self.direction_pin_rx = direction_pin_rx
        self.direction_pin_tr = direction_pin_tr
        self.serial = serial_instance

    def send_ax_packet(self, packet, length):
        self.serial.write(packet)
        self.serial.flush()

    def send_ax_packet_no_error(self, packet, length):
        self.send_ax_packet(packet, length)

    def read_data(self):
        return self.serial.read()

    def peek_data(self):
        return self.serial.peek()

    def available_data(self):
        return self.serial.available()

    def begin(self, baud):
        self.serial.begin(baud)
        self.set_d_pin(self.direction_pin_tx, GPIO.OUT)
        self.set_d_pin(self.direction_pin_rx, GPIO.IN)
        self.set_d_pin(self.direction_pin_tr, GPIO.OUT)

    def end(self):
        self.serial.end()

    def set_d_pin(self, dir_pin, mode):
        GPIO.setup(dir_pin, mode)

    def switch_com(self, dir_pin, mode):
        serial_port.write(dir_pin, mode)

    def reset(self, id):
        length = 6
        packet = bytearray([AX_START, AX_START, id, AX_RESET_LENGTH, AX_RESET])

        checksum = (~(id + AX_RESET_LENGTH + AX_RESET)) & 0xFF
        packet.append(checksum)

        return self.send_ax_packet(packet, length)

    def ping(self, id):
        length = 6
        packet = bytearray([AX_START, AX_START, id, AX_READ_DATA, AX_PING])

        checksum = (~(id + AX_READ_DATA + AX_PING)) & 0xFF
        packet.append(checksum)

        return self.send_ax_packet(packet, length)

    def set_id(self, id, new_id):
        length = 8
        packet = bytearray([AX_START, AX_START, id, AX_ID_LENGTH, AX_WRITE_DATA, AX_ID, new_id])

        checksum = (~(id + AX_ID_LENGTH + AX_WRITE_DATA + AX_ID + new_id)) & 0xFF
        packet.append(checksum)

        return self.send_ax_packet(packet, length)

    def set_bd(self, id, baud):
        length = 8
        packet = bytearray([AX_START, AX_START, id, AX_BD_LENGTH, AX_WRITE_DATA, AX_BAUD_RATE])

        baud_rate = (2000000 / baud) - 1
        checksum = (~(id + AX_BD_LENGTH + AX_WRITE_DATA + AX_BAUD_RATE + baud_rate)) & 0xFF

        packet.append(baud_rate)
        packet.append(checksum)

        return self.send_ax_packet(packet, length)

    def move(self, id, position):
        position_h = position >> 8
        position_l = position

        length = 9
        packet = bytearray([AX_START, AX_START, id, AX_GOAL_LENGTH, AX_WRITE_DATA, AX_GOAL_POSITION_L, position_l, position_h])

        checksum = (~(id + AX_GOAL_LENGTH + AX_WRITE_DATA + AX_GOAL_POSITION_L + position_l + position_h)) & 0xFF
        packet.append(checksum)

        return self.send_ax_packet(packet, length)

    # Implement other methods similarly

# Example usage:
if __name__ == "__main__":
    # Define your serial port
    serial_port = serial.Serial('/dev/ttyUSB0', 100000)  # Replace with your actual serial port and baud rate

    # Initialize AX12A object
    ax12a = AX12A(1, 2, 3, serial_port)

    # Example usage:
    ax12a.begin(9600)
    ax12a.ping(1)
    ax12a.move(1, 512)