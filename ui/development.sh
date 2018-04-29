#!/bin/bash

program_name=$0

function usage {
    echo "usage: $program_name [command and arguments to run in node docker container]"
    exit 1
}

[ -z $1 ] && { usage; }

set -e

IMAGE_NAME=node
NODE_VERSION=8.9.1
USER=`whoami`

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd $script_directory

docker run \
    --rm \
    -v /etc/group:/etc/group:ro \
    -v /etc/passwd:/etc/passwd:ro \
    -u `id -u`:`id -g` \
    -v `pwd`:/vision \
    -v ~/.npm:/home/$USER/.npm \
    -v ~/.config:/home/$USER/.config \
    -v ~/.cache:/home/$USER/.cache \
    -v ~/.local:/home/$USER/.local \
    --name euro-container \
    -p 4200:4200 \
    $IMAGE_NAME:$NODE_VERSION \
    /bin/bash -c "cd vision && $*"


