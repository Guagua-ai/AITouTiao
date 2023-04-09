import os
from pull.puller import Puller
from translator.core import TranslatorCore
from steps.step import Step


class PullStep(Step):
    ''' Pull step for executing pulling data from sources. '''

    def __init__(self, *args, **kwargs):
        super().__init__("pull", "Step to pull data from sources", PullStep.execute(), *args, **kwargs)

    def execute():
        ''' Run the puller asynchronously'''
        assert os.getenv('OPENAI_API_KEY'), 'Please provide an OpenAI API key'
        assert os.getenv('REDIS_URL'), 'Please provide a Redis URL'
        puller = Puller(
            api_key=os.getenv('OPENAI_API_KEY'),
            translator=TranslatorCore(api_key=os.getenv('OPENAI_API_KEY')),
            local=os.getenv('LOCAL'))
        return puller.run()
