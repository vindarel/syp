
tox:
	tox

test:
	python -m unittest tests

install:
	pip install -U pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
