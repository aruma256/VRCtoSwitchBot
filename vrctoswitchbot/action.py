from typing import Any

from .switchbot.switchbot_controller import SwitchBotController
from .switchbot.switchbot_device import SwitchBotDevice


class Action:

    def __init__(self,
                 controller: SwitchBotController,
                 exparam_name: str,
                 switchbot_device: SwitchBotDevice,
                 command: str,
                 ) -> None:
        self._controller = controller
        self._exparam_name = exparam_name
        self._osc_address = '/avatar/parameters/' + exparam_name
        self._switchbot_device = switchbot_device
        self._command = command

    def is_acceptable(self, address) -> bool:
        return address == self._osc_address

    def on_osc(self, address: str, value: Any) -> None:
        assert self.is_acceptable(address)
        if not isinstance(value, bool):
            raise RuntimeError('recieved non-bool value')
        if value is True:
            self.execute()

    def execute(self) -> None:
        self._controller.send_device_command(
            device_id=self._switchbot_device.get_id(),
            command=self._command,
        )
