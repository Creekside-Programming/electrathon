from machine import UART, Pin
import time

# imagine this as a dataclass
class ReceivedMessageData:
    address: int
    """Transmitter Address ID"""
    length: int
    """Data Length"""
    data: str
    """Data"""
    rssi: int
    """Received Signal Strength Indicator"""
    snr: int
    """Signal-to-noise ratio"""

    def __init__(self, address: int, length: int, data: str, rssi: int, snr: int):
        self.address = address
        self.length = length
        self.data = data
        self.rssi = rssi
        self.snr = snr

    def __str__(self) -> str:
        return f"ReceivedMessageData[address={self.address},length={self.length},data={self.data},rssi={self.rssi},snr={self.snr}]"

class RYLR896:
    def __init__(self, uart_id: int, tx_pin: Pin, rx_pin: Pin):
        self.uart = UART(uart_id, baudrate=115200, tx=tx_pin, rx=rx_pin, timeout=1000)

        self.band = 915000000
        self.parameter = [10, 7, 1, 7]

    # --- Internal Methods ---
    def _print(self, message: str) -> None:
        print(f"[RYLR896] {message}")

    def _read_response(self, timeout_ms: int = 1500) -> str:
        """Read UART until timeout or newline. Returns raw decoded string."""
        start = time.ticks_ms()
        buffer = b""

        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    buffer += chunk
                    # Many AT responses end with \r\n
                    if b"\r\n" in buffer:
                        break
            time.sleep_ms(1)

        try:
            return buffer.decode("utf-8").strip()
        except UnicodeError:
            return ""

    def _send_command(self, cmd: str, expect_ok: bool = True, timeout_ms: int = 1500) -> str:
        """Send a command and return the response. Optionally check for \"OK\"."""
        self._print(f"Sending command: {cmd}")
        self.uart.write(cmd + "\r\n")

        response = self._read_response(timeout_ms)
        self._print(f"Response: {response}")

        if expect_ok and "OK" not in response:
            self._print("WARNING: Expected 'OK' but did not receive it")

        return response
    
    # --- Public Methods ---
    def init_lora(self, network_id: int, address: int) -> None:
        self._print(f"Initializing LoRa with address {address} on network id {network_id}, band {self.band/1000000}MHz, parameter {self.parameter}")
        
        self._send_command(f"AT+NETWORKID={str(network_id)}")
        self._send_command(f"AT+ADDRESS={address}")
        self._send_command(f"AT+BAND={self.band}")
        self._send_command(f"AT+PARAMETER={",".join(map(str, self.parameter))}") # formats so [1,2,3] -> "1,2,3"

    def send(self, address: int, data: str) -> bool:
        """Send a message and return True if OK
        
        Parameters
        ----------
        address : int
            Address to send to, must be from 0-65535
        data : str
            ASCII Format, payload length must not exceed 240 bytes
        """

        # Check for parameter validity
        if address < 0 or address > 65535:
            self._print(f"Cannot send to address {address}: invalid address")
            return False

        if len(data) > 240:
            self._print(f"Cannot send to address {address}: Payload Length exceeds maximum")
            return False

        self._print(f"Sending to address {address}: {data}")
        resp = self._send_command(f"AT+SEND={address},{len(data)},{data}")

        return "OK" in resp

    def read_message(self, timeout_ms: int = 50):
        """Return one parsed RCV message, or None if nothing available."""
        # If no data, wait briefly
        if not self.uart.any():
            time.sleep_ms(timeout_ms)
            if not self.uart.any():
                return None

        raw = self.uart.read()
        if not raw:
            return None

        try:
            text = raw.decode("utf-8")
        except:
            return None

        # Split into lines (handles multiple +RCV packets)
        lines = text.split("\r\n")

        for line in lines:
            if not line.startswith("+RCV="):
                continue

            # Example: +RCV=0,31,b'chs-elec...',-51,57
            parts = line.split(",")

            if len(parts) < len("+RCV="):
                # incomplete line, skip it
                continue

            try:
                address = int(parts[0].split("=")[1])
                length  = int(parts[1])
                data    = parts[2]
                rssi    = int(parts[3])
                snr     = int(parts[4])
            except ValueError:
                continue  # skip malformed lines

            return ReceivedMessageData(address, length, data, rssi, snr)

        return None

    def read_forever(self) -> None:
        """This function runs forever and prints any data it receives. This should probably be at the end of the program."""
        self._print("Listening for incoming LoRa messages...")
        while True:
            msg = self.read_message()
            if msg:
                print(str(msg))
            time.sleep_ms(5)
