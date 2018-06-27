import Filter

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

	def ATTRIBUTES(self):
		c = ""
		# Declare hidden varibles.
		c = c + "var $%s;\n\t" % 'oid'
		c = c + "var $%s;\n\t" % 'uid'
		c = c + "var $%s;\n\t" % 'gid'
		c = c + "var $%s;\n\t" % 'cid'
		for v in self.vars:
			c = c + v.declaration()
		return c

	def NUM_VIEWABLE_ATTRS(self):
		n = 0
		for v in self.vars:
			# TBD: Check visibility of var
			if v.visibility == True or v.visibility == 'read':
				n = n + 1
		return "%d" % (n)

	def METHOD_VISIBILITY(self):
		c = "var $visibility = array(\n\t"
		c = c + "'view' => 'public',\n\t"
		c = c + "'select' => 'public',\n\t"
		c = c + "'submit' => 'public',\n\t"
		c = c + "'edit' => 'public',\n\t"
		c = c + "'delete' => 'public',\n\t"
		c = c + "'add' => 'public',\n\t"
		c = c + "'control' => 'public'\n\t"
		c = c + ");\n"
		return c

	def GLOBALOBJECT(self):
		#return "@PREFIX@Globals"
		return "ufoGlobals"
	def DBOBJECT(self):
		#return "@PREFIX@Db"
		return "ufoDb"
	def SESSIONOBJECT(self):
		#return "@PREFIX@Session"
		return "ufoSession"
	def TABLENAME(self):
		return "@PREFIX@_%s" % self.className
	def INITIMPL(self):
		c = ""
		c = c + '$this->oid = "0";\n\t\t'
		c = c + '$this->uid = "0";\n\t\t'
		c = c + '$this->gid = "0";\n\t\t'
		c = c + '$this->cid = "0";\n\t\t'

		for v in self.vars:
			c = c + '$this->%s = "%s";\n\t\t' % (v.name, v.default)
		return c
		
	def SELECTIMPL(self):
		nvars = 3
		c = ""
 		c = c + "$query = \"SELECT id, uid, gid, cid";
		for v in self.vars:
			if v.type == 'collection':
				continue
			if nvars > 0:
				c = c + ", "
			nvars = nvars + 1
# let's handle the UNIX_TIMESTAMP conversion elsewhere
#			if v.type == 'date':
#				c = c + "UNIX_TIMESTAMP(%s) as %s" % (v.name,v.name)
#			else:
#				c = c + v.name

		c = c + " FROM @TABLENAME@ WHERE id=$oid\";"
		return c

	def IDENTIFIABLE_NAME_IMPL(self):
	       c = 'return "{$this->className}_{$this->oid}";'
	       return c

	def INITROWIMPL(self):
		i = ""
		c = ""
		c = c + "global $ufoGlobals;\n\t\t"
		c = c + "$this->oid = $row['id'];\n\t\t"
		c = c + "$this->uid = $row['uid'];\n\t\t"
		c = c + "$this->gid = $row['gid'];\n\t\t"
		c = c + "$this->cid = $row['cid'];\n\t\t"
		for v in self.vars:
			if v.select == 'multiple':
				c = c + "$%s = explode(':', $row['%s']);\n\t\t" % (v.name,v.name)
				c = c + "$this->%s =& array_combine($%s,$%s);\n\t\t" % (v.name,v.name,v.name)
			else:
				if v.type == 'date' or v.type == 'timestamp':
					c = c + "$this->%s = $ufoGlobals->unix_timestamp($row['%s']);\n\t\t" % (v.name,v.name)
				elif v.type == 'object':
					i = "global $@SESSIONOBJECT@;\n"
					c = c + "$this->%s =& $ufoSession->lookupContainer('%s',$row['%s']);\n\t\t" % (v.className, v.name, v.name)
				elif v.type == 'collection':
					for w in v.vars:
						if w.type == 'object':
							if w.className == self.className:
								containerName = self.atts.containerName
							else:
								ctx = self.getContext(w.name)
								containerName = ctx.atts.containerName
							c = c + "$this->%s = new @PREFIX@_%s(0);\n\t\t" % ( v.name, containerName )
							# check constraint type
							c = c + "$this->%s->selectByContainer($this->oid);\n\t\t" % ( v.name )
				else:
					c = c + "$this->%s = $row['%s'];\n\t\t" % (v.name,v.name)

		return i + c
	def COPYIMPL(self):
		c = ""
		for v in self.vars:
			c = c + "$this->%s = $obj->%s;\n\t\t" % (v.name, v.name)
		return c

	################################################################
	# This tag writes PHP functions which return enumeration values
	# or object references that are the options of a select list.
	################################################################
	def MENUOPTIONFUNCTIONS(self):
		c = ""
		for v in self.vars:
			if v.type == "enum":
				c = c + self.MENUOPTIONFUNCTIONS_ENUM(v)
			elif v.type == "object":
				c = c + self.MENUOPTIONFUNCTIONS_OBJECT(v)

		return c

	#######################################################
	#  Generate a PHP function that returns the options
	#  of a select list for object references.
	#######################################################
	def MENUOPTIONFUNCTIONS_OBJECT(self, v):
		c = ""
		# Get the container name of this object.
		ctx = self.getContext(v.name)
		containerName = ctx.atts.containerName

		if v.constraint.source == 'user':
			c = c + """
	function %sMenuOptions() {
		$c = "";
		$container = new %s_%s(0);
		$container->selectByUser();

		foreach ($container->items() as $item ) {
			$oid = $item->oid;
			$name = $item->identifiableName();
			if (!strcmp($this->%s->oid, $oid)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option value=\\"{$oid}\\" {$select}>{$name}</option>";
		}
		return $c;
	}
					\t""" % (v.name, self.table_prefix, containerName, v.name)

		elif v.constraint.source == 'group':
			print "GROUP CONSTRAINT"
			# Generate values from range function
			c = c + """
	function %sMenuOptions() {
		$c = "";
		for ($i=%s; $i<%s; $i += %s) {
			$v = "$i";
			if (!strcmp($this->%s, $v)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option name=\\"{$i}\\" {$select}>{$i}</option>";
		}
		return $c;
	}
					\t""" % (v.name, v.constraint.min, v.constraint.max, v.constraint.incr, v.name)
		elif v.constraint.source == 'container':
			print "CONTAINER CONSTRAINT"
			# Values are explicitly enumerated
			arrvals = ""
			comma = ""
			for i in v.constraint.values:
				arrvals = "%s%s'%s'" % (arrvals,comma,i)
				comma = ", "
				if v.select == 'multiple':
					c = c + """
	function %sMenuOptions() {
		$c = "";
		$values = array(%s);
		while (list($k,$v) = each($values)) {
			if (isset($this->%s[$v])) {
				$select = "checked";
			} else {
				$select = "";
			}
			$c .= "<input type=\\"checkbox\\" name=\\"ufo[%s][{$v}]\\" {$select}>{$v}<br>";
		}
		return $c;
	}
					\t""" % (v.name, arrvals, v.name, v.name)

				else:
					c = c + """
	function %sMenuOptions() {
		$c = "";
		$values = array(%s);
		while (list($k,$v) = each($values)) {
			if (!strcmp($this->%s, $v)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option name=\\"{$v}\\" {$select}>{$v}</option>";
		}
		return $c;
	}
					\t""" % (v.name, arrvals, v.name)
					
		else:
			 raise Exception("\n\n################################\n[%sMenuOptions] Unknown object constraint source: %s\n################################\n" % (v.name, v.constraint.source))

		return c

	#######################################################
	#  Generate a PHP function that returns the options
	#  of a select list for a particular enumeration type
	#######################################################
	def MENUOPTIONFUNCTIONS_ENUM(self, v):
		c = ""
		if v.constraint.source == 'table':
			c = c + """
	function %sMenuOptions() {
		$c = "";
		$query = "SELECT name FROM %s_%s";
		$result = mysql_query($query) or die("Query failed : " . mysql_error());
		while ($row = mysql_fetch_row($result)) {
			$v = $row[0];
			if (!strcmp($this->%s, $v)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option name=\\"{$v}\\" {$select}>{$v}</option>";
		}
		return $c;
	}
					\t""" % (v.name, self.table_prefix, v.constraint.table, v.name)

		elif v.constraint.source == 'range':
			# Generate values from range function
			c = c + """
	function %sMenuOptions() {
		$c = "";
		for ($i=%s; $i<%s; $i += %s) {
			$v = "$i";
			if (!strcmp($this->%s, $v)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option name=\\"{$i}\\" {$select}>{$i}</option>";
		}
		return $c;
	}
					\t""" % (v.name, v.constraint.min, v.constraint.max, v.constraint.incr, v.name)
		elif v.constraint.source == 'enumerated':
			# Values are explicitly enumerated
			arrvals = ""
			comma = ""
			for i in v.constraint.values:
				arrvals = "%s%s'%s'" % (arrvals,comma,i)
				comma = ", "
			if v.select == 'multiple':
				c = c + """
	function %sMenuOptions() {
		$c = "";
		$values = array(%s);
		while (list($k,$v) = each($values)) {
			if (isset($this->%s[$v])) {
				$select = "checked";
			} else {
				$select = "";
			}
			$c .= "<input type=\\"checkbox\\" name=\\"ufo[%s][{$v}]\\" {$select}>{$v}<br>";
		}
		return $c;
	}
					\t""" % (v.name, arrvals, v.name, v.name)

			else:
				c = c + """
	function %sMenuOptions() {
		$c = "";
		$values = array(%s);
		while (list($k,$v) = each($values)) {
			if (!strcmp($this->%s, $v)) {
				$select = "selected";
			} else {
				$select = "";
			}
			$c .= "<option name=\\"{$v}\\" {$select}>{$v}</option>";
		}
		return $c;
	}
					\t""" % (v.name, arrvals, v.name)
					
		else:
			 raise Exception("\n\n################################\n[%sMenuOptions] Unknown enumeration constraint source: %s\n################################\n" % v.name, v.constraint.source)

		return c

	def CREATETABLE(self):
		return self.persistenceDelegate.CREATETABLE()

	def EXEC_QUERY(self):
		return self.persistenceDelegate.EXEC_QUERY()

	def EXEC_FETCH_ASSOC(self):
		return self.persistenceDelegate.EXEC_FETCH_ASSOC()

	def EXEC_FREE_RESULT(self):
		return self.persistenceDelegate.EXEC_FREE_RESULT()

	def DBSEQNAME(self):
		return self.persistenceDelegate.replace('DBSEQNAME')

	def DELETESQL(self):
		return self.persistenceDelegate.deleteSql()

	def INSERTSQL(self):
		return self.persistenceDelegate.insertSql()

	def UPDATESQL(self):
		return self.persistenceDelegate.updateSql()

	def VALIDATEIMPL(self):
		c = ""
		return c

	def SUBMITIMPL(self):
		c = ""

		c = c + "if (isset($ufo['uid'])) { $this->uid = $ufo['uid']; }\n\t\t"
		c = c + "if (isset($ufo['gid'])) { $this->gid = $ufo['gid']; }\n\t\t"
		c = c + "if (isset($ufo['cid'])) { $this->cid = $ufo['cid']; }\n\t\t"

		for v in self.vars:
			if v.visibility == False or v.visibility == 'read':
				continue
			if v.type == 'bool':
				c = c + "if (isset($ufo['%s'])) { $this->%s = True; } else { $this->%s = False; }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'string':
				c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'int':
				c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'float':
				c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'date':
				c = c + "if (isset($ufo['%s'])) { $this->%s = $@GLOBALOBJECT@->unix_timestamp($ufo['%s']); }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'enum':
				if v.select == 'multiple':
					c = c + "if (isset($ufo['%s'])) { $this->%s = array_combine(array_keys($ufo[%s]),array_keys($ufo['%s'])); }\n\t\t" % (v.name, v.name, v.name, v.name)
				else:
					c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
			if v.type == 'object':
				if v.select == 'multiple':
					c = c + "if (isset($ufo['%s'])) { $this->%s = array_combine(array_keys($ufo[%s]),array_keys($ufo['%s'])); }\n\t\t" % (v.name, v.name, v.name, v.name)
				else:
					c = c + "if (isset($ufo['%s'])) { $this->%s = new %s_%s($ufo['%s']); }\n\t\t" % (v.name, v.name, self.atts.prefix, v.name, v.name)

		c = c + "$this->save();\n\t\t"
		c = c + "$this->readOnly = TRUE;\n"
		return c

	def TABLE_HEADERS(self):
		c = ""
		for v in self.vars:
			if v.visibility == False:
				continue
			c = c + '\n<td>\n'
 			c = c + v.text
			c = c + '\n</td>'
		return c

	def VIEWROIMPL(self):
		c = ""
		c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\" width=\\"50%\\">'
		for v in self.vars:
			if v.visibility == False or v.visibility == 'write':
				continue
			if v.type == 'object':
				c = c + '\" . $this->%s->view() . \"' % (v.name)
			else:
	 			c = c + v.viewRO()
		c = c + '\n</table>'
		c = c + '\n[<a href=\\"main.php?obj=%s&ufo[oid]={$this->oid}&method=edit\\">edit</a>]' % (self.className)
		return c

	def INITVIEWIMPL(self):
		c = ""
		if self.readOnly:
			return c

		c = c + '\n<form action=\\"main.php?obj=%s&method=submit&page=$page\\" method=\\"post\\">' % self.className
		c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\" width=\\"50%\\">'

		for v in self.vars:
			if v.visibility == False or v.visibility == 'read':
				continue
			# Variable knows how to present itself.
			if v.type == 'collection':
				continue
			c = c + v.formInput()
		c = c + '\n</table>'

		#c = c + '\n<input type=\\"hidden\\" name=\\"ufo[oid]\\" value=\\"{$this->oid}\\">'
		c = c + '\n<input type=\\"hidden\\" name=\\"ufo[gid]\\" value=\\"{$this->gid}\\">'
		c = c + '\n<input type=\\"hidden\\" name=\\"ufo[cid]\\" value=\\"{$this->cid}\\">'
		c = c + '\n<input type=\\"hidden\\" name=\\"method\\" value=\\"submit\\">'
		c = c + '\n<input type=\\"submit\\" name=\\"submit\\" value=\\"submit\\">'
		c = c + '\n</form>'
		return c

	def OBJECT_REF_INCLUDES(self):
		c = ""
		for v in self.vars:
			# Variable knows how to present itself.
			if v.type == 'collection':
				for w in v.vars:
					if w.type == 'object':
						# Include its container if it has one.
						# Special logic to include your own container.
						if w.className == self.className:
							containerName = self.atts.containerName
						else:
							print "Getting context %s" % w.name
							ctx = self.getContext(w.name)
							containerName = ctx.atts.containerName
						if containerName:
							c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,containerName)
						else:
							c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,w.className)
	
			if v.type == 'object':
				# Include its container if it has one.
				ctx = self.getContext(v.name)
				containerName = ctx.atts.containerName
				if containerName:
					c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,containerName)
				else:
					c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,v.className)
		return c

	def viewimplvars(self, vars):
		c = ""
		for v in vars:
			if v.visibility == False or v.visibility == 'read':
				continue
			# Variable knows how to present itself.
			if v.const == True:
				c = c + v.viewRO()
			else:
				c = c + v.formInput()
		return c

	def viewimplvars_td(self, vars):
		c = ""
		for v in vars:
			if v.visibility == False or v.visibility == 'write':
				continue
			# Variable knows how to present itself.
			if v.const == True:
				c = c + v.viewRO_td()
			else:
				c = c + v.formInput_td()
		return c

	def FACETS(self):
		c = ""
		lfirst = True
		for f in self.facets:
			if lfirst:
				c = c + "var $facets = array(\n\t"
				lfirst = False
			else:
				c = c + ","
			c = c + "'%s'" % f
		if not lfirst:
			c = c + ");"
		return c

	def SELECTOR(self):
		lfirst = True
		c = ""
		for f in self.facets:
			if lfirst:
				c = c + "var $selected = array(\n\t"
				lfirst = False
			else:
				c = c + ","
			c = c + "'%s' => False\n\t" % f
		if lfirst:
			c = "var $selected = False;"
		else:
			c = c + ");"
		return c


	# Here I'm writing an entire PHP method in triple quotes
	def SELECTMETHODS(self):
		c = """
	function SELECT($argv) {
		$c = "";
		if ( isset($argv['facet']) ) {
			$facet = $argv['facet'];
			$this->selected[$facet] = TRUE;
		} 
	}
		\t"""
		return c


	# Here I'm writing an entire PHP method in triple quotes
	def VIEWMETHODS(self):
		c = """
	function view_facet($argv) {
		global $@GLOBALOBJECT@;
		global $page;
		global $CHECKED;
		global $BOOLSTR;
		$c = "";
		if ($this->readOnly == TRUE) {
		$c = "
		@VIEWROIMPL@
		"; 
		} else {
		  if ($this->initialized == TRUE) {
		$c = "
		@VIEWIMPL@
		";
		  } else {
		$c = "
		@INITVIEWIMPL@
		";
		  }
		}
		return $c;
	}
		\t"""
		return c



	def VIEW_ROW_ROIMPL(self):
		c = ""
		for v in self.vars:
			if v.visibility == False or v.visibility == 'write':
				continue
 			c = c + v.viewRO_td()
		return c

	def INITVIEW_ROW_IMPL(self):
		c = ""
		return c

	def VIEW_ROW_IMPL(self):
		c = ""
		if self.readOnly:
			return c

		c = c + '\n<form action=\\"main.php?obj=%s&method=submit&page=$page\\" method=\\"post\\">' % self.className

		if len(self.facets):
			for f in self.facets.keys():

				c = c + "<tr><td>%s</td>\";\n" % (f)
				c = c + "if ($this->selected['%s']) {" % f
				c = c + "\n$c .= \"\n"
				c = c + self.viewimplvars_td(self.facets[f])
				c = c + "</tr>\";\n}\n $c .= \"\n"

		else:
			c = c + self.viewimplvars_td(self.vars)

		c = c + '\n<input type=\\"hidden\\" name=\\"ufo[oid]\\" value=\\"$this->oid\\">'
		c = c + '\n<input type=\\"hidden\\" name=\\"method\\" value=\\"submit\\">'
		c = c + '\n<input type=\\"submit\\" name=\\"submit\\" value=\\"submit\\">'
		c = c + '\n</form>'
		return c

	def VIEWIMPL(self):
		c = ""
		page = self.atts.containerName
		if self.readOnly:
			return c

		c = c + '\n<form action=\\"main.php?obj=%s&method=submit&page=%s\\" method=\\"post\\">' % (self.className, page)
		c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\" width=\\"50%\\">'

		if len(self.facets):
			for f in self.facets.keys():
				c = c + "\";\n"
				c = c + "if ($this->selected['%s']) {" % f
				c = c + "$LFACET=TRUE;\n"
				c = c + "\n$c .= \"\n"
				c = c + self.viewimplvars(self.facets[f])
				c = c + "\";\n}\n $c .= \"\n"
			
			c = c + "\";\n"
			c = c + "if ( ! $LFACET ) {"
			c = c + "\n$c .= \"\n"
			c = c + self.viewimplvars(self.vars)
			c = c + "\";\n}\n $c .= \"\n"

		else:
			c = c + self.viewimplvars(self.vars)

		c = c + '\n</table>'

		c = c + '\n<input type=\\"hidden\\" name=\\"ufo[oid]\\" value=\\"$this->oid\\">'
		c = c + '\n<input type=\\"hidden\\" name=\\"method\\" value=\\"submit\\">'
		c = c + '\n<input type=\\"submit\\" name=\\"submit\\" value=\\"submit\\">'
		c = c + '\n</form>'
		return c
		
	
