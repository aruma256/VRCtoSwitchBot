from pythonosc import udp_client


class OSCSender:

    def __init__(self, ip: str, port: int) -> None:
        self._client = udp_client.SimpleUDPClient(ip, port)

    def send(self, address: str, value) -> None:
        self._client.send_message(address, value)
