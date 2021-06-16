#!/bin/bash

set -e

conda activate $CONDA_ENV

exec "$@"
