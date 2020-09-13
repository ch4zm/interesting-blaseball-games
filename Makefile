help:
	cat Makefile


# dependencies
requirements:
	python3 -m pip install --upgrade -r requirements.txt

dev:
	python3 -m pip install --upgrade -r requirements-dev.txt


# build
pypi: dist
	twine upload --repository pypi dist/*

testpypi: dist
	twine upload --repository testpypi dist/* --verbose

distcheck: dist
	twine check dist/*

dist: build
	python3 setup.py sdist bdist_wheel

build: clean
	python3 setup.py build install

clean:
	rm -fr build dist __pycache__ *.egg-info/
