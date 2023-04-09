import configparser

class ChatbotConfig(object):
    config = None
    translation_engine = None
    translation_max_tokens = None
    translation_n = None
    translation_stop = None
    translation_temperature = None

    def __init__(self) -> None:
        # Create a ConfigParser object and read the config file
        self.config = configparser.ConfigParser()
        self.config.read('./config/config.ini')

        # Read the translation settings from the config file
        self.translation_engine = self.config.get('translation', 'engine')
        self.translation_max_tokens = self.config.getint(
            'translation', 'max_tokens')
        self.translation_n = self.config.getint('translation', 'n')
        self.translation_stop = self.config.get('translation', 'stop')
        self.translation_temperature = self.config.getfloat(
            'translation', 'temperature')