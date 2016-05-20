#!/usr/bin/env python2.7
"""
Author: Jake Houser (jake@x2engine.com)
Date: 2016-05-11
"""

from __future__ import print_function

import sys, os, argparse, subprocess, re

def parse_arguments():
	"""
	"""

	parser = argparse.ArgumentParser()
	
	parser.add_argument('command', choices = ['setup', 'rsync', 'reinstall', 'testing'], help = "Command to be run, corresponding to a series of actions related to installing or manipulating X2CRM installations")

	parser.add_argument('-g', '--gitdir', default = os.environ["GITDIR"], help = 'Direcory of your X2CRM Git Repository')
	parser.add_argument('-d', '--directory', default = os.environ["WORKINGDIR"], help = 'Directory of your working fileset for X2CRM')
	parser.add_argument('-u', '--mysqluser', default = os.environ["MYSQLUSER"], help = 'User with the ability to drop/create their own database')
	parser.add_argument('-p', '--mysqlpass', default = os.environ["MYSQLPASS"], help = "Password corresponding to the provided MySQL user")
	parser.add_argument('-m', '--database', default = os.environ["MYSQLDATABASE"], help = "Database name to use for installing X2CRM")
	parser.add_argument('-r', '--refresh', type=int, default=1, help = 'Toggles refreshing the existing database')
	parser.add_argument('-a', '--dummydata', type=int, default=1, help = 'Toggles including dummy data with the installation process')
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
		'-name', '[^t]*'], stdout=subprocess.PIPE)
	tailcmd = subprocess.Popen(['tail', '-n', '+2'], stdin=assetscmd.stdout, stdout=subprocess.PIPE)
	rmcmd = subprocess.check_call(['xargs', '-r', 'rm', '-r'], stdin=tailcmd.stdout)
	
	print('deleting directory '+options.directory)
	cmd = ['sudo', 'rsync', '-avc', '--delete', options.gitdir+'/', options.directory]
	subprocess.check_call(cmd)

	if options.installremote != 1:
		cmd = ['sudo', 'chown', '-R', '33', options.directory+'/X2CRM/x2engine']
		subprocess.check_call(cmd)
	else:
		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver, 'sudo', 'chown', '-R', options.remoteuser+':'+options.remoteuser, options.remotewebroot]
		subprocess.check_call(cmd)

		cmd = ['rsync', '-avzcO', '--delete', options.directory+'/X2CRM/x2engine/', 
			options.remoteuser+'@'+options.remoteserver+':'+options.remotewebroot]
		subprocess.check_call(cmd)

		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver, 'sudo', 'chown', '-R', '33', options.remotewebroot]
		subprocess.check_call(cmd)


def refresh_install_files(options):
	"""
	"""
	files = [
		'/initialize.php',
		'/initialize_pro.php',
		'/install.php',
		'/installConfig.php',
		'/webConfig.php',
	]

	for file in files:
		cmd = ['cp', options.gitdir+'/X2CRM/x2engine'+file, options.directory]
		subprocess.check_call(cmd)

	if options.installremote != 1:
		cmd = ['sudo', 'chown', '-R', '33', options.directory+'/X2CRM/x2engine']
		subprocess.check_call(cmd)
	else:
		cmd = ['ssh', options.remoteuser+'@'+options.remoteserver, 'sudo', 'chown', '-R', options.remoteuser+':'+options.remoteuser, options.remotewebroot]
		subprocess.check_call(cmd)

		for file in files:
			cmd = ['rsync', '-avzcO', options.directory+'/X2CRM/x2engine'+file, options.remoteuser+'@'+options.remoteserver+':'+options.remotewebroot]
			subprocess.check_call(cmd)

        cmd = ['ssh', options.remoteuser+'@'+options.remoteserver, 'sudo', 'chown', '-R', '33', options.remotewebroot]
        subprocess.check_call(cmd)


def prep_installation(options, testing=0):
	"""
	"""

	sedlist = [
		"s/host = 'localhost/host = '127.0.0.1/",
		"s/adminPassword = 'admin/adminPassword = '1/",
		"s/db=''/db='"+options.database+"'/",
		"s/user=''/user='"+options.mysqluser+"'/",
		"s/pass=''/pass='"+options.mysqlpass+"'/",
		"s/adminEmail = ''/adminEmail = '1\@1.com'/",
		"s/dummyData = 0/dummyData = "+str(options.dummydata)+"/"
	]
	if testing == 1:
		sedlist.append("s/test_db = 0/test_db = 1/")

	sedstr = ';'.join(sedlist)

	if options.installremote == 1:
		basecmd = ['ssh', options.remoteuser+'@'+options.remoteserver]
		sedstr = '"' + sedstr + '"'
		filepath = options.remotewebroot+'/installConfig.php'
	else:
		basecmd = []
		filepath = options.directory+'/X2CRM/x2engine/installConfig.php'
	
	subprocess.check_call(basecmd + ['sed', '-i', sedstr, filepath])

def chset(options, flags = {}):
	"""
	Flag values:
	d - Debug mode
	D - X2Dev mode
	u - Unit testing
	v - Pro/pla edition
	t - Test Debug level
	b - Partner branding
	f - Load fixtures for tests
	c - Load fixtures for class only
	s - Skip all unit tests
	"""
	flag_data = {
		'd': {
			'sedstr' : "s/YII_DEBUG',[:space:]*[a-zA-Z]+/YII_DEBUG',{value}/",
			'file' : '/constants.php'
		},
		'D': {
			'sedstr' : "s/X2_DEV_MODE',[:space:]*[a-zA-Z]+/X2_DEV_MODE',{value}/",
			'file' : '/constants.php'
		},
		'u': {
			'sedstr' : "s/YII_UNIT_TESTING',[:space:]*[a-zA-Z]+/YII_UNIT_TESTING',{value}/",
			'file' : '/constants.php'
		},
		'v' : {
			'sedstr' : "s/PRO_VERSION',[:space:]*[0-9]+/PRO_VERSION',{value}/",
			'file' : '/constants.php'
		},
		't' : {
			'sedstr' : "s/X2_TEST_DEBUG_LEVEL',[:space:]*[0-9]+/X2_TEST_DEBUG_LEVEL',{value}/",
			'file' : '/protected/tests/testconstants.php'
		},
		'b' : {
			'sedstr' : "s/BRANDING',[:space:]*[a-zA-Z]+/BRANDING',{value}/",
			'file' : '/protected/partner/branding_constants-custom.php'
		},
		'f' : {
			'sedstr' : "s/LOAD_FIXTURES',[:space:]*[a-zA-Z]+/LOAD_FIXTURES',{value}/",
			'file' : '/protected/tests/testconstants.php'
		},
		'c' : {
			'sedstr' : "s/LOAD_FIXTURES_FOR_CLASS_ONLY',[:space:]*[a-zA-Z]+/LOAD_FIXTURES_FOR_CLASS_ONLY',{value}/",
			'file' : '/protected/tests/testconstants.php'
		},
		's' : {
			'sedstr' : "s/X2_SKIP_ALL_TESTS',[:space:]*[a-zA-Z]+/X2_SKIP_ALL_TESTS',{value}/",
			'file' : '/protected/tests/testconstants.php'
		}
	}
	
	if options.installremote == 1:
		install_path = options.remotewebroot
		base_cmd = ['ssh', options.remoteuser+'@'+options.remoteserver]
	else:
		install_path = options.directory+'/X2CRM/x2engine'
		base_cmd = []
	for flag in flags:
		sedstr = flag_data[flag]['sedstr'].replace('{value}',str(flags[flag]))
		if options.installremote == 1:
			sedstr = sedstr.replace("'","\\'")
		file_path = install_path + flag_data[flag]['file']
		cmd = base_cmd + ['sed', '-i', '-r',  sedstr, file_path]
		subprocess.check_call(cmd)

def get_setting(options, flag):
	"""
	"""
	flag_data = {
		'd' : {
			'regex' : "YII_DEBUG',\s*(\w+)",
			'file' : '/constants.php',
		},
		'D' : {
			'regex' : "X2_DEV_MODE',\s*(\w+)",
			'file' : '/constants.php',
		},
		'u' : {
			'regex' : "YII_UNIT_TESTING',\s*(\w+)",
			'file' : '/constants.php'
		},
		'v' : {
			'regex' : "PRO_VERSION',\s*(\d+)",
			'file' : '/constants.php',
		},
		'b' : {
			'regex' : "BRANDING',\s*(\w+)",
			'file' : '/protected/partner/branding_constants-custom.php',
		},
		'f' : {
			'regex' : "LOAD_FIXTURES',\s*(\w+)",
			'file' : '/protected/tests/testconstants.php',
		},
		't' : {
			'regex' : "X2_TEST_DEBUG_LEVEL',\s*(\d+)",
			'file' : '/protected/tests/testconstants.php',
		},
		's' : {
			'regex' : "SKIP_ALL_TESTS',\s*(\w+)",
			'file' : '/protected/tests/testconstants.php'
		},
		'c' : {
			'regex' : "LOAD_FIXTURES_FOR_CLASS_ONLY',\s*(\w+)",
			'file' : '/protected/tests/testcontstants.php'
		},
	}

	if options.installremote == 1:
		base_cmd = ['ssh', options.remoteuser+'@'+options.remoteserver]
		install_path = options.remotewebroot
	else:
		base_cmd = []
		install_path = options.directory + '/X2CRM/x2engine'

	cmd = base_cmd + ['cat', install_path + flag_data[flag]['file']]
	ret = subprocess.check_output(cmd)

	match = re.search(flag_data[flag]['regex'], ret)
	if match:
		return match.group(1)


def initialize(options):
	"""
	"""
	if options.installremote == 1:
		base_cmd = ['ssh', options.remoteuser+'@'+options.remoteserver]
		file_path = options.remotewebroot
	else:
		base_cmd = []
		file_path = options.directory

	cmd = base_cmd + ['php', file_path+'/initialize.php', 'silent']
	subprocess.check_call(cmd)

def rsync_live_to_gitdir(options):
	"""
	"""

	old_u_val = get_setting(options, 'u')
	old_D_val = get_setting(options, 'D')
	old_d_val = get_setting(options, 'd')
	
	chset(options, {'u':'false', 'D': 'false', 'd':'false'})

	if options.installremote == 1:
		file_path = options.remoteuser+'@'+options.remoteserver+':'+options.remotewebroot+'/'
	else:
		file_path = options.directory+'/X2CRM/x2engine/'

	cmd = ['rsync', '-avczO','--delete', '--exclude-from', '.rsync_exclude', file_path, options.gitdir+'/X2CRM/x2engine/']
	subprocess.check_call(cmd)

	chset(options, {'u': old_u_val, 'D': old_D_val, 'd': old_d_val})


def run_setup_full(options):
	"""
	"""

	if options.refresh == 1:
		refresh_database(options)
	install_gitdir(options)
	chset(options, {'d':'true'})
	prep_installation(options, 0)
	initialize(options)

def run_rsync_live_to_gitdir(options):
	"""
	"""

	rsync_live_to_gitdir(options)

def run_reinstall(options):
	"""
	"""
	if options.refresh:
		refresh_database(options)

	refresh_install_files(options)
	chset(options, {'d':'true'})
	prep_installation(options,0)
	initialize(options)

def run_reinstall_for_testing(options):
	"""
	"""
	if options.refresh:
		refresh_database(options)

	refresh_install_files(options)
	prep_installation(options, 1)
	chset(options, {'u':'true', 'd':'true'})
	initialize(options)

def main(args):
	"""
	"""
	commands = {
		'setup' : run_setup_full,
		'rsync' : run_rsync_live_to_gitdir,
		'reinstall' : run_reinstall,
		'testing' : run_reinstall_for_testing,
	}
	options = parse_arguments()
	commands[options.command](options)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

