import asyncio
import os
import subprocess
import sys
import time
from typing import TextIO

import aiohttp as aiohttp

running: asyncio.Future
superhet: asyncio.subprocess.Process
superhet_out: TextIO
missed: int


async def start(apology: bool = False):
    global superhet
    global superhet_out
    global missed
    print("Starting Superhet")
    missed = -1
    superhet_out = open(f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log", "w")
    if sys.platform.startswith('win'):
        superhet = await asyncio.create_subprocess_shell(
            f"venv\\Scripts\\python.exe main.py {'--apology' if apology else ''}",
            stdout=superhet_out, stderr=superhet_out, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        superhet = await asyncio.create_subprocess_shell(f"venv/bin/python main.py {'--apology' if apology else ''}",
                                                         stdout=superhet_out, stderr=superhet_out)
    print("Superhet is started")


async def run():
    global superhet
    global superhet_out
    while True:
        print("Waiting for retrun code")
        print(f"Return code: {await superhet.wait()}")
        await start()


async def end():
    if sys.platform.startswith('win'):
        kill = f"TASKKILL /F /T /PID {superhet.pid}"
    else:
        kill = f"kill -9 {superhet.pid+1}"
    print(kill)
    os.system(kill)
    superhet_out.close()


async def watch():
    global missed
    async with aiohttp.ClientSession() as session:
        while True:
            if missed >= 0:
                missed += 1
            try:
                async with session.get('http://localhost:8080/api/ping') as response:
                    print(await response.text())
                    missed = 0
            except Exception as e:
                print(f"Missed {missed} pings")
                if missed > 2:
                    print("Restarting")
                    await end()
            await asyncio.sleep(10)


async def main():
    global running
    await start(False)
    asyncio.create_task(run())
    asyncio.create_task(watch())
    loop = asyncio.get_running_loop()
    running = loop.create_future()
    try:
        await running
    except KeyboardInterrupt:
        print("ERROR")
        pass
    finally:
        print("FINALLYB")
        await end()


if __name__ == '__main__':
    asyncio.run(main())
    exit(0)
