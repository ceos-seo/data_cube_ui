# Open Data Cube Database Installation Guide

This document is a guide for installing and configuring 
the Open Data Cube index database - which the ODC will query
to determine where to retrieve data from (e.g. local or remote GeoTIFFs).

## <a name="prerequisites"></a> Prerequisites

Docker must already be installed on your system.

Follow the [Docker Installation Guide](docker_install.md) if you
do not have Docker installed yet.

## <a name="installation_procedure"></a> Installation Procedure
Ultimately, the database should be a Postgres instance accessible 
from the ODC installations you want to access it from.

You will need to know the host name (IP or domain name of the database),
database name (name of the database within Postgres to use for ODC),
user name (name of the Postgres user that will access the database),
and password (password for the aforementioned user). These values will
need to be set in the `.datacube.conf` file for all ODC installations
that should index this database.

We can't include full instructions for how to set up the database on 
all cloud providers, but the instructions for setting it up locally
using Unix shell commands are included below. 

>## Creating the database on this machine
The following commands should be run from the top-level 
`data_cube_ui` directory.

This command creates a Postgres ODC index database container in Docker.
The `-e` flags specify values for environment variables for Postgres.
Remember what values you set for these environment variables, since, as
mentioned above, you will need to set them in the `.datacube.conf` 
files of ODC installations that will use this database.
In its formulation below, the database will only be accessible from
other Docker containers on this machine.
```
docker network create odc
docker container rm odc-db
docker run -d \
-e POSTGRES_DB=datacube \
-e POSTGRES_USER=dc_user \
-e POSTGRES_PASSWORD=localuser1234 \
--name=odc-db \
--network="odc" \
postgres:10-alpine
```

If you want this database to be accessible from anywhere, just
specify the mapping of the Postgres port (`5432`) to the port on
the host that it should be available from with the argument 
`-p <host port>:5432` after `run` and before `postgres` in the above command.
Use `-p 5432:5432` if possible.

ODC installations on this machine (e.g. the ODC UI) can be pointed to this 
index database by setting the **db_hostname** value in the
**~/.datacube.conf** file to the `name` of the database Docker container 
(**odc-db** in the case above), but ODC installations outside this machine 
will set **db_hostname** to `<IP>:<port>`, where `IP` is the IP or 
domain name of the machine the database is running on and `port` 
is the host port specified previously, assuming it was specified.

