import configparser

class TweetConfig(object):
    config = None
    max_results = None

    def __init__(self) -> None:
        # Create a ConfigParser object and read the config file
        self.config = configparser.ConfigParser()
        self.config.read('./config/config.ini')

        # Read the translation settings from the config file
        self.max_results = self.config.getint('twitter', 'max_num_results')
