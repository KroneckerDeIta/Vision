# Use the base image.
FROM vision-server-base:latest

RUN pip3 install cx_freeze
RUN pip3 install mock
RUN pip3 install nose

# Set the password to password in the development container.
RUN service mysql start && mysqladmin -u root password password
RUN service mysql start && mysql -uroot -ppassword -e "grant all privileges on *.* to vision@localhost identified by 'visionpass';"
