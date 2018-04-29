#
# Ubuntu Dockerfile
#
# https://github.com/dockerfile/ubuntu
#

# Pull base image.
FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

# Install.
RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y build-essential
RUN apt-get install -y software-properties-common
RUN apt-get install -y curl unzip vim wget
RUN apt-get install -y python3-dev python3-pip libssl-dev libffi-dev
RUN apt-get install -y mysql-server libmysqlclient-dev

RUN pip3 install --upgrade pip

RUN pip3 install mysqlclient
RUN pip3 install tornado
RUN pip3 install passlib
