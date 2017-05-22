# X2CRM Developer Utilities
## Installation & Configuration
Clone the Git repository and either add the directory to your path
or copy both x2util and .x2util_rsync_exclude to a directory within
your path.

Futhermore, the following environment variables must be configured
or passed to x2util via command line options. A sample .bashrc file
has been provided with this repository.

GITDIR - The location of your X2CRM git repository (path up to but not including /X2CRM)

WORKINGDIR - The location of the files you will be developing on (path up to but not including /X2CRM)

MYSQLUSER - The username of your MySQL user. Must have permissions to create/drop their own database

MYSQLPASS - The password with the associated MySQL user

MYSQLDATABASE - The name of the MySQL database to install to

INSTALLREMOTE - 0 or 1, whether to install to a remote server. If 1, the next 3 options are required

REMOTEUSER - The username to connect to the remote server with

REMOTESERVER - The hostname of the remote server to connect to

REMOTEWEBROOT - The location of the webroot to install X2CRM to on the remote server

## Usage
Simply run "x2util [command]" where command is one of the options documented
in the help text for x2util. Run "x2util -h" for more information on the command
line options

## Developing in the Vagrant Environment
To simplify setup and configuration, a Vagrantfile has been provided. You will need to have [Vagrant](https://www.vagrantup.com/) installed with your chosen virtualization platform. VirtualBox is supported by default, and is both easy to use and available for Windows, OS X, and Linux.

Once you have Vagrant installed, fork and clone the X2CRM repo from [GitHub](https://github.com/X2Engine/X2CRM) into the developer tools directory. Then, create a new branch for your feature or fix, following a naming convention of "{name}\_{feature}". You can then bring up the Vagrant environment, perform your first setup, and begin developing!

```bash
local$ vagrant up
# Lots of output the first time this machine is brought up
local$ vagrant ssh
vagrant$ x2util setup
```

A new `workdir` directory will be created, which is synced to the virtual machines webroot at /var/www/html. You can edit the source code in your IDE from this directory to have the changes automatically propagated to your web server in the virtual machine. When you have finished developing your feature or fix, sync your changes back into the Git repo, commit and push the changes, then submit a pull request to the X2CRM repo.

```bash
vagrant$ x2util rsync
vagrant$ exit
local$ vagrant halt
local$ cd X2CRM
local$ git add -p
local$ git commit
local$ git push
```

A helper utility is provided within the Vagrant environment to simplify test execution. While writing your unit tests, you can execute them using the `x2test` command. Tab completion is provided for the files within the protected/tests directory. If no test is specified, the entire unit test suite will be executed.

```bash
vagrant$ x2test
# Executes the complete unit testing suite. This will take 30+ minutes, depending on hardware.
# Don't worry if you see the translation test fail, this is likely caused by the performance
# hit due to the synced directory.
vagrant$ x2test unit/components/X2IPAddressTest.php
# Executes a specific test
```

## Future Plans
* Add support for ignoring server-specific unit/functional testing configuration
* Rebuild additional existing scripts in python as we discover we need them
