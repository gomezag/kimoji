import asyncio
import random
import threading
import time

from fastapi import HTTPException, WebSocket, status

from kimoji.lib.crud import get_simulation_run, edit_simulation_run
from kimoji.lib.db import SessionLocal


class ConnectionManager:
    def __init__(self):
        self.active_channels: list[SimulationRunChannel] = []

    async def connect(self, websocket: WebSocket, sim_id: int):
        if sim_id not in [ch.simulation_id for ch in self.active_channels]:
            channel = SimulationRunChannel(sim_id)
            self.active_channels.append(channel)
        else:
            channel = next(ch for ch in self.active_channels if sim_id == ch.simulation_id)
        await channel.connect(websocket)

    def disconnect(self, websocket: WebSocket):
        for ch in self.active_channels:
            if websocket in ch.active_connections:
                ch.disconnect(websocket)
                if not ch.active_connections:
                    ch.__del__()


class SimulationRunChannel:
    def __init__(self, sim_id: int):
        self._db = SessionLocal()
        self.simulation_id = sim_id
        self.active_connections: list[WebSocket] = []
        self.broadcast_thread = SimulationRunBroadcaster(self)
        run = get_simulation_run(self._db, sim_id, key='id')
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation run ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        self.broadcast_thread.start()

    def __del__(self):
        self._db.close()
        self.broadcast_thread.stop()
        for conn in self.active_connections:
            conn.close()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_sim_loss(self):
        run = edit_simulation_run(self._db, self.simulation_id, random.random()*100, 'loss')
        message = "{:.2f}".format(run.loss)
        if message:
            for connection in self.active_connections:
                await connection.send_text(message)


class SimulationRunBroadcaster(threading.Thread):

    def __init__(self,  channel: SimulationRunChannel, *args, **kwargs):
        self.channel = channel
        super(SimulationRunBroadcaster, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.loop = asyncio.new_event_loop()

    def stop(self):
        self.loop.close()
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped:
            self.loop.run_until_complete(self.channel.broadcast_sim_loss())
            time.sleep(3)


manager = ConnectionManager()
