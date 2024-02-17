import logging
import ssl
import threading
import uuid
from enum import Enum
from typing import List, Any, Dict, Callable

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTv311

from network.mqtt.mqttresponsecode import MqttResponseCode
from network.mqtt.mqtttopic import MqttTopic
from network.url import BasicAuthURL
from utils.stringutils import is_empty_string


class MqttLoopType(Enum):
    BLOCKING = 0
    NOT_BLOCKING = 1
    CUSTOM = 2
    NO_LOOP = 3 # Si el cliente solo va a publicar no es necesario tener un loop

    def __eq__(self, other):
        if not isinstance(other, MqttLoopType):
            return False
        return self.value == other.value


class MqttClient:
    def __init__(self, client_id: str = None, broker_url: BasicAuthURL = None, subscribed_topics: List[MqttTopic] = [],
                 loop_type: MqttLoopType = MqttLoopType.NOT_BLOCKING,
                 use_web_sockets: bool = False, on_connect_success: Callable = None,
                 on_connect_error: Callable = None, custom_loop_callback: Callable = None):

        self.client_id = str(uuid.uuid1()) if is_empty_string(client_id) else f"{client_id}_{str(uuid.uuid1())}"
        self.broker_url = broker_url
        self.mqtt_client = None
        self.running = False
        self.loop_type = loop_type
        self.subscribed_topics = subscribed_topics
        self.subscribed_topics_by_name: Dict[str, MqttTopic] = {}
        self.use_web_sockets = use_web_sockets
        self.on_connect_success = on_connect_success
        self.on_connect_error = on_connect_error
        self.custom_loop_callback = custom_loop_callback

    def __enter__(self):
        self.init_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_context()

    def init_context(self):
        self.__connect_mqtt__()

    def close_context(self):
        self.stop_loop()

    def start_loop(self):
        self.running = True
        logging.info(f"MQTT client with ID = {self.client_id} is starting loop.")
        if self.loop_type == MqttLoopType.BLOCKING:
            try:
                self.mqtt_client.loop_forever()
            except ssl.SSLError:
                pass
        elif self.loop_type == MqttLoopType.NOT_BLOCKING:
            self.mqtt_client.loop_start()
        elif self.loop_type == MqttLoopType.CUSTOM:
            self.__custom_loop__()

    def stop_loop(self):
        logging.info(f"MQTT client with ID = {self.client_id} is stopping loop.")
        self.running = False
        if self.loop_type == MqttLoopType.NOT_BLOCKING:
            self.mqtt_client.loop_stop()
        try:
            self.mqtt_client.disconnect()
        except ssl.SSLZeroReturnError:
            # Según la documentación de Paho MQTT el loop bloqueante solo se puede parar cuando se llama a disconnect.
            # Para que no salten excepciones relacionadas con SSL cuando llamamos a disconecct con un loop bloqueante se
            # hace este apaño
            pass
        logging.info(f"MQTT client with ID = {self.client_id} loop is stopped.")

    def publish(self, topic: MqttTopic, payload: Any):
        result = self.mqtt_client.publish(topic=topic.name, qos=topic.qos, payload=payload)
        status = MqttResponseCode(result[0])
        if status != MqttResponseCode.NO_ERROR:
            logging.error(f"Failed to send message to topic = {topic}. Status code = {str(status)}. Trying to reconnect...")
            self.close_context()
            self.init_context()

    def __connect_mqtt__(self):
        logging.info(f"Connecting MQTT client with ID = {self.client_id}")
        # Set Connecting Client ID
        if self.use_web_sockets:
            self.mqtt_client = mqtt_client.Client(client_id=self.client_id, protocol=MQTTv311, transport='websockets')
        else:
            self.mqtt_client = mqtt_client.Client(client_id=self.client_id, protocol=MQTTv311)

        if self.broker_url.tls_cert_path is not None:
            self.mqtt_client.tls_set(self.broker_url.tls_cert_path)

        if isinstance(self.broker_url, BasicAuthURL) and self.broker_url.user is not None and \
                self.broker_url.passwd is not None:
            self.mqtt_client.username_pw_set(self.broker_url.user, self.broker_url.passwd)

        self.mqtt_client.on_connect = self.__on_connect__
        self.mqtt_client.on_disconnect = self.__on_disconnect__
        self.mqtt_client.connect(self.broker_url.hostname, self.broker_url.port)

    def __on_connect__(self, client, userdata, flags, rc):
        rc = MqttResponseCode(rc)
        if rc == MqttResponseCode.NO_ERROR:
            logging.info(f"MQTT client with id = {self.client_id} is connected to Broker!")
            topics = []
            for topic in self.subscribed_topics:
                topics.append((topic.name, topic.qos))
                self.subscribed_topics_by_name[topic.name] = topic
            self.__subscribe__(topics)
            if self.on_connect_success is not None:
                self.on_connect_success()
        else:
            logging.error(f"MQTT client with id = {self.client_id} connection attempt failed: {str(rc)}")
            if self.on_connect_error is not None:
                self.on_connect_error()

    def __on_disconnect__(self, client, userdata, rc):
        rc = MqttResponseCode(rc)
        if rc != MqttResponseCode.NO_ERROR:
            logging.error(f"MQTT client with id = {self.client_id}. Unexpected disconnection! Response code = {str(rc)}.")
        else:
            logging.info(f"MQTT client with id = {self.client_id} disconnected successfully.")

    def __subscribe__(self, topics: List[MqttTopic]):
        def on_message(client, userdata, msg):
            logging.debug("topic = {}, payload = {}".format(msg.topic, msg.payload))
            if self.subscribed_topics_by_name[msg.topic].threaded_callback:
                t = threading.Thread(target=self.subscribed_topics_by_name[msg.topic].callback,
                                     args=(msg.topic, msg.payload))
                t.start()
            else:
                self.subscribed_topics_by_name[msg.topic].callback(msg.topic, msg.payload)

        if len(topics) > 0:
            self.mqtt_client.subscribe(topics)
            self.mqtt_client.on_message = on_message

    def __custom_loop__(self):
        while self.running:
            self.mqtt_client.loop(0)
            if self.custom_loop_callback is not None:
                self.custom_loop_callback()
