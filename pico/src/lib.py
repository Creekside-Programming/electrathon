import struct

# ---
# MARK: SystemMessage
# ---

class SystemMessage:
    ID_CHAR: str = "@"
    """Character used to identify a message as a system message. Do not change."""

    @classmethod
    def message_id(cls) -> str:
        ...
    @property
    def message_data(self) -> str:
        ...

    def __str__(self) -> str:
        return f"{self.ID_CHAR}{self.message_id()}[{self.message_data}]"

    @classmethod
    def from_message_data(cls, message_data: str) -> "SystemMessage":
        """When given message_data from this message, handle it and produce a new message instance"""
        ...

# pretend this is a dataclass (can't be bc micropython)
class ReceivedDataMessage(SystemMessage):
    """Formerly known as ReceivedMessageData
    
    Described the format for logging a message received over LoRa"""

    @classmethod
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
    def message_id(cls) -> str:
        return "RDM"

    @property
    def message_data(self) -> str:
        return f"a={self.address},l={self.length},d={self.data},r={self.rssi},s={self.snr}"

# ---
# MARK: Packet
# ---
class Packet:
    """Describes packets to be sent along the RYLR896 from the car to the pits over LoRa"""

    @classmethod
    def is_valid_packed_packet(cls, raw: bytes) -> bool:
        if len(raw) < 12:
            return False

        # Check header (exact 8-byte match with padding)
        expected_header = cls.HEADER.encode('ascii')[:8].ljust(8, b'\x00')
        if raw[:8] != expected_header:
            return False

        # Check packet_id is valid ASCII (4 bytes)
        try:
            raw[8:12].decode('ascii')
        except UnicodeDecodeError:
            return False

        return True

    @classmethod
    def from_packed(cls, raw: bytes) -> "Packet":
        """NOTE: make sure that packet is valid using `is_valid_packed_packet`"""
        ...

    HEADER: str = "chs-elec"
    """In case someone is somehow on the same network id as us then this header should be used to 100% ensure that the data we are parsing is actually ours"""

    @classmethod
    def packet_id(cls) -> str:
        ...
 
    def data(self) -> bytes:
        ...

    def pack(self) -> bytes:
        header = Packet.HEADER.encode("ascii")[:8].ljust(8, b'\x00')
        packet_id = self.packet_id().encode("ascii")[:4].ljust(4, b'\x00')
        return header + packet_id + self.data()

class BatteryStatusPacket(Packet):
    """Generic battery status update packet. Will be sent approx. every one second"""

    @classmethod
    def from_packed(cls, raw: bytes) -> "BatteryStatusPacket":
        if not cls.is_valid_packed_packet(raw):
            raise ValueError("Cannot parse packed packet "+str(raw)+", it is invalid")
        
        voltages = struct.unpack(cls.ENCODE_FORMAT, raw[12:24])

        return cls(voltages[0], voltages[1], voltages[2])

    @classmethod
    def packet_id(cls) -> str:
        return "BATT"

    def data(self) -> bytes:
        return struct.pack(BatteryStatusPacket.ENCODE_FORMAT, self.voltage1, self.voltage2, self.voltage3)

    ENCODE_FORMAT: str = "fff"

    #! note: this is temp data; actual numbers we get are still TBD
    voltage1: float
    voltage2: float
    voltage3: float

    def __init__(self, voltage1: float, voltage2: float, voltage3: float) -> None:
        super().__init__()

        self.voltage1 = voltage1
        self.voltage2 = voltage2
        self.voltage3 = voltage3

class WarningPacket(Packet):
    """A warning from the *car* to the backend. Message cannot exceed `WarningPacket.MAXIMUM_LENGTH` characters.

    .. note::
        Not to be confused with :class:`WarningMessage`, which is a warning 
        from exclusively the pits pico (as the car can only communicate with 
        packets and not SystemMessages).

        NOTE: what was described above has not actually been implemented yet :-)
    
    ---

    If you want to get the data from this packet:
    ```python
    struct.unpack(BatteryStatusPacket.ENCODE_FORMAT, packet.data())
    ```
    """

    @classmethod
    def from_packed(cls, raw: bytes) -> "WarningPacket":
        if not cls.is_valid_packed_packet(raw):
            raise ValueError("Cannot parse packed packet "+str(raw)+", it is invalid")
        
        message = raw[12:(12 + cls.MAXIMUM_LENGTH)].decode("ascii")

        return cls(message)

    MAXIMUM_LENGTH: int = 64 # TODO: is 64 a good choice?
    """Maximum length of warning message"""

    @classmethod
    def packet_id(cls) -> str:
        return "WARN"

    def data(self) -> bytes:
        return self.message.encode('ascii')[:WarningPacket.MAXIMUM_LENGTH].ljust(WarningPacket.MAXIMUM_LENGTH, b'\x00')

    message: str
    """Warning message to send (truncated if length is greater than :attr:`MAXIMUM_LENGTH`)."""

    def __init__(self, message: str):
        self.message = message