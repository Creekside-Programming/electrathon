from abc import ABC, abstractmethod
from typing import override

class SystemMessage(ABC):
    ID_CHAR: str = "@"
    """Character used to identify a message as a system message. Do not change."""

    @classmethod
    @abstractmethod
    def message_id(cls) -> str:
        ...
    @property
    @abstractmethod
    def message_data(self) -> str:
        ...

    def __str__(self) -> str:
        return f"{self.ID_CHAR}{self.message_id()}[{self.message_data}]"

    @classmethod
    @abstractmethod
    def from_message_data(cls, message_data: str) -> "SystemMessage":
        """When given message_data from this message, handle it and produce a new message instance"""
        ...

# pretend this is a dataclas (can't be bc micropython)
class ReceivedDataMessage(SystemMessage):
    """Formerly known as ReceivedMessageData
    
    Described the format for logging a message received over LoRa"""

    @classmethod
    @override
    def from_message_data(cls, message_data: str) -> "ReceivedDataMessage":
        data = dict(pair.split("=") for pair in message_data.split(","))

        return cls(
            address=int(data["a"]),
            length=int(data["l"]),
            data=data["d"],
            rssi=float(data["r"]),
            snr=float(data["s"]),
        )

    address: int
    """Transmitter Address ID"""
    length: int
    """Data Length"""
    data: str
    """Data"""
    rssi: float
    """Received Signal Strength Indicator"""
    snr: float
    """Signal-to-noise ratio"""

    def __init__(self, address: int, length: int, data: str, rssi: float, snr: float):
        self.address = address
        self.length = length
        self.data = data
        self.rssi = rssi
        self.snr = snr

        if length != len(data): # why not
            print(f"Warning: length of {length} for RDM {data} is not consistent, something has gone terribly wrong.")

    @classmethod
    @override
    def message_id(cls) -> str:
        return "RDM"

    @property
    @override
    def message_data(self) -> str:
        return f"a={self.address},l={self.length},d={self.data},r={self.rssi},s={self.snr}"

print(SystemMessage.ID_CHAR.__doc__)