import csv
import datetime
import os
import openai
from config.chatbot import ChatbotConfig
from chat.result import format_results
from chat import Tweet, get_connection
from utils.time import standard_format


class Chatbot:
    '''Chatbot class to handle all chatbot related functions'''

    def __init__(self, api_key, html_mode=False):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.config = ChatbotConfig()
        self.html_mode = html_mode

    # Read the CSV file and store the contents in a list
    def read_csv(self, filename):
        data = []
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for i, row in enumerate(csv_reader):
                row['id'] = i + 1
                data.append(row)
        return data

    # Use GPT-3 to generate keywords from the user input
    def generate_keywords(self, user_input):
        try:
            response = openai.Completion.create(
                engine=self.config.translation_engine,
                prompt=f"Extract important keywords from the following text for easy query: '{user_input}'",
                max_tokens=self.config.translation_max_tokens,
                n=self.config.translation_n,
                stop=None,
                temperature=self.config.translation_temperature,
            )
            keywords = response.choices[0].text.strip().split(', ')
            return keywords
        except openai.error.RateLimitError:
            return user_input.split()

    # Count the number of records
    def count_total_records(self):
        return Tweet.count_tweets()

    # Find relevant results based on user input
    def find_relevant_results(self, user_input, use_keyword=False):
        def has_keywords(text, keywords):
            return any(keyword.lower() in text.lower() for keyword in keywords)

        keywords = user_input.split()
        if use_keyword:
            keywords = self.generate_keywords(user_input)

        print(
            f"Keywords: {keywords}\n" if keywords else "No keywords found.\n")
        
        results = Tweet.get_tweet_by_keywords(keywords)
        return results

    # Format the results for display
    def format_results(self, results):
        if not results:
            return "No matching results found."
        if self.html_mode:
            return format_results(results, html_mode=True)
        response = "Matching results:\n\n"
        for result in results:
            response += f"Author: {result['author']}\nDisplayName: {result['displayname']}\nTweet URL: {result['url']}\nTweet Text: {result['title']}\nTranslated Text: {result['content']}\n\n"
        return response

    # Get the tweet data
    def get_tweet_data(self):
        self.data = Tweet.get_all_tweets()

        tweet_data = []
        for row in self.data:
            tweet_data.append({
                "id": row.id,
                "source": {
                    'id': row.source_id,
                    'name': row.source_name
                },
                "author": row.author,
                "displayname": row.display_name,
                "title": row.title,
                "description": row.description,
                "url": row.url,
                "urlToImage": row.url_to_image,
                "publishedAt": standard_format(row.published_at),
                "content": '',
                "likes": row.num_likes,
            })

        return tweet_data

    # Main chatbot function with response
    def run_with_response(self, user_input, use_keyword=False):
        relevant_results = self.find_relevant_results(user_input, use_keyword)
        print(f"Found {len(relevant_results)} relevant results.\n")
        response = self.format_results(relevant_results)
        return response

    # Main chatbot function
    def run(self, user_input, use_keyword=False):
        relevant_results = self.find_relevant_results(user_input, use_keyword)
        print(f"Found {len(relevant_results)} relevant results.\n")
        response = self.format_results(relevant_results)
        print(response)
