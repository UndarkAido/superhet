from datetime import datetime, date, timedelta

import holidays
from sortedcontainers import SortedDict

NEWSFEED = "https://feeds.npr.org/500005/podcast.xml"
MUSICDIR = "music"
BREAKDIR = "breaks"

# WTTRIN_SRC = "http://wttr.in"
# WTTRIN_LOC = ""  # "Austin+TX"

OPENWEATHER_LOC = "lat=30.267151&lon=-97.743057"

epoch_year = date.today().year
us_holidays = holidays.CountryHoliday('US', years=epoch_year)

year_start = date(epoch_year, 1, 1)
thanksgiving: date = us_holidays.get_named("Thanksgiving")[0]
christmas: date = us_holidays.get_named("Christmas")[0]
year_end = date(epoch_year, 12, 31)

music_mix = SortedDict({
    year_start: {
        "normal": 1.0
    },
    thanksgiving: {
        "normal": 1.0
    },
    thanksgiving + timedelta(days=1): {
        "normal": 0.9,
        "holidays": 0.1
    },
    christmas - timedelta(weeks=1): {
        "holidays": 1.0
    },
    christmas: {
        "holidays": 1.0
    },
    year_end: {
        "normal": 1.0
    }
})
