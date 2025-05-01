import serial as s
import numpy as np
import numpy.random as r
import time
from serial_utils import SerialUtil, list_serial_ports
from can_addr import CAN_DG, CAN_SN

PORT = 'COM7'
BAUD_RATE = 115200
SECONDS = 0.5

PING_PACKET_ID = "f5"
PING_PACKET_DATA = "00 00 0f"

try:
    list_serial_ports()
    query = input(f"{PORT} is correct? (y/n): ")
    if query == 'y':
        s = SerialUtil(PORT, BAUD_RATE)  # Replace 'COM3' with your serial port
        print("Serial port connected")

        s.read_from_serial(False)

        while True:
            # Generate an array of 16 random bytes (0-255)
            random_bytes = r.randint(0, 256, size=1, dtype=np.uint8)
            # Convert to hex string like '00' to 'ff'
            hex_string = ''.join(f'{b:02x}' for b in random_bytes)
            # Optional: space-separated version
            dg = ' '.join(f'{b:02x}' for b in random_bytes)

            # Generate an array of 16 random bytes (0-255)
            random_bytes = r.randint(0, 256, size=1, dtype=np.uint8)
            # Convert to hex string like '00' to 'ff'
            hex_string = ''.join(f'{b:02x}' for b in random_bytes)
            # Optional: space-separated version
            sn = ' '.join(f'{b:02x}' for b in random_bytes)

            dg = "04"
            sn = "02"

            s.write_to_serial(f"1 {dg} {sn} {PING_PACKET_ID} {PING_PACKET_DATA}")
            time.sleep(0.01)

except s.SerialException as e:
    print(f"Error: {e}")

finally:
    if 's' in locals() and s.ser.is_open:
        s.ser.close()
        print("Serial port closed")