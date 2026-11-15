"""계산 기록 관리."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    expression: str
    result: str

    def __str__(self):
        return f"{self.expression} = {self.result}"


class History:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self._entries: list[Entry] = []

    def add(self, expression: str, result: str) -> None:
        self._entries.insert(0, Entry(expression, result))  # 최신 항목이 맨 앞
        del self._entries[self.max_size:]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def entries(self) -> list[Entry]:
        return list(self._entries)

    def __len__(self):
        return len(self._entries)
