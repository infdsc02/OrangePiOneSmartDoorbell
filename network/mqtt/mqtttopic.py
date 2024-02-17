from typing import Callable
from dataclasses import dataclass

@dataclass
class MqttTopic:
    name: str = None
    qos: int = 0
    threaded_callback: bool = False
    callback: Callable = None

    def __repr__(self):
        return f"MQTTTopic[name = {self.name}, qos = {self.qos}]"
