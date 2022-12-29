import os

from mqtt import register_callbacks
from paho.mqtt.client import Client

from config import Config, get_config

TESTING = os.environ.get("TESTING", False)


class Adapter:
    def __init__(self):
        self.config: Config = get_config()

        # Init mqtt client
        self._client = Client()
        self._client.username_pw_set(self.config.mqtt.user, self.config.mqtt.password)

        if self.config.mqtt.tls:
            self._client.tls_set()

        register_callbacks(self._client)

        self._client.connect(host=self.config.mqtt.url, port=self.config.mqtt.port)

    def loop_forever(self):
        self._client.loop_forever()


if __name__ == "__main__":
    Adapter().loop_forever()
