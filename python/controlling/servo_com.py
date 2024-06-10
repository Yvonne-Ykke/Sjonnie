import time
import RPi.GPIO as GPIO
import serial

# Configuratie van de GPIO-pins
TX_Pin = 8
RX_Pin = 10
TR_Pin = 12
BAUD_RATE = 1000000

# Definieer IDs van de servos
S1_ID = 3
S2_ID = 61

# Initialiseer RPi.GPIO en seriële communicatie
GPIO.setmode(GPIO.BCM)
GPIO.setup(TX_Pin, GPIO.OUT)
GPIO.setup(RX_Pin, GPIO.IN)
GPIO.setup(TR_Pin, GPIO.IN)
print("setup succesvol")
# Open de seriële poort
ser = serial.Serial('/dev/serial0', BAUD_RATE, timeout=1)  # Pas aan naar de juiste seriële poort
print("setup succesvol")

def switchCom(mode):
    GPIO.setup(TR_Pin, mode)


def send_command(command):
    ser.write((command + '\n').encode())

def read_position(servo_id):
    send_command(f"R{servo_id}")
    response = ser.readline().decode().strip()
    try:
        position = int(response)
    except ValueError:
        position = -1
    return position

def move_speed(servo_id, position, speed):
    print(f"M{servo_id},{position},{speed}")
    switchCom(GPIO.OUT)
    send_command(f"M{servo_id},{position},{speed}")
    switchCom(GPIO.IN)


def led_status(servo_id, status):
    send_command(f"L{servo_id},{status}")

def main():
    time.sleep(2)  # Wacht even tot de seriële communicatie is opgezet

    while True:
        move_speed(S2_ID, 0, 30)
        led_status(S2_ID, 'ON')
        move_speed(S1_ID, 0, 30)
        time.sleep(0.1)
        position = read_position(S1_ID)
        print(position)
        time.sleep(10)

        move_speed(S2_ID, 512, 30)
        led_status(S2_ID, 'OFF')
        move_speed(S1_ID, 512, 30)
        time.sleep(0.1)
        position = read_position(S1_ID)
        print(position)
        time.sleep(10)

        move_speed(S2_ID, 1023, 30)
        led_status(S2_ID, 'ON')
        move_speed(S1_ID, 1023, 30)
        time.sleep(0.1)
        position = read_position(S1_ID)
        print(position)
        time.sleep(10)

        move_speed(S2_ID, 512, 30)
        led_status(S2_ID, 'OFF')
        move_speed(S1_ID, 512, 30)
        time.sleep(0.1)
        position = read_position(S1_ID)
        print(position)
        time.sleep(10)

if __name__ == '__main__':
    main()

# Zorg ervoor dat GPIO's netjes worden afgesloten
GPIO.cleanup()
