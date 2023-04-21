from datetime import datetime, timedelta
from babel.dates import format_datetime


def standard_format(published_at: datetime):
    # Calculate time difference
    now = datetime.now()
    time_diff = now - published_at
    days = time_diff.days
    hours = time_diff.seconds // 3600

    if days == 0:
        return f"{hours}小时前"
    elif days == 1:
        return "1天前"
    elif days <= 7:
        return f"{days}天前"
    else:
        # Format the datetime object using Babel
        published_at_formatted = format_datetime(
            published_at, "yyyy年MM月dd日 HH:mm:ss", locale='zh_CN')
        return published_at_formatted
