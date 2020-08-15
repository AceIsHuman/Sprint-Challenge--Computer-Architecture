#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) < 2:
  print('Please provide a path to a program file.')
  print('Usage:   python3 ls8.py [PATH_TO_FILE]')
  sys.exit(1)

cpu = CPU()
path = sys.argv[1]

cpu.load(path)
cpu.run()