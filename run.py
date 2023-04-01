import os
from app import app
from cli import CliRunner
from dotenv import load_dotenv


if __name__ == '__main__':
    # Load the environment variables
    load_dotenv('.env')

    # Run the CLI
    cli_runner = CliRunner(os.getenv('OPENAI_API_KEY'))
    cli_runner.run()

    # Run the Flask app
    app.run(port=8080, debug=True)
