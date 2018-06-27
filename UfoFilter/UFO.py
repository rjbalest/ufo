import Filter
import string

####################################################################
# UFO.py
#
# Author: Russell Balest
# E-mail: russell@balest.com
#
# Copyright (C) 2002 Russell Balest
# Copyright (C) 2003 Russell Balest
# Copyright (C) 2004 Russell Balest
# Copyright (C) 2005 Russell Balest
# Copyright (C) 2006 Russell Balest
#
# History:
#
# This context contains ufo runtime directives.
#
####################################################################


class Context ( Filter.Context ):
	def __init__(self, name=None, parent=None):
 	   	Filter.Context.__init__(self, name, parent)

                # Default log level set to error
		self.tagDefault('logLevel', "4")
		self.tagDefault('logToFile', "false")
		self.tagDefault('logToDb', "false")
		self.tagDefault('logLevelDb', "1")
                
	###########################################################
	#/////////////////////////////////////////////////////////#
	#          Code Templates below here:                     #
	#/////////////////////////////////////////////////////////#
	###########################################################

	#############################
	# Class Template
	#############################
	def CLASSTEMPLATE(self):
		c = r'''
@@@include(generated/@UCLASSNAME@_base.html)@@@
'''
		return c

	#############################
	# Class Base Template
	#############################
	def CLASSBASETEMPLATE(self):
		c = r'''
		<html>
		<body>
		<h1>@CLASSNAME@</h1>
		</body>
		</html>
		'''
		return c

	#############################
	# Container Template
	#############################
	def CONTAINERTEMPLATE(self):
		c = r'''
@@@include(generated/@UCLASSNAME@Container_base.html)@@@'''
		return c

	#############################
	# Container Base Template
	#############################
	def CONTAINERBASETEMPLATE(self):
		c = r'''
		'''
		return c
