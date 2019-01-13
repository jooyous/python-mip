#!/bin/bash

rm -f *.csv

python queens.py 
mv python-gurobi.csv python-gurobi-cpython.csv
mv python-cbc.csv python-cbc-cpython.csv

pypy3 queens.py 
mv python-gurobi.csv python-gurobi-pypy.csv
mv python-cbc.csv python-cbc-pypy.csv

python queens-pulp.py
mv python-pulp.csv python-pulp-cpython.csv
mv python-pulp.csv python-pulp-pypy.csv

python queens-gurobi.py
