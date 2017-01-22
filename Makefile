.PHONY: build

tox:
	tox

test:
	pytest syp/

install:
	pip install -U pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

build:
	python setup.py bdist_egg
	python setup.py sdist

upload:
	python setup.py sdist bdist_wheel upload
