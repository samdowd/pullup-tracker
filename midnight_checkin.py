import os
import dataset
import time
import json
import subprocess
from stuf import stuf
from gtts import gTTS

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Connect to the databases
roommates_db = dataset.connect('postgresql://sam:hellfire@localhost:5432/roommates', row_type=stuf)
users_db = roommates_db['users']
sets_db = roommates_db['sets']
dtotals_db = roommates_db['daily_totals']

# Find the users
sam = users_db.find_one(name='Sam')
zach = users_db.find_one(name='Blade')
jarrod = users_db.find_one(name='J-bod')

# Find today's loser
today_worst_count = min(sam.day_total, zach.day_total, jarrod.day_total)
today_loser = users_db.find_one(day_total=today_worst_count)

# Add daily totals and month to date to daily_totals database and reset to 0
for user in users_db:
    dtotals_db.insert(dict(user_name=user.name,
                           total=user.day_total,
                           month_to_date=user.month_total,
                           date=time.strftime("%Y-%m-%d"))
                      )
    users_db.update(dict(name=user.name,
                         day_total=0),
                    ['name'])

# Update users
sam = users_db.find_one(name='Sam')
zach = users_db.find_one(name='Blade')
jarrod = users_db.find_one(name='J-bod')

# Find winner and loser for all time
alltime_best_count = max(sam.total, zach.total, jarrod.total)
alltime_winner = users_db.find_one(total=alltime_best_count)
alltime_worst_count = min(sam.total, zach.total, jarrod.total)
alltime_loser = users_db.find_one(total=alltime_worst_count)

# Call out the losers
if alltime_loser.name == today_loser.name:
    message = gTTS(text="{} is pathetic and is the biggest bitch today and always... {} is the current champion!".format(today_loser.name, alltime_winner.name), lang="en")
else:
    message = gTTS(text="{} is a little bitch, but {} is still the biggest bitch of all time... {} is the current champion!"
                   .format(today_loser.name, alltime_loser.name, alltime_winner.name), lang="en")
message.save("nightly_speech.mp3")
os.system('mpg123 nightly_speech.mp3 &')
time.sleep(10)

# Make the new image and freeze json file for site to use
sams_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Sam' ORDER BY date;")
zachs_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Blade' ORDER BY date;")
jarrods_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'J-bod' ORDER BY date;")
dataset.freeze(sams_days, format='json', filename='sams_days.json')
dataset.freeze(zachs_days, format='json', filename='zachs_days.json')
dataset.freeze(jarrods_days, format='json', filename='jarrods_days.json')

dataset.freeze(users_db, format='json', filename='overview.json')

print("datasets frozen")
time.sleep(10)

sams_days = json.load(open('sams_days.json', 'r'))['results']
zachs_days = json.load(open('zachs_days.json', 'r'))['results']
jarrods_days = json.load(open('jarrods_days.json', 'r'))['results']

sam_totals = [0]
days = [15]
for day in sams_days:
    sam_totals.append(day['month_to_date'])
    days.append(day['date'][8:])
zach_totals = [0]
for day in zachs_days:
    zach_totals.append(day['month_to_date'])
jarrod_totals = [0]
for day in jarrods_days:
    jarrod_totals.append(day['month_to_date'])

totals = sam_totals + zach_totals + jarrod_totals

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(days, sam_totals, 'r-', days, zach_totals, 'b-', days, jarrod_totals, 'g-')
plt.xlabel("Day of the month")
plt.ylabel("Number of Pullups")
plt.title("Monthly Running Total by Day")
sam_patch = mpatches.Patch(color='red', label='Sam')
zach_patch = mpatches.Patch(color='blue', label='Zach')
jarrod_patch = mpatches.Patch(color='green', label='Jarrod')
plt.legend(handles=[sam_patch, zach_patch, jarrod_patch])
plt.axis([0, 31, 0, max(totals) * 2])

fig.savefig('./pullupstats/static/dailies.png')

# Push to heroku
subprocess.call(["git", "add", "."])
subprocess.call(["git", "commit", "-m", "'auto'"])
subprocess.call(["git", "push", "heroku", "master"])
