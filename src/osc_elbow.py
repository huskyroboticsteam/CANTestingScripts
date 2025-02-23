import serial as s
import numpy as np
from serial.tools import list_ports
import time

PORT = 'COM6'
BAUD_RATE = 115200
L_SN = "0d"
R_SN = "04"
SECONDS = 2

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
    write_to_serial(f"1 04 01 00 00")
    write_to_serial(f"1 04 02 00 00")

    write_to_serial(f"1 04 {L_SN} f5 00 00 0f")
    read_from_serial()
    read_from_serial()
    
    write_to_serial(f"1 04 {R_SN} f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 04 04 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 04 01 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    write_to_serial(f"1 04 02 f5 00 00 0f")
    read_from_serial()
    read_from_serial()

    # for _ in range(100):
    #     write_to_serial(f"1 04 01 f5 00 00 0f")
    #     read_from_serial()
    #     read_from_serial()

    #     write_to_serial(f"1 04 02 f5 00 00 0f")
    #     read_from_serial()
    #     read_from_serial()

    last_data = 0
    scaled = 0
    while True:
        data = input("PWM (%) to send (q to quit): ")
        print("data", data)

        if data:
            scaled = int(int(data) / 100.0 * np.iinfo(np.int16).max)
            last_data = scaled
        else:
            data = last_data

        twos_c = np.binary_repr(scaled, width=16)
        print("scaled:", scaled)
        print("2c:", twos_c)
        
        data_post = str(hex(int(twos_c, 2)))[2:]
        data_post = "0" * (4-len(data_post)) + data_post
        print(data_post)
        data_post = data_post[:2] + " " + data_post[2:]

        write_to_serial(f"1 04 01 03 {data_post}")

    # for _ in range(1):
    #     start_time = time.time()
    #     while (time.time() - start_time < SECONDS):
    #         write_to_serial(f"1 04 04 03 19 98")

        # start_time = time.time()
        # while (time.time() - start_time < SECONDS):
        #     write_to_serial(f"1 04 04 03 ec 00")


except s.SerialException as e:
    print(f"Error: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed")