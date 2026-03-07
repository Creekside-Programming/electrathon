from machine import Pin
from rylr896 import RYLR896
from common import network_id

ADDRESS = 1

lora = RYLR896(1, Pin(8), Pin(9))

lora.init_lora(network_id, ADDRESS)

lora.send(1, "Hello world!")

lora.read_forever()