import pytest

from microservice_websocket.app.utils.enums import NodeState


def test_to_irma_ui_state():
    expected = [
        (NodeState.ERROR, "off"),
        (NodeState.READY, "ok"),
        (NodeState.RUNNING, "rec"),
        (NodeState.ALERT_READY, "alert-ready"),
        (NodeState.ALERT_RUNNING, "alert-running"),
    ]

    for state, result in expected:
        assert (
            NodeState.to_irma_ui_state(state) == result
        ), "Invalid conversion of NodeState to ui string"

    with pytest.raises(ValueError):
        NodeState.to_irma_ui_state(NodeState.ALERT_RUNNING + 1)
