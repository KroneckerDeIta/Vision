#!/bin/bash

# Description: Script which zips up the release container and scripts to run up the application.

program_name=$0

function usage {
    echo "Usage: $program_name [year the contest is being run in]"
    exit 1
}

[ -z $1 ] && { usage; }

set -e

export contest_year=$1
release_directory=vision_release_${contest_year}

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

mkdir -p ${release_directory}

docker save vision-server-release > ${release_directory}/vision-server-release.tar

cp run.sh ${release_directory}/run.sh
# Replace the database directory so that it is created in the unzipped release directory.
perl -p -i -e 's/(\s*VISION_DATABASE_DIRECTORY=).*/\1\$\{script_directory\}\/vision_database_$ENV{"contest_year"}/g' run.sh

# Copy the setup script so which untars the Docker container.
cp docker/server/release/setup.sh ${release_directory}/setup.sh

# Copy the stop script.
cp docker/server/release/stop.sh ${release_directory}/stop.sh

# Copy the README which describes what the user needs to do to setup the Docker container.
cp docker/server/release/README.md ${release_directory}/README.md

# Copy configuration files that will be mounted into the Docker container.
mkdir -p ${release_directory}/server/configuration
cp server/configuration/settings.py ${release_directory}/server/configuration/settings.py
cp server/configuration/entries.json ${release_directory}/server/configuration/entries.json
mkdir -p ${release_directory}/ui/public/
cp ui/public/constants.js ${release_directory}/ui/public/constants.js

# Zip up the contents of the release directory.
zip -r ${release_directory}.zip ${release_directory}

# Finally remove the release directory.
rm -rf ${release_directory}