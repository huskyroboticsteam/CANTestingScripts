import serial as s
import numpy as np
from serial.tools import list_ports
import time

PORT = 'COM6'
BAUD_RATE = 115200
L_SN = "0d"
R_SN = "04"
SECONDS = 0.5

def list_serial_ports():
    ports = list_ports.comports()
    for port in ports:
        print(f"Port: {port.device} - {port.description}")

def write_to_serial(msg):
    print(f"sending: {msg}")
    msg = msg + "\n\r"
    ser.write(msg.encode())
    time.sleep(0.1)  # Optional delay

def read_from_serial():
    if ser.in_waiting > 0:
        data = ser.read_all().decode('utf-8').strip()
        print(f"Received: {data}")

try:
    list_serial_ports()

    ser = s.Serial(PORT, BAUD_RATE)  # Replace 'COM3' with your serial port
    print("Serial port connected")

    write_to_serial(f"1 04 {L_SN} 00 00")
    write_to_serial(f"1 04 {R_SN} 00 00")
    write_to_serial(f"1 04 04 00 00")

    write_to_serial(f"1 04 {L_SN} f5 00 00 0f")
    read_from_serial()
    read_from_serial()
    
    write_to_serial(f"1 04 {R_SN} f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 04 04 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 07 02 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 07 12 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 07 03 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 07 13 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

except s.SerialException as e:
    print(f"Error: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed")