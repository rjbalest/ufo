#!/usr/bin/python
from PHPSerialize import *
from test_data import data 
try:
	print PHPSerialize().serialize(data)
except Exception, e:
	print e

