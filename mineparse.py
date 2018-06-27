#!/usr/bin/env python

import re
import sys
import os.path
import Filter
import string

import UfoFilter
from UfoFilter import *
import Balest

from xml.sax import make_parser, handler, parseString, saxutils

####################################################################
# parseUfo.py
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
# * May 2002: Working definition and implementation of UFO XML schema.
#
# The UFO XML schema defines an abstract object model which is 
# used to define an object relational mapping and generate 
# source code with database persistence in any languages and
# database combinations that are implemented.  Current implementations
# are PHP for the language, and Postgres, MySql, and PDO database
# layers.
#
####################################################################

class stringConstraint:
	def __init__(self, constraint):
		self.source = None
		self.value = None

		# parse the constraint string to determine the source
		# the possible constraint syntax choices are:
		#
		#   syntax                                interpretation
		#
		#   constraint="<email>|<phone>|<url>"    Named constraint
		#   constraint="/regex/"                  Regex constraint
		#
		# Named constraints can be any name.  The assumption is tht a corresponding
		# validation function for that name will exist at runtime.
		#
		rex = re.compile('(?P<named>[0-9a-zA-Z_]+)|(?P<regex>/.*/)')
		reo = rex.search(constraint)
		if not reo:
			print "Unrecognized string constraint [ %s ]" % constraint
			# Throw an error
			sys.exit(1)
		
		if reo.group('named'):
			self.source = 'named'
			self.value = reo.group('named')
			print "Got string named constraint: %s" % self.value
		elif reo.group('regex'):
			self.source = 'regex'
			self.value = reo.group('regex')
			print "Got string regex constraint: %s" % self.value
		else:
			print "Unknown string constraint type"
		
class enumConstraint:
	def __init__(self, constraint):
		self.source = None
		self.values = None
		self.min = None
		self.max = None
		self.incr = None
		self.table = None
		self.column = None
		
		# parse the constraint string to determine the source
		# the possible constraint syntax choices are:
		#
		#   syntax                                interpretation
		#
		#   constraint="range(min, max)"          Numerical range
		#   constraint="range(min, max, incr)"    Num. range w/incr
		#   constraint="named"                    Foreign key table
		#   constraint="named.subname"            F.K. table column
		#   constraint="(a,b,c)"                  Enumerated values
		#
		rex = re.compile('(?P<range>range)\((?P<min>[\-0-9]+),(?P<max>[\-0-9]+),?(?P<incr>[0-9]+)?\)|(?P<table>[a-zA-Z_]+)(.(?P<column>[a-zA-Z_]+))?|(?P<enumerated>\((?P<values>[a-zA-Z_0-9, -]+)\))')
		reo = rex.search(constraint)
		if reo.group('range'):
			self.source = 'range'
			self.min = reo.group('min') 
			self.max = reo.group('max')
			if reo.group('incr'):
				self.incr = reo.group('incr') 
			else:
				self.incr = "1"
		elif reo.group('table'):
			self.source = 'table'
			self.table = reo.group('table')
			if reo.group('column'):
				self.column = reo.group('column')
		elif reo.group('enumerated'):
			self.source = 'enumerated'
			s = reo.group('values')
			self.values = s.split(',')
		else:
			print "Unknown enumeration type"

class objectConstraint:
	def __init__(self, constraint):
		self.source = constraint

class UfoRef:
	def __init__(self, atts):
		self.atts = atts
		self.type = "strict"
		self.is_polymorphic = False
		self.initAttrs( atts )
		
	def initAttrs(self, atts):
		print "Initializing Reference ",
		if atts.has_key('type'):
			self.type = atts['type']
			if self.type == 'polymorphic':
				self.is_polymorphic = True
				self.repr = UfoVar({})
				self.repr.type = 'string'
				self.repr.width = 32
				
class UfoVar:
	def __init__(self, atts):
		self.atts = atts
		self.namespace = None
		self.name = ''
		self.type = ''
		self.doc= ''
		self.constraint = None
		self.className = None
		self.default = None
		self.persistence = True
		self.is_reference = False
		self.reference = None
		
		# This var might be inherited from a parent class.
		self.is_inherited = False
		
		# Possible values for visibility attr
		self.visibility_values = {}
		self.visibility_values['all'] = True
		self.visibility_values[None] = True
		self.visibility_values[''] = True
		self.visibility_values['True'] = True
		self.visibility_values['true'] = True
		self.visibility_values['none'] = False
		self.visibility_values['false'] = False
		self.visibility_values['False'] = False
		self.visibility_values['readOnly'] = 'read'
		self.visibility_values['writeOnly'] = 'write'

		# Possible values for mutable attr
		self.mutability_values = {}
		self.mutability_values[None] = True
		self.mutability_values[''] = True
		self.mutability_values['True'] = True
		self.mutability_values['true'] = True
		self.mutability_values['false'] = False
		self.mutability_values['False'] = False
		self.mutability_values['explicit'] = 'explicit'
		self.mutability_values['onInit'] = 'onInit'

		self.initAttrs(atts)

	def initAttrs(self, atts):
		if atts.has_key('name'):
			self.name = atts['name']
		if atts.has_key('type'):
			self.parseType( atts['type'] )
		if atts.has_key('label'):
			self.text = atts['label']
		else:
			self.text = self.name
		if atts.has_key('width'):
			self.width = atts['width']
		else:
			self.width = 20
		if atts.has_key('const'):
			self.const = True
		else:
			self.const = False
		if atts.has_key('transient'):
			self.transient = True
		else:
			self.transient = False
		if atts.has_key('visibility'):
			vis = atts['visibility']
			if self.visibility_values.has_key(vis):
				self.visibility = self.visibility_values[vis]
			else:
				print "Visibility string %s invalid" % vis
				sys.exit(1)
		else:
				self.visibility = self.visibility_values['all']			
		if atts.has_key('mutable'):
			mut = atts['mutable']
			if self.mutability_values.has_key(mut):
				self.mutable = self.mutability_values[mut]
			else:
				print "Mutability string %s invalid" % mut
				sys.exit(1)
		else:
				self.mutable = True			

		if atts.has_key('constraint'):
			if self.type == 'enum':
				self.constraint = enumConstraint( atts['constraint'] )
			elif self.type == 'string':
				self.constraint = stringConstraint( atts['constraint'] )
			elif self.type == 'object':
				self.constraint = objectConstraint( atts['constraint'] )
			elif self.type == 'date':
				self.constraint = atts['constraint']
			else:
				self.constraint = None
		else:
			self.constraint = None
		if atts.has_key('default'):
			self.default = atts['default']
		else:
			self.default = self.defaultDefault()
		if atts.has_key('select'):
			self.select = atts['select']
		else:
			self.select = None
		if atts.has_key('doc'):
			self.doc = atts['doc']

	def parseType(self, name):
		idx = string.rfind(name, '.')
		# print "idx of %s is: %d" % (name,idx)
		if idx > 0:
			self.namespace = name[:idx]
			self.type = name[idx+1:]
		else:
			self.type = name
		if self.type == 'object':
			self.default = "0"
	
	def defaultDefault(self):
		if self.type == 'int':
			self.default = '0'
		elif self.type == 'float':
			self.default = '0'
		elif self.type == 'currency':
			self.default = '0'
		elif self.type == 'bool':
			self.default = '0'
		elif self.type == 'date' or self.type == 'timestamp' or self.type == 'real_timestamp':
			self.default = 'null'
		else:
			self.default = ''

	def mysqlType(self):
		return "VARCHAR(%d)" % (self.width)

	def pgsqlType(self):
		return "text"


	def declaration(self):
		c = ""
		c = c + "$%s;\n\t" % self.name
		if self.is_reference:
			if self.reference.is_polymorphic:
				# Add a hidden variable
				c = c + "var $%s_class;\n\t" % self.name
		return c

	def documentation(self):
		c = ""
		t = ""
		if len(self.doc) > 0:
			if len(self.type) > 0:
				t = "\n\t * @var %s" % self.type
			c = c + """
	/**
	 * %s%s
	 */\n\t""" % (self.doc, t)
		return c

	def viewRO(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td  class=\\"label\\">%s:</td>' % self.text
		 c = c + self.viewRO_td()
		 c = c + '\n</tr>'
		 return c

	def viewRO_td(self):
		 c = ""
		 if self.type == "enum":
			if self.select == 'multiple':
				 c = c + '\n<td  class=\\"labelValue\\">\" . implode(\",\", array_keys($this->%s)) . \"</td>' % (self.name)
			else:
				 c = c + '\n<td  class=\\"labelValue\\">$this->%s </td>' % (self.name)
			return c	

		 if self.type == "date":
			 c = c + '\n<td  class=\\"labelValue\\">\" . $@GLOBALOBJECT@->human_from_mysql_timestamp($this->%s) . \"</td>' % (self.name)
			 return c	

		 if self.type == "timestamp":
			 c = c + '\n<td  class=\\"labelValue\\">\" . $@GLOBALOBJECT@->human_from_mysql_timestamp($this->%s) . \"</td>' % (self.name)
			 return c	

		 if self.type == "real_timestamp":
			 c = c + '\n<td  class=\\"labelValue\\">\" . $@GLOBALOBJECT@->human_from_mysql_timestamp($this->%s) . \"</td>' % (self.name)
			 return c	

		 if self.type == "bool":
			 c = c + '\n<td  class=\\"labelValue\\">{$BOOLSTR[$this->%s]} </td>' % (self.name)
			 return c
	
		 if self.type == "object":

			 if self.is_reference:
				 c = c + '\n<td  class=\\"labelValue\\">" . $this->get@UCCNAME(%s)@()->identifiableName() ."</td>' % (self.name)
				 return c

			 elif self.select == 'multiple':
			 	 c = c + '\n<td  class=\\"labelValue\\"><select>" . $this->get@UCCNAME(%s)@()->viewAsMenuOptions() ."</select></td>' % (self.name)


			 else:
				 c = c + '\n<td  class=\\"labelValue\\">" . $this->%s->link() ."</td>' % (self.name)
				 return c	
	
		 if self.type == "string":
			 c = c + '\n<td  class=\\"labelValue\\">$this->%s </td>' % (self.name)
			 return c	
	
		 if self.type == "blob":
			 c = c + '\n<td  class=\\"labelValue\\"><a href=\\"image.php?imageId={$this->oid}\\">%s</a></td>' % (self.name)
			 return c	

		 else:
			 c = c + '\n<td  class=\\"labelValue\\">$this->%s </td>' % (self.name)
			 return c	

	def formInput(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td class=\\"label\\">%s : </td>' % self.text
		 c = c + self.formInput_td()
		 c = c + '\n</tr>'

		 return c

	def formInput_td(self):
		 c = ""
		 if self.type == "enum":
			if self.select == 'multiple':
				c = c + '\n<td class=\\"labelValue\\">'
				c = c + '\" . $this->%sMenuOptions() . \"' % (self.name)	
				c = c + '\n</td>'
			else:
				c = c + '\n<td class=\\"labelValue\\">'
				c = c + '\n<select id=\\"%s\\" name=\\"ufo[%s]\\">' % (self.name, self.name)
				c = c + '\" . $this->%sMenuOptions() . \"' % (self.name)	
				c = c + '\n</select>'
				c = c + '\n</td>'
			return c

		 if self.type == "object":
			if self.select == 'multiple':
				c = c + '\n<td class=\\"labelValue\\">'
				c = c + '\" . $this->%sMenuOptions() . \"' % (self.name)	
				c = c + '\n</td>'
			else:
				c = c + '\n<td class=\\"labelValue\\">'
				c = c + '\n<select id=\\"%s\\" name=\\"ufo[%s]\\">' % (self.name, self.name)
				c = c + '\" . $this->%sMenuOptions() . \"' % (self.name)	
				c = c + '\n</select>'
				c = c + '\n</td>'
			return c

		 if self.type == "blob":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"file\\" name=\\"%s\\" value=\\"<filename>\\"</td>' % (self.name)
			 return c

		 if self.type == "bool":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"checkbox\\" name=\\"ufo[%s]\\" value=\\"1\\" {$CHECKED[$this->%s]}></td>' % (self.name, self.name)
			 return c

		 if self.type == "string":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "int":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "float":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "currency":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "date":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "timestamp":
			 c = c + '\n<td class=\\"labelValue\\"><input type=\\"text\\" name=\\"ufo[%s]\\" value=\\"$this->%s\\"></td>' % (self.name, self.name)
			 return c

		 if self.type == "real_timestamp":
			 c = c + '\n<td class=\\"labelValue\\">$this->%s</td>' % self.name
			 return c

		 else:
			 raise Exception("\n\n################################\n[formInput] Unknown type: %s\n################################\n" % self.type)


class UfoCollection(UfoVar):
	 def __init__(self, atts):
		 UfoVar.__init__(self,atts)
		 self.vars = []
		 self.type = 'collection'
		 self.initAttrs(atts)

	 def appendVar(self, var):
		 self.vars.append(var)
		 # Grab the attrs from the var if we don't have them
		 self.initAttrs(var.atts)
		 self.initAttrs(self.atts)		 
		 self.type = 'collection'

 	 def declaration(self):
		c = ""
		for v in self.vars:
			if v.is_reference:
				c = c + "$%s = array();\n\t" % v.name
			else:
				c = c + "$%s;\n\t" % v.name
		return c

	 def documentation(self):
		c = ""
		t = ""
		for v in self.vars:
			if len(self.doc) > 0:
				if len(self.type) > 0:
					if self.type == 'collection':
						t = "\n\t * @var object"
					else:
						t = "\n\t * @var %s" % self.type
				c = c + """
	/**
	 * %s%s
	 */\n\t""" % (self.doc, t)
		return c


 	 def viewRO(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td  class=\\"label\\">" . $this->get@UCCNAME(%s)@()->link() . "</td>' % self.name
		 c = c + self.viewRO_td()
		 c = c + '\n</tr>'
		 return c

	 def viewRO_td(self):
		 c = ""
		 for v in self.vars:
			 if v.type == "object":
			 	c = c + '\n<td  class=\\"labelValue\\"><select>" . $this->get@UCCNAME(%s)@()->viewAsMenuOptions() ."</select></td>' % (self.name)
		 return c	

	 def formInput(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td  class=\\"label\\">" . $this->get@UCCNAME(%s)@()->link() . "</td>' % self.name
		 c = c + self.viewRO_td()
		 c = c + '\n</tr>'
		 return c


	 def formInput_td(self):
		 return self.viewRO_td()


class UfoMethod(UfoVar):
         def __init__(self, atts):
		# since we handle the visibility attribute differently than
		# a normal UfoVar, let's keep UfoVar from choking on the one
		# we were given
		self.visibility_roles = ''
		vis = ''
		if atts.has_key('visibility'):
			vis = atts['visibility']
			del atts['visibility']
		else:
			vis = 'public'

		UfoVar.__init__(self,atts)
		self.atts = atts
		self.params = []
		self.type = 'method'

		# now do our custom visibility thing
		if vis:
			roles = []
			for role in vis.replace(' ', '').split(','):
				if self.isValidRole(role):
					roles.append(role)
			self.visibility_roles = ','.join(roles)

	 # TODO: implement proper validation
	 def isValidRole(self, role):
	 	return True

         def addParam(self, param):
                self.params.append(param)

         def declaration(self):
		c = ""
		args = ""
		for p in self.params:
			args = args + "\n\t * @param %s %s %s" % (p.type, p.name, p.doc)
		if len(self.doc) > 0 or len(args) > 0:
			c = c + """
	/**
	 * %s%s
	 */\n\t""" % (self.doc, args)
                c = c+ "var $%s;\n\t" % (self.name)
		return c


 	 def viewRO(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td  class=\\"label\\">" . $this->%s->link() . "</td>' % self.name
		 c = c + self.viewRO_td()
		 c = c + '\n</tr>'
		 return c

	 def viewRO_td(self):
		 c = ""
		 return c	

	 def formInput(self):
		 c = ""
		 c = c + '\n<tr>'
		 c = c + '\n<td  class=\\"label\\">" . $this->%s->link() . "</td>' % self.name
		 c = c + self.viewRO_td()
		 c = c + '\n</tr>'
		 return c


	 def formInput_td(self):
		 return self.viewRO_td()


class UfoMethodParam(UfoVar):
        def __init__(self, atts):
                UfoVar.__init__(self,atts)
                self.atts = atts
                self.initAttrs(atts)

	def initAttrs(self, atts):
		if atts.has_key('name'):
			self.name = atts['name']
		if atts.has_key('type'):
			self.type = atts['type']
		if atts.has_key('constraint'):
			if self.type == 'enum':
				self.constraint = enumConstraint( atts['constraint'] )
			elif self.type == 'object':
				self.constraint = objectConstraint( atts['constraint'] )
		else:
			self.constraint = None
		if atts.has_key('default'):
			self.default = atts['default']
		else:
			self.default = self.defaultDefault()




# --- The ContentHandler
class UfoGenerator(handler.ContentHandler):

     def __init__(self, persistenceDelegate, out = sys.stdout):
	 handler.ContentHandler.__init__(self)
	 self.persistenceDelegate = persistenceDelegate
	 self._out = out
	 self.oid = None
	 self.prefix = 'ufo'
	 self.className = ''

	 # List of ufos that this class contains
	 self.containedUfos = []
	 
	 # True means use the default persistenceDelegate:
	 self.persistence = True
	 self.linkname = None
	 self.containerName = None
	 self.owner = None
	 self.templateType = 'class'
	 self.vars = []
	 self.facets = {}
	 self.parent_classes = {}
	 self.extends = None
	 self.is_interface = None
	 self.namespaces = {}
	 self.in_facet = None
	 self.in_var = None
	 self.currentRef = None
	 self.currentVar = None
	 self.in_reference = False
	 self.in_collection = False
	 self.readOnly = False
	 self.version = '1.0'
	 self.enum = None
	 
	 # For nesting ufos
         self.in_import = False
         self.import_file = None
         self.import_name = None

         self.parent = self
         self.subcontexts = {}

	 self.tdir = 'Templates/'
	 self.odir = 'Output/'
	 self.odir_sql = 'Output/'
	 self.idir = '.'

     def storeVersion(self, file, lang='python'):
	     path = "%s/%s" % ( self.odir_sql, file )
	     versions = {}
	     # Store both as python and php serialized
	     if os.access( path, os.F_OK ):
		     versions = Balest.Load(path,lang)
	     versions[self.className] = self.version
	     if self.containerName:
		     versions[self.containerName] = self.version
		     # parse the directory path
		     d = os.path.dirname(file) 
		     self.storeContainer('%s/containers.ser' % (d), lang)
	     Balest.Store(path, versions, lang)

     def storeParentContainers(self, file, lang='python'):
	     ufodir = os.path.dirname( self.odir_sql )
	     path = "%s/%s" % ( ufodir, file )
	     parentContainers = {}
	     # Store both as python and php serialized
	     if os.access( path, os.F_OK ):
		     parentContainers = Balest.Load(path,lang)
	     cc = self.className
	     for ufo in self.containedUfos:
		     if parentContainers.has_key( ufo ):
			     pc = parentContainers[ufo]
			     if ( pc != cc ):
				     print "Warning: previous parent container of %s was %s but now is %s" % (ufo,pc,cc)
		     parentContainers[ufo] = cc
	     Balest.Store(path, parentContainers, lang)

     def storeContainer(self, file, lang):
	     path = "%s/%s" % ( self.odir_sql, file )
	     containers = {}
	     if os.access( path, os.F_OK ):
		     containers = Balest.Load(path,lang)
	     if self.containerName:
		     containers[self.className] = self.containerName
	     Balest.Store(path, containers, lang)
		     
     # Nested contexts access
     def getParent(self):
        """
        Return the parent context.
        """
        return self.parent

     def getContext(self, name):
        """
        Return the subcontext with the given name.
        """
        if self.parent.subcontexts.has_key(name):
            return self.parent.subcontexts[name]
        else:
            return None

     def addContext(self, context, name):
        """
        Add a context to the top level.
        """
	# Set the context's parent to my parent.
	context.parent = self.parent
        self.parent.subcontexts[name] = context


     # Accessors
     def setTemplateDir( self, path ):
	 self.tdir = path + '/'
     def setOutDir( self, path ):
	 self.odir = path + '/'
     def appendInDir( self, path ):
	 self.idir = path + '/'
     def setSqlOutDir( self, path ):
	 self.odir_sql = path + '/'

     def setPrefix( self, prefix ):
	 self.prefix = prefix

     # ContentHandler methods

     def startDocument(self):
	 self._out.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')

     def startElement(self, name, attrs):
	 if hasattr(self, 'start_' + name):
	     attr = getattr(self, 'start_' + name)
	     if callable(attr):
		 attr(dict(attrs))
	     else:
		 print "%s not callable" % attr
	 else:
	     print "Unknown element: %s" % name

	 #self._out.write('<' + name)
	 for (name, value) in attrs.items():
	     #self._out.write(' %s="%s"' % (name, saxutils.escape(value)))
	     None
	 #self._out.write('>')

     def endElement(self, name):
	 if hasattr(self, 'end_' + name):
	     attr = getattr(self, 'end_' + name)
	     if callable(attr):
		 attr()
	     else:
		 print "%s not callable" % attr
	 else:
	     print "Unknown element: %s" % name
	 #self._out.write('</%s>' % name)

     def appendVar(self, var):
	 if self.in_collection:
		 self.vars[len(self.vars)-1].appendVar(var)
	 else:
		 self.vars.append(var)
     def start_ufo(self, attrs):
	 None
     def end_ufo(self):
	 None
     def start_page(self, attrs):
	 None
     def end_page(self):
	 None
     
     # Enumeration class 
     def start_enum(self, attrs):
	     self.templateType = 'enum'
	     None

     def end_enum(self):
	     None
     def start_value(self, attrs):
	     None
     def end_value(self):
	     None

     def start_class(self, attrs):
	 self.className = attrs['name']
         self.templateType = 'class'

	 if attrs.has_key('version'):
		 self.version = attrs['version']


	 if attrs.has_key('linkname'):
		 self.linkname = attrs['linkname']

	 if attrs.has_key('parent'):
		 self.parent_classes[attrs['parent']] = True

	 if attrs.has_key('extends'):
		 self.extends = attrs['extends'];

	 if attrs.has_key('type'):
		 if attrs['type'] == 'interface':
			 self.is_interface = True

	 if attrs.has_key('persistence'):
		 self.persistence = attrs['persistence']

	 if attrs.has_key('prototype'):
		 self.templateType = attrs['prototype']

	 if attrs.has_key('enum'):
		 self.enum = attrs['enum']

	 if attrs.has_key('namespace'):
		 self.namespace = attrs['namespace']
	 else:
		 self.namespace = self.prefix
	 if attrs.has_key('oid'):
		 self.oid = attrs['oid']
	 else:
		 self.oid = 'foreign'
	 if attrs.has_key('readOnly'):
		 self.readOnly = True
	 else:
		 self.readOnly = False
	 if attrs.has_key('container'):
		 self.containerName = attrs['container']
		 if attrs.has_key('owner'):
			self.owner = attrs['owner']
	 else:
		 self.containerName = None

     def end_class(self):
	 if self.extends:
		 self.extend_from( self.extends )
 
     def start_import(self, attrs):
	 self.in_import = True
	 if attrs.has_key('file'):
	    	self.import_file = attrs['file']	 

     def end_import(self):
	 self.in_import = False
	 rootctx = self.parent
         if rootctx.getContext(self.import_name):
	 	return 
         newctx = UfoGenerator(self.persistenceDelegate, self._out)
	 newctx.appendInDir( self.idir )
	 rootctx.addContext(newctx, self.import_name)
	 parser = make_parser()
         parser.setContentHandler(newctx)
	 newfile = self.idir + self.import_file
         parser.parse(newfile)

         self.import_name = None
         self.import_file = None

     def extend_from( self, cname ):
	 rootctx = self.parent
         if rootctx.getContext(cname):
		 None
	 else:
		 print "Unknown base class %s. Did you import it?" % ( cname )
		 # FIXME: throw exception
		 sys.exit(1)
		 
         newctx = UfoGenerator(self.persistenceDelegate, self._out)
	 newctx.appendInDir( self.idir )
	 rootctx.addContext(newctx, cname)
	 parser = make_parser()
         parser.setContentHandler(newctx)
	 newfile = self.idir + cname + '.ufo'
         parser.parse(newfile)

	 # Absorb all this things attributes
	 for v in newctx.vars:
		 # Set inherited flag
		 v.is_inherited = True
		 self.appendVar(v)
	     
     def start_reference(self, attrs):
	 self.in_reference = True
	 self.currentRef = UfoRef( attrs )
     def end_reference(self):
	 self.in_reference = False
	 self.currentRef = None

     def start_parent(self, attrs):

	 if attrs.has_key('name'):
		 className = attrs['name']
	 else:
   		 raise "Required attribute 'name' missing in parent element"

	 self.parent_classes[className] = True

	 if attrs.has_key('namespace'):
		 namespace = attrs['namespace']
	 else:
   		 raise "Required attribute 'namespace' missing in parent element"
	 self.namespaces[namespace] = True

     def end_parent(self):
 	 None

     def start_facet(self, attrs):
	 if self.in_facet:
		print "Missing </facet> for facet: %s" % self.in_facet
		exit(1)
	 if attrs.has_key('name') :
		name = attrs['name']
		# Start a new list of vars in this facet.
		self.facets[name] = []
		self.in_facet = name
	 else:
		print "Facet requires name attribute"
		exit(1)
     def end_facet(self):
	 self.in_facet = None

     def start_collection(self, attrs):
	 var = UfoCollection(attrs)
	 print "Start Collection"
	 print var
     	 self.currentVar = var
	 self.appendVar(var)
	 self.in_collection = True
     def end_collection(self):
	print "End Collection"
        self.in_collection = False

     def start_var(self, attrs):
	self.in_var = True
	var = UfoVar(attrs)

	if self.in_reference:
		var.is_reference = True
		var.reference = self.currentRef
		
	if self.in_collection:
		self.currentVar.appendVar(var)
	else:
		self.currentVar = var
        	self.appendVar(var)
	if var.namespace:
		print "got namespace: %s" % var.namespace
		self.namespaces[var.namespace] = True

	if self.in_facet:
		self.facets[self.in_facet].append(var)

     def end_var(self):
	self.in_var = False
        None

     def start_method(self, attrs):
        method = UfoMethod(attrs)
        self.currentMethod = method
	self.visibility_roles = method.visibility_roles
        self.appendVar(method)
        self.in_method = True

     def end_method(self):
        self.in_method = False

     def start_param(self, attrs):
        param = UfoMethodParam(attrs)
        self.in_param = True

        if self.in_method:
                self.currentMethod.addParam(param)
        else:
                # do we want to add this param, or is skipping it okay?
                print "Warning: param '%s' appears outside a method definition; skipping" % param.name

     def end_param(self):
        self.in_param = False


     def characters(self, content):
	if self.in_var:
		if self.currentVar.type == 'object':
			self.currentVar.className = content
		elif  self.currentVar.type == 'collection':
			self.currentVar.vars[0].className = content
			if self.currentVar.vars[0].type == 'object':
				self.containedUfos.append( content )				
	elif self.in_import:
			self.import_name = content

     def ignorableWhitespace(self, content):
        #self._out.write(content)
        None
	
     def processingInstruction(self, target, data):
        self._out.write('<?%s %s?>' % (target, data))


     def generateCode(self, language, major=None, minor=None):
	if language == 'php':
		return self.generatePHP(major, minor)
	if language == 'perl':
		return self.generatePerl(major, minor)
	if language == 'javascript':
		return self.generateJavascript(major, minor)
	elif language == 'csharp':
		return self.generateCSharp()
	elif language == 'html':
		return self.generateHTML()
	elif language == 'dot':
		return self.generateDOT()
	else:
		print "%s bindings not implemented." % language

     def generateORMappings(self, language):
	if language == 'NHibernate':
		return self.generateNHibernate()
	else:
		print "%s bindings not implemented." % language


     def generateCSharp(self):
        """
        Generate CSharp class        
        """
        # turn over all our attrs
        ctx = UfoFilter.CSharpContext(self)

        tdir = 'Templates/'
        template = tdir + 'class.cs.T'
        outfile = tdir + '%s.%s.cs' % (self.namespace,self.className)
        Filter.Parser(template, outfile, ctx)

	# generate container if requested
	if self.containerName:
	        template = tdir + 'container.cs.T'
        	outfile = tdir + '%s_%s.cs' % (self.prefix,self.containerName)
        	Filter.Parser(template, outfile, ctx)

     def generatePHP(self, major, minor):
        """
        Generate PHP class        
        """
        # turn over all our attrs
	if major == '5':
	        ctx = UfoFilter.PHP5.Context(self)
		# Add sub-contexts
		for c in self.subcontexts:
			subctx = UfoFilter.PHP5.Context(self.subcontexts[c], c)
			ctx.addContext(subctx)
	else:
	        ctx = UfoFilter.PHP.Context(self)
		# Add sub-contexts
		for c in self.subcontexts:
			subctx = UfoFilter.PHP.Context(self.subcontexts[c], c)
			ctx.addContext(subctx)

	self.persistenceDelegate.setContext( ctx )

        tdir = self.tdir
	odir = self.odir

	# Generate User Class - but only if it's not there as either a .php or a .php.T file.
        template = tdir + 'ufo_' + self.templateType + '.T'
        outfile = odir + '%s_%s.php' % (self.prefix,self.className)
        outfileT = odir + '%s_%s.php.T' % (self.prefix,self.className)
	if not os.access(outfile, os.F_OK) and not os.access(outfileT, os.F_OK):
	        Filter.Parser(template, outfile, ctx)
	else:
		print "Will not overwrite %s" % outfile

	# Generate Base Class
        template = tdir + 'ufo_' + self.templateType + '_base.T'
        outfile = odir + '%s_%s_base.php' % (self.prefix,self.className)
        Filter.Parser(template, outfile, ctx)

	# generate container if requested
	if self.containerName:
	        template = tdir + 'ufo_container.T'
        	outfile = odir + '%s_%s.php' % (self.prefix,self.containerName)
        	outfileT = odir + '%s_%s.php.T' % (self.prefix,self.containerName)

		# Generate User Class - but only if it's not there as either a .php or a .php.T file.
		if not os.access(outfile, os.F_OK) and not os.access(outfileT, os.F_OK):
	        	Filter.Parser(template, outfile, ctx)
		else:
			print "Will not overwrite %s" % outfile

		# Generate Base Class
	        template = tdir + 'ufo_container_base.T'
        	outfile = odir + '%s_%s_base.php' % (self.prefix,self.containerName)
        	Filter.Parser(template, outfile, ctx)

	return ctx

     def generateJavascript(self, major=None, minor=None):
        """
        Generate Javascript class        
        """
        # turn over all our attrs
        ctx = UfoFilter.Javascript.Context(self)
	# Add sub-contexts
	for c in self.subcontexts:
		subctx = UfoFilter.Javascript.Context(self.subcontexts[c], c)
		ctx.addContext(subctx)

	# Probably want a remoting context instead.
	self.persistenceDelegate.setContext( ctx )


        tdir = self.tdir
	odir = self.odir

	uclassname = string.capwords(self.className, '_')
	uclassname = string.replace(uclassname, '_', '')

	# Generate User Class - but only if it's not there.
        template = tdir + 'ufo_' + self.templateType + '.T'
        outfile = odir + '%s.js.T' % (uclassname)
	if not os.access(outfile, os.F_OK):
	        Filter.Parser(template, outfile, ctx)
	else:
		print "Will not overwrite %s" % outfile

	# Generate Base Class - Disabled
        template = tdir + 'ufo_' + self.templateType + '_base.T'
        outfile = odir + 'generated/%s_base.js' % (uclassname)
        Filter.Parser(template, outfile, ctx)

	# generate container if requested
	if self.containerName:
	        template = tdir + 'ufo_container.T'
        	outfile = odir + '%sContainer.js.T' % (uclassname)

		# Generate User Class - but only if it's not there.
		if not os.access(outfile, os.F_OK):
	        	Filter.Parser(template, outfile, ctx)
		else:
			print "Will not overwrite %s" % outfile

		# Generate Base Class
	        template = tdir + 'ufo_container_base.T'
        	outfile = odir + 'generated/%sContainer_base.js' % (uclassname)
        	Filter.Parser(template, outfile, ctx)

	return ctx

     def generateHTML(self, major=None, minor=None):
        """
        Generate HTML documentation        
        """
	# Turn off persistence generating code
	self.persistence = False
	
        # turn over all our attrs
        ctx = UfoFilter.HTML.Context(self)
	# Add sub-contexts
	for c in self.subcontexts:
		subctx = UfoFilter.HTML.Context(self.subcontexts[c], c)
		ctx.addContext(subctx)

        tdir = self.tdir
	odir = self.odir

	uclassname = string.capwords(self.className, '_')
	uclassname = string.replace(uclassname, '_', '')

	# Generate User HTML - but only if it's not there.
        template = tdir + 'ufo_' + self.templateType + '.T'
        outfile = odir + '%s.html.T' % (uclassname)
	if not os.access(outfile, os.F_OK):
	        Filter.Parser(template, outfile, ctx)
	else:
		print "Will not overwrite %s" % outfile

	# Generate Base HTML
        template = tdir + 'ufo_' + self.templateType + '_base.T'
        outfile = odir + 'generated/%s_base.html' % (uclassname)
        Filter.Parser(template, outfile, ctx)

	return ctx

     def generateDOT(self, major=None, minor=None):
        """
        Generate DOT declarations
        """
	# Turn off persistence generating code
	self.persistence = False
	
        # turn over all our attrs
        ctx = UfoFilter.DOT.Context(self)
	# Add sub-contexts
	for c in self.subcontexts:
		subctx = UfoFilter.DOT.Context(self.subcontexts[c], c)
		ctx.addContext(subctx)

        tdir = self.tdir
	odir = self.odir

	uclassname = string.capwords(self.className, '_')
	uclassname = string.replace(uclassname, '_', '')

	# Generate User DOT - but only if it's not there.
        template = tdir + 'ufo_' + self.templateType + '.T'
        outfile = odir + '%s.dot.T' % (uclassname)
	if not os.access(outfile, os.F_OK):
	        Filter.Parser(template, outfile, ctx)
	else:
		print "Will not overwrite %s" % outfile

	# Generate Base DOT
        template = tdir + 'ufo_' + self.templateType + '_base.T'
        outfile = odir + 'generated/%s_base.dot' % (uclassname)
        Filter.Parser(template, outfile, ctx)

	return ctx

     def generateNHibernate(self):
        """
        Generate NHibernate mappings
        """
        # turn over all our attrs
        ctx = UfoFilter.NHibernateContext(self)
	self.persistenceDelegate.setContext( ctx )

        tdir = 'Templates/'
        template = tdir + 'nhibernate.hbm.xml.T'
        outfile = tdir + '%s_%s.hbm.xml' % (self.prefix,self.className)
        Filter.Parser(template, outfile, ctx)

     def generateSql(self, ctx):
        """
        Generate MySql SQL statements        
        """
	self.persistenceDelegate.setContext( ctx )

        tdir = self.tdir
	odir = self.odir_sql
        template = tdir + 'ufo_mysql.T'
        outfile = odir + '%s_%s.sql' % (self.prefix,self.className)
        Filter.Parser(template, outfile, ctx)

        
# --- The main program

# Parge Command Line arguments
# At least 5 arguments are required currently
if len(sys.argv) > 5:
	ufofile = sys.argv[1]
else:
	print "Usage: parseUfo.py <ufo> <outdir> <sqloutdir> <templatedir> <language> [<version>=1] [<sqldialect>='mysql'] [<sqlversion>=1] [prefix='ufo']"
	sys.exit(1)

if len(sys.argv) > 2:
	outdir = sys.argv[2]

if len(sys.argv) > 3:
	sqloutdir = sys.argv[3]

if len(sys.argv) > 4:
	templatedir = sys.argv[4]

if len(sys.argv) > 5:
	language = sys.argv[5]

if len(sys.argv) > 6:
	major = sys.argv[6]
else:
	major = "1"
	
if len(sys.argv) > 7:
	sqldialect = sys.argv[7]
else:
	sqldialect = "mysql"

if len(sys.argv) > 8:
	dbversion = sys.argv[8]
else:
	dbversion = "1"

if len(sys.argv) > 9:
	prefix = sys.argv[9]
else:
	prefix = 'ufo'

# The parser parses class templates.
parser = make_parser()

# Create a generator with default specified SQL dialect persistence.
ufo = UfoGenerator( UfoFilter.SQL.makeGenerator( sqldialect ) )
ufo.setPrefix(prefix)
ufo.setOutDir( outdir ) 
ufo.setSqlOutDir( sqloutdir ) 
ufo.setTemplateDir( templatedir )
ufo.appendInDir( os.path.dirname(ufofile) )

# ufo will transform the template as it is parsed.
parser.setContentHandler(ufo)
parser.parse(ufofile)

# Generate language classes with OR mappings.
langctx = ufo.generateCode( language, major )

# Store the version for ease of use later.
ufo.storeVersion('versions.ser')

# Store parentContainers for later use.
ufo.storeParentContainers('parentContainers.ser')

# Store it as php as well
# Not working yet ...
ufo.storeVersion('../../versions.ser', 'php')
ufo.storeParentContainers('../../parents.ser', 'php')

# Generate 3rd party OR mappings 
# ufo.generateORMappings( 'NHibernate' )

# Generate Sql statements for DB creation.
if ufo.persistence == True:
	ufo.generateSql(langctx)

