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
	gunicorn app:app -b 0.0.0.0:8080 --timeout 300

test:
	$(PYTHON) -m pytest tests/

collect:
	$(PYTHON) run.py --collect

clean:
	rm -f *.pyc
	rm -rf __pycache__
	rm -rf *.egg-info

collect:
	$(PYTHON) run.py --collect --local

update:
	$(PIP) freeze > requirements.txt

.PHONY: all install run test clean update collect
