import os
import modules
from app import app, db
from cli import CliRunner


if __name__ == '__main__':
    # Run the CLI
    cli_runner = CliRunner(os.getenv('OPENAI_API_KEY'))
    cli_runner.run()

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run(port=8080, debug=True)
