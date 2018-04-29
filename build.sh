#!/bin/bash

# Build the Project.

set -e

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}/ui

# Build the UI.
./build.sh

cd ${script_directory}

# Create the base image that both the development and release image are based off.
docker build -f docker/server/base/Dockerfile -t vision-server-base .

# Create the development image.
docker build -f docker/server/development/Dockerfile -t vision-server-development .

# Create the release image.
docker build -f docker/server/release/Dockerfile -t vision-server-release .
