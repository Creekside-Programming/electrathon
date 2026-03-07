from machine import Pin
from rylr896 import RYLR896
from common import network_id, packet_format, sync_header
import struct
import time

ADDRESS = 0

lora = RYLR896(1, Pin(8), Pin(9))

lora.init_lora(network_id, ADDRESS)

while True:
    voltage = 12.5
    amperage = 3.7

    data = struct.pack(packet_format, sync_header, voltage, amperage)

    lora.send(1, str(data))
    
    time.sleep(1)

