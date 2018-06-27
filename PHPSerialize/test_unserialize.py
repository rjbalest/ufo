#!/usr/bin/python
import sys, pprint
from PHPUnserialize import *

# Unserialize serialized data from STDIN

pp = pprint.PrettyPrinter()
try:
	data = sys.stdin.readline()
	#print data
	out = PHPUnserialize().unserialize(data)
	pp.pprint(out)	
except Exception, e:
	print e
