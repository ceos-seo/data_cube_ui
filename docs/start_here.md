


# Before Installation
#### configure user name
This document assumes that a local user, not an admin user, will be used to run all of the processes.  We use `localuser` as the user name, but it can be anything you want.  We recommend the use of `localuser` however as a considerable number of our configuration 
files assume the use of this name.  To use a different name may require the modification of several additional configuration files that otherwise would not need modification. Do not use special characters such as <b>è</b>, <b>Ä</b>, or <b>î</b> in this username 
as it can potentially cause issues in the future. We recommend an all-lowercase underscore-separated string.

#### configure user privelages 
The local user will need `sudo` privileges for the initial setup but you may want to remove the user from the `sudo` group after setup is completed. You can set up the OS with a single user and just use that as your local user if desired as well however. 

To simplify this process, instructions for setting up a local user can be found below.  As an admin user, execute the following.
```
sudo adduser localuser
```
After running through the user friendly prompts for the setup of that user, that user will need to be added to the `sudo` group.  You can use the following command:

```
sudo addgroup localuser sudo
```

Once added to the `sudo` group, that user is ready to be used in the setup of the Data Cube, Notebook Server, and UI Server.  To switch to that user conveniently use the command.

```
sudo su - localuser
```
You are now ready to begin the installation process as that local user.

## Installation Order

The first installation document that needs to be followed is:
<b>open_data_cube_install.md</b>

That document will guide the installation process for the Open Data Cube backend that will allow you to leverage the data cube from Open Data Cube Notebooks and the Open Data Cube UI.

Since the Open Data Cube Notebooks and the Open Data Cube UI both rely on data to be indexed into the PostgreSQL database at a minimum, it is a good idea to refer to the following documents as they cover indexing as well as ingestion.

---- 
<b>
ingestion.md<br>
ingestion_guide.md<br>
ingestion_guide_gpm.md<br>
ingestion_guide_gpm_stripped.md</b>
<br>  

---- 
Indexing and ingestion:  

- `Indexing`   refers to recording the locations of the data in the PostgreSQL database.<br>
- `ingestion` is a convenience which takes those data and creates a NetCDF formatted dataset that allows for the rapid loading of data.  NetCDF is a high-dimensional data format that the Open Data Cube can leverage. For more information on NetCDF see 
[here](https://www.unidata.ucar.edu/software/netcdf/docs/).
  
  
After data has been indexed, and possibly ingested, the user can begin the installation of one of the following analysis platforms:

## Open Data Cube Notebooks

The Jupyter Notebook platform is useful for performing custom analysis on GIS data.  The data will be loaded in [xarray](http://xarray.pydata.org/en/stable/) format and is compatible with a wide array of [Numpy](http://www.numpy.org/) operations. The Open Data 
Cube Notebooks are a flexible platform that allows the user to use several Python libraries to perform their analyses.  There are also several notebook examples that can help get the user started.  For installation, please see: <b>notebook_install.md</b>


## Open Data Cube User Interface
The User Interface, commonly referred to as the data cube UI, is a user-friendly platform that allows for quick selection of a region and simple analyses.  There are a variety of functions available from the UI.  For more information on the installation process 
of the UI please refer to: <b>ui_install.md</b>

To add additional algorithms to the UI please refer to: <b>adding_new_pages.md</b>
