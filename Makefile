# Define variables
APP_NAME=myflaskapp
PYTHON=python3
PIP=pip3

# Define targets
all: install run

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) run.py

prod:
	gunicorn --timeout 300 --bind 0.0.0.0:8080 'run:create_app()'

test:
	$(PYTHON) -m pytest tests/

clean:
	rm -f *.pyc
	rm -rf __pycache__
	rm -rf *.egg-info

collect:
	$(PYTHON) run.py --collect --local

update:
	$(PIP) freeze > requirements.txt

migrate:
	alembic upgrade head

.PHONY: all install run prod test clean update collect migrate
