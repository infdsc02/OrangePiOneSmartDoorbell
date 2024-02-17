class NoMqttConfSection(Exception):
    def __init__(self):
        super().__init__("No mqtt_broker section into configuration file. Mqtt client isn't going to start.")

class NoMqttHostSection(Exception):
    def __init__(self):
        super().__init__("No mqtt_broker host section into configuration file. Mqtt client isn't going to start.")