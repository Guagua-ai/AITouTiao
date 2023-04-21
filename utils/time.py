import locale
from datetime import datetime, timedelta


def standard_format(published_at: datetime):
    # Set the locale to Chinese (Simplified)
    try:
        locale.setlocale(locale.LC_TIME, 'zh_CN.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
        except locale.Error:
            raise Exception("Chinese locale not supported on your system.")

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
        # Format the datetime object to the desired format
        published_at_formatted = published_at.strftime('%Y年%m月%d日')
        return published_at_formatted
