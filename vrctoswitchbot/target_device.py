from typing import List, Union

from vrctoswitchbot.switchbot_controller import SwitchBotController

class TargetDevice:

    def __init__(self, controller:SwitchBotController, id_:str, name:str, param_name:str):
        self._controller = controller
        self._id = id_
        self._name = name
        self._param_name = param_name
        self._osc_address = '/avatar/parameters/' + param_name

    def get_id(self):
        return self._id

    def get_address(self):
        return self._osc_address

    def on_osc(self, value):
        if value:
            self._controller.turn_on_device(self.get_id())
        else:
            self._controller.turn_off_device(self.get_id())

TARGET_DEVICES:List[Union[TargetDevice, None]] = {}
