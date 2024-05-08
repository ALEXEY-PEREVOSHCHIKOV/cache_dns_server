from __future__ import annotations

import json
import os.path
import time
from json import JSONDecodeError


class Cache:
    def __init__(self):
        self.cache_records = {}

    def push(self, key: str, type_record: str, rdata, ttl: int) -> None:
        self.cache_records[key] = (type_record, rdata, ttl, time.time())

    def clean(self) -> None:
        self.cache_records.clear()

    def get(self, key: str, type_record: str) -> None or str:
        timer = time.time()

        for key, values in self.cache_records.copy().items():
            if timer - values[3] > values[2]:
                self.cache_records.pop(key)

        value_key = self.cache_records.get(key)

        if value_key is None:
            return None

        record = value_key[0]

        if record == type_record:
            return value_key[1], value_key[2]

    def from_json(self, name: str):
        if not os.path.exists(name):
            file = open(name, 'w')
            file.close()

        with open(name, 'r') as file:
            try:
                data = json.load(file)
            except JSONDecodeError:
                return None

            self.cache_records = data

    def to_json(self, name: str):
        with open(name, 'w') as file:
            data = self.cache_records
            json.dump(data, file, default=lambda x: x.__dict__)