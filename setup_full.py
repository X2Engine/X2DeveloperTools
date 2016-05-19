#!/usr/bin/env python2.7
"""
Author: Jake Houser (jake@x2engine.com)
Date: 2016-05-11
"""

from __future__ import print_function

import os, sys, subprocess, x2util

def main(args):
	"""
	"""
	options = x2util.parse_arguments()
	if options.refresh == 1:
		x2util.refresh_database(options)
	
	x2util.install_gitdir(options)
	x2util.prep_installation(options)
	x2util.chset(options, {'D':'true'})
	x2util.initialize(options)
	x2util.rsync_live_to_gitdir(options)

if __name__ == "__main__":
	sys.exit(main(sys.argv))
