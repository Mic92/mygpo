all: help

help:
	@echo 'make test            synchronize DB and run local webserver'
	@echo 'make clean           clean up files'
	@echo 'make unittest        run unittests'

test:
	./manage.py syncdb
	./manage.py runserver

unittest:
	./manage.py test

clean:
	find -name "*.pyc" -exec rm '{}' \;


.PHONY: all help test clean unittest

