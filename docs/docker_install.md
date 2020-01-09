# Docker Installation Guide

This document is a guide for installing Docker.

## Installation
For Windows users, install [Docker for Windows (Docker Desktop)](https://docs.docker.com/docker-for-windows/).

For Ubuntu users, run the following commands:
```
sudo apt-get update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
# The following steps are for enabling use 
# of the `docker` command for the current user
# without using `sudo`
sudo groupadd docker
sudo usermod -aG docker $USER
```
After running the above commands, logout and then login again.

## Testing 
Once Docker is installed, test it with 
the following command: `docker run hello-world`

You should see output beginning with `Hello from Docker!`.