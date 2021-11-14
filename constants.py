import pygame

OW_CODE_SPOKEN_CURRENT = {
    # Group 2xx: Thunderstorm
    # thunderstorm with light rain
    200: "there is a thunderstorm with light rain",
    # thunderstorm with rain
    201: "there is a thunderstorm with rain",
    # thunderstorm with heavy rain
    202: "there is a thunderstorm with heavy rain",
    # light thunderstorm
    210: "there is a light thunderstorm",
    # thunderstorm
    211: "there is a thunderstorm",
    # heavy thunderstorm
    212: "there is a heavy thunderstorm",
    # ragged thunderstorm
    221: "there is a ragged thunderstorm",
    # thunderstorm with light drizzle
    230: "there is a thunderstorm with light drizzle",
    # thunderstorm with drizzle
    231: "there is a thunderstorm with drizzle",
    # thunderstorm with heavy drizzle
    232: "there is a thunderstorm with heavy drizzle",
    # Group 3xx: Drizzle
    # light intensity drizzle
    300: "there is a light intensity drizzle",
    # drizzle
    301: "there is a drizzle",
    # heavy intensity drizzle
    302: "there is a heavy intensity drizzle",
    # light intensity drizzle rain
    310: "there is a light intensity drizzle rain",
    # drizzle rain
    311: "there is a drizzle rain",
    # heavy intensity drizzle rain
    312: "there is a heavy intensity drizzle rain",
    # shower rain and drizzle
    313: "there is a shower rain and drizzle",
    # heavy shower rain and drizzle
    314: "there is a heavy shower rain and drizzle",
    # shower drizzle
    321: "there is a shower drizzle",
    # Group 5xx: Rain
    # light rain
    500: "there is light rain",
    # moderate rain
    501: "there is moderate rain",
    # heavy intensity rain
    502: "there is heavy intensity rain",
    # very heavy rain
    503: "there is very heavy rain",
    # extreme rain
    504: "there is extreme rain",
    # freezing rain
    511: "there is freezing rain",
    # light intensity shower rain
    520: "there is light intensity shower rain",
    # shower rain
    521: "there is shower rain",
    # heavy intensity shower rain
    522: "there is heavy intensity shower rain",
    # ragged shower rain
    531: "there is ragged shower rain",
    # Group 6xx: Snow
    # light snow
    600: "there is light snow",
    # Snow
    601: "there is snow",
    # Heavy snow
    602: "there is heavy snow",
    # Sleet
    611: "there is sleet",
    # Light shower sleet
    612: "there is light shower sleet",
    # Shower sleet
    613: "there is shower sleet",
    # Light rain and snow
    615: "there is light rain and snow",
    # Rain and snow
    616: "there is rain and snow",
    # Light shower snow
    620: "there is light shower snow",
    # Shower snow
    621: "there is shower snow",
    # Heavy shower snow
    622: "there is heavy shower snow",
    # Group 7xx: Atmosphere
    # mist
    701: "there is mist",
    # Smoke
    711: "there is smoke",
    # Haze
    721: "there is haze",
    # sand/ dust whirls
    731: "there is sand or dust whirls",
    # fog
    741: "there is fog",
    # sand
    751: "there is sand",
    # dust
    761: "there is dust",
    # volcanic ash
    762: "there is volcanic ash",
    # squalls
    771: "there are squalls",
    # tornado
    781: "there is a tornado",
    # Group 800: Clear
    # clear sky
    800: "there is a clear sky",
    # Group 80x: Clouds
    # few clouds: 11-25%
    801: "there are few clouds",
    # scattered clouds: 25-50%
    802: "there are scattered clouds",
    # broken clouds: 51-84%
    803: "there are broken clouds",
    # overcast clouds: 85-100%
    804: "there are overcast clouds",
}

OW_CODE_SPOKEN_FUTURE = {
    # Group 2xx: Thunderstorm
    # thunderstorm with light rain
    200: "there will be a thunderstorm with light rain",
    # thunderstorm with rain
    201: "there will be a thunderstorm with rain",
    # thunderstorm with heavy rain
    202: "there will be a thunderstorm with heavy rain",
    # light thunderstorm
    210: "there will be a light thunderstorm",
    # thunderstorm
    211: "there will be a thunderstorm",
    # heavy thunderstorm
    212: "there will be a heavy thunderstorm",
    # ragged thunderstorm
    221: "there will be a ragged thunderstorm",
    # thunderstorm with light drizzle
    230: "there will be a thunderstorm with light drizzle",
    # thunderstorm with drizzle
    231: "there will be a thunderstorm with drizzle",
    # thunderstorm with heavy drizzle
    232: "there will be a thunderstorm with heavy drizzle",
    # Group 3xx: Drizzle
    # light intensity drizzle
    300: "there will be a light intensity drizzle",
    # drizzle
    301: "there will be a drizzle",
    # heavy intensity drizzle
    302: "there will be a heavy intensity drizzle",
    # light intensity drizzle rain
    310: "there will be a light intensity drizzle rain",
    # drizzle rain
    311: "there will be a drizzle rain",
    # heavy intensity drizzle rain
    312: "there will be a heavy intensity drizzle rain",
    # shower rain and drizzle
    313: "there will be a shower rain and drizzle",
    # heavy shower rain and drizzle
    314: "there will be a heavy shower rain and drizzle",
    # shower drizzle
    321: "there will be a shower drizzle",
    # Group 5xx: Rain
    # light rain
    500: "there will be light rain",
    # moderate rain
    501: "there will be moderate rain",
    # heavy intensity rain
    502: "there will be heavy intensity rain",
    # very heavy rain
    503: "there will be very heavy rain",
    # extreme rain
    504: "there will be extreme rain",
    # freezing rain
    511: "there will be freezing rain",
    # light intensity shower rain
    520: "there will be light intensity shower rain",
    # shower rain
    521: "there will be shower rain",
    # heavy intensity shower rain
    522: "there will be heavy intensity shower rain",
    # ragged shower rain
    531: "there will be ragged shower rain",
    # Group 6xx: Snow
    # light snow
    600: "there will be light snow",
    # Snow
    601: "there will be snow",
    # Heavy snow
    602: "there will be heavy snow",
    # Sleet
    611: "there will be sleet",
    # Light shower sleet
    612: "there will be light shower sleet",
    # Shower sleet
    613: "there will be shower sleet",
    # Light rain and snow
    615: "there will be light rain and snow",
    # Rain and snow
    616: "there will be rain and snow",
    # Light shower snow
    620: "there will be light shower snow",
    # Shower snow
    621: "there will be shower snow",
    # Heavy shower snow
    622: "there will be heavy shower snow",
    # Group 7xx: Atmosphere
    # mist
    701: "there will be mist",
    # Smoke
    711: "there will be smoke",
    # Haze
    721: "there will be haze",
    # sand/ dust whirls
    731: "there will be sand or dust whirls",
    # fog
    741: "there will be fog",
    # sand
    751: "there will be sand",
    # dust
    761: "there will be dust",
    # volcanic ash
    762: "there will be volcanic ash",
    # squalls
    771: "there will be squalls",
    # tornado
    781: "there will be a tornado",
    # Group 800: Clear
    # clear sky
    800: "there will be a clear sky",
    # Group 80x: Clouds
    # few clouds: 11-25%
    801: "there will be few clouds",
    # scattered clouds: 25-50%
    802: "there will be scattered clouds",
    # broken clouds: 51-84%
    803: "there will be broken clouds",
    # overcast clouds: 85-100%
    804: "there will be overcast clouds",
}

SONG_END = pygame.USEREVENT + 1
