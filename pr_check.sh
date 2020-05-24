#!/bin/bash

set -exvo pipefail

make install-requirements
make check
