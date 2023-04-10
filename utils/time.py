from datetime import datetime


def standard_format(published_at: datetime.timestamp):
    # Format the datetime object to the desired format
    # published_at_formatted = published_at.strftime('%Y-%m-%d %H:%M:%S')
    published_at_formatted = published_at.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return published_at_formatted
