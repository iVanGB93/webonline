from django.contrib import admin
from .models import MonthIncome, Spent

admin.site.register(MonthIncome)
admin.site.register(Spent)
