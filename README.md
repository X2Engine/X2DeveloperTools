#X2CRM Developer Utilities
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

## Future Plans
-Add support for ignoring server-specific unit/functional testing configuration

-Rebuild additional existing scripts in python as we discover we need them
