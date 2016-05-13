#!/usr/bin/env python2.7
"""
Author: Jake Houser (jake@x2engine.com)
Date: 2016-05-11
"""

from __future__ import print_function

import os, argparse, subprocess

def parse_arguments():
	"""
	"""

	parser = argparse.ArgumentParser()
	
	parser.add_argument('-g', '--gitdir', default = os.environ["GITDIR"], help = 'Direcory of your X2CRM Git Repository')
	parser.add_argument('-d', '--directory', default = os.environ["WORKINGDIR"], help = 'Directory of your working fileset for X2CRM')
	parser.add_argument('-u', '--mysqluser', default = os.environ["MYSQLUSER"], help = 'User with the ability to drop/create their own database')
	parser.add_argument('-p', '--mysqlpass', default = os.environ["MYSQLPASS"], help = "Password corresponding to the provided MySQL user")
	parser.add_argument('-m', '--database', default = os.environ["MYSQLDATABASE"], help = "Database name to use for installing X2CRM")
	parser.add_argument('-r', '--refresh', type=int, default=1, help = 'Toggles refreshing the existing database')
	parser.add_argument('-i', '--installremote', type=int, default=os.environ["INSTALLREMOTE"], help = "Toggles installation to a remote server")
	parser.add_argument('-l', '--remoteuser', help = "Username to connect to the remote server with, only required with -i" )
	parser.add_argument('-s', '--remoteserver', help = "Remote hostname to connect to, only required iwith -i")
	parser.add_argument('-w', '--remotewebroot', help = "Remote webroot where X2CRM is being deployed to")

	args = parser.parse_args()
	
	if args.installremote == 1:
		if args.remoteuser is None:
			args.remoteuser = os.environ["REMOTEUSER"]
		if args.remoteserver is None:
			args.remoteserver = os.environ["REMOTESERVER"]
		if args.remotewebroot is None:
			args.remotewebroot = os.environ["REMOTEWEBROOT"]

	return args

def refresh_database(options):
	"""
	"""
	cmd = ['mysql', '-u', options.mysqluser, '-p"'+options.mysqlpass+'"', '-e', 
		'"drop database if exists '+options.database+'; create database '+options.database+'"']

	if options.installremote == 1:
		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver] + cmd
	
	subprocess.check_call(cmd)

def install_gitdir(options):
	"""
	"""
	assetscmd = subprocess.Popen(['find', options.gitdir+'/X2CRM/x2engine/assets', '-maxdepth', '1', 
		'-name', "\'[^t]*\'"], stdout=subprocess.PIPE)
	tailcmd = subprocess.Popen(['tail', '-n', '+2'], stdin=assetscmd.stdout, stdout=subprocess.PIPE)
	rmcmd = subprocess.check_call(['xargs', '-r', 'rm'], stdin=tailcmd.stdout)
	
	print('deleting directory '+options.directory)
	cmd = ['sudo', 'rsync', '-avc', '--delete', options.gitdir+'/', options.directory]
	subprocess.check_call(cmd)

	if options.installremote != 1:
		cmd = ['sudo', 'chown', '-R', '33', options.directory+'/*']
		subprocess.check_call(cmd)
	else:
		cmd = ['rsync', '-avzcO', '--delete', options.directory+'/X2CRM/x2engine/', 
			options.remoteuser+'@'+options.remoteserver+':'+options.remotewebroot]
		subprocess.check_call(cmd)

		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver, 'sudo', 'chown', '-R', '33', options.remotewebroot+'/*']
		subprocess.check_call(cmd)


	
