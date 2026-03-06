from machine import UART, Pin
import time

class RYLR896:
    def __init__(self, uart_id: int, tx_pin: Pin, rx_pin: Pin):
        self.uart = UART(uart_id, baudrate=115200, tx=tx_pin, rx=rx_pin)

        self.band = 915000000
        self.parameter = [10, 7, 1, 7]

    def _print(self, message: str) -> None:
        print(f"[RYLR896] {message}")

    def _send_command(self, cmd: str) -> None:
        self.uart.write(cmd + "\r\n")
        time.sleep(0.5)
        if self.uart.any():
            data = self.uart.read()
            if data is not None:
                response = data.decode("utf-8")
                self._print("Response: " + response)

    def init_lora(self, network_id: int, address: int) -> None:
        self._print(f"Initializing LoRa with address {address} on network id {network_id}, band {self.band/1000000}MHz, parameter {self.parameter}")
        self._send_command(f"AT+NETWORKID={str(network_id)}")
        self._send_command(f"AT+ADDRESS={address}")
        self._send_command(f"AT+BAND={self.band}")
        self._send_command(f"AT+PARAMETER={",".join(map(str, self.parameter))}") # formats so [1,2,3] -> "1,2,3"

    def send(self, address: int, data: str):
        self._print(f"Sending to {address}: {data}")
        self._send_command(f"AT+SEND={address},{len(data)},{data}")