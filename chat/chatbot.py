import csv
import os
import openai

from chat.result import format_results


class Chatbot:
    def __init__(self, api_key, local=True, html_mode=False):
        assert api_key, 'Please provide an OpenAI API key'
        openai.api_key = api_key
        self.html_mode = html_mode
        self.local = local

    # Read the CSV file and store the contents in a list
    def read_csv(self, filename):
        data = []
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                data.append(row)
        return data

    # Use GPT-3 to generate keywords from the user input
    def generate_keywords(self, user_input):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Extract important keywords from the following text for easy query: '{user_input}'",
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )

        keywords = response.choices[0].text.strip().split(', ')
        return keywords

    # Find relevant results based on user input
    def find_relevant_results(self, user_input):
        def has_keywords(text, keywords):
            return any(keyword.lower() in text.lower() for keyword in keywords)

        keywords = self.generate_keywords(user_input)
        print(
            f"Keywords: {keywords}\n" if keywords else "No keywords found.\n")

        results = [
            row for row in self.data
            if any(has_keywords(row[key], keywords) for key in row)
        ]

        return results

    # Format the results for display
    def format_results(self, results):
        if not results:
            return "No matching results found."
        if self.html_mode:
            return format_results(results, html_mode=True)
        response = "Matching results:\n\n"
        for result in results:
            response += f"Author: {result['author']}\nTweet URL: {result['url']}\nTweet Text: {result['title']}\nTranslated Text: {result['content']}\n\n"
        return response

    # Get the tweet data
    def get_tweet_data(self):
        tweet_data = []
        for row in self.data:
            tweet_data.append({
                "source": row['source'],
                "author": row['author'],
                "title": row['title'],
                "description": row['description'],
                "url": row['url'],
                "urlToImage": row['urlToImage'],
                "publishedAt": row['publishedAt'],
                "content": row['content']
            })

        return tweet_data

    # Main chatbot function

    def run(self, user_input):
        assert os.path.exists(
            'ai_tweets_translated.csv'), 'Please run `python pull/puller.py` first'
        if self.local:
            self.data = self.read_csv('ai_tweets_translated.csv')
        relevant_results = self.find_relevant_results(user_input)
        print(f"Found {len(relevant_results)} relevant results.\n")
        response = self.format_results(relevant_results)
        print(response)
