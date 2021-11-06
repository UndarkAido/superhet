#! /usr/bin/python3
import json
import os
import random
import time
import urllib
from collections import deque
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional
from urllib import request

import feedparser
import gtts
from pygame import mixer

import config
import constants
import secrets

lastTrack: Optional[str] = None
track: Optional[str] = None
trackQueue = deque()

lastHour: datetime.hour = None
lastHalfHour: int = None
lastMinute: datetime.minute = None

checkingFeed: bool = False
lastFeedCheck: Optional[datetime] = None
lastFeedItem: Optional[str] = None

weatherLoaded: bool = False
weather: json = None

firstBreak: bool = True

mixer.init()


# https://codereview.stackexchange.com/a/202801
def get_random_file(ext, top=os.getcwd(), subdir="**"):
    file_list = list(Path(top).glob(f"{subdir}/*.{ext}"))
    if not len(file_list):
        return None # f"No files matched that extension: {ext}"
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
        trackQueue.append(get_random_file("mp3", config.MUSICDIR + "/normal"))


def playNext():
    global lastTrack
    global track
    if len(trackQueue) < 1:
        getNext()
    if len(trackQueue) > 0:
        lastTrack = track
        track = str(trackQueue[0])
        print("Playing", trackQueue[0])
        mixer.music.load(trackQueue[0])
        mixer.music.play()
        trackQueue.popleft()
        getNext()


def checkFeed():
    print("Checking the RSS feed...")
    global checkingFeed
    global lastFeedItem
    global lastFeedCheck
    lastFeedCheck = datetime.now()
    nf = feedparser.parse(config.NEWSFEED)
    if nf.bozo:
        print("Feed parse failed because", nf.bozo_exception.reason)
        return
    link = nf['entries'][0]['links'][0]['href']
    if link != lastFeedItem:
        success = False
        while not success:
            try:
                print("Downloading...")
                request.urlretrieve(link, 'news.mp3')
                print("Download successful!")
                lastFeedItem = link
                trackQueue.appendleft('news.mp3')
                success = True
            except urllib.error.URLError as e:
                print("Download failed because", e.reason)
                # time.sleep(10)
    else:
        print("There was no new entry.")


def loadWeatherData():
    global weather
    global weatherLoaded
    url = "https://api.openweathermap.org/data/2.5/onecall?" + config.OPENWEATHER_LOC + "&appid=" + secrets.OpenWeatherKey + "&units=imperial"
    print(url)
    try:
        weather = json.load(request.urlopen(url))
        weatherLoaded = True
    except urllib.error.URLError as e:
        print("loadWeatherData failed because", e.reason)
        weatherLoaded = False


def genWeatherReport():
    print("Generating a weather report...")
    # try:
    #     with request.urlopen(config.WTTRIN_SRC + "/" + config.WTTRIN_LOC + "?format=j1") as res:
    #         data = json.load(res)
    #         report = "The temperature is " + data["current_condition"][0]["temp_F"] + " degrees and it feels like " + \
    #                  data["current_condition"][0]["FeelsLikeF"] + ". " + constants.WWWO_CODE_SPOKEN[
    #                      data["current_condition"][0]["weatherCode"]] + "."
    #         try:
    #             gtts.gTTS(report).save('report.mp3')
    #             trackqueue.appendleft('report.mp3')
    #             print("Done!")
    #         except gtts.tts.gTTSError as e:
    #             print("Weather failed because", e.msg)
    # except urllib.error.URLError as e:
    #     print("Weather failed because", e.reason)
    current = weather["current"]
    print(current)
    report = "Currently the temperature is " + str(round(current["temp"])) + " degrees and it feels like " + str(
        round(current["feels_like"])) + ". " + constants.OW_CODE_SPOKEN_CURRENT[
                 current["weather"][0]["id"]] + "."
    try:
        gtts.gTTS(report).save('report.mp3')
        trackQueue.appendleft('report.mp3')
        print("Done!")
    except gtts.tts.gTTSError as e:
        print("Weather failed because", e.msg)


def genWeatherForecast(index=0, index_spoken="Today"):
    print("Generating a weather forecast...")
    today = weather["daily"][index]
    print(today)
    report = index_spoken + " the high will be " + str(round(today["temp"]["max"])) + " and the low will be " + str(
        round(today["temp"]["min"])) + "." + constants.OW_CODE_SPOKEN_FUTURE[
                 today["weather"][0]["id"]] + " with a " + str(
        round(today["pop"] * 100)) + " percent chance of rain."
    try:
        gtts.gTTS(report).save('forecast' + str(index) + '.mp3')
        trackQueue.appendleft('forecast' + str(index) + '.mp3')
        print("Done!")
    except gtts.tts.gTTSError as e:
        print("Weather failed because", e.msg)


def interruptMusic():
    if track is not None:
        if track == "news.mp3" or track == "report.mp3" or track == "forecast.mp3":
            mixer.music.pause()
        else:
            mixer.music.set_volume(.25)


def unInterruptMusic():
    if track is not None:
        if track == "news.mp3" or track == "report.mp3" or track.startswith("forecast"):
            mixer.music.unpause()
        else:
            mixer.music.set_volume(1.0)


if __name__ == '__main__':
    getNext()
    while True:
        if not mixer.music.get_busy():
            playNext()
        if lastHour is None or datetime.now().hour != lastHour:
            lastHour = datetime.now().hour
            loadWeatherData()
            if weather is not None:
                genWeatherForecast(1, "Tomorrow")
                genWeatherForecast()
                if weatherLoaded:
                    genWeatherReport()
        if lastMinute is None or datetime.now().minute != lastMinute:
            lastMinute = datetime.now().minute
        if lastHalfHour is None or int(datetime.now().minute / 30) != lastHalfHour:
            lastHalfHour = int(datetime.now().minute / 30)
            interruptMusic()
            sayidentity = mixer.Sound(get_random_file("ogg", "breaks", f"*/identify/{'normal'}"))
            saytime = mixer.Sound(get_random_file(
                f"{datetime.now().hour:02d}-{lastHalfHour * 30:02d}.ogg",
                "breaks",
                "*/time"
            ))
            mixer.Channel(0).play(sayidentity)
            if firstBreak:
                firstBreak = False
            else:
                time.sleep(sayidentity.get_length())
                mixer.Channel(0).play(saytime)
            time.sleep(saytime.get_length())
            unInterruptMusic()
        if lastFeedCheck is None or datetime.now() > lastFeedCheck + timedelta(minutes=1):
            checkFeed()
        time.sleep(.5)
