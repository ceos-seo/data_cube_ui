Data Cube Jupyter Notebook Installation Guide
=================

This document will guide users through the process of installing and configuring our Jupyter notebook Data Cube examples. In this guide, you will be required to install packages (Python and system level) and start a webserver.

Contents
=================

  * [Introduction](#introduction)
  * [Prerequisites](#prerequisites)
  * [Installation Process](#installation_process)
  * [Configuration](#configuration)
  * [Using the Notebooks](#using_notebooks)
  * [Next Steps](#next_steps)
  * [Common problems/FAQs](#faqs)

<a name="introduction"></a> Introduction
========  
Jupyter notebooks are extremely useful as a learning tool and as an introductory use case for the Data Cube. Our Jupyter notebook examples include many of our algorithms and some basic introductory Data Cube API use tutorials. After we have installed all of the required packages, we will verify that our Data Cube installation is working correctly.  

<a name="prerequisites"></a> Prerequisites
========  

To run our Jupyter notebook examples, the following prerequisites must be complete:

* The full Data Cube Installation Guide must have been followed and completed. This includes:
  * You have a local user that is used to run the Data Cube commands/applications
  * You have a database user that is used to connect to your `datacube database`
  * The Data Cube is installed and you have successfully run `datacube system check`

<a name="installation_process"></a> Installation Process
========  

You will need to be in the virtual environment for this entire guide. If you have not done so, please run:

```
source ~/Datacube/datacube_env/bin/activate
```

The Notebook repository can be downloaded as follows:
```
cd ~/Datacube
git clone https://github.com/ceos-seo/data_cube_notebooks.git
cd data_cube_notebooks
git submodule init && git submodule update
```

Now install the following Python packages:

```
pip install folium hdmedians rasterstats seaborn sklearn scikit-image lcmap-pyccd==2017.6.8 jupyter
```

At the time of writing this document, the `ipython` package had a dependency issue.
Run the following command if the notebook server crashes.

```
pip install ipython==6.5.0
``` 

<a name="configuration"></a> Configuration
========  

The first step is to generate a notebook configuration file. Run the following commands:
<b>Note:</b> ensure that you're in the virtual environment. If not, activate it with `source ~/Datacube/datacube_env/bin/activate`

```
cd ~/Datacube/data_cube_notebooks
jupyter notebook --generate-config
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

Jupyter will create a configuration file in `~/.jupyter/jupyter_notebook_config.py`. Now set the password and edit the server details.  Remember this for future reference, you will need it later.

```
jupyter notebook password
```

Edit the generated configuration file (`~/.jupyter/jupyter_notebook_config.py`) to include relevant details. 
You'll need to find the following entries in the file:

```
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8080
```

Save the file and then run the notebook server with the following command.
If this fails with a permissions error (`OSError: [...] Permission denied [...]`),
run the command `export XDG_RUNTIME_DIR=""`.

```
cd ~/Datacube/data_cube_notebooks
jupyter notebook
```

Open a web browser and go to `localhost:8080` if your browser is running on the same machine as the server. 
Otherwise run `ifconfig` on the server to get its IP address and go to {ip}:8080. Once you successfully connect to the notebook server, you will be greeted with a password field. Enter the password from the previous step.

<a name="using_notebooks"></a> Using the Notebooks
========  

Now that your notebook server is running and the Data Cube is set up, you can run any of our examples.

Open the notebook titled `Data_Cube_API_Demo` and run through all of the cells using either the button on the toolbar or CTRL+Enter.

You'll see that a connection to the Data Cube is established, some metadata is listed, and some data is loaded and plotted. Further down the page, you'll see that we are also demonstrating our API that includes getting acquisition dates, scene metadata, and data.

<a name="next_steps"></a> Next Steps
========  

Now that we have the notebook server setup and our examples running, you are able to play with many of our algorithms and become more familiar with the Data Cube and accessing metadata and data. The next step is to set up our web based user interface. You can find that documentation [here](./ui_install.md).

<a name="faqs"></a> Common problems/FAQs
========  
----  

Q: 	
 >I’m having trouble connecting to my notebook server from another computer.

A:  
>	There can be a variety of problems that can cause this issue. Check your notebook configuration file, your network settings, and your firewall settings.

---
