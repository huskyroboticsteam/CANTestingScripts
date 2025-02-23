import serial as s
from serial_utils import SerialUtil, list_serial_ports
from can_addr import CAN_DG, CAN_SN

PORT = 'COM6'
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

        for dg_k, dg_v in CAN_DG.items():
            if dg_k in CAN_SN.keys():
                for sn_k, sn_v in CAN_SN[dg_k].items():
                    s.write_to_serial(f"1 {dg_v} {sn_v} {PING_PACKET_ID} {PING_PACKET_DATA}")
                    data = s.read_latest_line()
                    if data:
                        print(f">> {sn_k} in {dg_k} group: SUCCESS")
                    else:
                        print(f">> {sn_k} in {dg_k} group: FAIL")

except s.SerialException as e:
    print(f"Error: {e}")

finally:
    if 's' in locals() and s.ser.is_open:
        s.ser.close()
        print("Serial port closed")