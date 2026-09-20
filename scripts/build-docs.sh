#!/bin/bash

set -vxeuo pipefail

sphinx-build -E -n -W --keep-going -b html docs/source docs/build/html
