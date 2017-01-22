
tox:
	tox

test:
	pytest syp/

install:
	pip install -U pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
