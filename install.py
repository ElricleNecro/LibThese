#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import sys, os
import subprocess as s

if s.call(["python", "setup.py"] + sys.argv[1:]) != 0:
	raise RuntimeError()

if "--user" in sys.argv:
	install_dir = os.path.join(os.path.expanduser("~"), ".local/")
	s.call(["python", "setup.py", "install_data", "-d", install_dir])
else:
	s.call(["python", "setup.py", "install_data"])
