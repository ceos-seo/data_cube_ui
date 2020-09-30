# Open Data Cube Database Installation Guide

This document is a guide for installing and configuring 
the Open Data Cube index database - which the ODC will query to determine where to retrieve data from (e.g. local or remote GeoTIFFs).

## Contents

  * [Prerequisites](#prerequisites)
  * [Installation Procedure](#installation_procedure)
    * [Creating the database locally](#creating_locally)
  * [External Connections](#external_connections)

## <a name="prerequisites"></a> Prerequisites
-------

Docker must already be installed on your system.

Follow the [Docker Installation Guide](docker_install.md) if you do not have Docker installed yet.

You must also have the `make` command installed.

## <a name="installation_procedure"></a> Installation Procedure
-------

Ultimately, the database should be a Postgres instance accessible from the ODC installations you want to access it from.

You will need to know:
* The host name (IP or domain name of the database)
* The database name (name of the database within Postgres to use for ODC) 
* The user name (name of the Postgres user that will access the database) 
* The password (password for the aforementioned user)

These values will need to be set in the `datacube.conf` file for all ODC installations that should index this database. See the [ODC Environment Configuration](https://datacube-core.readthedocs.io/en/stable/ops/config.html) documentation for information on setting up ODC configuration files.

We can't include full instructions for how to set up the database on all cloud providers, but the instructions for setting it up locally with Docker using Linux shell commands are included below.

>### <a name="creating_locally"></a> Creating the database locally
The following commands should be run from the top-level directory (directory containing `Makefile`).

First we need to create a network for the Docker container. The database will only be accessible from other Docker containers on this machine in the `odc` Docker network.

Run the following command to do this:
`make create-odc-network`

Next we need to create a filesystem volume for the database data so that it remains on the local filesystem and is not lost whenever the Docker container for the database terminates.

Run the following command to do this:
`make create-odc-db-volume`

Now we need to create the Docker container for the database.
In the `Makefile` file at the top-level directory, find the `create-odc-db` target. Here you will see the command to create the ODC database Docker container. You can replace the values for `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` with the desired Postgres database name, user name, and password, but if you use the defaults here, you will not need to change corresponding settings for applications that use them, like the [CEOS Open Data Cube Notebooks](https://github.com/ceos-seo/data_cube_notebooks) or the [CEOS Open Data Cube UI](https://github.com/ceos-seo/data_cube_ui).

Once you are ready to start the database, run this command:
`make create-odc-db`

## <a name="external_connections"></a> External Connections
-------

If you want this database to be accessible from anywhere, just specify the mapping of the Postgres port (`5432`) to the port on the host that it should be available from with the argument `-p <host port>:5432` after `run` and before `postgres` in the command for the `create-odc-db` target in the `Makefile` file.
Use `-p 5432:5432` if possible.

ODC installations on this machine (e.g. the ODC UI) can be pointed to this index database by setting the `db_hostname` value in the `datacube.conf` file to the `name` of the database Docker container (`odc-db` in this case), but ODC installations outside this machine will set `db_hostname` to `<IP>:<port>`, where `IP` is the IP or domain name of the machine the database is running on and `port` is the host port specified previously.

