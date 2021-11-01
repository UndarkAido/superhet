import os
from collections import deque
from pathlib import Path

import gtts
from pydub import AudioSegment

targetdir = "breaks/gtts"
station = "Superhet Radio"

generated = deque()


def generate(message, output):
    fullpath = targetdir + "/" + output + '.mp3'
    print(fullpath)
    if not os.path.exists(os.path.dirname(fullpath)):
        os.makedirs(os.path.dirname(fullpath))
    gtts.gTTS(message).save(fullpath)
    generated.append(fullpath)


def convert():
    while len(generated) > 0:
        AudioSegment.from_mp3(generated[0]).export(Path(generated[0]).with_suffix('.ogg'), format="ogg")
        generated.popleft()


if __name__ == '__main__':
    generate(f"This is {station}.", "identify/normal/thisis")
    generate(f"You're listening to {station}.", "identify/normal/yourelistening")
    generate(f"You're tuned to {station}.", "identify/normal/youretuned")
    generate(f"Thank you for listening to {station}.", "identify/normal/thankyou")
    for hour in range(0, 24):
        clockhour = 12 if (hour % 12) == 0 else hour % 12
        for periods in [["abb", "AM", "PM"], ["phon", "in the morning", "in the evening"]]:
            period = periods[1] if hour / 12 < 1 else periods[2]
            for fraction in [["00", ["{}", "{} o'clock"]], ["30", ["{}:30", "half past {}"]]]:
                for fi in range(len(fraction[1])):
                    time = fraction[1][fi].format(clockhour) + " " + period
                    prefix = "time/"
                    suffix = f".{periods[0]}.{fi:02d}.{hour:02d}-{fraction[0]}"
                    print(time, suffix)
                    generate(f"It is {time}.", f"{prefix}itis{suffix}")
                    generate(f"It is now {time}.", f"{prefix}itisnow{suffix}")
                    if periods[0] != "phon":
                        generate(f"The time is {time}.", f"{prefix}thetimeis{suffix}")
                        generate(f"The time is now {time}.", f"{prefix}thetimeisnow{suffix}")
    convert()
