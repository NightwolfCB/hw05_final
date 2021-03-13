import datetime as dt


def today(request):
    today = dt.datetime.today()
    return {'today': today}
