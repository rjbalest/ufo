#!/usr/bin/python
import sys, pprint
from PHPUnserialize import *

# Unserialize serialized data from STDIN

pp = pprint.PrettyPrinter()
try:
	data = sys.stdin.readline()
	session = PHPUnserialize().session_decode(data)
	pp.pprint(session)	
except Exception, e:
	print e
