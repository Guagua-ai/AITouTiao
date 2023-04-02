import argparse
import sys

from chat import chatbot
from pull import puller


class CliRunner:
    def __init__(self, api_key):
        # Initialize arguments parser
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '--collect', action='store_true', help='Execute tweets_pull function')
        self.parser.add_argument(
            '--chat', type=str, help='Execute chatbot function with a user input string')
        self.parser.add_argument(
            '--local', action='store_true', default=False, help='Execute tweets pull function by storing data locally')
        self.parser.add_argument(
            '--keyword', action='store_true', default=False, help='Wheteher to use keyword from OpenAI to search or not')
        self.args = self.parser.parse_args()

        # Initialize chatbot and puller
        self.chatbot = chatbot.Chatbot(api_key=api_key, local=self.args.local)
        self.puller = puller.Puller(api_key=api_key, local=self.args.local)

    def run(self):
        # Run the chatbot or puller based on the arguments
        if self.args.chat:
            self.chatbot.run(self.args.chat, self.args.keyword)

        # Run the puller if the collect argument is passed
        if self.args.collect:
            self.puller.run()
