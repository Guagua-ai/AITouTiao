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

test:
	$(PYTHON) -m pytest tests/

clean:
	rm -f *.pyc
	rm -rf __pycache__
	rm -rf *.egg-info

update:
	$(PIP) freeze > requirements.txt

.PHONY: all install run test clean update
