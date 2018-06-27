#!/usr/bin/python
from PHPSerialize import *
from test_data import *
try:
	print PHPSerialize().session_encode(session)
except Exception, e:
	print e

