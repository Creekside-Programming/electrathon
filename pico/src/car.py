from machine import I2C, Pin
from lib import BatteryStatusPacket
from rylr896 import RYLR896
from ina228 import INA228
from common import network_id
import time

ADDRESS = 0

lora = RYLR896(1, Pin(8), Pin(9))
lora.init_lora(network_id, ADDRESS)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

ina228 = INA228()

while True:
    battery_packet = BatteryStatusPacket(11.9, 23.4, 35.2)

    lora.send(1, str(battery_packet.pack()))
    
    time.sleep(1)