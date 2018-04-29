#!/bin/bash

# Get the directory of the script.
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the directory of this script.
cd ${script_directory}

reset_database=false
while getopts ":r" opt; do
  case ${opt} in
    r ) reset_database=true
      ;;
  esac
done

IMAGE_NAME=vision-server-release
IMAGE_VERSION=latest

if [[ -z "${VISION_DATABASE_DIRECTORY}" ]]; then
    VISION_DATABASE_DIRECTORY=${script_directory}/vision_database_2018
fi

if [[ -z "${VISION_SETTINGS_PATH}" ]]; then
    VISION_SETTINGS_PATH=${script_directory}/server/configuration/settings.py
fi

if [[ -z "${VISION_ENTRIES_JSON}" ]]; then
    VISION_ENTRIES_JSON=${script_directory}/server/configuration/entries.json
fi

if [[ -z "${VISION_CONSTANTS_PATH}" ]]; then
    VISION_CONSTANTS_PATH=${script_directory}/ui/public/constants.js
fi

if [[ -z "${VISION_REMOVE_CONTAINER}" ]]; then
    VISION_REMOVE_CONTAINER=true
fi

if [ ${VISION_REMOVE_CONTAINER} ]; then
    remove_database_command="--rm"
fi

docker run \
    ${remove_database_command} \
    -d \
    -p 80:15555 \
    -v ${VISION_DATABASE_DIRECTORY}:/var/lib/mysql \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${VISION_SETTINGS_PATH}:/opt/vision/configuration/settings.py:ro \
    -v ${VISION_ENTRIES_JSON}:/opt/vision/configuration/entries.json:ro \
    -v ${VISION_CONSTANTS_PATH}:/opt/vision/dist/constants.js:ro \
    -e RESET_DATABASE=${reset_database} \
    --name vision-server \
    ${IMAGE_NAME}:${IMAGE_VERSION}
