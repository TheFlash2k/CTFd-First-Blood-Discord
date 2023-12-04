# CTFd API endpoint
HOST = "http://192.168.163.168"

# CTFd API token
API_TOKEN = ""

# How frequently to check for new solves
POLL_PERIOD = 5

# Discord webhook url
FIRST_BLOOD_WEBHOOK_URL = ""
SOLVE_WEBHOOK_URL = ""

# Announcer Endpoint:
ANNOUNCER_URL = ""

# Available template variables are:
# User Name (if individual mode) / Team Name (if team mode): {team_name} {user_name}
# Challenge Name: {chal_name}
# Category: {category}
FIRST_BLOOD_ANNOUNCE_STRING = ":knife::drop_of_blood: First Blood for challenge **{chal_name}** goes to **{user_name}** of team **__{team_name}__**! {emojis}"

# To be used with announce_all_solves
SOLVE_ANNOUNCE_STRING = "**{user_name}** of **__{team_name}__** just solved **{chal_name}**! {emojis}"

# Whether or not to announce all solves as well as first bloods
ANNOUNCE_ALL_SOLVES = True

# Category Emojis (if any)
CATEGORY_EMOJIS = {
    "web": [":globe_with_meridians:"],
    "crypto": [":sob::closed_lock_with_key:"],
    "pwn": [":bug:"],
    "rev": [":rewind:"],
    "forensics": [":mag:"],
    "osint": [":detective:"],
    "blockchain": [":white_large_square::chains:"],
    "misc": [":jigsaw:"],
}
