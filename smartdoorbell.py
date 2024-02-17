from datetime import datetime
import logging
import wiringpi
import sys

import yaml
from wiringpi import GPIO

from network.mqtt.mqttclient import MqttClient, MqttLoopType
from network.mqtt.mqttconf import MqttConf
from network.mqtt.mqttexceptions import NoMqttConfSection, NoMqttHostSection
from soundplayer.soundplayer import SoundPlayer


class SmartDoorbell:
    DEFAULT_LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(processName)s : %(threadName)s - %(funcName)s : %(filename)s : %(lineno)d - %(message)s"
    DEFAULT_LOG_LEVEL = logging.INFO
    LOG_LEVELS_DICT = {'error': logging.ERROR,
                       'warning': logging.WARNING,
                       'info': logging.INFO,
                       'debug':logging.DEBUG}

    DEFAULT_AUDIO_PATH = './data/sounds'
    DEFAULT_AUDIO_VOLUME = 0.5

    DEFAULT_SWITCH_PIN = 10

    def __init__(self, cfg_path: str = 'data/cfg/conf.yaml'):
        self.cfg = {}
        self.mqtt_client = None
        with open(cfg_path) as cfg_file:
            self.cfg = yaml.safe_load(cfg_file)

        self.__setup_logger__()
        self.__setup_mqtt_client__()
        self.__setup_gpio__()
        self.__setup_audio__()

    def __enter__(self):
        self.init_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_context()

    def __setup_logger__(self):
        root = logging.getLogger()
        hdlr = logging.StreamHandler()
        logging_format = self.DEFAULT_LOG_FORMAT
        level = self.DEFAULT_LOG_LEVEL
        if 'logging' in self.cfg:
            logging_cfg  = self.cfg['logging']
            if 'format' in logging_cfg:
                logging_format = logging_cfg['format']
            else:
                logging.warning("No logging format section into configuration file. Using default format.")
            if 'level' in logging_cfg:
                level_name = str(logging_cfg['level']).lower()
                level = self.LOG_LEVELS_DICT[level_name] if level_name in self.LOG_LEVELS_DICT else self.DEFAULT_LOG_LEVEL
            else:
                logging.warning("No logging level section into configuration file. Using debug level.")
        else:
            logging.warning("No logging section into configuration file. Using default logging setup.")
        hdlr.setFormatter(fmt=logging.Formatter(logging_format))
        root.addHandler(hdlr)
        root.setLevel(level)

    def __setup_mqtt_client__(self):
        try:
            self.mqtt_conf = MqttConf.create_from_dict(self.cfg)
            self.mqtt_client = MqttClient(broker_url=self.mqtt_conf.url, loop_type=MqttLoopType.NO_LOOP)
        except NoMqttConfSection | NoMqttHostSection as e:
            logging.warning(str(e))

    def __setup_gpio__(self):
        switch_pin = self.DEFAULT_SWITCH_PIN
        if 'gpio' in self.cfg:
            gpio_cfg = self.cfg['gpio']
            if 'switch_pin' in gpio_cfg:
                switch_pin = gpio_cfg['switch_pin']
            else:
                logging.warning("No gpio switch_pin in conf file. It's going to use default switch pin = {}"
                                .format(self.DEFAULT_SWITCH_PIN))
        else:
            logging.warning("No gpio section in conf file. It's going to use default switch pin = {}"
                            .format(self.DEFAULT_SWITCH_PIN))

        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(switch_pin, GPIO.INPUT)
        wiringpi.pullUpDnControl(switch_pin, wiringpi.GPIO.PUD_UP)
        wiringpi.wiringPiISR(switch_pin, wiringpi.GPIO.INT_EDGE_RISING, self.__button_callback__)

    def __setup_audio__(self):
        self.sound_player = SoundPlayer()
        self.audio_path = self.DEFAULT_AUDIO_PATH
        self.audio_volume = self.DEFAULT_AUDIO_VOLUME

        if 'audio' in self.cfg:
            audio_cfg = self.cfg['audio']
            if 'path' in audio_cfg:
                self.audio_path = audio_cfg['path']
            else:
                logging.warning("No audio path in conf file. It's going to use default path = {}"
                                .format(self.DEFAULT_AUDIO_PATH))
            if 'volume' in audio_cfg:
                self.audio_volume = audio_cfg['volume']
            else:
                logging.warning("No audio volume in conf file. It's going to use default volume = {}"
                                .format(self.DEFAULT_AUDIO_VOLUME))
        else:
            logging.warning("No audio section in conf file. It's going to use default values. Sounds path = {}, "
                            "Volume = {}".format(self.DEFAULT_AUDIO_PATH, self.DEFAULT_AUDIO_VOLUME))
        self.sound_player.set_volume(self.audio_volume)

    def __button_callback__(self):
        logging.debug("Button pressed!")
        self.sound_player.play_sound(self.audio_path)
        if self.mqtt_client is not None:
            self.mqtt_client.publish(topic=self.mqtt_conf.topic, payload=str(datetime.now()))
        wiringpi.delay(200)

    def init_context(self):
        self.mqtt_client.init_context()
        self.sound_player.init_context()

    def close_context(self):
        self.mqtt_client.close_context()
        self.sound_player.close_context()

    def loop(self):
        logging.info("****************** Starting MP3 Doorbell ******************")
        while True:
            try:
                wiringpi.delay(2000)
            except KeyboardInterrupt:
                logging.info("\nexit")
                sys.exit(0)
            except Exception as e:
                logging.exception(str(e))
                sys.exit(-1)

