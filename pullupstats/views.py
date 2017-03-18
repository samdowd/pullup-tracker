from django.shortcuts import render

import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

import dataset
import time
import psycopg2
import json

from .models import Roommate

def index(request):
    jsonfile = open('testjson.json', 'r')
    users = json.load(jsonfile)['results']

    roommate1 = Roommate(users[0])
    roommate2 = Roommate(users[1])
    roommate3 = Roommate(users[2])

    roommates = (roommate1, roommate2, roommate3)

    context = {
        'roommates': roommates,
    }

    return render(request, 'index.html', context)
