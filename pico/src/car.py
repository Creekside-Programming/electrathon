from machine import I2C, Pin
from lib import BatteryStatusPacket
from rylr896 import RYLR896
from ina228 import INA228
from common import network_id
import time

# Pin configuration
PIN_LORA_TX = Pin(8)
PIN_LORA_RX = Pin(9)

PIN_I2C_SCL = Pin(15)
PIN_I2C_SDA = Pin(14)

ADDRESS = 0 # LoRa Address

lora = RYLR896(1, PIN_LORA_TX, PIN_LORA_RX)
lora.init_lora(network_id, ADDRESS)

i2c = I2C(1, scl=PIN_I2C_SCL, sda=PIN_I2C_SDA, freq=400000)

ina228 = INA228(i2c)

while True:
    voltage = ina228.bus_voltage

    print("[CAR] Voltage: "+str(voltage))

    battery_packet = BatteryStatusPacket(voltage)

    lora.send(1, str(battery_packet.pack()))
    
    time.sleep(1)