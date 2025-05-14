import serial
import struct
import time
from serial_utils import SerialUtil, list_serial_ports

PORT = 'COM18'
BAUD_RATE = 115200
NODE_ID = 0x3F  # Odrive node_id from config (63)
PRIORITY = 1    # Default priority for CAN packets

# Map Odrive parameters to cmd_id and data (simplified, based on CANSimple protocol)
# cmd_id values are hypothetical; replace with actual Odrive CANSimple cmd_ids
COMMANDS = [
    {"name": "dc_bus_overvoltage_trip_level", "cmd_id": 0x01, "value": 30.0, "type": "float"},
    {"name": "dc_bus_undervoltage_trip_level", "cmd_id": 0x02, "value": 10.5, "type": "float"},
    {"name": "dc_max_positive_current", "cmd_id": 0x03, "value": float('inf'), "type": "float"},
    {"name": "dc_max_negative_current", "cmd_id": 0x04, "value": -float('inf'), "type": "float"},
    {"name": "brake_resistor0.enable", "cmd_id": 0x05, "value": 0, "type": "int32"},
    {"name": "motor.motor_type", "cmd_id": 0x06, "value": 0, "type": "int32"},  # HIGH_CURRENT = 0
    {"name": "motor.pole_pairs", "cmd_id": 0x07, "value": 7, "type": "int32"},
    {"name": "motor.torque_constant", "cmd_id": 0x08, "value": 0.02642172523961661, "type": "float"},
    {"name": "motor.current_soft_max", "cmd_id": 0x09, "value": 9.25, "type": "float"},
    {"name": "motor.current_hard_max", "cmd_id": 0x0A, "value": 22.025, "type": "float"},
    {"name": "motor.calibration_current", "cmd_id": 0x0B, "value": 10.0, "type": "float"},
    {"name": "motor.resistance_calib_max_voltage", "cmd_id": 0x0C, "value": 2.0, "type": "float"},
    {"name": "calibration_lockin.current", "cmd_id": 0x0D, "value": 10.0, "type": "float"},
    {"name": "motor_thermistor.enabled", "cmd_id": 0x0E, "value": 0, "type": "int32"},
    {"name": "controller.control_mode", "cmd_id": 0x0F, "value": 2, "type": "int32"},  # VELOCITY_CONTROL = 2
    {"name": "controller.input_mode", "cmd_id": 0x10, "value": 2, "type": "int32"},  # VEL_RAMP = 2
    {"name": "controller.vel_limit", "cmd_id": 0x11, "value": 10.0, "type": "float"},
    {"name": "controller.vel_limit_tolerance", "cmd_id": 0x12, "value": 1.2, "type": "float"},
    {"name": "torque_soft_min", "cmd_id": 0x13, "value": -float('inf'), "type": "float"},
    {"name": "torque_soft_max", "cmd_id": 0x14, "value": float('inf'), "type": "float"},
    {"name": "trap_traj.accel_limit", "cmd_id": 0x15, "value": 10.0, "type": "float"},
    {"name": "controller.vel_ramp_rate", "cmd_id": 0x16, "value": 10.0, "type": "float"},
    {"name": "can.protocol", "cmd_id": 0x17, "value": 0, "type": "int32"},  # SIMPLE = 0
    {"name": "can.baud_rate", "cmd_id": 0x18, "value": 250000, "type": "int32"},
    {"name": "can.node_id", "cmd_id": 0x19, "value": 63, "type": "int32"},
    {"name": "can.heartbeat_msg_rate_ms", "cmd_id": 0x1A, "value": 100, "type": "int32"},
    {"name": "can.encoder_msg_rate_ms", "cmd_id": 0x1B, "value": 0, "type": "int32"},
    {"name": "can.iq_msg_rate_ms", "cmd_id": 0x1C, "value": 0, "type": "int32"},
    {"name": "can.torques_msg_rate_ms", "cmd_id": 0x1D, "value": 0, "type": "int32"},
    {"name": "can.error_msg_rate_ms", "cmd_id": 0x1E, "value": 0, "type": "int32"},
    {"name": "can.temperature_msg_rate_ms", "cmd_id": 0x1F, "value": 0, "type": "int32"},
    {"name": "can.bus_voltage_msg_rate_ms", "cmd_id": 0x20, "value": 0, "type": "int32"},
    {"name": "enable_watchdog", "cmd_id": 0x21, "value": 0, "type": "int32"},
    {"name": "encoder_bandwidth", "cmd_id": 0x22, "value": 100, "type": "int32"},
    {"name": "hall_encoder0.enabled", "cmd_id": 0x23, "value": 1, "type": "int32"},
    {"name": "load_encoder", "cmd_id": 0x24, "value": 2, "type": "int32"},  # HALL_ENCODER0 = 2
    {"name": "commutation_encoder", "cmd_id": 0x25, "value": 2, "type": "int32"},  # HALL_ENCODER0 = 2
    {"name": "enable_uart_a", "cmd_id": 0x26, "value": 0, "type": "int32"},
]

def float_to_bytes(value):
    """Convert float to 4-byte little-endian hex string."""
    if value == float('inf') or value == -float('inf'):
        value = 0  # Odrive may not handle inf; set to 0 or max value
    return struct.pack('<f', value).hex()

def int32_to_bytes(value):
    """Convert int32 to 4-byte little-endian hex string."""
    return struct.pack('<i', value).hex()

def format_data_bytes(data_hex):
    """Format hex string into space-separated two-digit pairs."""
    return ' '.join(data_hex[i:i+2] for i in range(0, len(data_hex), 2))

try:
    list_serial_ports()
    query = input(f"{PORT} is correct? (y/n): ")
    if query.lower() == 'y':
        ser = SerialUtil(PORT, BAUD_RATE)
        print("Serial port connected")

        ser.read_from_serial(False)

        for cmd in COMMANDS:
            # Calculate CAN ID: (node_id << 5) | cmd_id
            can_id = (NODE_ID << 5) | cmd["cmd_id"]
            # Convert CAN ID to dg and sn for PSoC
            dg = (can_id >> 6) & 0xF  # Bits 10:6
            sn = can_id & 0x3F        # Bits 5:0
            # Format dg and sn as two hex digits
            dg_str = f"{dg:02x}"
            sn_str = f"{sn:02x}"

            # Convert value to data bytes
            if cmd["type"] == "float":
                data_hex = float_to_bytes(cmd["value"])
            else:  # int32
                data_hex = int32_to_bytes(cmd["value"])
            data_str = format_data_bytes(data_hex)
            
            # Construct serial command
            serial_cmd = f"{PRIORITY} {dg_str} {sn_str} {data_str}"
            print(f"Sending: {serial_cmd}")
            ser.write_to_serial(serial_cmd)
            time.sleep(0.01)  # Small delay between commands

except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    if 'ser' in locals() and ser.ser.is_open:
        ser.ser.close()
        print("Serial port closed")
