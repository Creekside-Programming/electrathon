from machine import I2C
import time

# Register addresses
_CONFIG      = 0x00
_ADCCFG      = 0x01
_SHUNTCAL    = 0x02
_VSHUNT      = 0x04
_VBUS        = 0x05
_DIETEMP     = 0x06
_CURRENT     = 0x07
_POWER       = 0x08
_ENERGY      = 0x09
_CHARGE      = 0x0A
_MFG_UID     = 0x3E
_DVC_UID     = 0x3F

# Constants
_TEXAS_INSTRUMENTS_ID = 0x5449
_INA228_DEVICE_ID     = 0x228


class INA228:
    def __init__(self, i2c: I2C, addr=0x40):
        self.i2c = i2c
        self.addr = addr

        self.buf3 = bytearray(3)
        self.buf5 = bytearray(5)

        # Check manufacturer ID
        man = self.read_u16(_MFG_UID)
        if man != _TEXAS_INSTRUMENTS_ID:
            raise RuntimeError("INA228 not found (bad manufacturer ID)")

        # Check device ID
        dev = self.read_u16(_DVC_UID) >> 4
        if dev != _INA228_DEVICE_ID:
            raise RuntimeError("INA228 wrong device ID")

        # Default calibration
        self.set_calibration(0.015, 10.0)

    # -----------------------------
    # Low-level register access
    # -----------------------------

    def read_u16(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (data[0] << 8) | data[1]

    def write_u16(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([(value >> 8) & 0xFF, value & 0xFF]))

    def read_u24(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self.buf3)
        return (self.buf3[0] << 16) | (self.buf3[1] << 8) | self.buf3[2]

    def read_u40(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self.buf5)
        v = 0
        for b in self.buf5:
            v = (v << 8) | b
        return v

    # -----------------------------
    # Calibration
    # -----------------------------

    def set_calibration(self, shunt_res, max_current):
        self.shunt_res = shunt_res
        self.current_lsb = max_current / (1 << 19)

        cal = int(13107.2 * 1_000_000 * shunt_res * self.current_lsb)
        self.write_u16(_SHUNTCAL, cal)
        time.sleep_ms(1)

    # -----------------------------
    # Measurements
    # -----------------------------

    @property
    def bus_voltage(self):
        raw = self.read_u24(_VBUS)
        return (raw >> 4) * 195.3125e-6

    @property
    def shunt_voltage(self):
        raw = self.read_u24(_VSHUNT)
        if raw & 0x800000:
            raw -= 0x1000000
        return (raw / 16.0) * 312.5e-9

    @property
    def current(self):
        raw = self.read_u24(_CURRENT)
        if raw & 0x800000:
            raw -= 0x1000000
        return (raw / 16.0) * self.current_lsb

    @property
    def power(self):
        raw = self.read_u24(_POWER)
        return raw * 3.2 * self.current_lsb

    @property
    def energy(self):
        raw = self.read_u40(_ENERGY)
        return raw * 16.0 * 3.2 * self.current_lsb

    @property
    def charge(self):
        raw = self.read_u40(_CHARGE)
        if raw & (1 << 39):
            raw |= -1 << 40
        return raw * self.current_lsb

    @property
    def die_temperature(self):
        raw = self.read_u16(_DIETEMP)
        return raw * 7.8125e-3