#!/bin/bash
# Description: Runs the unit tests for the server.

set -e

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

nosetests -v --nocapture --nologcapture tests/*
