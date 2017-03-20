from django.shortcuts import render
import json

from .models import Roommate


def index(request):
    # Load overview
    overview_file = open('overview.json', 'r')
    users = json.load(overview_file)['results']

    # Define all roommates
    roommate1 = Roommate(users[0])
    roommate2 = Roommate(users[1])
    roommate3 = Roommate(users[2])
    roommates = (roommate1, roommate2, roommate3)

    # Find all time best and best max
    top_score = max([roommate.total_pullups for roommate in roommates])
    top_max = max([roommate.max_pullups for roommate in roommates])
    for roommate in roommates:
        if roommate.total_pullups == top_score:
            top_alltime = roommate
        if roommate.max_pullups == top_max:
            top_max_roommate = roommate

    # Find amount of daily wins
    number_of_days = json.load(open('sams_days.json', 'r'))['count']
    sams_days = json.load(open('sams_days.json', 'r'))['results']
    zachs_days = json.load(open('zachs_days.json', 'r'))['results']
    jarrods_days = json.load(open('jarrods_days.json', 'r'))['results']
    roommate_days = (sams_days, zachs_days, jarrods_days)

    sam_wins = 0
    zach_wins = 0
    jarrod_wins = 0
    i = 0
    while i < number_of_days:
        best_score = 0
        for days in roommate_days:
            if days[i]['total'] > best_score:
                best_score = days[i]['total']
                best_user = days[i]['user_name']
        if best_user == 'Sam':
            sam_wins += 1
        if best_user == 'Blade':
            zach_wins += 1
        if best_user == 'J-bod':
            jarrod_wins += 1
        i += 1

    wins = (sam_wins, zach_wins, jarrod_wins)
    max_wins = max(wins)
    if max_wins == sam_wins:
        daily_wins_winner = 'Sam'
    elif max_wins == zach_wins:
        daily_wins_winner = 'Blade'
    elif max_wins == jarrod_wins:
        daily_wins_winner = 'J-bod'

    context = {
        'roommates': roommates,
        'alltimechamp': top_alltime,
        'topmax': top_max_roommate,
        'daily_wins_winner': daily_wins_winner,
        'daily_wins_top': max_wins,
    }

    return render(request, 'index.html', context)
