import dataset
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


roommates_db = dataset.connect('postgresql://sam:hellfire@localhost:5432/roommates')
users_db = roommates_db['users']
dtotals_db = roommates_db['daily_totals']

sams_days = roommates_db.query("SELECT total, date FROM daily_totals WHERE user_name = 'Sam' ORDER BY date;")
zachs_days = roommates_db.query("SELECT total, date FROM daily_totals WHERE user_name = 'Blade' ORDER BY date;")
jarrods_days = roommates_db.query("SELECT total, date FROM daily_totals WHERE user_name = 'J-bod' ORDER BY date;")
dataset.freeze(sams_days, format='json', filename='sams_days.json')
dataset.freeze(zachs_days, format='json', filename='zachs_days.json')
dataset.freeze(jarrods_days, format='json', filename='jarrods_days.json')

dataset.freeze(users_db, format='json', filename='overview.json')

sams_days = json.load(open('sams_days.json', 'r'))['results']
zachs_days = json.load(open('zachs_days.json', 'r'))['results']
jarrods_days = json.load(open('jarrods_days.json', 'r'))['results']

sam_totals = []
for day in sams_days:
    sam_totals.append(day['total'])
zach_totals = []
for day in zachs_days:
    zach_totals.append(day['total'])
jarrod_totals = []
for day in jarrods_days:
    jarrod_totals.append(day['total'])

totals = sam_totals + zach_totals + jarrod_totals

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(sam_totals, 'r-', zach_totals, 'b-', jarrod_totals, 'g-')
plt.gca().axes.get_xaxis().set_visible(False)
plt.ylabel("Number of Pullups")
plt.title("Daily Totals")
sam_patch = mpatches.Patch(color='red', label='Sam')
zach_patch = mpatches.Patch(color='blue', label='Zach')
jarrod_patch = mpatches.Patch(color='green', label='Jarrod')
plt.legend(handles=[sam_patch, zach_patch, jarrod_patch])
plt.axis([0, len(totals) * 1.1 / 3.0, 0, max(totals) * 1.1])

fig.savefig('pullupstats/static/dailies.png')