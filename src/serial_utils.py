import serial
from serial.tools import list_ports
import time

__all__ = ["list_serial_ports", "SerialUtil"]

def list_serial_ports():
    ports = list_ports.comports()
    for port in ports:
        print(f"Port: {port.device} - {port.description}")


class SerialUtil:

    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud)

    def write_to_serial(self, msg):
        print(f"sending: {msg}")
        msg = msg + "\n\r"
        self.ser.write(msg.encode())
        time.sleep(0.1)  # Optional delay

    def read_from_serial(self, log=True):
        if self.ser.in_waiting > 0:
            data = self.ser.read_all().decode('utf-8').strip()
            if log:
                print(f"Received: {data}")
            return data
        else:
            return None
        
    def read_latest_line(self, log=True):
        data = self.read_from_serial(False)
        if data == None:
            return None
        
        data = data.split("\n")[-1]
        if log:
            print(f"Received: {data}")
        return data

