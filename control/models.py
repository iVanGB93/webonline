from django.db import models
from django.utils import timezone


class MonthIncome(models.Model):
    months = (
        (1, 'Jan'),
        (2, 'Feb'),
        (3, 'Mar'),
        (4, 'Apr'),
        (5, 'May'),
        (6, 'Jun'),
        (7, 'Jul'),
        (8, 'Aug'),
        (9, 'Sep'),
        (10, 'Oct'),
        (11, 'Nov'),
        (12, 'Dec'),
    )
    date = models.DateTimeField(default=timezone.now)
    month = models.CharField(max_length=20, choices=months)
    year = models.IntegerField(default=timezone.now().year)
    days = models.IntegerField()
    gross_income = models.IntegerField()
    total_spent = models.IntegerField()
    income = models.IntegerField()
    closed = models.BooleanField(default=False)
    sync = models.BooleanField(default=False)

    def __str__(self):
        return str(self.month) + " - " + str(self.year)

class Spent(models.Model):
    month = models.ForeignKey(MonthIncome, on_delete=models.CASCADE)
    service = models.CharField(max_length=20, null=True, blank=True)
    note = models.CharField(max_length=30, null=True, blank=True)
    spent = models.IntegerField()

    def __str__(self):
        return str(self.month) + " - " + str(self.service) + " - " + str(self.note) + " - " + str(self.spent)