import Filter
import string

####################################################################
# UfoFilter.py
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
# * Jun 2006: Bindings to Javascript/Dojo
# * Nov 2005: Support for Postgres database.
# * May 2002: Implementation of PHP Context with MySql support.
#
# The UFO Tag Functions contained herein, in conjunction with the 
# associated UFO Templates, are an application of the Ufo 
# Filter mechanism for the purpose of generating the source code for
# persistent classes that comprise the elements of a web based object
# system that utilizes http as the communication mechanism.
#
# The current implementation supports generation of PHP code via the 
# PHPContext.
#
# The context can be configured to support MySql, Postgres, and PDO
# persistent layers.
#
####################################################################


class Context ( Filter.Context ):
	def __init__(self, atts=None, name=None, parent=None):
 	   	Filter.Context.__init__(self, name, parent)

		self.persistenceDelegate = atts.persistenceDelegate
		self.persistenceDelegate.setContext(self)		
		
		self.tagDefine('CLASSNAME', atts.className)
		self.tagDefine('CONTAINERNAME', atts.containerName)
		self.tagDefine('PREFIX', atts.prefix)
		self.vars = atts.vars
		self.facets = atts.facets
		self.owner = atts.owner
		self.className = atts.className
		self.table_prefix = atts.prefix
		self.oid = atts.oid
		self.readOnly = atts.readOnly
		self.atts = atts

	# Upper camel-case of classname
	def UCLASSNAME(self):
		classname = self.replace('CLASSNAME')
		uclassname = string.capwords(classname,'_')
		uclassname = string.replace(uclassname, '_', '')
		return uclassname

	# Upper camel-case of argument
	def UCCTYPE(self, ctype):
		uclassname = string.capwords(ctype,'_')
		uclassname = string.replace(uclassname, '_', '')
		return uclassname


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
