# -*- coding: utf-8 -*-

"""
Keyword spotting using snowboy
"""

import os
import threading
try:
    import Queue as queue
except ImportError:
    import queue

from snowboy import snowboydetect

from .element import Element


class KWS(Element):
    def __init__(self):
        super(KWS, self).__init__()

        self.queue = queue.Queue()
        self.done = False

        self.on_detected = None

    def put(self, data):
        self.queue.put(data)

    def start(self):
        self.done = False
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.done = True

    def run(self):
        resource_path = os.path.join(os.path.dirname(snowboydetect.__file__), 'resources')
        detector = snowboydetect.SnowboyDetect(
            os.path.join(resource_path, 'common.res'),
            os.path.join(resource_path, 'snowboy.umdl'))
        detector.SetAudioGain(1)
        detector.ApplyFrontend(True)
        detector.SetSensitivity('0.6'.encode())

        while not self.done:
            data = self.queue.get()
            ans = detector.RunDetection(data)
            if ans > 0:
                if callable(self.on_detected):
                    self.on_detected(ans)

            super(KWS, self).put(data)

    def set_callback(self, callback):
        self.on_detected = callback


def main():
    import time
    from voice_engine.source import Source

    src = Source()
    kws = KWS()

    src.link(kws)

    def on_detected(keyword):
        print('found {}'.format(keyword))

    kws.on_detected = on_detected

    kws.start()
    src.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    kws.stop()
    src.stop()


if __name__ == '__main__':
    main()