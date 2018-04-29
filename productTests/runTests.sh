#!/bin/bash
# Description: Runs the Selenium integration tests.
# This will perform the builds, create a build directory, and then run the tests.

set -e

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

setup_build_directory() {
    rm -rf build
    mkdir -p build

    cp ../server/configuration/settings.py build/
    cp ../ui/public/constants.js build/
}

export_variables() {
    export PYTHONPATH="$PYTHONPATH:${script_directory}"

    # The command to run to start the application.
    export APPLICATION_START_COMMAND="cd ${script_directory}/.. && ./run.sh"

    # The command to run to stop the application (empty string if there is no stop command required).
    export APPLICATION_STOP_COMMAND="docker kill vision-server"

    # The directory for storing the database for the product tests.
    export VISION_DATABASE_DIRECTORY="/var/data/vision_product_tests_database"

    # Path to the server's settings.py file (this will be edited by the tests).
    export VISION_SETTINGS_PATH=${script_directory}/build/settings.py

    # Path to the UI's constant.js file (this will be edited by the tests).
    export VISION_CONSTANTS_PATH=${script_directory}/build/constants.js
}

check_container_runs() {
    export VISION_REMOVE_CONTAINER=false
    container_id=`eval ${APPLICATION_START_COMMAND}`
    sleep 10
    docker ps -q --no-trunc | grep -q ${container_id}
    if [ $? != 0 ]; then
        echo "The Server failed to start the logs for the container are below:"

        echo "############## Logs Start ##############"
        docker logs ${container_id}
        echo "############### Logs End ###############"

        eval ${APPLICATION_STOP_COMMAND}

        exit 1
    fi
    eval ${APPLICATION_STOP_COMMAND}
    export VISION_REMOVE_CONTAINER=true
}

run_tests() {
    echo "Running integration tests..."
    nosetests -v --nocapture --nologcapture tests/*
}

teardown() {
    docker kill vision-server &>/dev/null
    rm -rf build
}

setup_build_directory
export_variables
check_container_runs
run_tests
teardown
