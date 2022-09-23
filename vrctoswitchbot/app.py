import json
from pathlib import Path
import threading
from typing import Any

from .action import Action
from .gui.gui_window import GUIWindow
from .switchbot.switchbot_device import SwitchBotDevice
from .switchbot.switchbot_controller import SwitchBotController
from .vrchat_osc.osc_listener import OSCListener
from .vrchat_osc.osc_sender import OSCSender
from . import const
from . import version_checker

UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json'  # noqa
CONFIG_PATH = Path('config.json')


class App:

    def __init__(self):
        if not CONFIG_PATH.exists():
            self._generate_default_config()
        with CONFIG_PATH.open(encoding='utf-8') as f:
            self._config = config = json.load(f)
        self._actions: list[Action | None] = [None] * const.N
        self._switchbot_controller = SwitchBotController()
        self._osc_listener = OSCListener(app=self, **config['OSC']['listen'])
        self._osc_sender = OSCSender(**config['OSC']['send'])
        self._gui_window = GUIWindow(self)

    def start_gui(self) -> None:
        self._load_devices()
        threading.Thread(target=self._update_check, daemon=True).start()
        self._gui_window.mainloop()

    def get_switchbot_controller(self) -> SwitchBotController:
        return self._switchbot_controller

    def get_osc_sender(self) -> OSCSender:
        return self._osc_sender

    def _load_devices(self) -> None:
        if 'actions' not in self._config:
            return
        for i, config_action in enumerate(self._config['actions']):
            if not config_action:
                continue
            device = SwitchBotDevice(config_action['device']['id'],
                                     config_action['device']['name'])
            action = Action(app=self,
                            osc_address=config_action['osc_address'],
                            switchbot_device=device,
                            command=config_action['command'])
            self.register_action(i, action)

    def _generate_default_config(self) -> None:
        self._config = {
            'OSC': {
                'listen': {
                    'ip': '127.0.0.1',
                    'port': 9001,
                },
                'send': {
                    'ip': '127.0.0.1',
                    'port': 9000,
                },
            },
        }
        with CONFIG_PATH.open(mode='w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)

    def save(self) -> None:
        actions = []
        for action in self._actions:
            if action is None:
                actions.append(None)
                continue
            actions.append(
                {
                    'device': {
                        'id': action._switchbot_device.get_id(),
                        'name': action._switchbot_device.get_name(),
                    },
                    'osc_address': action._osc_address,
                    'command': action._command,
                }
            )
        self._config['actions'] = actions
        with CONFIG_PATH.open(mode='w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)
            self._gui_window.show_info('保存しました')

    def register_action(self, i: int, action: Action) -> None:
        self._actions[i] = action
        self._gui_window.set_action(i, action)

    def unregister_action(self, i: int) -> None:
        self._actions[i] = None
        self._gui_window.clear_action(i)

    def get_action(self, i: int) -> Action:
        return self._actions[i]

    def broadcast_osc(self, address: str, value: Any) -> None:
        for action in filter(None, self._actions):
            if action.is_acceptable(address):
                action.on_osc(address, value)

    def _update_check(self) -> None:
        if version_checker.is_newer_version_available(const.VERSION):
            self._gui_window.show_info('新しいバージョンが公開されています')
