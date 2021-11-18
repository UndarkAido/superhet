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


async def start(apology: bool = False):
    global superhet
    global superhet_out
    print("here1")
    superhet_out = open(f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log", "w")
    if sys.platform.startswith('win'):
        superhet = await asyncio.create_subprocess_shell(
            f"venv\\Scripts\\python.exe main.py {'--apology' if apology else ''}",
            stdout=superhet_out, stderr=superhet_out, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        superhet = await asyncio.create_subprocess_shell(f"venv/bin/python main.py {'--apology' if apology else ''}",
                                                         stdout=superhet_out, stderr=superhet_out)
    print("here2")


async def run():
    global superhet
    global superhet_out
    while True:
        try:
            print(await superhet.wait())
        except KeyboardInterrupt:
            print("ERROR")
            pass
        finally:
            print("FINALLYA")
            # await end()
        await start()


async def end():
    if sys.platform.startswith('win'):
        os.system(f"TASKKILL /F /T /PID {superhet.pid}")
    else:
        os.system(f"kill -s SIGKILL {superhet.pid}")
        superhet.kill()
    superhet_out.close()


async def watch():
    missed = -1
    async with aiohttp.ClientSession() as session:
        while True:
            if missed >= 0:
                missed += 1
            try:
                async with session.get('http://localhost:8080/api/playing') as response:
                    print(await response.text())
                    missed = 0
                await asyncio.sleep(10)
            except Exception as e:
                if missed > 3:
                    print("Restarting")
                    await end()


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
