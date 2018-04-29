#!/bin/bash

# Build the UI.

set -e

# Builds the Vision UI.

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd $script_directory

./development.sh npm install

./development.sh ./node_modules/bower/bin/bower install

./development.sh ./node_modules/ember-cli/bin/ember build --environment=production
