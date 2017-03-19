import dataset


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

