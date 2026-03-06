from machine import UART, Pin
import time

ADDRESS = 0
NETWORK_ID = 5

# Initialize UART (adjust pins for your board)
uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

def send_command(cmd):
    uart.write(cmd + "\r\n")
    time.sleep(0.5)
    if uart.any():
        data = uart.read()
        if data is not None:
            response = data.decode("utf-8")
            print("Response:", response)

def send(address: int, data: str):
    send_command(f"AT+SEND={address},{len(data)},{data}")
        
def init_lora(network_id: int, address: int) -> None:
    print(f"Initializing LoRa with address {address} on network id {network_id}")
    send_command(f"AT+NETWORKID={str(network_id)}")
    send_command(f"AT+ADDRESS={address}")
    send_command(f"AT+BAND=915000000")
    # Format:
    #AT+PARAMETER=SF,BW,CR,Preamble
    send_command("AT+PARAMETER=10,7,1,7")

init_lora(NETWORK_ID, ADDRESS)

# Send message
# Format: AT+SEND=<address>,<length>,<message>
send(1, "Hello world!")

while True:
    if uart.any():
        data = uart.read()
        if data is not None:
            print(str(data.decode("utf-8")))
    
    time.sleep(0.1)