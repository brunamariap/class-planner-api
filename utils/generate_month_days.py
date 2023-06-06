from datetime import datetime, timedelta, date

def get_days_from_month(month = date.today().month, year = date.today().year):
    days = []
    date = datetime(year, month, 1)

    while date.month == month:
        days.append(date.date())
        date += timedelta(days=1)

    return days