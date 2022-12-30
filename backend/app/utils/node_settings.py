from ..entities.node import Node
from ..exceptions import NotFoundException
from ..models.node_settings import DetectorSettings, SensorSettings
from ..services.database import NodeSettings


async def get_node_settings(nodeID: int) -> NodeSettings:
    node = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    settings = await NodeSettings.find_one(NodeSettings.node == node.id)
    if settings is None:
        raise NotFoundException("NodeSettings")

    return settings


async def send_update_settings_sensor(
    node: Node,
    sensor_settings: SensorSettings,
    detector: int,
    sipm: int,
):
    if sensor_settings.w1_low is not None:
        node.set_window_low(detector, sipm, 1, sensor_settings.w1_low)
    if sensor_settings.w1_high is not None:
        node.set_window_high(detector, sipm, 1, sensor_settings.w1_high)
    if sensor_settings.w2_low is not None:
        node.set_window_low(detector, sipm, 2, sensor_settings.w2_low)
    if sensor_settings.w2_high is not None:
        node.set_window_high(detector, sipm, 2, sensor_settings.w2_high)
    if sensor_settings.w3_low is not None:
        node.set_window_low(detector, sipm, 3, sensor_settings.w3_low)
    if sensor_settings.w3_high is not None:
        node.set_window_high(detector, sipm, 3, sensor_settings.w3_high)
    if sensor_settings.hv is not None:
        node.set_hv(detector, sipm, sensor_settings.hv)


async def send_update_settings_detector(
    node: Node,
    detector_settings: DetectorSettings,
    detector: int,
):
    if detector_settings.s1 is not None:
        await send_update_settings_sensor(node, detector_settings.s1, detector, 1)
    if detector_settings.s2 is not None:
        await send_update_settings_sensor(node, detector_settings.s2, detector, 2)


async def send_update_settings(
    node: Node,
    node_settings: NodeSettings | NodeSettings.Serialized,
):
    if node_settings.d1 is not None:
        await send_update_settings_detector(node, node_settings.d1, 1)
    if node_settings.d2 is not None:
        await send_update_settings_detector(node, node_settings.d2, 2)
    if node_settings.d3 is not None:
        await send_update_settings_detector(node, node_settings.d3, 3)
    if node_settings.d4 is not None:
        await send_update_settings_detector(node, node_settings.d4, 4)


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
        await send_update_settings(node, settings)

        return

    old_settings_dict = settings.serialize().dict()
    new_settings_dict = payload.dict()
    delta_settings: NodeSettings.Serialized = NodeSettings.Serialized.parse_obj(
        delta_dict_recursive(new_settings_dict, old_settings_dict)
    )

    settings.d1 = payload.d1
    settings.d2 = payload.d2
    settings.d3 = payload.d3
    settings.d4 = payload.d4
    await settings.save()

    await send_update_settings(node, delta_settings)
