#!/usr/bin/env bash

set -e

trunk fmt --ci
trunk check --ci
pyre infer --in-place --annotate-attributes
pyre check
pytest --cov=. --cov-branch --cov-report=xml
