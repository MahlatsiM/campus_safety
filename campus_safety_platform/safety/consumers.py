# safety/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import asyncio
import random

class SafetyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.send_task = asyncio.create_task(self.send_data_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "send_task"):
            self.send_task.cancel()

    async def send_data_loop(self):
        while True:
            try:
                for category in ["safety", "route", "loadshedding"]:
                    data = {
                        "category": category,
                        "value": random.randint(0, 10),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await self.send(text_data=json.dumps(data))
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
