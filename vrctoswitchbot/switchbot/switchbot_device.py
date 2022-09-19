class SwitchBotDevice:

    def __init__(self, id_: str, name: str):
        self._id = id_
        self._name = name

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name
