import os
import boto3
from datetime import datetime, timedelta

def get_ce_client():
    """
    Returns an ce client.
    """
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    return boto3.client('ce', 
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_access_key)


def get_daily_aws_cost():
    try:
        client = get_ce_client()
        now = datetime.utcnow()
        start = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')

        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        return response['ResultsByTime'][0]['Groups']
    except Exception as e:
        print(f"Error fetching AWS cost data: {e}")
        return None