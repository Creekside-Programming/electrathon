import asyncio
import struct
import ast
from typing import List, Literal

from .serial import start_serial_thread, buffer_lock, line_buffer
from .lib import BatteryStatusPacket, ReceivedDataMessage, SystemMessage

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BatteryStatus(BaseModel):
    voltage: float
    amperage: float


class BatteryMessage(BaseModel):
    """Represents an update to battery status"""

    type: Literal["battery"]
    data: List[BatteryStatus]


@app.on_event("startup")
def startup_event():
    start_serial_thread()


@app.get("/are_you_alive")
def are_you_alive():
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        with buffer_lock:
            last_line = line_buffer[-1] if line_buffer else None

        if last_line == None:
            await asyncio.sleep(1)
            continue

        rdm = ReceivedDataMessage.from_message_data(SystemMessage.get_message_data_from_string(last_line))
        packet = BatteryStatusPacket.from_packed(ast.literal_eval(rdm.data)) # literal_eval converts a str that looks like a stringified bytes back into a bytes

        message = BatteryMessage(
            type="battery",
            data=[
                BatteryStatus(voltage=packet.voltage, amperage=0.0),
            ],
        )

        await websocket.send_json(message.model_dump())
        await asyncio.sleep(1)