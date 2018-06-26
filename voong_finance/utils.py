import datetime

def iso_to_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
