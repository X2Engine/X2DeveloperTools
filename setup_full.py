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
	
	#x2util.install_gitdir()
	#x2util.prep_installation()
	#x2util.chset()
	#x2util.initialize()

	print(options)

if __name__ == "__main__":
	sys.exit(main(sys.argv))
