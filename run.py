import os
import modules
from app import app, db
from cli import CliRunner


def create_app():
    # Create the database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    # Run the CLI
    cli_runner = CliRunner(os.getenv('OPENAI_API_KEY'))
    cli_runner.run()

    # Run the Flask app
    app.run(port=8080, debug=True)
