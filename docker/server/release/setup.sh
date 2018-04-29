#!/bin/bash

# Description: Setup the release image on the target machine. This script assumes the tar file
# containing the Docker image is in the same directory.

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

docker load --input vision-server-release.tar