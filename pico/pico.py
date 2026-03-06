from machine import Pin
from rylr896 import RYLR896

ADDRESS = 0
NETWORK_ID = 5

lora = RYLR896(1, Pin(8), Pin(9))

lora.init_lora(NETWORK_ID, ADDRESS)

lora.send(1, "Hello world!")

# while True:
#     if uart.any():
#         data = uart.read()
#         if data is not None:
#             print(str(data.decode("utf-8")))

#     time.sleep(0.1)