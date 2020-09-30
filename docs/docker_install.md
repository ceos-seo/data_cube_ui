# Docker Installation Guide

This document is a guide for installing Docker.

## Installation
-------

For Windows users, install [Docker for Windows (Docker Desktop)](https://docs.docker.com/docker-for-windows/). We encourage you to use the [Windows Subsystem for Linux Version 2 (WSL2)](https://docs.microsoft.com/en-us/windows/wsl/install-win10). We recommend choosing the latest version of Ubuntu for the Linux distribution. 

For Ubuntu users (**not WSL Ubuntu**), ensure you are a sudoer (user that can run `sudo`). Run the `sudo-ubuntu-install-docker` target in `Makefile` from the top-level directory to install Docker:
```
make sudo-ubuntu-install-docker
```
After running the above commands, logout and then login again.

## Testing
-------

Once Docker is installed, test it with 
the following command: `docker run hello-world`

You should see output beginning with `Hello from Docker!`.