# CEOS Open Data Cube UI Guide

This document will guide users through the process of installing, configuring, and running our Open Data Cube (ODC) user interface. 

Our interface is a full Python web server stack
using Django, Celery, PostgreSQL, and Boostrap3. 

In this guide, both Python and system packages will be installed and configured and users will learn how to start
the asynchronous task processing system.

- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Process](#installation-process)
  - [Pre-start Configuration](#pre-start-configuration)
  - [Launch Django Database](#launch-django-database)
  - [Starting Stopping Restarting](#starting-stopping-restarting)
  - [SSH to the UI](#ssh-to-the-ui)
  - [UI first-time post-start setup](#ui-first-time-post-start-setup)
- [UI Database Backups and Restoration](#ui-database-backups-and-restoration)
- [Clearing Migrations](#clearing-migrations)
- [Clearing Tasks](#clearing-tasks)
- [Access the UI](#access-the-ui)
- [Task System Overview](#task-system-overview)
- [Adding Data to an App](#adding-data-to-an-app)
- [Upgrades](#upgrades)
- [Logging](#logging)
  - [Logging Django Database](#logging-django-database)
  - [Logging Postgres Database](#logging-postgres-database)
- [Troubleshooting](#troubleshooting)
  - [Running Celery non-daemonized](#running-celery-non-daemonized)
- [Common Problems/FAQs](#common-problemsfaqs)

## Introduction
----

The CEOS ODC UI is a full stack Python web application used to perform analysis
on raster datasets using the Open Data Cube. Using common and widely accepted frameworks
and libraries, our UI is a good tool for demonstrating ODC capabilities and some possible applications and architectures. The UI's core technologies are:

- [**Django**](https://www.djangoproject.com/):
  Web framework, ORM, template processor, entire MVC stack
- [**Celery**](https://docs.celeryproject.org/en/stable/) + [**Redis**](https://redis.io/):
  Asynchronous task processing
- [**Open Data Cube**](http://datacube-core.readthedocs.io/en/stable/):
  API for data access and analysis
- [**PostgreSQL**](https://www.postgresql.org/):
  Database backend for both the Data Cube and our UI
- [**Apache/Mod WSGI**](https://en.wikipedia.org/wiki/Mod_wsgi):
  Standard service based application running our Django application while still providing hosting for static files
- [**Bootstrap3**](http://getbootstrap.com/):
  Simple, standard, and easy front end styling

Using these common technologies provides a good starting platform for users who want to develop ODC applications. Using Celery allows for simple distributed task processing while still being performant. Our UI is designed for high level use of the Data Cube and allows users to:

- Access various datasets that we have ingested
- Run custom analysis cases over user-defined areas and time ranges
- Generate both visual (image) and data products (GeoTIFF/NetCDF)
- Provide easy access to metadata and previously run analysis cases

## System Requirements
----

These are the base requirements for the UI:

- **Memory**: 8GiB
- **Local Storage**: 50GiB

## Prerequisites
----

To set up and run the ODC UI, the following conditions must be met:

- The [Environment Setup Guide](https://ceos-odc.readthedocs.io/en/latest/modules/install_docs/environment_setup.html) must have been completed.
- The [ODC Database Installation Guide](https://ceos-odc.readthedocs.io/en/latest/modules/install_docs/database_install.html) must have been completed.

If you want to analyze data from the UI, you must add data through indexing. See the [ODC Indexer](https://github.com/ceos-seo/odc_manual_indexer) to learn how to index data. The UI will work without any indexed data,
but no analysis can occur.

Before we begin, note that multiple commands should not be copied and pasted to be run simultaneously unless you know it is acceptable in a given command block. Run each line individually.

## Installation Process
----

>### Pre-start Configuration

Run `git submodule init && git submodule update` from the top level directory of this repository to retrieve the utility code in a `utils` directory.

You can set the port that the UI will be available on with the `HOST_PORT` environment varaible in the `build/docker/dev/.env` file. By default, the UI will be available on port `8000` in the development environment.

The `DJANGO_DB_*` and `ODC_DB_*` variables in the `build/docker/dev/.env` file are the connection credentials for the Django database and the ODC database. The `ODC_DB_*` variables are set to match the default settings for the ODC database container, but if these settings were changed in the command for the `create-odc-db` target in the `Makefile` file, they will need to be changed here.

The `ADMIN_EMAIL` setting is unsued and the `MPLCONFIGDIR` setting should not be changed.

If you want to access data on S3, you will need to set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` variables. By default, they are set to use the values of identically named environment variables. You should set these environment variables before running the UI. Do not write these AWS credentials to the `build/docker/dev/.env` file directly.

>### Launch Django Database

We need to create a filesystem volume for the Django database data so that it remains on the local filesystem and is not lost whenever the Docker container for the Django database terminates.

Run the following command to do this:
`make dev-create-django-db-volume`

>### Starting Stopping Restarting

To start the development environment, run this command:

```bash
make dev-up
```

To stop the development environment, run this command:

```bash
make dev-down
```

To restart the development environment, run this command:

```bash
dev-restart
```

When starting or restarting in the future, you can use the `-no-build` versions of the `Makefile` targets if the dependencies have not changed (e.g. if only changes have been made to the UI code). These target variants complete faster than their counterparts which do rebuild (few seconds difference usually). These include:

- `dev-up-no-build`
- `dev-restart-no-build`

>### SSH to the UI

To connect to the development environment through a bash shell over SSH, run this command:

```bash
make dev-ssh
```

Once connected, run this command to activate the Python virtual environment:

```bash
source datacube_env/bin/activate
```

This must be run for every connection with `make dev-ssh`.

>### UI first-time post-start setup

In the development environment, you will need to run these commands in the UI container **only if this is the first time starting the UI** - they must be run once before the UI will work (connect through SSH as explained in the [instructions above](#install_ssh)).

```bash
bash scripts/migrations.sh
bash scripts/load_default_fixture.sh
```

The second command sets the UI (Django) database state to a default one. Do not run this command later if you have modified the UI database and want to keep your modifications (e.g. [Area objects added for the UI to access your own Data Cube products](#adding_data)), because they will be lost when running `bash scripts/load_default_fixture.sh`.

## UI Database Backups and Restoration
----

To backup the UI database, run `bash scripts/create_fixture.sh <path>`, where `<path>` is the desired path to your new database backup JSON file, such as `db_backups/init_database_YYYY_MM_DD.json`, where `YYYY_MM_DD` is the date, such as `2020_09_10` for September 10, 2020.

To restore the UI database, run `bash scripts/load_fixture.sh <path>`, where `<path>` is the path to your database backup JSON file.

## Clearing Migrations

You can clear the Django migrations with `bash scripts/clear_migrations.sh`.

## Clearing Tasks

You can clear the UI's task history (not Celery's task queue) with `bash scripts/`.

## Access the UI
----

In the development environment, you can connect to the UI on the host machine at `localhost:<HOST_PORT>`, where `<HOST_PORT>` is the value of the `HOST_PORT` environment variable specified in `build/docker/dev/.env`.

## Task System Overview
----

The task system can seem complex at first, but the basic workflow is shown below:

- The Django view receives form data from the web page.
  This form data is processed into a Query model for the application
- The main Celery worker receives a task with a Query model and pulls all of the
  required parameters from this model
- Using predefined chunking options, the main Celery task splits the parameters
  (latitude, longitude, time) into smaller chunks
- These smaller chunks of (latitude, longitude, time) are sent off to the Celery
  worker processes - there should be more worker processes than master processes
- The Celery worker processes load in the data in the parameters they received
  and perform some analysis. The results are saved to disk and the paths are returned
- The master process waits until all chunks have been processed then loads all
  of the result chunks. The chunks are combined into a single product and saved
  to disk
- The master process uses the data product to create images and data products
  and saves them to disk, deleting all the remnant chunk products
- The master process creates a Result and Metadata model based on what was just
  created and returns the details to the browser

## Adding Data to an App
----

To finish the configuration, we will need to create an `Area` object in the UI for a Data Cube product that you have indexed.

First, we need to find the bounding box of your data. Use the following commands in the UI Docker container to open a Django Python shell and query the Data Cube for your product's extents:

```bash
source ~/datacube_env/bin/activate
python3 manage.py shell

from utils.data_cube_utilities import data_access_api

api = data_access_api.DataAccessApi()

api.get_datacube_metadata(<product_name>,<platform_name>)
```

Record the latitude and longitude extents.

Go back to the admin page (`localhost:<port>/admin`), select `Dc_Algorithm -> Areas`, delete all of the
initial areas, then click the 'Add' button.

Give the area an ID and a name. The name is what will be shown in the UI.

Enter the latitude and longitude bounds in all of the latitude/longitude min/max fields.

For the imagery field, enter `/static/assets/images/black.png` - this will give a black area preview, but will still contain the data we specify. You can also include your own image in `/static/assets/images` and specify that to be used here.

Select an appropriate `Satellite` (`LANDSAT_7`, `LANDSAT_8`, etc.) and save your new `Area` (click the `SAVE` button in the lower right).

Navigate back to the main admin page and select `Dc_Algorithm -> Area products map`. Click the 'Add' button. Specify an ID (e.g. for Landsat 8 data, you can use a format like `<Area-id>-ls8`). Select the `Area` you just added in the `Area` dropdown list. Select the `Satellite` you chose for your `Area`. Type in the product name you want to load data for in the `Product names` field. If there are multiple products for the `Satellite` (e.g. combinations like `LANDSAT_7,LANDSAT_8`), separate them with commas (`,`).

Navigate back to the main admin page and select `Dc_Algorithm -> Applications`. Choose `custom_mosaic_tool` and select your area in the `Areas` field. Save the model and exit.

Go back to the main site and navigate back to the Custom Mosaic Tool. You will see that your area is the only one in the list - select this area to load the tool. Make sure your Celery workers are running (`service data_cube_ui status`) and submit a task over the default time over some small area you know you have data for and watch it complete. The web page should show an image over the query area when the task completes.

## Upgrades
----

Upgrades can be pulled directly from our GitHub releases using Git. There are a few steps that will need to be taken to complete an upgrade from an earlier release version:

- Pull the code from our repository.
- [Restart the UI](#starting-stopping-restarting).
- Make and run the Django migrations with `bash scripts/migrations.sh`. We do not keep our migrations in Git so these are specific to your system.
- If we have added any new applications (found in the `apps` directory) then you will need to obtain the default state for that app with `python manage.py loaddata db_backups/default/{app_name}.json`.

## Logging
----

>### Logging Django Database

To see logs for the Django database, follow these steps to setup logging to the filepath `/datacube/ui_results/support.log`, which you can specify to whatever path you want:
1. In `settings.py`:
   1. Set `DEBUG = True`.
   2. Add the following text (say, at the bottom of the file):
    ```python
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/datacube/ui_results/support.log',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['file', ],
            },
        }
    }
    ```

2. Run `sudo service apache2 restart` to restart the webserver.

>### Logging Postgres Database

To also log Postgres output (not database changes from the perspective of Django - these are the Postgres logs, separate from Django):
1. Backup the current `postgresql.conf` file:
   1. `cd ~/Datacube/data_cube_ui/config`
   2. `sudo cp /etc/postgresql/{version}/main/postgresql.conf postgresql_backup.conf` where version is probably 9.5 or 10
   3. `cp postgresql_backup.conf postgresql.conf `
2. Make the following edits to `~/Datacube/data_cube_ui/config/postgresql.conf`:
   1. Uncomment `log_statement` and set it to `'all'`.
   2. Uncomment `log_destination`.
3. Put the new `postgresql.conf` file in its proper location:
`sudo cp postgresql.conf /etc/postgresql/{version}/main/postgresql.conf`.
4. Run `sudo service postgresql restart`.

## Troubleshooting
----

The general workflow for troubleshooting the UI is found below:

- Check for errors in the log files:
  - To check for Celery errors, run `grep -re Error /var/log/celery`. Examine the files containing error logs with `cat <path-to-file>`.
  - To check for Django (website) errors, run `grep -e Error log/ODC_UI.log`
  - To check for Apache (webserver) errors, run `grep -e Error /var/log/apache2/error.log`.
- Search the internet for suggested solutions to the error messages you encounter.
- If there is a 500 HTTP error or a Django error page without enough information about the error, ensure that `DEBUG` is set to `True` in `settings.py`, [restart the UI](#install_restart) if you had to change it to `True`, and observe the error message in the logs (`log/ODC_UI.log`) or the error page (in the browser).
- Fix the error described by the message and then [restart the UI](#install_restart).

If you are having trouble diagnosing issues with the UI, feel free to contact us with a description of the issue and all relevant logs or screenshots. To ensure that we are able to assist you quickly and efficiently, please verify that your
server is running with `DEBUG = True`.

>### Running Celery non-daemonized
----

When troubleshooting, you may consider running Celery manually (non-daemonized).
Only do this if you are sure that Celery is not functioning properly when daemonized.
Otherwise, skip this subsection.

Open two new terminal sessions and activate the virtual environment in both.
We usually use `tmux` to handle multiple detached windows to run commands in the background.
You can install `tmux` with the command `apt-get install tmux`.
A reference is available [here](https://gist.github.com/MohamedAlaa/2961058).
For all terminals, ensure the virtual environment is activated and you are in the UI directory:

```bash
source ~/Datacube/datacube_env/bin/activate
cd ~/Datacube/data_cube_ui
```

In the first terminal, run the celery process with:

```bash
celery -A data_cube_ui worker -l info -c 4
```

In the second terminal, run the single-use Data Cube Manager queue.

```bash
celery -A data_cube_ui worker -l info -c 2 -Q data_cube_manager --max-tasks-per-child 1 -Ofair
```

Additionally, you can run both simultaneously using `celery multi`:

```bash
celery multi start -A data_cube_ui task_processing data_cube_manager -c:task_processing 10 -c:data_cube_manager 2 --max-tasks-per-child:data_cube_manager=1  -Q:data_cube_manager data_cube_manager -Ofair
```

To start the task scheduler, run the following command:

```bash
celery -A data_cube_ui beat
```

## Common Problems/FAQs
----

Q:

> I’m getting a “Permission denied error.” How do I fix this?

A:

> More often than not the issue is caused by a lack of permissions on the folder where the application is located. Grant full access to the folder and its subfolders and files (this can be done by using the command `chmod -R 777 FOLDER_NAME`).

----

Q:

> I'm getting a "too many connections" error when I run a task in the UI,
> such as
> `org.postgresql.util.PSQLException: FATAL: sorry, too many clients already.`

A:

> The Celery worker processes have opened too many connections for your database
> setup. In the configuration file for the ODC database (usually `/var/lib/pgsql/data/postgresql.conf`), increase `max_connections`
> and `shared_buffers` in an equal proportion. The `max_connections` setting
> is the maximum number of concurrent connections to Postgres. Note that
> every UI task can and often does make several connections to Postgres.
> Also set `kernel.shmmax` to a value slightly large than `shared_buffers`.
> Finally, run `sudo service postgresql restart`.
> If the settings are already suitable, then the celery workers may be opening
> connections without closing them. To diagnose this issue, start the celery
> workers with a concurrency of 1 (i.e. `-c 1`) and check to see what tasks are
> opening postgres connections and not closing them. Ensure that you stop the
> daemon process (`service data_cube_ui stop`) before creating the console Celery worker process.

----

Q:

> When running tasks, I receive errors like
> `ValueError: No products match search terms {...}`.

A:

> First ensure the following is true:
>
> 1. The area has been added
>    to the app via the admin menu `Dc_Algorithm -> Applications -> [app_name]`.
> 1. The selected area is the desired area.
> 1. The Data Cube product name abides by the naming constraints described in
>    the section titled `Customize the UI` in this document.
> 1. The query extents overlap the Data Cube product for the selected satellite and area combination.
>
> If these parameters really should be returning data, run `dc.load()` queries with
> `python manage.py shell` in the top-level `data_cube_ui` directory with parameters
> matching the ones in errors like this in your Celery log files.

----

Q:

> My tasks won't run - there is an error produced and the UI creates an alert.

A:

> Start your celery worker in the terminal with debug mode turned on and `loglevel=info`.
>
> Stop the daemon process if it is started to ensure that all tasks will be visible. Run the task that is failing and observe any errors. The terminal output will tell you what task caused the error and what the general problem is.

----

Q:

> Tasks don't start - when submitted on the UI, a progress bar is created but
> there is never any progress.

A:

> This state means that the Celery worker pool is not accepting your task.
> If the system has worked recently and no changes have occurred recently to the code, follow these steps:
>> 1. Stop all Celery workers with this command:<br>
`ps aux | grep 'celery worker' | awk '{print $2}' | xargs kill`
>> 2. Run this command in the UI directory (repository root directory) to purge the task queue (otherwise Celery may crash again on restart as it tries to process the tasks in the task queue):<br>
>> `bash scripts/celery/purge_task_queue.sh`
>> 3. Restart the `data_cube_ui` service:
>> * `sudo service data_cube_ui restart` OR
>> * `sudo /etc/init.d/data_cube_ui restart` (if the former fails)
>> Tasks submitted should now complete successfully.
>
> If the system has not worked recently or changes have occurred to the code, follow these steps:
>> 1. Check your server to ensure that a Celery worker process is running with `ps aux | grep celery`. 
>> 2. If there is a Celery worker running, check that the `MASTER_NODE` setting is set in the `settings.py` file to point to your server (should be by default) and that Celery is able to connect. To do this, stop Celery (`service data_cube_ui stop`) and [run the worker in the terminal](#celery_non_daemonized).

----

Q:

> I'm seeing some SQL-related errors in the Celery logs that prevent tasks from running.

A:

> Run the Django migrations to ensure that you have the latest database schemas.
> If you have updated recently, ensure that you have a database table for each app.
> If any are missing, run `python manage.py makemigrations {app_name}` followed
> by `python manage.py migrate`.

----

Q:

> How do I refresh the Data Cube Visualization tool?<br/>
> My regions are not showing up in the Data Cube Visualization tool.

A:

> Activate the Data Cube virtual environment:<br/> > `source ~/Datacube/datacube_env/bin/activate`<br/>
> enter the Django console:<br/> > `cd ~/Datacube/data_cube_ui`<br/> > `python manage.py shell`<br/>
> then run this function, which should update the cache:<br/> > `import apps.data_cube_manager.tasks as dcmt`<br/> > `dcmt.update_data_cube_details()`

----
