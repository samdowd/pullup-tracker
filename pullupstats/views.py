from django.shortcuts import render
import json

from .models import Roommate


def index(request):
    overview_file = open('overview.json', 'r')
    users = json.load(overview_file)['results']

    roommate1 = Roommate(users[0])
    roommate2 = Roommate(users[1])
    roommate3 = Roommate(users[2])

    roommates = (roommate1, roommate2, roommate3)

    context = {
        'roommates': roommates,
    }

    return render(request, 'index.html', context)
