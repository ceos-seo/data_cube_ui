
# Open Data Cube UI Installation Guide

This document will guide users through the process of installing and configuring 
our Data Cube user interface. Our interface is a full Python web server stack 
using Django, Celery, PostgreSQL, and Boostrap3. In this guide, both Python and 
system packages will be installed and configured and users will learn how to start 
the asynchronous task processing system.

## Contents

  * [Introduction](#introduction)
  * [System Requirements](#system_requirements)
  * [Prerequisites](#prerequisites)
  * [Installation Process](#installation_process)
    * [Docker Installation](#docker_install)
    * [Manual Installation](#manual_install)
  * [Configuring the Server](#configuration)
  * [Initializing the Database](#database_initialization)
  * [Starting Workers](#starting_workers)
  * [Task System Overview](#task_system_overview)
  * [Customize the UI](#customization)
  * [Maintenance, Upgrades, and Debugging](#maintenance)
  * [Cleaning Up](#cleaning_up)
  * [Next Steps](#next_steps)
  * [Common problems/FAQs](#faqs)

## <a name="introduction"></a> Introduction
-------

The CEOS Data Cube UI is a full stack Python web application used to perform analysis 
on raster datasets using the Data Cube. Using common and widely accepted frameworks 
and libraries, our UI is a good tool for demonstrating the Data Cube capabilities 
and some possible applications and architectures. The UI's core technologies are:

* [**Django**](https://www.djangoproject.com/): 
Web framework, ORM, template processor, entire MVC stack
* [**Celery + Redis**](http://www.celeryproject.org/): 
Asynchronous task processing
* [**Data Cube**](http://datacube-core.readthedocs.io/en/stable/): 
API for data access and analysis
* [**PostgreSQL**](https://www.postgresql.org/): 
Database backend for both the Data Cube and our UI
* [**Apache/Mod WSGI**](https://en.wikipedia.org/wiki/Mod_wsgi): 
Standard service based application running our Django application while still providing hosting for static files
* [**Bootstrap3**](http://getbootstrap.com/): 
Simple, standard, and easy front end styling

Using these common technologies provides a good starting platform for users 
who want to develop Data Cube applications. Using Celery allows for simple 
distributed task processing while still being performant. Our UI is designed 
for high level use of the Data Cube and allows users to:

* Access various datasets that we have ingested
* Run custom analysis cases over user-defined areas and time ranges
* Generate both visual (image) and data products (GeoTIFF/NetCDF)
* Provide easy access to metadata and previously run analysis cases

## <a name="system_requirements"></a> System Requirements
-------

The UI currently runs on the Ubuntu 18.04 LTS Operating System. The base requirements can be found below:

* **Memory**: 8GiB
* **Local Storage**: 50GiB

## <a name="prerequisites"></a> Prerequisites
-------

To set up and run our Data Cube UI, the following conditions must be met:

* The [Open Data Cube Database Installation Guide](odc_db_setup.md) must have been followed and completed. 
<!-- This includes:
  * You have a user that is used to run the Data Cube commands/applications.
  * You have a database user that is used to connect to your `datacube` database.
  * The Data Cube is installed and you have successfully run `datacube system check`.
  * You are in the Datacube virtual environment, having run `source ~/Datacube/datacube_env/bin/activate`. -->

If these requirements are not met, please see the associated documentation. 
Please take some time to get familiar with the documentation of our core 
technologies - most of this guide is concerning setup and configuration 
and is not geared towards teaching about our tools.

If you want to analyze data from the UI, the 
[Open Data Cube Ingestion Guide](ingestion.md) must have been 
followed and completed. The UI will work without any ingested data, 
but no analysis can occur. The steps include:
* A sample Landsat 7 scene was downloaded and uncompressed in your `/datacube/original_data` directory
* The ingestion process was completed for that sample Landsat 7 scene.

Before we begin, note that multiple commands should not be copied and pasted 
to be run simultaneously unless you know it is acceptable in a given command block. 
Run each line individually.

## <a name="installation_process"></a> Installation Process
-------

>## <a name="docker_install"></a> Docker Installation (preferred)

>### <a name="docker_install_build"></a> Build the Image

The following commands should be run from the top-level 
`data_cube_ui` directory.
```
docker build docker/ui -t <tag>
docker run -d <tag> 
```

>### <a name="docker_install_build"></a> Build the Image

>## <a name="manual_install"></a> Manual Installation

>### <a name="manual_install_venv_setup"></a> Virtual Environment Setup

We need to install the virtual environment and source it before we start installing packages with `pip`. This is a way to compartmentalize the Python 
packages and keep your operating environment unaffected by changes to Python 
made from within the virtual environment.

```
sudo pip3 install virtualenv 
virtualenv ~/Datacube/datacube_env
source ~/Datacube/datacube_env/bin/activate
```

The installation process includes both system-level packages and Python packages. 
You will need to have the virtual environment activated for this entire guide.

>### <a name="manual_install_download"></a> Download the UI

The UI can be downloaded as follows:

```
cd ~/Datacube
git clone https://github.com/ceos-seo/data_cube_ui.git
cd data_cube_ui
git submodule init && git submodule update
```

>### <a name="manual_install_create_user"></a> Create a User

These documents assume the username is `localuser`, but it can be anything 
you want.  We recommend the use of `localuser`, however, as a considerable 
number of our configuration files for the UI assume the use of this name. 
To use a different name may require the modification of several additional 
configuration files that otherwise would not need modification. 
Do not use special characters such as <b>è</b>, <b>Ä</b>, or <b>î</b> in 
this username as it can potentially cause issues in the future. 
We recommend an all-lowercase underscore-separated string.

You can execute the following commands to create this user:
```
sudo adduser localuser
sudo usermod -aG sudo localuser
sudo su localuser
```
This user has sudo (or "admin" or "root") privileges for now to make installing
things convenient, but we will remove these privileges from this user later for 
security reasons.

>### <a name="manual_install_apache"></a> Install Apache

Run the following commands to install Apache, Apache-related packages, 
Redis, and image processing libraries.

```
sudo apt-get install apache2 libapache2-mod-wsgi-py3 redis-server libfreeimage3 imagemagick

sudo service redis-server start
```

>### <a name="manual_install_python"></a> Install Python Dependencies

Next, you'll need various Python packages that are responsible for running the application:

```
pip install hdmedians lcmap-pyccd==2017.6.8
pip install rasterio
pip install numpy xarray scipy
pip install sklearn scikit-image
pip install shapely cloudpickle Cython netcdf4
pip install sqlalchemy psycopg2-binary
pip install matplotlib seaborn

pip install stringcase imageio
pip install django==2.2.10 django-bootstrap3
pip install celery redis
```

>### <a name="manual_install_results_dir"></a> Create Results Directory

You will also need to create a base directory structure for results:

```
sudo mkdir /datacube/ui_results
sudo chmod 777 /datacube/ui_results
```

>### <a name="manual_install_mail"></a> Setup Mail Server

The Data Cube UI also sends admin mail, so a mail server is required.
Be sure to configure it as an internet site.

```
sudo apt-get install -y mailutils
```

Make the necessary changes to `/etc/postfix/main.cf`:

```
myhostname = {your site name here}
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = localhost
```

and run `sudo service postfix restart`.

To test the installation and setup of the mail server run the following command.
Change `your_email@mail.com` to your email address.

```
echo "Body of the email" | mail -s "The subject line" your_email@mail.com
```

With all of the packages above installed, you can now move on to the configuration step.

>### <a name="manual_install_configuration"></a> Configuring the Server

The configuration of our application involves ensuring that configuration files
have correct contents, moving those configuration files to the correct locations, 
and then enabling the systems.

Specifically, we need to setup the Open Data Cube and Apache configuration files.

To setup the Open Data Cube configuration file, open 
`~/Datacube/data_cube_ui/config/.datacube.conf` and ensure that the 
the `db_hostname`, `db_database`, `db_username`, and `db_password` values are
set correctly. These values were determined during the Open Data Cube Core 
installation process. If these details are not correct, please correct them 
and save the file.

**Please note that our UI application uses the configuration file 
`config/.datacube.conf` for everything 
rather than the default `~/.datacube.conf` file.**

Next, we'll need to update the Apache configuration file. 
Open the file found at `~/Datacube/data_cube_ui/config/dc_ui.conf`:

```
<VirtualHost *:80>
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	#ServerName www.example.com

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf

	# django wsgi
	WSGIScriptAlias / ${DC_UI_DIR}/data_cube_ui/wsgi.py
	WSGIDaemonProcess dc_ui python-home=${DC_UI_PYTHONHOME} python-path=${DC_UI_PYTHONPATH}

	WSGIProcessGroup dc_ui
	WSGIApplicationGroup %{GLOBAL}

	<Directory "${DC_UI_DIR}/data_cube_ui/">
		Require all granted
	</Directory>

	#django static
	Alias /static/ ${DC_UI_DIR}/static/
	<Directory ${DC_UI_DIR}/static>
		Require all granted
	</Directory>

	#results.
	Alias /datacube/ /datacube/
	<Directory /datacube/>
		Require all granted
	</Directory>

	# enable compression
	SetOutputFilter DEFLATE

</VirtualHost>
```

Run the following commands to set some environment variables needed by
the Apache configuration file:
```
DATACUBE_DIR=${HOME}/Datacube
DC_UI_DIR=${DATACUBE_DIR}/data_cube_ui
DC_UI_PYTHONHOME=${DATACUBE_DIR}/datacube_env
DC_UI_PYTHONPATH=${DC_UI_DIR}
```

<!-- This file assumes a standard installation with a virtual environment located 
in the location specified in the installation documentation. -->

We'll now copy the configuration files to where they need to be. 
The `~/.datacube.conf` file is overwritten with the UI version for consistency.

```
sudo cp ~/Datacube/data_cube_ui/config/.datacube.conf ~/.datacube.conf
sudo cp ~/Datacube/data_cube_ui/config/dc_ui.conf /etc/apache2/sites-available/dc_ui.conf
```

The next step is to edit the credentials found in the Django settings. 
Open the `settings.py` file found at `~/Datacube/data_cube_ui/data_cube_ui/settings.py`. 
There are a few small changes that need to be made for consistency with your settings.

The `MASTER_NODE` setting refers to a clustered/distributed setup. 
This should remain `'127.0.0.1'` on the main machine, 
while the other machines will enter the IP address of the main machine here. 
For instance, if your main machine's public IP is 52.200.156.1, 
then the worker nodes will enter `'52.200.156.1'` as the `MASTER_NODE` value.

```
MASTER_NODE = '127.0.0.1'
```

The application settings are definable as well. 
Change the `BASE_HOST` setting to the URL that your application will be accessed with.  
The `ADMIN_EMAIL` setting should be the email address that you want the UI to send emails as. 
Email activation and feedback will be sent from the email address here. 
The host and port are configurable based on where your mail server is. 
We leave it running locally on port 25.

```
# Application definition
BASE_HOST = "localhost:8000/"
ADMIN_EMAIL = "example@your_domain.org"
EMAIL_HOST = "localhost"
EMAIL_PORT = "25"
```

Next, replace `localuser` with whatever your local system user is. 
This corresponds to the values you entered in the Apache configuration file.

```
LOCAL_USER = "localuser"
```

The database credentials need to be entered here or as environment variables. 
Enter the database name, username, and password that you entered in your `.datacube.conf` file as the second values for the `os.environ.get()` calls, or as the environment variables `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`, `DB_HOSTNAME`, and `POSTRES_PORT`.

```
db_user = os.environ.get('DB_USER', 'dc_user')
db_pass = os.environ.get('DB_PASSWORD', 'localuser1234')
db_name = os.environ.get('DB_DATABASE', 'datacube')
db_host = os.environ.get('DB_HOSTNAME', '127.0.0.1')
db_port = os.environ.get('POSTGRES_PORT', '5432')
```

>### <a name="manual_install_apache_enable"></a> Enable the Site for Apache

Now that the Apache configuration file is in place and the Django settings 
have been set, we will now enable the site and disable the default. 
Use the commands listed below:

```
sudo a2dissite 000-default.conf
sudo a2ensite dc_ui.conf
sudo service apache2 reload
```

>### <a name="manual_install_pgpass"></a> Create a PGPASS file

Additionally, a `.pgpass` Postgres file is required for the Data Cube On Demand functionality. 
In `config/.pgpass`, replace `dc_user` with your database user name and replace `localuser1234` with you database user password 
and copy that file into the home directory of your user.

```
cp config/.pgpass ~/.pgpass
chmod 600 ~/.pgpass
```

>### <a name="manual_install_database_initialization"></a> Initializing the Database

Now that all of the requirements have been installed and all of the configuration 
details have been set, it is time to initialize the database.

Django manages all database changes automatically through the ORM/migrations model. 
When there are changes in the `models.py` files, Django detects them and creates 
'migrations' that make changes to the database according to the Python changes. 
This requires some initialization now to create the base schemas.

Run the following commands:

```
cd ~/Datacube/data_cube_ui
python manage.py makemigrations {data_cube_ui, accounts, cloud_coverage, coastal_change, custom_mosaic_tool, data_cube_manager, dc_algorithm, fractional_cover, slip, spectral_anomaly, spectral_indices, task_manager, tsm, urbanization, water_detection}

python manage.py makemigrations
python manage.py migrate

python manage.py loaddata db_backups/init_database.json
```

This string of commands makes the migrations for all applications 
and creates all of the initial database schemas. 
The last command loads in the default sample data that we use - 
including some areas, result types, etc.

Next, create a super user account on the UI for personal use:

```
python manage.py createsuperuser
```

Now that we have everything initialized, we can view 
the site and see what we've been creating. 
Visit the site in your web browser - either by IP 
from an outside machine or at the URL `localhost` within the machine. 
You should now see a introduction page. Log in using 
one of the buttons and view the Custom Mosaic Tool. 
You'll see all of our default areas. **This does not give access to all 
of these areas because they are examples with no associated data. 
You will need to add your own areas and remove the defaults.**

Visit the administration panel by going to either `{IP}/admin` or `localhost/admin`. 
You'll see a page that shows all of the various models and default values.

>### <a name="manual_install_starting_workers"></a> Starting Celery Workers

We use Celery workers in our application to handle the asynchronous task processing. 

To test the workers we will need to add an area and dataset that you have ingested 
into the UI's database. This will happen in a separate section.

In the `config` directory, ensure the following for both the `celeryd_conf` 
and `celerybeat_conf` files:
1. `CELERY_BIN` is set to the path to Celery in your virtual environment.
2. `CELERYD_CHDIR` is set to the path to the `data_cube_ui` directory.
3. `CELERYD_USER` and `CELERYD_GROUP` are set to the username of the user.

Then run the following commands to daemonize the Celery workers and 
start the `data_cube_ui` system service.

```
sudo cp config/celeryd_conf /etc/default/data_cube_ui && sudo cp config/celeryd /etc/init.d/data_cube_ui
sudo chmod 777 /etc/init.d/data_cube_ui
sudo chmod 644 /etc/default/data_cube_ui
sudo /etc/init.d/data_cube_ui start

sudo cp config/celerybeat_conf /etc/default/celerybeat && sudo cp config/celerybeat /etc/init.d/celerybeat
sudo chmod 777 /etc/init.d/celerybeat
sudo chmod 644 /etc/default/celerybeat
sudo /etc/init.d/celerybeat start
```

You can start, stop, kill, restart, etc. the workers using `sudo /etc/init.d/data_cube_ui`.
For example `sudo /etc/init.d/data_cube_ui restart` will restart the Celery workers.
You can run `sudo /etc/init.d/data_cube_ui` to print information about available commands.

To instead access this service with `sudo service data_cube_ui [command]`, run the following commands:

```
systemctl daemon-reload
sudo service data_cube_ui start
```

You will need to select the user to authenticate as by entering a number,
and then finally enter the password for your user.

>### <a name="manual_install_remove_sudo"></a> Removing Sudo Access

To disallow sudo (or "admin" or "root") privileges for the UI user after installation, run the following command,
substituting your Linux user name for `localuser`:
```
sudo deluser localuser sudo
```

>### <a name="manual_install_celery_non_daemonized"></a> Running Celery Non-Daemonized (troubleshooting only)

If the above does not work, you may consider running Celery manually (non-daemonized). 
But only do this if you are sure that Celery is not functioning properly when daemonized.
Otherwise, skip this subsection. 

<!--For the current implementation, we use multiple worker instances - one for general task processing and one for the Data Cube manager functionality.--> 
<!--The Data Cube manager worker has a few specific parameters that make some of the database creation and deletion operations work a little more smoothly.-->

Open two new terminal sessions and activate the virtual environment in both.
We usually use `tmux` to handle multiple detached windows to run commands in the background. 
You can install `tmux` with the command `apt-get install tmux`. 
A reference is available [here](https://gist.github.com/MohamedAlaa/2961058).
For all terminals, ensure the virtual environment is activated and you are in the UI directory:

```
source ~/Datacube/datacube_env/bin/activate
cd ~/Datacube/data_cube_ui
```

In the first terminal, run the celery process with:

```
celery -A data_cube_ui worker -l info -c 4
```

In the second terminal, run the single-use Data Cube Manager queue.

```
celery -A data_cube_ui worker -l info -c 2 -Q data_cube_manager --max-tasks-per-child 1 -Ofair
```

Additionally, you can run both simultaneously using `celery multi`:

```
celery multi start -A data_cube_ui task_processing data_cube_manager -c:task_processing 10 -c:data_cube_manager 2 --max-tasks-per-child:data_cube_manager=1  -Q:data_cube_manager data_cube_manager -Ofair
```

To start the task scheduler, run the following command:

```
celery -A data_cube_ui beat
```

>## End of Manual Installation Instructions

## <a name="task_system_overview"></a> Task System Overview
-------

The task system can seem complex at first, but the basic workflow is shown below:

* The Django view receives form data from the web page. 
  This form data is processed into a Query model for the application
* The main Celery worker receives a task with a Query model and pulls all of the 
  required parameters from this model
* Using predefined chunking options, the main Celery task splits the parameters 
  (latitude, longitude, time) into smaller chunks
* These smaller chunks of (latitude, longitude, time) are sent off to the Celery 
  worker processes - there should be more worker processes than master processes
* The Celery worker processes load in the data in the parameters they received 
  and perform some analysis. The results are saved to disk and the paths are returned
* The master process waits until all chunks have been processed then loads all 
  of the result chunks. The chunks are combined into a single product and saved 
  to disk
* The master process uses the data product to create images and data products 
  and saves them to disk, deleting all the remnant chunk products
* The master process creates a Result and Metadata model based on what was just 
  created and returns the details to the browser

## <a name="customization"></a> Customize the UI
-------

To finish the configuration, we will need to create an area and product that you have ingested. 
For this section, we make a few assumptions:

* Your ingested product definition's name is `'ls7_ledaps_general'`.
* You have ingested a Landsat 7 scene.

First, we need to find the bounding box of your area. Open a Django Python 
shell and use the following commands:

```
source ~/Datacube/datacube_env/bin/activate
cd ~/Datacube/data_cube_ui
python manage.py shell

from utils.data_cube_utilities import data_access_api

dc = data_access_api.DataAccessApi()

dc.get_datacube_metadata('ls7_ledaps_general','LANDSAT_7')
```

Record the latitude and longitude extents.
They should be:

```
lat=(7.745543874267876, 9.617183768731897)
lon=(-3.5136704023069685, -1.4288602909212722)
```

Go back to the admin page, select `Dc_Algorithm -> Areas`, delete all of the 
initial areas, then click the 'Add Area' button.

Give the area an ID and a name.
For the Area ID, enter `general`, or whatever area you've named that is 
prepended by `ls7_ledaps_`. 
More generally, the Data Cube product name for your area must be the concatenation of 
`Dc_Algorithm -> Satellites -> [selected satellite] -> Product prefix` 
and the `Area` ID. For example, an `Area` with an `Id` of `general` should have 
a product with a name of `ls7_ledaps_general` for the satellite `LANDSAT_7`, or 
`ls8_lasrc_general` for the satellite `LANDSAT_8`. So the `Name` of an `Area` can be 
whatever you want, but the `Id` of an `Area` and names of the corresponding Data Cube 
products are constrained in this way.

Enter the latitude and longitude bounds in all of the latitude/longitude min/max fields 
for both the top and the detail fields.

For all of the imagery fields, enter `/static/assets/images/black.png` - this will give 
a black area preview, but will still contain the data we specify.

Select `LANDSAT_7` in the satellites field and save your new area.

Navigate back to the main admin page and select `Dc_Algorithm -> Applications`. 
Choose `custom_mosaic_tool` and select your area in the `Areas` field. 
Save the model and exit.

Go back to the main site and navigate back to the Custom Mosaic Tool. 
You will see that your area is the only one in the list - select this area to 
load the tool. Make sure your workers are running and submit a task over the 
default time over some area and watch it complete. The web page should overlay 
an image result.


## <a name="maintenance"></a> Maintenance, Upgrades, and Debugging
-------

Upgrades can be pulled directly from our GitHub releases using Git. There are a 
few steps that will need to be taken to complete an upgrade from an earlier 
release version:

* Pull the code from our repository.
* Make and run the Django migrations with `python manage.py makemigrations && python manage.py migrate`. 
  We do not keep our migrations in Git so these are specific to your system.
* If we have added any new applications (found in the apps directory) then you'll 
  need to run the specific migration with `python manage.py makemigrations {app_name} && python manage.py migrate`
* If there are any new migrations, load the new initial values from our .json file with 
  `python manage.py loaddata db_backups/init_database.json`
* Now that your database is working, stop your existing Celery workers 
  (daemon and console) and run a test instance in the console with `celery -A data_cube_ui worker -l info`
* To test the current codebase for functionality, run `python manage.py runserver 0.0.0.0:8000`. 
  Any errors will be printed to the console - make any required updates.
* Restart Apache (`sudo service apache2 restart`) for changes to appear on the 
  live site and restart your Celery worker. Ensure that only one instance of the 
  worker is running.

Occasionally there may be some issues that need to be debugged. 
The general workflow is found below:

* Stop the daemon Celery process and start a console instance
* Run the task that is causing your error and observe the error message 
  in the console
* If there is a 500 http error or a Django error page, ensure that `DEBUG` 
  is set to `True` in `settings.py` and observe the error message in the logs 
  or the error page.
* Fix the error described by the message, restart apache, restart workers

If you are having trouble diagnosing issues with the UI, feel free to contact us 
with a description of the issue and all relevant logs or screenshots. To ensure 
that we are able to assist you quickly and efficiently, please verify that your 
server is running with `DEBUG = True` and your Celery worker process is running 
in the terminal with loglevel `info`.

It can be helpful when debugging to check the Celery logs, which by default are 
at `/var/log/celery`. 

<a name="next_steps"></ha> Next Steps
========  
Now that we have the UI setup, you are able to play with many of our algorithms, such as water detection, coastal change detection, and more.
You may also consider setting up a Jupyter Notebook server for accessing ODC. The notebooks repository is [here]().

<a name="faqs"></a> Common problems/FAQs
========   

If you daemonized the UI, the first thing to try when experiencing issues 
with the UI is to restart the UI: `sudo /etc/init.d/data_cube_ui restart` 
or `sudo service data_cube_ui restart`.

---

Q:
 >I’m getting a “Permission denied error.”  How do I fix this?  

A:  
>	More often than not the issue is caused by a lack of permissions on the 
>   folder where the application is located.  Grant full access to the folder 
>   and its subfolders and files (this can be done by using the command 
>   `chmod -R 777 FOLDER_NAME`).  

---

Q: 	
> I'm getting a "too many connections" error when I run a task in the UI, 
> such as
> ```org.postgresql.util.PSQLException: FATAL: sorry, too many clients already.```

A:  
> The Celery worker processes have opened too many connections for your database 
> setup. In `/var/lib/pgsql/data/postgresql.conf`, increase `max_connections` 
> and `shared_buffers` in an equal proportion. The `max_connections` setting 
> is the maximum number of concurrent connections to Postgres. Note that 
> every UI task can and often does make several connections to Postgres.
> Also set `kernel.shmmax` to a value slightly large than `shared_buffers`.
> Finally, run `sudo service postgresql restart`.
> If the settings are already suitable, then the celery workers may be opening 
> connections without closing them. To diagnose this issue, start the celery 
> workers with a concurrency of 1 (i.e. `-c 1`) and check to see what tasks are 
> opening postgres connections and not closing them. Ensure that you stop the 
> daemon process before creating the console Celery worker process.

---

Q:
> When running tasks, I receive errors like 
>`ValueError: No products match search terms {...}`.

A:
> First ensure the following is true:
> 1. The area has been added 
> to the app via the admin menu `Dc_Algorithm -> Applications -> [app_name]`.
> 1. The selected area is the desired area.  
> 1. The Data Cube product name abides by the naming constraints described in
> the section titled `Customize the UI` in this document.
> 1. The query extents overlap the Data Cube product for the selected satellite and area combination.
> 
> If these parameters really should be returning data, run `dc.load()` queries with 
> `python manage.py shell` in the top-level `data_cube_ui` directory with parameters 
> matching the ones in errors like this in your Celery log files.

---

Q: 	
>   My tasks won't run - there is an error produced and the UI creates an alert.

A:  
>	Start your celery worker in the terminal with debug mode turned on and `loglevel=info`. 
    Stop the daemon process if it is started to ensure that all tasks will be visible. 
    Run the task that is failing and observe any errors. 
    The terminal output will tell you what task caused the error and what the general problem is.

---

Q: 	
> Tasks don't start - when submitted on the UI, a progress bar is created but 
> there is never any progress.

A:  
> This state means that the Celery worker pool is not accepting your task. 
> Check your server to ensure that a celery worker process is running with 
> `ps aux | grep celery`. If there is a Celery worker running, check that 
> the `MASTER_NODE` setting is set in the `settings.py` file to point to 
> your server and that Celery is able to connect - if you are currently using 
> the daemon process, stop it and run the worker in the terminal.  

---

Q: 	
> I'm seeing some SQL-related errors in the Celery logs that prevent tasks from 
> running.

A:  
> Run the Django migrations to ensure that you have the latest database schemas. 
> If you have updated recently, ensure that you have a database table for each app. 
> If any are missing, run `python manage.py makemigrations {app_name}` followed 
> by `python manage.py migrate`.

---

Q:
 > How do I refresh the Data Cube Visualization tool?<br/>
 > My regions are not showing up in the Data Cube Visualization tool.

A:
 > Activate the Data Cube virtual environment:<br/>
 > `source ~/Datacube/datacube_env/bin/activate`<br/>
 > enter the Django console:<br/>
 > `cd ~/Datacube/data_cube_ui`<br/>
 > `python manage.py shell`<br/>
 > then run this function, which should update the cache:<br/>
 > `import apps.data_cube_manager.tasks as dcmt`<br/>
 > `dcmt.update_data_cube_details()`

---