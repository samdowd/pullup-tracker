# -*- coding: utf-8 -*-
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

# Update users
sam = users_db.find_one(name='Sam')
zach = users_db.find_one(name='Blade')
jarrod = users_db.find_one(name='J-bod')

# Make the new image and freeze json file for site to use
sams_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Sam' AND date::date > '2017-04-30'::date ORDER BY date;")
zachs_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Blade' AND date::date > '2017-04-30'::date ORDER BY date;")
jarrods_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'J-bod' AND date::date > '2017-04-30'::date ORDER BY date;")
dataset.freeze(sams_days, format='json', filename='/home/pi/pulluptracker/sams_days.json')
dataset.freeze(zachs_days, format='json', filename='/home/pi/pulluptracker/zachs_days.json')
dataset.freeze(jarrods_days, format='json', filename='/home/pi/pulluptracker/jarrods_days.json')

dataset.freeze(users_db, format='json', filename='/home/pi/pulluptracker/overview.json')

print("datasets frozen")
time.sleep(10)

sams_days = json.load(open('/home/pi/pulluptracker/sams_days.json', 'r'))['results']
zachs_days = json.load(open('/home/pi/pulluptracker/zachs_days.json', 'r'))['results']
jarrods_days = json.load(open('/home/pi/pulluptracker/jarrods_days.json', 'r'))['results']

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

print(sam_totals)
print(zach_totals)
print(jarrod_totals)

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

fig.savefig('/home/pi/pulluptracker/pullupstats/static/dailies.png')

# Push to heroku
subprocess.call(["git", "add", "."], cwd="/home/pi/pulluptracker/")
subprocess.call(["git", "commit", "-m", "'auto'"], cwd="/home/pi/pulluptracker/")
subprocess.call(["git", "push", "heroku", "master"], cwd="/home/pi/pulluptracker/")
