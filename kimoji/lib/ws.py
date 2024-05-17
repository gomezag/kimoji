import logging
import random
import threading
import time

from fastapi import HTTPException, WebSocket, status

from kimoji.lib.crud import get_simulation_run, edit_simulation_run
from kimoji.lib.db import SessionLocal

logger = logging.getLogger("kimoji")

broadcast_lock = threading.Lock()


class ConnectionManager:
    def __init__(self):
        logger.info('Starting connection manager.')
        self.active_channels: list[SimulationRunChannel] = []

    async def connect(self, websocket: WebSocket, sim_id: int):
        if sim_id not in [ch.simulation_id for ch in self.active_channels]:
            logger.debug('Starting new channel.')
            channel = SimulationRunChannel(sim_id)
            await channel.connect(websocket)
            self.active_channels.append(channel)
            channel.broadcast_thread.start()
        else:
            logger.debug('Adding connection to existing channel.')
            channel = next(ch for ch in self.active_channels if sim_id == ch.simulation_id)
            await channel.connect(websocket)
        return channel

    async def disconnect(self, websocket: WebSocket):
        for ch in self.active_channels:
            if websocket in ch.active_connections:
                await ch.disconnect(websocket)


class SimulationRunChannel:
    def __init__(self, sim_id: int):
        self._db = SessionLocal()
        self.simulation_id = sim_id
        self.active_connections: list[WebSocket] = []

        run = get_simulation_run(self._db, sim_id, key='id')
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation run ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        self._last_loss = run.loss
        self.broadcast_thread = SimulationRunBroadcaster(self)

    def __del__(self):
        self.broadcast_thread.stop()
        for conn in self.active_connections:
            try:
                conn.close()
            except RuntimeError:
                pass

    @property
    def last_loss(self):
        return self._last_loss

    def update_loss(self):
        logger.debug('Updating Loss')
        run = edit_simulation_run(self._db, self.simulation_id, random.random()*100, 'loss')
        if run:
            self._last_loss = run.loss
        else:
            for connection in self.active_connections:
                connection.close(1001, reason='The simulation run has been deleted')
            del self

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            await websocket.close()
        except RuntimeError:
            pass
        self.active_connections.remove(websocket)
        if not self.active_connections:
            self.broadcast_thread.stop()
            del self


class SimulationRunBroadcaster(threading.Thread):

    def __init__(self,  channel: SimulationRunChannel, *args, **kwargs):
        self.channel = channel
        super(SimulationRunBroadcaster, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        logger.debug('Stopping updater')
        self._stop_event.set()

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped:
            self.channel.update_loss()
            time.sleep(3)


manager = ConnectionManager()
