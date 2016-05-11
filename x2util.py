#!/usr/bin/env python2.7
"""
Author: Jake Houser (jake@x2engine.com)
Date: 2016-05-11
"""

import os, argparse, subprocess

def parse_arguments():
	"""
	"""

	parser = argparse.ArgumentParser()
	
	parser.add_argument('-g', '--gitdir', default = os.environ["GITDIR"], help = 'Direcory of your X2CRM Git Repository')
	parser.add_argument('-d', '--directory', default = os.environ["INSTALLEDDIR"], help = 'Directory of your X2CRM installation')
	parser.add_argument('-u', '--mysqluser', default = os.environ["MYSQLUSER"], help = 'User with the ability to drop/create their own database')
	parser.add_argument('-p', '--mysqlpass', default = os.environ["MYSQLPASS"], help = "Password corresponding to the provided MySQL user")
	parser.add_argument('-m', '--database', default = os.environ["MYSQLDATABASE"], help = "Database name to use for installing X2CRM")
	parser.add_argument('-r', '--refresh', type=int, default=1, help = 'Toggles refreshing the existing database')
	parser.add_argument('-i', '--installremote', type=int, default=os.environ["INSTALLREMOTE"], help = "Toggles installation to a remote server")
	parser.add_argument('-l', '--remoteuser', help = "Username to connect to the remote server with, only required with -i" )
	parser.add_argument('-s', '--remoteserver', help = "Remote hostname to connect to, only required iwith -i")

	args = parser.parse_args()
	
	if args.installremote == 1:
		if args.remoteuser is None:
			args.remoteuser = os.environ["REMOTEUSER"]
		if args.remoteserver is None:
			args.remoteserver = os.environ["REMOTESERVER"]

	return args

def refresh_database(options):
	"""
	"""
	cmd = ['mysql', '-u', options.mysqluser, '-p"'+options.mysqlpass+'"', '-e', 
		'"drop database if exists '+options.database+'; create database '+options.database+'"']

	if options.installremote:
		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver] + cmd
	
	try:
		ret = subprocess.check_output(cmd)
	except subprocess.CalledProcessError:
		pass
