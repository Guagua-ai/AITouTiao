import re


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))


def is_valid_phone(phone):
    phone_regex = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(phone_regex, phone))
