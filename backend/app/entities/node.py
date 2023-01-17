from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from beanie import PydanticObjectId
from beanie.operators import And, Eq
from pydantic import BaseModel

from ..config import config as Config
from ..services.database.custom_document import CustomDocument
from ..utils.enums import NodeState

logger = logging.getLogger(__name__)


class Node(CustomDocument):
    nodeID: int
    nodeName: str
    application: PydanticObjectId
    state: NodeState
    lastSeenAt: datetime

    def start_rec(self):
        self._publish("command", "start:0")

    def stop_rec(self):
        self._publish("command", "stop")

    def set_demo_1(self):
        self._publish("command", "start:1")

    def set_demo_2(self):
        self._publish("command", "start:2")

    def set_hv(self, detector: int, sipm: int, value: int):
        data = json.dumps(
            {"type": "hv", "detector": detector, "sipm": sipm, "value": value}
        )
        self._publish("set", data)

    def set_window_low(self, detector: int, sipm: int, window_number: int, value: int):
        data = json.dumps(
            {
                "type": "window_low",
                "n": window_number,
                "detector": detector,
                "sipm": sipm,
                "value": value,
            }
        )
        self._publish("set", data)

    def set_window_high(self, detector: int, sipm: int, window_number: int, value: int):
        data = json.dumps(
            {
                "type": "window_high",
                "n": window_number,
                "detector": detector,
                "sipm": sipm,
                "value": value,
            }
        )
        self._publish("set", data)

    def _publish(self, subtopic: str, data: str | bytes):
        from ..services.mqtt import publish

        publish(f"{str(self.application)}/{self.nodeID}/{subtopic}", data)

    async def just_seen(self) -> bool:
        self.lastSeenAt = datetime.now()

        if self.state != NodeState.ERROR:
            await self.save()
            return False

        self.state = NodeState.READY

        if await self.has_pending_alert():
            self.state = NodeState.ALERT_READY

        await self.save()
        return True

    async def on_start_rec(self):
        self.state = NodeState.RUNNING
        await self.save()

    async def on_stop_rec(self):
        self.state = NodeState.READY
        await self.save()

    async def on_alert(self):
        self.state = NodeState.ALERT_READY
        await self.save()

    async def on_handle(self):
        self.state = NodeState.READY

        if self.is_timed_out():
            self.state = NodeState.ERROR

        await self.save()

    async def on_launch(self):
        from ..services.database.models import NodeSettings
        from ..utils.node_settings import send_update_settings

        self.state = NodeState.READY

        if await self.has_pending_alert():
            self.state = NodeState.ALERT_READY

        await self.save()

        settings = await NodeSettings.find_one(NodeSettings.node == self.id)
        if settings is None:
            logger.info("No settings found for node: %s", self)
            return

        await send_update_settings(self, settings)

    async def on_timeout(self):
        if self.state != NodeState.ALERT_READY:
            self.state = NodeState.ERROR

        await self.save()

    async def on_window_reading(self):
        if self.state != NodeState.RUNNING:
            self.stop_rec()

    async def has_pending_alert(self) -> bool:
        from ..services.database.models import Alert

        return (
            await Alert.find_one(
                And(Eq(Alert.node, self.id), Eq(Alert.isHandled, False))
            )
        ) is not None

    def is_timed_out(self) -> bool:
        return (datetime.now() - self.lastSeenAt) > timedelta(
            seconds=Config.app.NODE_TIMEOUT_INTERVAL
        )

    @classmethod
    async def from_id(cls, nodeID: int, applicationID: str) -> Node | None:
        return await cls.find_one(
            And(
                Eq(cls.nodeID, nodeID),
                Eq(cls.application, PydanticObjectId(applicationID)),
            )
        )

    class Serialized(BaseModel):
        nodeID: int
        nodeName: str
        application: str
        state: str
        lastSeenAt: int
        unhandledAlertIDs: list[str]

    async def serialize(self) -> Node.Serialized:
        from ..services.database.models import Alert

        unhandledAlerts = await Alert.find(
            And(Eq(Alert.node, self.id), Eq(Alert.isHandled, False))
        ).to_list()
        unhandledAlertIDs = [str(x.id) for x in unhandledAlerts]

        return Node.Serialized(
            nodeID=self.nodeID,
            nodeName=self.nodeName,
            application=str(self.application),
            state=NodeState.to_irma_ui_state(self.state),
            lastSeenAt=int(self.lastSeenAt.timestamp()),
            unhandledAlertIDs=unhandledAlertIDs,
        )
