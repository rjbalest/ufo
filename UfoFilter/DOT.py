import Filter
import string

####################################################################
# DOT.py
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
# * Dec 2006: Template for DOT output
#
# Summary:
#   Generate DOT output suitable for displaying a UML diagram of
#   classes and relationships
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


        # Emit the DOT node declaration for this context
        def declareNode(self):
            color = "gray"
            if self.atts.is_interface:
                color = "red"
            elif self.atts.extends:
                color = "yellow"
            c = """
        %s [
                 label = "{%s}"
                 fillcolor = "{%s}"
        ]
        """ % (self.className, self.className, color)
            return c

        # Emit the DOT edge declarations for this context
        def declareEdges(self):
            c = ""

            # If this class extends, show the inheritance
            if self.atts.extends:
                c = c + """
        edge [
                arrowhead = "normal"
                style = "solid"
                headlabel = ""
                taillabel = ""
        ]
        %s -> %s  [ color = "red" ]        
""" % ( self.className, self.atts.extends )
                
            for v in self.vars:
                if self.atts.extends and v.is_inherited:
                    continue
                elif v.type == 'collection':
                    w = v.vars[0]
                    if w.type == 'object':
                        c = c + """
        edge [
                arrowhead = "diamond"
                style = "solid"
                headlabel = ""
                taillabel = ""
        ]
        %s -> %s          
""" % ( self.className, w.className )

                elif v.type == 'object':
                    if v.is_reference:
                        c = c + """
        edge [
                arrowhead = "vee"
                style = "dashed"
                headlabel = ""
                taillabel = ""
        ]
        %s -> %s          
""" % ( self.className, v.className )                        
            return c
        
        # Main template for declaring all the nodes
        def NODES(self):
            c = ""
            # loop over all contexts
            for n in self.subcontexts.values():
                c = c + n.declareNode()
            return c

        # Main template for declaring all the edges
        def EDGES(self):
            c = ""
            # loop over all contexts
            for n in self.subcontexts.values():
                c = c + n.declareEdges()            
            return c
        
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
@@@include(generated/@UCLASSNAME@_base.dot)@@@
'''
		return c

	#############################
	# Class Base Template
	#############################
	def CLASSBASETEMPLATE(self):
		c = r'''
digraph G {
        fontname = "Bitstream Vera Sans"
        fontsize = 8

        node [
                fontname = "Bitstream Vera Sans"
                fontsize = 8
                shape = "record"
                style = "filled"
                
        ]

        edge [
                fontname = "Bitstream Vera Sans"
                fontsize = 8
        ]

        @NODES@
        @EDGES@
}                
		'''
		return c

	#############################
	# Container Template
	#############################
	def CONTAINERTEMPLATE(self):
		c = r'''
@@@include(generated/@UCLASSNAME@Container_base.dot)@@@'''
		return c

	#############################
	# Container Base Template
	#############################
	def CONTAINERBASETEMPLATE(self):
		c = r'''
		'''
		return c
