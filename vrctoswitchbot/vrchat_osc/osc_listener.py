from threading import Thread
from typing import Any, TYPE_CHECKING

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

if TYPE_CHECKING:
    from ..app import App


class OSCListener:

    def __init__(self, app: 'App', ip: str, port: int) -> None:
        self._app = app
        self._ip = ip
        self._port = port
        self.run()

    def run(self) -> None:
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._on_osc)
        server = BlockingOSCUDPServer((self._ip, self._port), dispatcher)
        Thread(target=server.serve_forever, daemon=True).start()

    def _on_osc(self, address: str, value: Any) -> None:
        self._app.broadcast_osc(address, value)
