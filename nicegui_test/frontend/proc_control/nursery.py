import asyncio
from collections import UserDict
from dataclasses import dataclass
from enum import StrEnum, auto
import os
from pathlib import Path
from typing import Any
import uuid
import sys
import logging


class ProcessStates(StrEnum):
    starting = auto()
    running = auto()
    stopping = auto()
    stopped = auto()


@dataclass
class Crib:
    id: uuid.UUID
    name: str
    log_path: Path
    state: ProcessStates = ProcessStates.starting

    process: asyncio.subprocess.Process | None = None
    stdin: asyncio.StreamWriter | None = None
    stdout: asyncio.StreamReader | None = None
    running_task: asyncio.Task | None = None


class CribDict(UserDict):
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


cribs: CribDict[uuid.UUID, Crib] = CribDict({})


def create_process(name: str, logs_dir: Path) -> Crib:
    cid = uuid.uuid4()
    log_path = Path(
        os.path.expandvars(os.path.expanduser(logs_dir / f"{str(cid)}.txt"))
    ).absolute()
    crib = Crib(
        id=cid,
        name=name,
        log_path=log_path,
    )
    cribs[crib.id] = crib
    task = asyncio.create_task(_crib_lifecycle(crib))
    crib.running_task = task
    return crib


def restart_procss(crib: Crib):
    task = asyncio.create_task(_crib_lifecycle(crib))
    crib.running_task = task


def stop_process(crib: Crib):
    if crib.running_task:
        crib.running_task.cancel()


async def remove_process(crib: Crib, force_cancel: bool = False):
    if crib.state != ProcessStates.stopped:
        if not force_cancel:
            raise ValueError(
                "Process is running. Use `force_cancel` to remove running processes."
            )
        if crib.process:
            crib.running_task.cancel()
            await crib.running_task

    cribs.pop(crib.id)


async def _crib_lifecycle(crib: Crib):
    try:
        process = await asyncio.create_subprocess_exec(
            *[
                sys.executable,
                # -u makes the output unbufered, making it possible
                # to read from stdout while the process is running
                # https://stackoverflow.com/questions/46592284/reading-stdout-from-a-subprocess-in-real-time
                "-u",
                "-m",
                "nicegui_test.proc",
                str(crib.log_path),
                # "--write-random-records",
            ],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        crib.process = process
        crib.stdin = process.stdin
        crib.stdout = process.stdout
        crib.state = ProcessStates.running
        await process.wait()
    except asyncio.CancelledError:
        print(f"Canceled crib {crib.id}")
    except Exception as ex:
        logging.getLogger("uvicorn").exception("Error with process")
        raise
    finally:
        crib.state = ProcessStates.stopping
        try:
            if process and not process.returncode:
                process.kill()
        except ProcessLookupError:
            pass

        crib.state = ProcessStates.stopped
        crib.running_task = None
