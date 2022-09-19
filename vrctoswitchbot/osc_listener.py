from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class OSCListener:

    def __init__(self, ip, port, gui):
        self._ip = ip
        self._port = port
        self._gui = gui
        self.run()

    def run(self):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._on_osc)
        server = BlockingOSCUDPServer((self._ip, self._port), dispatcher)
        Thread(target=server.serve_forever, daemon=True).start()

    def _on_osc(self, address, value):
        self._gui.broadcast_osc(address, value)
