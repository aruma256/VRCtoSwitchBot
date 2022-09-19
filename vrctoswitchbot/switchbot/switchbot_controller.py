import json
from pathlib import Path
import requests

from vrctoswitchbot.switchbot.switchbot_device import SwitchBotDevice

SWITCHBOT_URL = 'https://api.switch-bot.com'
API_DEVICE_LIST = '/v1.0/devices'
STATUS_SUCCESS = 100
TOKEN_FILE = Path('token.json')


def _load_token():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, mode='r') as f:
            return json.load(f)['token']
    return None


def _save_token(token):
    with open(TOKEN_FILE, mode='w') as f:
        json.dump({'token': token}, f)


class SwitchBotController:

    def __init__(self) -> None:
        self._devicelist: list[SwitchBotDevice] = []
        self._token = _load_token()
        self.fetch_device_list()

    def _get_headers(self) -> dict:
        return {
            'Authorization': self._token,
            'Content-Type': 'application/json; charset=utf8'
        }

    def is_token_valid(self) -> bool:
        return bool(self._devicelist)

    def set_new_token(self, token) -> bool:
        self._token = token
        valid = bool(self.fetch_device_list())
        if valid:
            _save_token(token)
        return valid

    def clear_device_list(self) -> None:
        self._devicelist.clear()

    def fetch_device_list(self) -> bool:
        self.clear_device_list()
        if not self._token:
            return False
        res = requests.get(
            url=SWITCHBOT_URL + API_DEVICE_LIST,
            headers=self._get_headers()
        )
        if res.status_code != 200:
            return False
        content = json.loads(res.content)
        if content.get('statusCode') != STATUS_SUCCESS:
            return False
        body = content['body']
        for device_json in (body['deviceList'] + body['infraredRemoteList']):
            device = SwitchBotDevice(device_json['deviceId'],
                                     device_json['deviceName'])
            self._devicelist.append(device)
        return True

    def get_device_list(self) -> list[SwitchBotDevice]:
        return self._devicelist.copy()

    def get_device_name_list(self) -> list[str]:
        return [device.get_name() for device in self._devicelist]

    def send_device_command(self, device_id, command) -> None:
        res = requests.post(
            f"{SWITCHBOT_URL}/v1.0/devices/{device_id}/commands",
            headers=self._get_headers(),
            data=json.dumps(
                {
                    "command": command,
                    "parameter": "default",
                    "commandType": "command"
                }
            )
        )
        print(res.content)
