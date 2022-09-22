#!/usr/bin/env bash

set -e

echo -e "\n> pyre infer"
pyre infer --in-place --annotate-attributes
echo -e "\n> pyre check"
pyre check
echo -e "\n> pytest"
pytest --cov=. --cov-branch --cov-report=xml
echo -e "\n> trunk fmt"
trunk fmt --ci
echo -e "\n>trunk check"
trunk check --ci
echo -e "\n< Done\n"
