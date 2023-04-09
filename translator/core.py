import os
import openai
from config.translator import TranslatorConfig

class TranslatorCore(object):
    ''' Translator class '''
    config = None

    def __init__(self, api_key=None):
        assert api_key is not None, 'API key is required'
        openai.api_key = api_key
        self.config = TranslatorConfig()

    def translate_to_chinese(self, text):
            response = openai.Completion.create(
                engine= self.config.translation_engine,
                prompt=f"Translate the following English text to Simplified Chinese: '{text}'",
                max_tokens=self.config.translation_max_tokens,
                n=self.config.translation_n,
                stop=None,
                temperature=self.config.translation_temperature,
            )

            translation = response.choices[0].text.strip()
            return translation
