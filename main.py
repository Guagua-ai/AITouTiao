import argparse
import os
import chatbot
import puller
from dotenv import load_dotenv


class InterfaceRunner:
    def __init__(self, api_key):
        self.chatbot = chatbot.Chatbot(api_key)
        self.puller = puller.Puller(api_key)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '--collect', action='store_true', help='Execute tweets_pull function')
        self.parser.add_argument(
            '--chat', type=str, help='Execute chatbot function with a user input string')
        self.args = self.parser.parse_args()

    def run(self):
        if self.args.chat:
            self.chatbot.run(self.args.chat)

        if self.args.collect:
            self.puller.run()


if __name__ == '__main__':
    load_dotenv('.env')
    interface_runner = InterfaceRunner(os.getenv('OPENAI_API_KEY'))
    interface_runner.run()
