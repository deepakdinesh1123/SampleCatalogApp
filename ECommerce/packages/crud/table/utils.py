import pytz
from datetime import datetime


def process_date_range(start_date, end_date):
    result = []
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    result = [start_date_dt, end_date_dt]
    return result


def process_datetime_range_with_timezone(start_date, end_date):
    result = []
    from django.db import connection

    tz = pytz.timezone(connection.tenant.timezone)
    start_date_dt = datetime.strptime(start_date + "-" + "00:00", "%Y-%m-%d-%H:%M")
    end_date_dt = datetime.strptime(end_date + "-" + "23:59", "%Y-%m-%d-%H:%M")
    result.append(tz.localize(start_date_dt, is_dst=None))
    result.append(tz.localize(end_date_dt, is_dst=None))
    return result
