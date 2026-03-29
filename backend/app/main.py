import asyncio
import random
from typing import List, Literal

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


@app.get("/are_you_alive")
def are_you_alive():
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = BatteryMessage(
            type="battery",
            data=[
                BatteryStatus(
                    voltage=round(random.uniform(10.0, 14.0), 1),
                    amperage=round(random.uniform(40.0, 60.0), 1),
                )
            ],
        )

        await websocket.send_json(message.model_dump())

        await asyncio.sleep(1)  # Simulate delay between updates
