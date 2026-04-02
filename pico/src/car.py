from machine import Pin
from lib import BatteryStatusPacket
from rylr896 import RYLR896
from common import network_id
import time

ADDRESS = 0

lora = RYLR896(1, Pin(8), Pin(9))

lora.init_lora(network_id, ADDRESS)

while True:
    battery_packet = BatteryStatusPacket(11.9, 23.4, 35.2)

    lora.send(1, str(battery_packet.pack()))
    
    time.sleep(1)