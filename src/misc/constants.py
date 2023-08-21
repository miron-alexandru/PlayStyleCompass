# List of platform IDs
"""
Pc(94)
Mac(17)
Mobile (123, 96)
Nintendo ( 21), (52)
Xbox (32)
PlayStation (22)
Linux (152)
Browser (140)
Wii (36)
"""

platform_ids = ['94', '17', '123', '96', '21', '52', '32', '22', '152', '140', '36' ]

genres = ['Action', 'Adventure', 'Role-Playing', 'Strategy', 'Sports', 'Shooter', 'Simulation', 'Puzzle', 'Horror']
platforms = ['PC', 'Mobile', 'Wii', 'Nintendo', 'Xbox', 'PlayStation', 'Mac', 'Linux', 'Browser']

# Modify API Key
API_KEY = ''

# URL
BASE_URL = 'https://www.giantbomb.com/api/'

headers = {
    "User-Agent": "PlayStyleCompass/1.0",
}