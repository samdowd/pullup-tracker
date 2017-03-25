import os
import dataset
import json
import time
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


roommates_db = dataset.connect('postgresql://sam:hellfire@localhost:5432/roommates')
users_db = roommates_db['users']
dtotals_db = roommates_db['daily_totals']

# Make the new image and freeze json file for site to use
sams_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Sam' ORDER BY date;")
zachs_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'Blade' ORDER BY date;")
jarrods_days = roommates_db.query("SELECT user_name, total, month_to_date, date FROM daily_totals WHERE user_name = 'J-bod' ORDER BY date;")
dataset.freeze(sams_days, format='json', filename='sams_days.json')
dataset.freeze(zachs_days, format='json', filename='zachs_days.json')
dataset.freeze(jarrods_days, format='json', filename='jarrods_days.json')

dataset.freeze(users_db, format='json', filename='overview.json')

print("datasets frozen")

sams_days = json.load(open('sams_days.json', 'r'))['results']
zachs_days = json.load(open('zachs_days.json', 'r'))['results']
jarrods_days = json.load(open('jarrods_days.json', 'r'))['results']

print("files loaded")

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

print("totals found")

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

fig.savefig('pullupstats/static/dailies.png')

print ("image made")

subprocess.call(["git", "add", "."])
subprocess.call(["git", "commit", "-m", "'auto'"])
subprocess.call(["git", "push", "heroku", "master"])

print(stdoutput)

print("git done")
