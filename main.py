import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

import os
import dataset
import time
from stuf import stuf

# Sets timezone so the data is stored with the right times
os.environ['TZ'] = "US/Central"

# Connects to the SQL database through the dataset library
roommates_db = dataset.connect('postgresql://sam:hellfire@localhost:5432/roommates', row_type=stuf)
users_db = roommates_db['users']
sets_db = roommates_db['sets']

# Sets up the infrared sensor as an input
GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.IN)

# Sets up the keypad pins as inputs
pad_pins = {4:13, 1:19, 3:6, 2:26}
for pin in pad_pins:
    GPIO.setup(pad_pins[pin],GPIO.IN)

# Specifies the GPIO pins that the LCD data pins have been connected to
lcd_rs        = 8
lcd_en        = 25
lcd_d4        = 24
lcd_d5        = 23
lcd_d6        = 18
lcd_d7        = 15
lcd_backlight = 4
lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)


def record_a_set(user, pullup_count):
    """
    Takes as inputs the user who has just done a set and the number of pullups they completed.
    No output.
    Adds the set to the user's daily, monthly, and all time totals, then inserts the set into the sets relation.
    """
    users_db.update(dict(name=user.name,
                         total=user.total+pullup_count,
                         month_total=user.month_total+pullup_count,
                         day_total=user.day_total+pullup_count),
                    ['name'])
    sets_db.insert(dict(user_name=user.name,
                        time=time.strftime("%Y-%m-%d %H:%M:%S"),
                        pullup_count=pullup_count))
    # Replaces the user's max if this is their highest set
    if (pullup_count > user.max):
        users_db.update(dict(name=user.name, max=pullup_count), ['name'])

def count_a_set(user):
    """
    Takes as input the user who will be performing the set.
    No output.
    Displays progress and calls record_a_set with the proper parameters when a set is completed successfully.
    """
    lcd.clear()
    lcd.show_cursor(False)
    lcd.blink(False)
    lcd.message("Welcome, {}!\nBegin.".format(user.name))
    set_complete = False
    while not set_complete:
        # Start the first time the user raises their body
        if GPIO.input(14):
            pullup_count = 0
            secondsPassed = 1.0
            # Wait 3 seconds between pullups, break when the user takes longer than 3 seconds
            while secondsPassed < 3.0:
                if GPIO.input(14) and secondsPassed >= 1.0:
                    os.system('mpg123 -q bang.mp3 &')
                    pullup_count += 1
                    lcd.clear()
                    lcd.message("Nice!\n%d pullups" % pullup_count)
                    secondsPassed = 0.0
                    # Wait for user to lower body
                    while GPIO.input(14):
                        time.sleep(0.05)
                if check_for_keypress():
                    break
                time.sleep(0.1)
                secondsPassed += .1

            set_complete = True
            os.system('mpg123 -q ding.mp3 &')
            record_a_set(user, pullup_count)
            lcd.clear()
            lcd.message("Month: {}\nToday:{} Max:{}".format(user.month_total+pullup_count,
                                                               user.day_total+pullup_count,
                                                               max(user.max,pullup_count)))
            time.sleep(3)
        if check_for_keypress():
            break
        time.sleep(0.25)


def count_a_guest_set():
    """
    No inputs or outputs.
    Useful for testing. Goes through all the motions of count_a_set, but skips any updates to the database.
    """
    lcd.clear()
    lcd.show_cursor(False)
    lcd.blink(False)
    lcd.message("Welcome!\nBegin.")
    set_complete = False
    while not set_complete:
        # Start the first time the user raises their body
        if GPIO.input(14):
            pullup_count = 0
            secondsPassed = 1.0
            # Wait 3 seconds between pullups, break when the user takes longer than 3 seconds
            while secondsPassed < 3.0:
                if GPIO.input(14) and secondsPassed >= 1.0:
                    os.system('mpg123 -q bang.mp3 &')
                    pullup_count += 1
                    lcd.clear()
                    lcd.message("Nice!\n%d pullups" % pullup_count)
                    secondsPassed = 0.0
                    # Wait for user to lower body
                    while GPIO.input(14):
                        time.sleep(0.05)
                if check_for_keypress():
                    break
                time.sleep(0.1)
                secondsPassed += .1

            set_complete = True
            os.system('mpg123 -q ding.mp3 &')
            lcd.clear()
            lcd.message("Total: {} Maxes:\nS:{} B:{} J:{}".format(pullup_count,
                                                                  users_db.find_one(name='Sam').max,
                                                                  users_db.find_one(name='Blade').max,
                                                                  users_db.find_one(name='J-bod').max,
                                                                 )
                       )
            time.sleep(3)
        if check_for_keypress():
            break
        time.sleep(0.25)


def check_for_keypress():
    """
    No inputs.
    Outputs the key that is depressed, or 0 if none.
    Iterates through each key on the pad and checks if the user is depressing it.
    Deals with false positives by confirming that multiple readings agree.
    """
    pad_pins = {4:13, 1:19, 3:6, 2:26}
    for pin in pad_pins:
        consecutive_presses = 0
        if (GPIO.input(pad_pins[pin])):
            while consecutive_presses < 20:
                time.sleep(0.01)
                if GPIO.input(pad_pins[pin]):
                    consecutive_presses += 1
                else:
                    break
            if consecutive_presses >= 5:
                return pin
                while GPIO.input(pad_pins[pin]):
                    pass
    return 0


def display_standings():
    """
    No inputs or outputs.
    Makes calls to the database to show the progress of each roommate for the day.
    """
    s_count = users_db.find_one(name='Sam').day_total
    b_count = users_db.find_one(name='Blade').day_total
    j_count = users_db.find_one(name='J-bod').day_total
    best_count = max(s_count, b_count, j_count)
    winner = users_db.find_one(day_total=best_count)
    lcd.message("S:{} B:{} J:{}\n{} leads".format(s_count, b_count, j_count, winner.name))
    time.sleep(3)


def wait_for_code(users):
    """
    Takes as input the list of users.
    No output.
    Waits until a user presses a key, then records each key until they hit 4 ('Return').
    Checks the code entered against the user codes, and calls count_a_set with the matching user.
    If not a user code, checks if it is one of ther other utility codes, and calls their functions.
    If not any code, displays an error and ends.
    """
    lcd.clear()
    lcd.show_cursor(True)
    lcd.blink(True)
    lcd.message("Code please.\n")
    key = 0
    code = []
    code_string=""
    while key != 4:
        key = 0
        while not key:
            key = check_for_keypress()
        if key != 4:
            code.append(key)
            code_string = ''.join(map(str, code))
            lcd.clear()
            lcd.message("Code please.\n{}".format(code_string))
    found_user = False
    for user in users:
        if code_string == str(user.code):
            count_a_set(user)
            found_user = True
    if not found_user:
        lcd.clear()
        lcd.show_cursor(False)
        lcd.blink(False)
        if code_string == '11':
            display_standings()
        elif code_string == '32':
            count_a_guest_set()
        else:
            lcd.message("Sorry!\nUnknown Code")
            time.sleep(.5)


# Constantly waits for a user to input a code
while True:
    wait_for_code(users_db)
