#! /usr/bin/python3
import asyncio
import json
import os
import random
import urllib
from collections import deque
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional
from urllib import request

import feedparser
import gtts
import pygame
from hypercorn import Config
from hypercorn.asyncio import serve
from mutagen.mp3 import MP3
from quart import send_from_directory
from quart_cors import cors
from quart_openapi import Pint, Resource

import config
import constants
import secrets

lastTracks = deque()
track: Optional[str] = None
trackQueue = deque()
is_paused: bool = True

lastHour: datetime.hour = None
lastHalfHour: Optional[int] = None
lastMinute: datetime.minute = None

checkingFeed: bool = False
lastFeedCheck: Optional[datetime] = None
lastFeedItem: Optional[str] = None

weatherLoaded: datetime.day = None
weather: json = None

running: asyncio.futures.Future

app = cors(Pint(__name__, title='Superhet', static_folder='frontend/build'))


@app.route('/')
async def root_api():
    print("Root")
    return await send_from_directory('frontend/build', 'index.html')


@app.route('/<path:path>')
async def path_api(path):
    print("Path", path)
    return await send_from_directory('frontend/build', path)


@app.route('/api/next')
class NextAPI(Resource):
    async def get(self):
        pygame.mixer.music.stop()
        return "done"

    async def post(self):
        pygame.mixer.music.stop()
        return "success"


@app.route('/api/ping')
class PingAPI(Resource):
    async def get(self):
        return "pong"


@app.route('/api/back')
class BackAPI(Resource):
    async def get(self):
        await playLast()
        return "done"

    async def post(self):
        await playLast()
        return "success"


@app.route('/api/playing')
class PlayingAPI(Resource):
    async def get(self):
        return json.dumps(
            {'last': list(map(str, lastTracks)), 'playing': str(track), 'next': list(map(str, trackQueue)),
             'time_left': -1 if is_paused else 1 + int(MP3(track).info.length * 1000) - pygame.mixer.music.get_pos()})


@app.route('/api/pause')
class PauseAPI(Resource):
    async def get(self):
        global is_paused
        pygame.mixer.music.pause()
        is_paused = True
        return "done"

    async def post(self):
        global is_paused
        pygame.mixer.music.pause()
        is_paused = True
        return "success"


@app.route('/api/unpause')
class UnpauseAPI(Resource):
    async def get(self):
        global is_paused
        pygame.mixer.music.unpause()
        is_paused = False
        return "done"

    async def post(self):
        global is_paused
        pygame.mixer.music.unpause()
        is_paused = False
        return "success"


@app.route('/api/weather')
class WeatherAPI(Resource):
    async def get(self):
        await do_weather()
        pygame.mixer.music.stop()
        return "done"

    async def post(self):
        await do_weather()
        pygame.mixer.music.stop()
        return "success"


@app.route('/api/break')
class BreakAPI(Resource):
    async def get(self):
        await do_break(False, True)
        return "done"

    async def post(self):
        await do_break(False, True)
        return "success"


@app.route('/api/stop')
class StopAPI(Resource):
    async def get(self):
        print("HERE")
        exit(0)

    async def post(self):
        print("HERE")
        exit(0)


# https://codereview.stackexchange.com/a/202801
def get_random_file(ext, top=os.getcwd(), subdir="**"):
    file_list = list(Path(top).glob(f"{subdir}/*.{ext}"))
    if not len(file_list):
        return None  # f"No files matched that extension: {ext}"
    rand = random.randint(0, len(file_list) - 1)
    return file_list[rand]


def calculate_mix(epoch=datetime.today().date()):
    if epoch in config.music_mix:
        return config.music_mix[epoch]
    last_date: date = next(config.music_mix.irange(maximum=epoch, reverse=True), None)
    next_date: date = next(config.music_mix.irange(minimum=epoch), None)
    last_mix: dict = config.music_mix[last_date]
    next_mix: dict = config.music_mix[next_date]
    if last_mix == next_mix:
        return last_mix
    since_last: int = (epoch - last_date).days
    until_next: int = (next_date - epoch).days
    last_weight: float = until_next / (since_last + until_next)
    next_weight: float = since_last / (since_last + until_next)
    epoch_mix = dict()
    for source in set(list(last_mix.keys()) + list(next_mix.keys())):
        epoch_mix[source] = (last_mix[source] * last_weight if source in last_mix else 0) + (
            next_mix[source] * next_weight if source in next_mix else 0)
    return epoch_mix


def getNext():
    global trackQueue
    mix = calculate_mix()
    tracks = []
    weights = []
    for source in mix.keys():
        source_track = get_random_file("mp3", config.MUSICDIR + "/" + source)
        if source_track is not None:
            tracks.append(source_track)
            weights.append(mix[source])
    if tracks:
        trackQueue.append(random.choices(tracks, weights)[0])
    else:
        file = get_random_file("mp3", config.MUSICDIR + "/instrumental")
        if file is not None:
            trackQueue.append(file)


async def playNext():
    global track
    global is_paused
    if len(trackQueue) < 1:
        getNext()
        if len(trackQueue) < 1:
            await asyncio.sleep(1)
            asyncio.get_running_loop().create_task(playNext())
            return
    if len(trackQueue) > 0:
        lastTracks.appendleft(track)
        if len(lastTracks) > 30:
            lastTracks.pop()
        track = str(trackQueue[0])
        print("Playing", list(trackQueue))  # [0]
        is_paused = False
        play = trackQueue.popleft()
        try:
            await asyncio.get_running_loop().run_in_executor(None, pygame.mixer.music.load, play)
            pygame.mixer.music.play()
        except Exception as e:
            pygame.mixer.music.unload()
            await move("broken")
            asyncio.get_running_loop().create_task(playNext())


async def playLast():
    global track
    global is_paused
    if lastTracks[0] is None:
        lastTracks.popleft()
    if len(lastTracks) > 0:
        trackQueue.appendleft(track)
        track = lastTracks[0]
        lastTracks.popleft()
        print("Rewinding", track)
        await asyncio.get_running_loop().run_in_executor(None, pygame.mixer.music.load, track)
        pygame.mixer.music.play()
        is_paused = False


async def checkFeed():
    print("Checking the RSS feed...")
    global checkingFeed
    global lastFeedItem
    global lastFeedCheck
    lastFeedCheck = datetime.now()
    nf = await asyncio.get_running_loop().run_in_executor(None, feedparser.parse, config.NEWSFEED)
    if nf.bozo:
        print("Feed parse failed because", nf.bozo_exception.reason)
        return
    link = nf['entries'][0]['links'][0]['href']
    if link != lastFeedItem:
        success = False
        while not success:
            try:
                print("Downloading...")
                await asyncio.get_running_loop().run_in_executor(None, request.urlretrieve, link, 'news.mp3')
                print("Download successful!")
                lastFeedItem = link
                trackQueue.append('news.mp3')
                success = True
            except urllib.error.URLError as e:
                print("Download failed because", e.reason)
                # time.sleep(10)
    else:
        print("There was no new entry.")


async def loadWeatherData():
    global weather
    global weatherLoaded
    url = "https://api.openweathermap.org/data/2.5/onecall?" + config.OPENWEATHER_LOC + "&appid=" + secrets.OpenWeatherKey + "&units=imperial"
    print(url)
    try:
        weather = json.load(await asyncio.get_running_loop().run_in_executor(None, request.urlopen, url))
        weatherLoaded = datetime.today()
    except urllib.error.URLError as e:
        print("loadWeatherData failed because", e.reason)


async def genWeatherReport():
    print("Generating a weather report...")
    current = weather["current"]
    print(current)
    report = "Currently the temperature is " + str(round(current["temp"])) + " degrees and it feels like " + str(
        round(current["feels_like"])) + ". " + constants.OW_CODE_SPOKEN_CURRENT[
                 current["weather"][0]["id"]] + "."
    try:
        (await asyncio.get_running_loop().run_in_executor(None, gtts.gTTS, report)).save(f'report.mp3')
        trackQueue.appendleft('report.mp3')
        print("Done!")
    except gtts.tts.gTTSError as e:
        print("Weather failed because", e.msg)


async def genWeatherForecast(index=0, index_spoken="Today"):
    print("Generating a weather forecast...")
    today = weather["daily"][index]
    print(today)
    report = f"{index_spoken} the high will be {round(today['temp']['max'])} " \
             f"and the low will be {round(today['temp']['min'])}. " \
             f"{constants.OW_CODE_SPOKEN_FUTURE[today['weather'][0]['id']]} " \
             f"with a {round(today['pop']) if today['pop'] > 1 else 0} percent chance of rain."
    try:
        (await asyncio.get_running_loop().run_in_executor(None, gtts.gTTS, report)).save(f'forecast{index}.mp3')
        trackQueue.appendleft(f'forecast{index}.mp3')
        print("Done!")
    except gtts.tts.gTTSError as e:
        print("Weather failed because", e.msg)


async def interruptMusic():
    global is_paused
    pygame.mixer.music.set_volume(config.volume * .75)
    await asyncio.sleep(1)
    pygame.mixer.music.set_volume(config.volume * .50)
    await asyncio.sleep(1)
    pygame.mixer.music.set_volume(config.volume * .25)
    await asyncio.sleep(1)
    if track is not None:
        if track == "news.mp3" or track == "report.mp3" or track == "forecast.mp3":
            pygame.mixer.music.pause()
            is_paused = True


async def unInterruptMusic():
    global is_paused
    if track is not None:
        if track == "news.mp3" or track == "report.mp3" or track.startswith("forecast"):
            pygame.mixer.music.unpause()
            is_paused = False
    await asyncio.sleep(1)
    pygame.mixer.music.set_volume(config.volume * .50)
    await asyncio.sleep(1)
    pygame.mixer.music.set_volume(config.volume * .75)
    await asyncio.sleep(1)
    pygame.mixer.music.set_volume(config.volume * 1)


async def move(dest: str, to_move: Optional[str] = None, src: Optional[str] = None):
    if to_move is None:
        to_move = str(track)
        #await playNext()
        #lastTracks.popleft()
    if src is None:
        src = config.MUSICDIR
    move_to = to_move.replace(src, dest)
    dest_subdir = os.path.dirname(move_to)
    os.makedirs(dest_subdir, exist_ok=True)
    os.rename(to_move, move_to)


def last_hour(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt - timedelta(minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)


def last_half_hour(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt - timedelta(minutes=(dt.minute % 30), seconds=dt.second, microseconds=dt.microsecond)


def last_minute(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt - timedelta(seconds=dt.second, microseconds=dt.microsecond)


def last_5_minutes(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt - timedelta(minutes=(dt.minute % 5), seconds=dt.second, microseconds=dt.microsecond)


def until_next_hour(dt=None):
    if dt is None:
        dt = datetime.now()
    return last_hour(dt) + timedelta(hours=1) - dt


def until_next_half_hour(dt=None):
    if dt is None:
        dt = datetime.now()
    return last_half_hour(dt) + timedelta(minutes=30) - dt


def until_next_minute(dt=None):
    if dt is None:
        dt = datetime.now()
    return last_minute(dt) + timedelta(minutes=1) - dt


def until_next_5_minutes(dt=None):
    if dt is None:
        dt = datetime.now()
    return last_5_minutes(dt) + timedelta(minutes=5) - dt


async def do_break(say_time=True, duck=True):
    if duck:
        await interruptMusic()
    sayidentity = pygame.mixer.Sound(get_random_file("ogg", "breaks", f"*/identify/{'normal'}"))
    pygame.mixer.Channel(0).play(sayidentity)
    await asyncio.sleep(sayidentity.get_length())
    if say_time:
        half_hour = last_half_hour()
        saytime = pygame.mixer.Sound(get_random_file(
            f"{half_hour.hour:02d}-{half_hour.minute:02d}.ogg",
            "breaks",
            "*/time"
        ))
        pygame.mixer.Channel(0).play(saytime)
        await asyncio.sleep(saytime.get_length())
    if duck:
        await unInterruptMusic()


async def loop_break():
    while True:
        await asyncio.sleep(until_next_half_hour().total_seconds())
        await do_break()


async def loop_feed():
    while True:
        await checkFeed()
        await asyncio.sleep(until_next_5_minutes().total_seconds())


async def do_weather():
    await loadWeatherData()
    if weather is not None:
        if weather is not None or weatherLoaded == datetime.today():
            await genWeatherForecast(1, "Tomorrow")
            await genWeatherForecast()
        if weatherLoaded:
            await genWeatherReport()


async def loop_weather():
    while True:
        await do_weather()
        await asyncio.sleep(until_next_half_hour().total_seconds())


def pygame_event_loop(loop, event_queue):
    while True:
        event = pygame.event.wait()
        asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)


async def handle_events(event_queue):
    while True:
        event = await event_queue.get()
        if event.type == pygame.QUIT:
            break
        elif event.type == constants.SONG_END:
            await playNext()
        else:
            pass
            # print("event", event)
    asyncio.get_event_loop().stop()


async def main():
    global running
    loop = asyncio.get_running_loop()
    running = loop.create_future()
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.set_endevent(constants.SONG_END)
    app_config = Config()
    app_config.bind = ["0.0.0.0:8080"]
    loop.create_task(serve(app, app_config))
    await do_break(False, False)
    event_queue = asyncio.Queue()
    pygame_task = loop.run_in_executor(None, pygame_event_loop, loop, event_queue)
    event_task = asyncio.ensure_future(handle_events(event_queue))
    asyncio.create_task(loop_break())
    asyncio.create_task(loop_weather())
    asyncio.create_task(loop_feed())
    asyncio.create_task(playNext())
    try:
        await running
    except KeyboardInterrupt:
        pass
    finally:
        event_task.cancel()


if __name__ == '__main__':
    asyncio.run(main())
    exit(0)
