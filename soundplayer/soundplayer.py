import logging
import threading
from pathlib import Path

from pygame import mixer
from utils.pathutils import get_random_file

class SoundPlayer:
    def __init__(self, volume=1):
        self.volume = volume
        self.channel_a = None
        self.lock = threading.Lock()

    def __enter__(self):
        self.init_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_context()

    def init_context(self):
        mixer.init()
        mixer.set_num_channels(1)

    def close_context(self):
        mixer.quit()

    def play_sound(self, sound_path):
        if mixer.get_init() is not None:
            t = threading.Thread(name="PlayerThread", target=self.__play_sound__, args=(sound_path,))
            t.start()
        else:
            logging.error("SoundPlayer is not initialized. You must call init_context function.")

    def set_volume(self, volume):
        if volume < 0 or volume > 1:
            logging.error("Volume value must be between 0 an 1.")
        else:
            with self.lock:
                self.volume = volume

    def __play_sound__(self, sound_path):
        with self.lock:
            if self.channel_a is not None and self.channel_a.get_busy():
                logging.debug("Channel is busy, stopping current sound.")
                self.channel_a.stop()
                mixer.stop()
            path = Path(sound_path)
            if path.is_dir():
                sound_path = get_random_file(walk_dir=str(path), file_ext_filter=['.wav', '.mp3'])
            sound = mixer.Sound(sound_path)
            sound.set_volume(self.volume)
            self.channel_a = sound.play()


