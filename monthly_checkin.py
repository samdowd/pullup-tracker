import os
import dataset
import datetime
from stuf import stuf
from gtts import gTTS

# Connect to the databases
roommates_db = dataset.connect('postgresql://sam:hellfire@localhost:5432/roommates', row_type=stuf)
users_db = roommates_db['users']
sets_db = roommates_db['sets']
dtotals_db = roommates_db['daily_totals']
mtotals_db = roommates_db['monthly_totals']

# Find the users
sam = users_db.find_one(name='Sam')
zach = users_db.find_one(name='Blade')
jarrod = users_db.find_one(name='J-bod')


# Find winner and loser for the month
month_best_count = max(sam.month_total, zach.month_total, jarrod.month_total)
month_winner = users_db.find_one(month_total=month_best_count)
month_worst_count = min(sam.month_total, zach.month_total, jarrod.month_total)
month_loser = users_db.find_one(month_total=month_worst_count)


# Add monthly totals to monthly_totals database and reset month total to 0
yesterday = month=datetime.date.today().replace(day=1) - datetime.timedelta(days=1)

for user in users_db:
    mtotals_db.insert(dict(name=user.name,
                           number=user.month_total,
                           month=yesterday.strftime("%B"))
                      )
    users_db.update(dict(name=user.name,
                         month_total=0),
                    ['name'])


# Call out the losers
message = gTTS(text="{} is the winner for {}. Congratulations! {} got last place. Worthless, worthless {}.".format(month_winner.name, yesterday.strftime("%B"), month_loser.name, month_loser.name))
message.save("monthly_speech.mp3")
os.system('mpg123 monthly_speech.mp3 &')
