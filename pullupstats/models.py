from __future__ import unicode_literals

from django.db import models

class Roommate(models.Model):
    name = models.CharField(max_length=20)
    code = models.IntegerField()
    max_pullups = models.IntegerField()
    total_pullups = models.IntegerField()
    daily_total_pullups = models.IntegerField(null = True, blank = True)
    monthly_total_pullups = models.IntegerField()

    def __init__(self, user_dict):
        self.name = user_dict['name']
        self.code = user_dict['code']
        self.max_pullups = user_dict['max']
        self.total_pullups = user_dict['total']
        self.monthly_total_pullups = user_dict['month_total']

