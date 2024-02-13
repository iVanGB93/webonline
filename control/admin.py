from django.contrib import admin
from .models import MonthIncome, Spent, CoinSold

admin.site.register(MonthIncome)
admin.site.register(Spent)
admin.site.register(CoinSold)
