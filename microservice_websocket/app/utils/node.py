from datetime import datetime, timedelta

from beanie import PydanticObjectId

from ..config import config as Config
from ..services.database import Application, Node, NodeSettings
from .enums import NodeState, PayloadType
from .exceptions import NotFoundException


def update_state_total_reading(current_state: NodeState, dato: int) -> NodeState:
    if current_state == NodeState.ERROR:
        current_state = NodeState.READY

    if dato >= Config.app.ALERT_TRESHOLD and current_state == NodeState.READY:
        return NodeState.ALERT_READY

    return current_state


def update_state_window_reading(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY or current_state == NodeState.ERROR:
        current_state = NodeState.RUNNING
    elif current_state == NodeState.ALERT_READY:
        current_state = NodeState.ALERT_RUNNING

    return current_state


def update_state_start_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.READY or current_state == NodeState.ERROR:
        return NodeState.RUNNING

    return current_state


def update_state_end_rec(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.RUNNING or current_state == NodeState.ERROR:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.ALERT_READY

    return current_state


def update_state_keep_alive(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ERROR:
        return NodeState.READY

    return current_state


def update_state_handle_alert(current_state: NodeState, *args) -> NodeState:
    if current_state == NodeState.ALERT_READY or current_state == NodeState.ERROR:
        return NodeState.READY
    elif current_state == NodeState.ALERT_RUNNING:
        return NodeState.RUNNING

    return current_state


def update_state(
    current_state: NodeState,
    lastSeenAt: datetime,
    typ: PayloadType | None = None,
    dato: int = 0,
) -> NodeState:

    FUNCTIONS = {
        PayloadType.TOTAL_READING: update_state_total_reading,
        PayloadType.WINDOW_READING: update_state_window_reading,
        PayloadType.START_REC: update_state_start_rec,
        PayloadType.END_REC: update_state_end_rec,
        PayloadType.KEEP_ALIVE: update_state_keep_alive,
        PayloadType.HANDLE_ALERT: update_state_handle_alert,
    }

    if typ is not None:
        current_state = FUNCTIONS[typ](current_state, dato)

    if (datetime.now() - lastSeenAt) > timedelta(
        seconds=Config.app.NODE_TIMEOUT_INTERVAL
    ):
        current_state = NodeState.ERROR

    return current_state


async def get_nodes(applicationID: str):
    application: Application | None = await Application.get(
        PydanticObjectId(applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    nodes: list[Node] = await Node.find(Node.application == application.id).to_list()

    # nodes = [x.to_dashboard() for x in nodes]

    return nodes


async def get_node_settings(nodeID: int) -> NodeSettings:
    node = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    settings = await NodeSettings.find_one(NodeSettings.node == node.id)
    if settings is None:
        raise NotFoundException("NodeSettings")

    return settings


def send_hv(detector: int, value: int):
    pass


def send_update_settings_sensor(sensor_settings: dict, detector: int, sensor: int):
    pass


def send_update_settings_detector(detector_settings: dict, detector: int):
    for key in detector_settings.keys():
        if key == "hv":
            send_hv(detector, detector_settings[key])
        elif key == "s1":
            pass
        elif key == "s2":
            pass
        else:
            raise ValueError(f"Unexpected key {key}")


def send_update_settings(node_settings: dict):
    for key in node_settings.keys():
        if key == "d1":
            send_update_settings_detector(node_settings[key], 1)
        elif key == "d2":
            send_update_settings_detector(node_settings[key], 2)
        elif key == "d3":
            send_update_settings_detector(node_settings[key], 3)
        elif key == "d4":
            send_update_settings_detector(node_settings[key], 4)
        else:
            raise ValueError(f"Unexpected key {key}")


def delta_dict_recursive(a: dict, b: dict) -> dict:
    delta_dict = {}

    for key in a.keys():
        if isinstance(a[key], dict):
            val = delta_dict_recursive(a[key], b[key])
            if val:
                delta_dict[key] = val
        else:
            if a[key] != b[key]:
                delta_dict[key] = a[key]

    return delta_dict


async def update_node_settings(nodeID: int, payload: NodeSettings.Serialized):

    node = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    settings = await NodeSettings.find_one(NodeSettings.node == node.id)
    if settings is None:
        settings = NodeSettings(
            node=node.id, d1=payload.d1, d2=payload.d2, d3=payload.d3, d4=payload.d4
        )
        await settings.save()

        # Send whole payload
        settings_dict = settings.serialize().dict()
        send_update_settings(settings_dict)

        return

    settings.d1 = payload.d1
    settings.d2 = payload.d2
    settings.d3 = payload.d3
    settings.d4 = payload.d4
    await settings.save()

    old_settings_dict = settings.serialize().dict()
    new_settings_dict = payload.dict()
    delta_dict = delta_dict_recursive(new_settings_dict, old_settings_dict)

    send_update_settings(delta_dict)
