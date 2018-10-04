# Before Installation

This document assumes that a local user, not an admin user, will be used to run all of the processes.  We use `localuser` as the user name, but it can be anything you want.  We recommend the use of `localuser` however as a considerable number of our configuration files assume the use of this name.  To use a different name may require the modification of several additional configuration files that otherwise would not need modification. Do not use special characters such as <b>è</b>, <b>Ä</b>, or <b>î</b> in this username as it can potentially cause issues in the future. We recommend an all-lowercase underscore-separated string.


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
