from dataclasses import dataclass
from pathlib import Path
import random
import signal
import os.path
import asyncio
import aioconsole
import aiofiles
from aioconsole import aprint, ainput

import typer
from datetime import datetime, UTC

from nicegui_test.procs.lisp_math import math_eval


stop_command = "cmd_stop"


def utcnow() -> datetime:
    return datetime.utcnow().astimezone(UTC)


def isonow() -> str:
    return utcnow().isoformat()


@dataclass
class _Semaphores:
    writer_stopped: asyncio.Future
    reader_stopped: asyncio.Future


_semaphores: _Semaphores

_queue: asyncio.Queue = None


async def _writer(file_to_write: Path, append: bool):
    mode = "a" if append else "w"
    async with aiofiles.open(file_to_write, mode) as file:
        while True:
            to_write = await _queue.get()

            if to_write == stop_command:
                await file.write(f"{isonow()} STOPPING")
                _queue.task_done()
                break

            # await aprint(to_write)
            print(to_write)
            await file.write(to_write)
            await file.write("\n")
            _queue.task_done()
    _semaphores.writer_stopped.set_result(True)


async def _do_record(to_record: str):
    await _queue.put(f"{isonow()} RECORD:{to_record}")


async def _do_math(exp: str):
    await _queue.put(f"{isonow()} MATH: Starting {exp}")
    try:
        result = math_eval(exp)
        await _queue.put(f"{isonow()} MATH: Result {result}")
    except ValueError as ex:
        await _queue.put(f"{isonow()} MATH: Parse fail, {str(ex)}")
    except Exception as ex:
        await _queue.put(f"{isonow()} MATH: Fail {str(ex)}")


async def _do_help():
    await aprint("record <text>")
    await aprint("math <example (+ 1 2)>")
    await aprint("to stop CMD_STOP")


async def _reader():
    while True:
        as_str = await aioconsole.ainput()
        command, *rest = as_str.split(" ", 1)
        if command == stop_command:
            await aprint("Stopping")
            await _queue.put(as_str)
            break
        match command.lower():
            case "record" if len(rest) > 0:
                await _do_record(rest[0])
            case "math" if len(rest) > 0:
                await _do_math(rest[0])
            case "help":
                await _do_help()
            case _:
                await _queue.put(
                    f"{isonow()} Unknown command {command} with args {rest}"
                )
    _semaphores.reader_stopped.set_result(True)


async def random_writer():
    while True:
        await _queue.put(f"{isonow()} RECORD: Random data {random.random()}")
        await asyncio.sleep(0.3)


async def main(file_to_write: Path, append: bool, random_records: bool):
    global _queue
    global _semaphores
    _semaphores = _Semaphores(
        writer_stopped=asyncio.get_event_loop().create_future(),
        reader_stopped=asyncio.get_event_loop().create_future(),
    )
    _queue = asyncio.Queue()
    await _queue.put(f"{isonow()} STARTING")
    asyncio.ensure_future(_reader())
    asyncio.ensure_future(_writer(file_to_write, append))
    if random_records:
        asyncio.ensure_future(random_writer())
    await asyncio.gather(_semaphores.reader_stopped, _semaphores.reader_stopped)


def _stop():
    if _queue:
        _queue.put_nowait("CMD_STOP")


def entrypoint(
    path_to_save: Path,
    append: bool = typer.Option(
        True, help="If the file should be appended or overwritten"
    ),
    write_random_records: bool = typer.Option(
        False, help="Writes random records from time to time."
    ),
):
    path_to_save = Path(os.path.expandvars(path_to_save.expanduser()))
    print(f"Starting in {path_to_save}")
    if not path_to_save.exists():
        path_to_save.parent.mkdir(parents=True, exist_ok=True)

    # asyncio.get_event_loop().add_signal_handler(signal.SIGINT, _stop)
    # asyncio.get_event_loop().add_signal_handler(signal.SIGTERM, _stop)

    asyncio.run(main(path_to_save, append, write_random_records))
    print("Bye :D")


def run():
    typer.run(entrypoint)


if __name__ == "__main__":
    run()
