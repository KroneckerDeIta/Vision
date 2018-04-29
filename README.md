# General information

This is a score entry application for your favourite song contest, one which features countries in Europe and beyond.

Disclaimer: I am in no way affiliated with your favourite song contest and I am not making any money from this application.

All the information about entries are to be set in the entries.json file, and when the contestants in the final are confirmed this will be filled in.

Whilst the UI has been written in Ember it is only meant to be run locally, and runs from a Docker container.

# Development setup

Dependencies:

# To build the release:
docker (https://docs.docker.com/install/)

# To run the tests:
python3 (sudo apt-get install python3)
pip (sudo apt-get install python3-pip)
nose (sudo pip3 install nose)
selenium (sudo pip3 install selenium)
geckodriver (wget https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz
             tar xzvf geckodriver-v0.20.0-linux64.tar.gz
             sudo mv geckodriver /usr/bin/
             rm geckodriver-v0.20.0-linux64.tar.gz)

# Building the development and release Docker images

From the top-level directory run:
./build.sh

# Running the Ember and server unit tests and the product tests

From the top-level directory run:
./runTests.sh

# Running the application after running build.sh

First create the directory the database will be stored in on the host:
mkdir -p /var/data

From the top-level directory run:
./run.sh

Then open a web browser and navigate to "localhost"
Note: tested on the latest versions of Firefox, Chrome, Opera and Safari.

# Packaging the application after running build.sh

./package.sh ```<year of contest>```
