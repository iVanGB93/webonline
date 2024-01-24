from django.utils import timezone
import datetime

from servicios.models import Oper
from .models import MonthIncome, Spent


def get_or_create_monthincome(year, month):
    if MonthIncome.objects.filter(year=year, month=month).exists():
        monthIncome = MonthIncome.objects.get(year=year, month=month)
        return monthIncome
    else:
        if month == 2:
            days = 28
        elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
            days = 31
        else:
            days = 30
        monthIncome = MonthIncome(month=month, year=year, days=days)
        monthIncome.save()
        return monthIncome

def get_internet_spent():
    days = timezone.now().day
    total_spent = days * 800 * 9/10
    return total_spent

def get_service_spent(spents):
    spent = 0
    for s in spents:
        spent = spent + s.spent
    return spent

def get_service_spents(year, month, service):
    month = MonthIncome.objects.get(year=year, month=month)
    spents = Spent.objects.filter(month_id=month, service=service)
    return spents

def get_non_services_spent(year, month):
    month = MonthIncome.objects.get(year=year, month=month)
    all = Spent.objects.filter(month_id=month)
    spents = []
    for a in all:
        print(a.service)
        if a.service != None:
            spents.append(a)
    return spents

def get_total_spent(year, month):
    month = MonthIncome.objects.get(year=year, month=month)
    all = Spent.objects.filter(month_id=month)
    total_spent = 0
    exists = False
    for a in all:
        if a.note == 'compra de horas':
            exists = True
        else:
            total_spent = total_spent + a.spent
    internet_spent_value = get_internet_spent()
    if not exists:
        internet_spent = Spent(month=month, service='internet', note='compra de horas', spent=internet_spent_value)
    else:
        internet_spent = Spent.objects.get(note='compra de horas')
        internet_spent.spent = internet_spent_value
    internet_spent.save()
    total_spent = total_spent + internet_spent_value
    return total_spent

def get_pays(year, month):
    day = timezone.now().day
    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, day)
    operations = Oper.objects.filter(fecha__range=[start, end])
    opers = []
    for oper in operations:
        if oper.tipo == 'PAGO':
            opers.append(oper)
    return opers

def get_service_pays(year, month, service):
    all_pays = get_pays(year, month)
    pays = []
    for pay in all_pays:
        if pay.servicio == service:
            pays.append(pay)
    return pays

def get_service_income(pays):
    income = 0
    for p in pays:
        income = income + p.cantidad
    return income

def get_gross_income(year, month):
    all_pays = get_pays(year, month)
    month = MonthIncome.objects.get(month=month)
    total = 0
    for pay in all_pays:
        total = total + pay.cantidad
    return total
    
    
