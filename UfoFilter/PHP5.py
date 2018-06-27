import PHP

class Context ( PHP.Context ):
	def __init__(self, atts=None, name=None, parent=None):
 	   	PHP.Context.__init__(self, atts, name, parent)

	def PUBLIC(self):
		return "public"

	def PRIVATE(self):
		return "private"

	def PROTECTED(self):
		return "protected"

	def RETURN_BY_REFERENCE(self):
		return ""

	def PASS_BY_REF(self):
		return ""

	def ASSIGN_BY_REF(self):
		return "="

	# No f-chaining in PHP4
	def FCHAIN(self, var, strchain='food'):
		return "%s->%s" % ( var, strchain )

	# Use public private
	# Changed the name so this doesn't override php4
	def ATTRIBUTES_OVERRIDE(self):
		c = ""
		# Declare hidden varibles.
		c = c + "public $%s;\n\t" % 'oid'
		c = c + "public $%s;\n\t" % 'uid'
		c = c + "public $%s;\n\t" % 'gid'
		c = c + "public $%s;\n\t" % 'cid'
		for v in self.vars:
			c = c + v.documentation()
			c = c + "public " + v.declaration()
		return c
