from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from vrctoswitchbot.target_device import TARGET_DEVICES


class OSCListener:

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self.run()

    def run(self):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._on_osc)
        server = BlockingOSCUDPServer((self._ip, self._port), dispatcher)
        Thread(target=server.serve_forever, daemon=True).start()

    def _on_osc(self, address, value):
        for device in TARGET_DEVICES:
            if device and device.get_address() == address:
                device.on_osc(value)
                break
