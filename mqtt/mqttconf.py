import logging
from dataclasses import dataclass

from mqtt.mqttexceptions import NoMqttHostSection, NoMqttConfSection
from mqtt.mqtttopic import MqttTopic
from network.url import BasicAuthURL


class MqttConf:
    def __init__(self, url: BasicAuthURL = BasicAuthURL(protocol="mqtt", hostname="127.0.0.1", port=1883),
                 topic: MqttTopic = None):
        self.url = url
        self.topic = topic


    @staticmethod
    def create_from_dict(cfg):
        if 'mqtt' in cfg and 'broker' in cfg['mqtt']:
            user = None
            passwd = None
            host = None
            port = 1883
            pub_topic_name = "ring_doorbell"
            mqtt_cfg = cfg['mqtt']['broker']

            if 'host' in mqtt_cfg:
                host = mqtt_cfg['host']
            else:
                raise NoMqttHostSection()

            if 'port' in mqtt_cfg:
                port = mqtt_cfg['port']
            else:
                logging.warning(
                    "No mqtt_broker port section into configuration file. Mqtt client is going to start using 1883 port.")

            if 'user' in mqtt_cfg:
                user = mqtt_cfg['user']
            else:
                logging.warning("No mqtt_broker user section into configuration file.")

            if 'passwd' in mqtt_cfg:
                passwd = mqtt_cfg['passwd']
            else:
                logging.warning("No mqtt_broker passwd section into configuration file.")

            if 'pub_topic' in cfg['mqtt']:
                pub_topic_name = cfg['mqtt']['pub_topic']
        else:
            raise NoMqttConfSection()

        url = BasicAuthURL(protocol="mqtt", hostname=host, port=port, user=user, passwd=passwd)
        topic = MqttTopic(name=pub_topic_name)
        return MqttConf(url=url, topic=topic)