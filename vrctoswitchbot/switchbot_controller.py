import json
from operator import itemgetter
from pathlib import Path
import requests

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

    def __init__(self):
        self._token = _load_token()
        self.device_names = []
        self.fetch_device_list()

    def _get_headers(self):
        return {
            'Authorization': self._token,
            'Content-Type': 'application/json; charset=utf8'
        }

    def is_token_valid(self):
        return bool(self._devicelist)

    def set_new_token(self, token):
        self._token = token
        valid = bool(self.fetch_device_list())
        if valid:
            _save_token(token)
        return valid

    def clear_device_list(self):
        self._devicelist = None

    def fetch_device_list(self):
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
        devicelist = body['deviceList'] + body['infraredRemoteList']
        self._devicelist = devicelist
        self.device_names.clear()
        self.device_names.extend(map(itemgetter('deviceName'), devicelist))
        return True

    def get_device_list(self):
        return self._devicelist

    def turn_on_device(self, device_id):
        self._control_device(device_id, 'turnOn')

    def turn_off_device(self, device_id):
        self._control_device(device_id, 'turnOff')

    def _control_device(self, device_id, command):
        res = requests.post(
            f"{SWITCHBOT_URL}/v1.0/devices/{device_id}/commands",
            headers=self._get_headers(),
            data=json.dumps({
                "command": command,
                "parameter": "default",
                "commandType": "command"
            })
        )
        print(res.content)

