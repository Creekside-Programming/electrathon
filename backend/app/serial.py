from collections import deque
import threading
import serial

SERIAL_PORT = "/dev/ttyACM1"

buffer_lock = threading.Lock()
line_buffer = deque(maxlen=10)

def serial_reader():
    ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)

    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            with buffer_lock:
                line_buffer.append(line)
                print("serial: "+line)

def start_serial_thread():
    thread = threading.Thread(target=serial_reader, daemon=True)
    thread.start()