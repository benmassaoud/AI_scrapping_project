import json


class Property:
    def __init__(self, data):
        self.__dict__ = json.loads(data)
