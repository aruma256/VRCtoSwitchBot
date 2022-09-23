class SwitchBotDevice:

    def __init__(self, id_: str, name: str) -> None:
        self._id = id_
        self._name = name

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name
