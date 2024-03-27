# Building 

poetry check

# Unit testing
pytest 
pytest -v   -verbose
pytest -k test_functname   test particular function

# Refactoring

## radon
radon cc tpkg/tpkg.py
radon mi tpkg/tpkg.py
radon hal tpkg/tpkg.py  - metrics

## vulture 
vulture tpkg/tpkg.py

## reformatting 
black tpkg/tpkg.py


