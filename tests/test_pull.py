import json
import time
import pandas as pd
from app import app


class TestCollectAPI:
    def test_collect_api(self):
        # Define the expected response
        expected_response = {
            'message': 'Tweets collected and saved to elonmusk_tweets_translated.csv'
        }
        
        # Send the API request
        with app.test_client() as client:
            response = client.get('/collect')
        
        # Check that the response status code is 200
        assert response.status_code == 200
        
        # Parse the JSON response
        data = json.loads(response.data)
        
        # Check that the response matches the expected response
        assert data == expected_response
        
        # Check that the CSV file was created and contains data
        df = pd.read_csv('elonmusk_tweets_translated.csv')
        assert not df.empty
