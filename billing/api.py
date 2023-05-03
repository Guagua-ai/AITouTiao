from datetime import datetime
import os
import openai

def get_daily_usage():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        r = openai.api_requestor.APIRequestor();
        resp = r.request("GET", '/usage?date={today_date}'.format(today_date=datetime.today().strftime('%Y-%m-%d')));
        resp_object = resp[0]
        resp_object.data
    except Exception as e:
        print(f"Error fetching usage data: {e}")
        return None