import os
from cli import CliRunner
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv('.env')
    cli_runner = CliRunner(os.getenv('OPENAI_API_KEY'))
    cli_runner.run()
