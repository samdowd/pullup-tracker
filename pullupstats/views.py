from django.shortcuts import render
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from .models import Roommate


def index(request):
    overview_file = open('overview.json', 'r')
    users = json.load(overview_file)['results']

    roommate1 = Roommate(users[0])
    roommate2 = Roommate(users[1])
    roommate3 = Roommate(users[2])

    roommates = (roommate1, roommate2, roommate3)

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

    fig.savefig('dailies.png')

    context = {
        'roommates': roommates,
    }

    return render(request, 'index.html', context)
