#!/bin/bash

if [[ -z ${RESET_DATABASE} ]]; then
    reset_database=false
else
    reset_database=${RESET_DATABASE}
fi

if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "Creating the default database"
    /usr/sbin/mysqld --initialize-insecure --datadir=/var/lib/mysql
    service mysql start
    mysqladmin -u root password password
    mysql -uroot -ppassword -e "grant all privileges on visiondb.* to vision@localhost identified by 'visionpass';"
else
    echo "MySQL database already initialiazed"
    service mysql start
fi

cd /opt/vision
python3 server.py --reset_database=${reset_database}