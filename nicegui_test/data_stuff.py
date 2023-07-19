from collections import UserDict
from dataclasses import dataclass
import enum
from typing import Any, Callable
import uuid
import asyncio


class DataState(enum.StrEnum):
    starting = enum.auto()
    ready = enum.auto()
    deleting = enum.auto()


@dataclass
class Data:
    id: uuid.UUID
    name: str
    state: DataState = DataState.starting

    async def startup(self, refresher: Callable, time: float = 1.0):
        await asyncio.sleep(time)
        self.state = DataState.ready
        refresher()

    async def stop(
        self, on_started: callable, on_finished: callable, time: float = 1.0
    ):
        self.state = DataState.deleting
        on_started()
        await asyncio.sleep(time)
        datas.pop(self.id, None)
        on_finished()


class DataDict(UserDict):
    def __init__(self, *args, **kwargs):
        self.on_change_list: list[callable] = []
        super().__init__(*args, **kwargs)

    def _call_on_change(self):
        for fun in self.on_change_list:
            if asyncio.iscoroutine(fun):
                asyncio.ensure_future(fun())
            else:
                fun()

    def __setitem__(self, key: Any, item: Any) -> None:
        super().__setitem__(key, item)
        self._call_on_change()

    def __delitem__(self, key: Any) -> None:
        super().__delitem__(key)
        self._call_on_change()


datas: DataDict[uuid.UUID, Data] = DataDict(
    {
        uuid.UUID("dfe48289-3cb8-4ecf-bfc1-665062f4718a"): Data(
            id=uuid.UUID("dfe48289-3cb8-4ecf-bfc1-665062f4718a"),
            name="Default 1",
            state=DataState.ready,
        )
    }
)
# datas.on_change_list.append(lambda: print("changed data"))
