#!/bin/bash
# Description: Runs the unit tests for the server.

set -e

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

print_running_test() {
    for i in {1..100}; do printf "#"; done
    echo
    echo $1
    for i in {1..100}; do printf "#"; done
    echo
}

print_running_test "Running Ember unit tests"
cd ui
./node_modules/ember-cli/bin/ember test

cd ${script_directory}

print_running_test "Running server unit tests"
./development.sh ./server/runTests.sh

print_running_test "Running product tests"
./productTests/runTests.sh
