#!/bin/bash

program_name=$0

function usage {
    echo "usage: $program_name [command and arguments to run in node docker container]"
    exit 1
}

[ -z $1 ] && { usage; }

set -e

IMAGE_NAME=vision-server-development
IMAGE_VERSION=latest
USER_ID=`id -u`
GROUP_ID=`id -g`

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

setup_commands="groupadd $GROUP_ID && useradd -g $GROUP_ID $USER_ID && service mysql start"

docker run \
    --rm \
    -v `pwd`:/vision \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    --name vision-server-dev-container \
    -p 15555:15555 \
    ${IMAGE_NAME}:${IMAGE_VERSION} \
    /bin/bash -c "$setup_commands && su - $USER_ID -c \"cd /vision && $*\""
