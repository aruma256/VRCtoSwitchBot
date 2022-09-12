import requests


UPDATE_JSON_URL = 'https://github.com/aruma256/VRCtoSwitchBot/raw/main/version_info.json'  # noqa


def is_newer_version_available(local_version: str) -> bool:
    try:
        res = requests.get(UPDATE_JSON_URL, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if _is_local_version_outdated(data['recommended'], local_version):
                return True
    except Exception:
        pass
    return False


def _is_local_version_outdated(remote_version: str, local_version: str) -> bool:
    remote = tuple(map(int, remote_version.split('.')))
    local = tuple(map(int, local_version.split('.')))
    return remote > local
