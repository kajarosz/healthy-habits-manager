from email.policy import default
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habit', null=True)
    WATER = 'WTR'
    WALKING = 'WLK'
    READING = 'REA'
    SLEEPING = 'SLP'
    EATING = 'EAT'
    SPORT = 'SPO'
    CATEGORY_CHOICES = [
        (WATER, 'drinking water'),
        (WALKING, 'walking'),
        (READING, 'reading books'),
        (SLEEPING, 'sleeping'),
        (EATING, 'eating meals'),
        (SPORT, 'train or exercise'),
    ]
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, default=WATER)
    DAY = 'DAY'
    WEEK = 'WEE'
    MONTH = 'MTH'
    INTERVAL_CHOICES = [
        (DAY, 'day'),
        (WEEK, 'week'),
        (MONTH, 'month')
    ]
    interval = models.CharField(max_length=3, choices=INTERVAL_CHOICES, default=DAY)
    FREQ_CHOICES = [(n, n) for n in range (1,11)]
    freq = models.IntegerField(choices=FREQ_CHOICES, default=1)
    remind = models.BooleanField(default=False)

    def __str__(self):
        return self.category
