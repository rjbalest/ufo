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
		c = c + "'remove' => 'public',\n\t"
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
#			if v.type == 'date' or v.type == 'timestamp':
#				c = c + "UNIX_TIMESTAMP(%s) as %s" % (v.name,v.name)
#			else:
#				c = c + v.name
			c = c + v.name

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
		for (var $i=%s; $i<%s; $i += %s) {
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
		for (var $i=%s; $i<%s; $i += %s) {
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

	def UCLASSNAME(self):
		classname = self.replace('CLASSNAME')
		uclassname = string.capwords(classname,'_')
		uclassname = string.replace(uclassname, '_', '')
		return uclassname

	def UCCTYPE(self, ctype):
		uclassname = string.capwords(ctype,'_')
		uclassname = string.replace(uclassname, '_', '')
		return uclassname

	def UCONTAINERNAME(self):
		container = self.replace('CONTAINERNAME')
		ucontainer = string.capwords(container,'_')
		ucontainer = string.replace(ucontainer, '_', '')
		return ucontainer

	def IDENTIFIABLE_NAME_IMPL(self):
		return "unimplemented"

	def initCollection(self, name, ctype):
		c = ""
		# Map type ot camel-case
		uctype = string.capwords(ctype, '_')
		uctype = string.replace(uctype, '_', '')

		c = c + """
		if (obj.%s != null) {
			if (obj.%s.length == 0 ) {
				this.%s=[];
			} else if (!dojo.lang.isArray(obj.%s)) {
				this.%s=null;
			} else {
				if (this.%s==null) {
					this.%s=[];
				}
				for (var x=0; x<obj.%s.length; x++) {
					var tmp = new ambassador.data.%s(obj.%s[x]);
					tmp.setParent(this);
					this.%s.push(tmp);
				}
			}
		}
		
		""" % (name,name,name,name,name,name,name,name,uctype,name,name)
		return c


	# Utility function for getting any collection, remotely
	# if necessary.  Atomic refers to avoiding race conditions 
	# between 2 simultaneous reqquest for the same collection.
	def getCollection(self, name, ctype):
		c = ""
		uname = string.capwords(name,'_')
		ucname = string.replace(uname, '_', '')

		# Map type ot camel-case
		uctype = string.capwords(ctype,'_')
		uctype = string.replace(uctype, '_', '')

		c = c + """
	get%s : function(view) {
		if (!this["%s"]) {
			if (this.haveRequested%s==false) {
				var request = {
					obj: "@CLASSNAME@",
					method: "get%s",
					"ufo[oid]": this.oid
				};
				if(view) {
					for(var i = 0; i < view.length; i++) {
						request["ufo[view][" + view[i] + "]"] = true;
					}
				}
		
				dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
				dojo.io.bind({
					url: "api.php",
					preventCache: true,
					load: dojo.lang.hitch(this,function(type,data,e) {
						dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
						this.%s = [];
						if(data && data.data && data.data.items) {
							for (var x=0; x < data.data.items.length; x++) {
								var tmp = new ambassador.data.%s(data.data.items[x]);
								tmp.setParent(this);
								this.%s.push(tmp);
								ambassador.ObjectCache.updateObject(tmp); 
								}
						} else {
							var tmp = {};
							this.%s.push(tmp);
						}
						this.get%sDeferred.callback(this.%s);
					}),
					mimetype: "text/json",
					content: request
				});
				this.haveRequested%s=true;
			} 
		} else {
			if (this.get%sDeferred.fired==-1) {
				this.get%sDeferred.callback(this.%s);
			}
		}
		return this.get%sDeferred;
       	},""" % (ucname,name,ucname,ucname,name,uctype,name,name,ucname,name,ucname,ucname,ucname,name,ucname)
		return c



	# Utility function for getting an object by ref, remotely
	# if necessary.  Atomic refers to avoiding race conditions 
	# between 2 simultaneous reqquest for the same object.
	def getObject(self, name, ctype):
		c = ""
		uname = string.capwords(name,'_')
		ucname = string.replace(uname, '_', '')

		# Map type ot camel-case
		uctype = string.capwords(ctype,'_')
		uctype = string.replace(uctype, '_', '')

		c = c + """
	get%s : function(view) {
		if (!this["%s"]) {
			if (this.haveRequested%s==false) {
				var request = {
					obj: "@CLASSNAME@",
					method: "get%s",
					"ufo[oid]": this.oid
				};
				if(view) {
					for(var i = 0; i < view.length; i++) {
						request["ufo[view][" + view[i] + "]"] = true;
					}
				}

				dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
				dojo.io.bind({
					url: "api.php",
					preventCache: true,
					load: dojo.lang.hitch(this,function(type,data,e) {
						dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
						if(data && data.data) {
						        // FIXME: broken for polymorphic refs like generic Site.
							var tmp = new ambassador.data.%s(data.data);
							if (tmp.getOid() != "0"){
								this.%s = tmp;
							}
						}
						this.get%sDeferred.callback(this["%s"]);
					}),
					mimetype: "text/json",
					content: request
				});
				this.haveRequested%s=true;
			}
		} else {
			if (!dojo.lang.isObject(this["%s"])) {
				var uuid = "this.%s_class-" + this.%s;
				var tmp = ambassador.ObjectCache.getObject(uuid); //need to calculate the uuid there
				if (tmp) {
					this.%s=tmp;
				} else {
					this["%s"] = null;
					return this.get%s();
				}
			}
		}
		return this.get%sDeferred;
	},""" % (ucname,name,ucname,ucname,uctype,name,ucname,name,ucname,name,name,name,name,name,ucname,ucname)
		return c

	# Utility function for getting any collection, remotely
	# if necessary.
	def getCollectionOriginal(self, name, ctype):

		c = ""
		uname = string.capwords(name,'_')
		ucname = string.replace(uname, '_', '')

		# Map type ot camel-case
		uctype = string.capwords(ctype,'_')
		uctype = string.replace(uctype, '_', '')

		c = c + """
	get%s : function(view) {
		var deferred = new dojo.Deferred();
		if (this.%s==null) {
			var request = {
				obj: "@CLASSNAME@",
				method: "get%s",
				"ufo[oid]": this.oid
			};
			if(view) {
				for(var i = 0; i < view.length; i++) {
					request["ufo[view][" + view[i] + "]"] = true;
				}
			}
			dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
			dojo.io.bind({
				url: "api.php",
				preventCache: true,
				load: dojo.lang.hitch(this,function(type,data,e) {
					dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
					this.%s = [];
					if(data && data.data && data.data.items) {
						for (var x=0; x < data.data.items.length; x++) {
							var tmp = new ambassador.data.%s(data.data.items[x]);
							tmp.setParent(this);
							this.%s.push(tmp);
						}
					} else {
						var tmp = {};
						this.%s.push(tmp);
					}
					deferred.callback(this.%s);
				}),
				mimetype: "text/json",
				content: request
			});	
		} else {
			deferred.callback(this.%s);
		}
		return deferred;
	},""" % (ucname,name,ucname,name,uctype,name,name,name,name)
		return c

	# Utility function for adding an object to a collection,
	# creating it if necessary.
	def addToCollection(self, name, ctype):
		c = ""
		# variable name of the collection mapped to camel-case
		uname = string.capwords(name,'_')
		ucname = string.replace(uname, '_', '')

		# Map type ot camel-case
		uctype = string.capwords(ctype,'_')
		uctype = string.replace(uctype, '_', '')

		c = c + """
	// Add a new %s as a child of this @CLASSNAME@ or reparent an existing %s.
	// Return the newly added %s.
	add%s : function(obj) {
		if (obj) {
			obj.uid = this.uid;
			obj.gid = this.gid;
			obj.cid = this.oid;
			obj.setParent(this);
			if(!this.%s) {
				this.%s = [];
			}
			this.%s.push(obj);
		} else {
			obj = new ambassador.data.%s();
			obj.oid = "0";
			obj.uid = this.uid;
			obj.gid = this.gid;
			obj.cid = this.oid;
			obj.update();
			obj.setParent(this);
			if(!this.%s) {
				this.%s = [];
			}
			this.%s.push(obj);
		}
		this.dirty["%s"]=this.%s;
		this.get%sDeferred=new dojo.Deferred();
		return obj;
	},""" % (uctype,uctype,uctype,uctype,name,name,name,uctype,name,name,name,name,name,ucname)
		return c

	# Javascript Getter methods
	def GETTER_STATE(self):
		c = ""
		for v in self.vars:
			if v.type == 'collection' or (v.type == 'object' and v.is_reference) :
				# variable name of the collection mapped to camel-case
				uname = string.capwords(v.name,'_')
				ucname = string.replace(uname, '_', '')
				c = c + """
		this.get%sDeferred = new dojo.Deferred();
		this.haveRequested%s = false;
				""" % ( ucname, ucname )
		return c

	# Javascript Getter methods
	def GETTERS(self):
		c = ""
		for v in self.vars:
			if v.type == 'collection':
				ctype = v.vars[0].className
				c = c + self.getCollection(v.name, ctype)
			elif v.type == 'object' and v.is_reference:
				c = c + self.getObject(v.name, v.className)
			elif v.type != 'method':
				uname = string.capwords(v.name, '_')
				ucname = string.replace(uname, '_', '')
				c = c + """
	get%s: function() {
		return this.%s;
	},""" % (ucname, v.name)
		return c

	# Javascript Setter methods
	def SETTERS(self):
		c = ""
		for v in self.vars:
			uname = string.capwords(v.name, '_')
			ucname = string.replace(uname, '_', '')
			if v.type == 'object':
				if v.is_reference:
					if v.reference.is_polymorphic:
						c = c + """
	set%s: function(%s) {
		this.%s = %s;
		// Have to tell what classname this new thing has.
		this.dirty["%s_class"]=%s.className;
		this.dirty["%s"]=%s.oid;
		this.get%sDeferred.results[this.get%sDeferred.fired]=this.%s;
	},""" % (ucname, v.name, v.name, v.name, v.name, v.name, v.name,v.name, ucname, ucname,v.name)

					else:
						# Non polymorphic version
						c = c + """
	set%s: function(%s) {
		this.%s = %s;
		this.dirty["%s"]=%s.oid;
		this.get%sDeferred.results[this.get%sDeferred.fired]=this.%s;
	},""" % (ucname, v.name, v.name, v.name, v.name,v.name, ucname, ucname,v.name)

			elif v.type == 'blob':
					c = c + """
	set%sFormNode: function( formNode ) {
		this.%sFormNode = formNode;
	},""" % (ucname, v.name )

			elif v.type == 'blob':
					c = c + """
	set%sFormNode: function( formNode ) {
		this.%sFormNode = formNode;
	},""" % (ucname, v.name )
				
				
			elif v.type != 'method':
				c = c + """
	set%s: function(%s) {
		if (this.%s != %s) {
			this.%s = %s;
			this.dirty["%s"]=%s;
		}
	},""" % (ucname, v.name, v.name, v.name, v.name, v.name, v.name, v.name)
		return c 

	# Javascript Adder methods
	def ADDERS(self):
		c = ""
		for v in self.vars:
			if v.type == 'collection':
				ctype = v.vars[0].className
				c = c + self.addToCollection(v.name, ctype)
		return c

	# User methods (specified in .ufo schemas)
	def USERMETHODS(self):
		c = ""
		for v in self.vars:
			if v.type == 'method':
				params=""
				for p in v.params:
					if len(params) > 0:
						params = params + ', '
					if len(p.type) > 0:
						params = params + "/* %s */ " % p.type
					params = params + p.name
				if len(v.doc) > 0:
					c = c + """
	/**
	 * %s
	 */""" % v.doc
				c = c + """
	%s: function(%s) {
		// implement %s here
	},\n\t""" % (v.name, params, v.name)
		return c 

	# Constructor/update implementation
	def INIT_FROM_OBJECT(self, obj):
		c = ""
		for v in self.vars:
			if v.type == 'collection':
				ctype = v.vars[0].className
				c = c + self.initCollection(v.name,ctype)

			elif v.type == 'object':
				if v.is_reference:
					if v.reference.is_polymorphic:
						c = c + 'if(!this.dirty["%s"]){this.%s_class = %s.%s_class;}\n\t\t' % (v.name,v.name,obj,v.name)
					else:
						None
				else:
					# Non-reference object
					c = c + "this.%s.onUpdate(%s.%s);\n\t\t" % (v.name,obj,v.name)
			
			elif v.type == 'date':
				c = c + 'if(!this.dirty["%s"] && %s.%s != null && %s.%s > 0){this.%s = new Date(%s.%s * 1000);}\n\t\t' % (v.name,obj,v.name,obj,v.name,v.name,obj,v.name)
			elif v.type != 'method':
				c = c + 'if(!this.dirty["%s"]){this.%s = %s.%s;}\n\t\t' % (v.name,v.name,obj,v.name)
		return c

	# used in object updates to clear dirty content
	def UPDATE_DIRTY(self):
		c = ""
		for v in self.vars:
			if v.type == 'object':
				if v.is_reference:
					None
				else:
					# Non-reference object
					c = c + "if(this.%s){this.%s._updateInFlight=true;this.%s.dirty=[];}" % (v.name,v.name,v.name)
		return c

	# Constructor implementation
	def INIT_TO_DEFAULTS(self):
		c = ""
		for v in self.vars:
			if v.default:
				default = v.default
			else:
				default = ""
			if v.type == 'collection':
				c = c + 'this.%s = null;\n\t' % (v.name)
			elif v.type == 'object':
				if v.is_reference:
					None
				else:
					c = c + 'this.%s = new ambassador.data.@UCCTYPE(%s)@();\n\t' % (v.name, v.className)
			elif v.type == 'string':
				c = c + 'this.%s = "%s";\n\t' % (v.name, default)
			elif v.type == 'enum':
				c = c + 'this.%s = "%s";\n\t' % (v.name, default)
			elif v.type == 'date':
				c = c + 'this.%s = "%s";\n\t' % (v.name, default)
			elif v.type == 'bool':
				c = c + 'this.%s = %s;\n\t' % (v.name, default)
			elif v.type == 'blob':
				c = c + 'this.%sFormNode = %s;\n\t' % (v.name, 'null')				
			elif v.type != 'method':
				c = c + 'this.%s = "%s";\n\t' % (v.name, default)
		return c

	def REMOVE_URL(self):
		c = 'api.php'
		return c

	def UPDATE_BIND_FORM(self):
		# If this object contains binary data, offer the possibility to load it from a form
		c = ""
		for v in self.vars:
			if v.type == 'blob':
				c = c + "formNode: this.%sFormNode,\n\t\t\t" % ( v.name )
		return c
	
	def UPDATE_URL(self):
		c = 'api.php?method=submit'
		# ?obj=@CLASSNAME@&method=submit&ufo[oid]="+this.oid'
		for v in self.vars:
			None
			#c = c + '+"&ufo[%s]="+this.%s' % (v.name,v.name)
		return c

	def DIRTYCONTENTIMPL(self):

		c = 'var request = {};'

		c = c + '\n\t\trequest["ufo" + prefix + "[oid]"] = this.oid;'
		c = c + '\n\t\trequest["ufo" + prefix + "[uid]"] = this.uid;'
		c = c + '\n\t\trequest["ufo" + prefix + "[gid]"] = this.gid;'
		c = c + '\n\t\trequest["ufo" + prefix + "[cid]"] = this.cid;'

	        c = c + '''
		// Return dirty content from this object
		for (var key in this.dirty) {
			   request["ufo" + prefix + "[" + key + "]"] = this.dirty[key];
		}'''

		# Add dirty elements from nested object
		for v in self.vars:
			if v.type == 'object':
				if v.is_reference:
					None
				else:
					c = c + '''
		var dirty = this.%s.getDirtyContent(prefix + '[%s]');
		for (var key in dirty) {
			   request[key] = dirty[key];		    
		}
		''' % ( v.name, v.name )
					
		c = c +'\n\t\treturn request;'
		return c

	def ISDIRTYCONTENTIMPL(self):
		c = 'for (var k in this.dirty){return true;}'
		
		# Add dirty elements from nested object
		for v in self.vars:
			if v.type == 'object':
				if v.is_reference:
					None
				else:
					c = c + '''
		if (this.%s.isDirty()) { return true; }
		''' % ( v.name )
		
		c = c + 'return false;'
		return c

	def MAJORVERSION(self):
		(major,minor) = string.split(self.atts.version, '.')
		return major

	def MINORVERSION(self):
		(major,minor) = string.split(self.atts.version, '.')
		return minor

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
@@@include(generated/@UCLASSNAME@_base.js)@@@
'''
		return c

	#############################
	# Class Base Template
	#############################
	def CLASSBASETEMPLATE(self):
		c = r'''
dojo.provide("ambassador.data.@UCLASSNAME@");
dojo.require("dojo.Deferred");
dojo.require("dojo.lang.*");

ambassador.data.@UCLASSNAME@ = function(obj) {

	this.className = "@UCLASSNAME@";
	this.version = "@MAJORVERSION@.@MINORVERSION@";
	this.dirty = [];
	this._updateInFlight=false;
	
	this.oid = "0";
	this.uid = "0";
	this.cid = "0";
	this.gid = "0";
	this.uuid = "0";
	@INIT_TO_DEFAULTS@

	@GETTER_STATE@


	if (obj) {
		
		// not returning obj version yet.
		//this.version = obj.version;

		this.oid = obj.oid;
		this.uid = obj.uid;
		this.cid = obj.cid;
		this.gid = obj.gid;

		this.uuid = "@CLASSNAME@-" + this.oid;

		@INIT_FROM_OBJECT(obj)@
	}
}

dojo.lang.extend(ambassador.data.@UCLASSNAME@, {

	// This is the version of the object instance.
	getVersion: function() {
		var words = this.version.split(".");
		return { major : words[0], minor : words[1] };
	},

	// This is the version of the class itself.
	getClassVersion: function() {
		return { major : @MAJORVERSION@, minor : @MINORVERSION@ };
	},

	setParent: function(parent) {
		this.parent=parent;
	},

	getParent: function() {
		return this.parent;
	},

	getOid: function() {
		return this.oid;
	},

	getCid: function() {
		return this.cid;
	},

	getUid: function() {
		return this.uid;
	},

	getGid: function() {
		return this.gid;
	},

	// This will create the parameter list used in the
	// HTTP request analogous to those in a query string.
	getUpdateParams: function() {

		var parms = this.getDirtyContent();

		// Add the object and method to it:

		parms["obj"] = "@CLASSNAME@";
		// Moved straight onto the URL because of form collision.
		// parms["method"] = "submit";
		return parms;
	},

	// This will create the remove parameter list used in the
	// HTTP request analogous to those in a query string.
	getRemoveParams: function() {
		var parms = {};
		// Add the object and method to it:
		parms["obj"] = "@CLASSNAME@";
		parms["method"] = "delete";
		parms["ufo[oid]"] = this.oid;
		return parms;
	},

	// This will give a set of NV pairs representing
	// the state which is changed on the client side
	// and needs to be sent	back to the server.
	getDirtyContent: function( parent ) {
		var prefix = "";
		if (parent) {
			prefix = parent;
		}
		
		@DIRTYCONTENTIMPL@
	},
	
	isDirty: function(){
		@ISDIRTYCONTENTIMPL@
	},
	
	isUpdating: function(){
		return this._updateInFlight;
	},
	
	@GETTERS@
	@SETTERS@
	@ADDERS@
	@USERMETHODS@

	update: function() {
		this._updateInFlight=true;
		dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
		dojo.io.bind({
			url: "@UPDATE_URL@",
			method: "post",
			load: dojo.lang.hitch(this, this._onUpdate),
			error: dojo.lang.hitch(this, this.onUpdateError),
			mimetype: "text/json",
			preventCache: true,
			@UPDATE_BIND_FORM@content: this.getUpdateParams()
		});
		@UPDATE_DIRTY@
	    this.dirty=[];
	},

	onUpdate: function(obj) {
	    // receives just the data part of the json return string
		if ( this.oid == 0 ) {
		   this.oid = obj.oid;
		}
		
		this.uuid = "@CLASSNAME@-" + obj.oid;

		@INIT_FROM_OBJECT(obj)@
		
		// reset the dirty array.
		this._updateInFlight=false;
	},

	_onUpdate: function(type, data, e) {
		
		dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
		if (dj_undef("data", data)){
			dojo.debug("Error with object update return, dumping to screen.");
			dojo.debug("_onUpdate (type:" + type + ", res:" + data + ", e: " + e + ")");
			dojo.event.topic.publish("error, failed to save changes: " + e.responseText);
			return;
		}
		
	    // receives the full json return string
		this.onUpdate(data.data);
	},

	onUpdateError: function(e) {
		dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
		this._updateInFlight=false;
		dojo.event.topic.publish("error", "Error updating @UCLASSNAME@: " + e.message);
		dojo.debug("Error updating @UCLASSNAME@: " + e.message);
	},

	remove: function() {
		this._updateInFlight=true;
		dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
		dojo.io.bind({
			url: "@REMOVE_URL@",
			method: "post",
			load: dojo.lang.hitch(this, this._onRemove),
			error: dojo.lang.hitch(this, this.onRemoveError),
			mimetype: "text/json",
			preventCache: true,
			content: this.getRemoveParams()
		});
	},

	onRemove: function(obj) {
		this._updateInFlight=false;
	    // receives just the data part of the json return string
	},

	_onRemove: function(type, data, e) {
		dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
		if (dj_undef("data", data)){
			dojo.debug("Error with object remove return, dumping to screen.");
			dojo.debug("_onRemove (type:" + type + ", res:" + data + ", e: " + e + ")");
			dojo.event.topic.publish("error, failed to save changes: " + e.responseText);
			return;
		}
		
	    // receives the full json return string
	    dojo.debug("@UCLASSNAME@ Object " + this.oid + " remove"); 
		this.onRemove(data.data);
	},

	onRemoveError: function(e) {
		this._updateInFlight=false;
		dojo.debug("Error removing @UCLASSNAME@[" + this.oid + "]: " + e.message);
	},

	toString: function() {
		return "@UCLASSNAME@: " + " oid: " + this.oid;
	}

});
		'''
		return c

	#############################
	# Container Template
	#############################
	def CONTAINERTEMPLATE(self):
		c = r'''
@@@include(generated/@UCLASSNAME@Container_base.js)@@@'''
		return c

	#############################
	# Container Base Template
	#############################
	def CONTAINERBASETEMPLATE(self):
		c = r'''
dojo.provide("ambassador.data.@UCLASSNAME@Container");
dojo.require("ambassador.data.@UCLASSNAME@");

ambassador.data.@UCLASSNAME@Container = function() {

	this.@CONTAINERNAME@ = [];

}

dojo.lang.extend(ambassador.data.@UCLASSNAME@Container, {

	get@UCONTAINERNAME@: function(someQuery) {
		dojo.event.topic.publish("ambassador.loading", {state: "LOADING"});
		dojo.io.bind({
			url: "/main.php",
			load: dojo.lang.hitch(this,this.onGet@UCLASSNAME@),
			error: dojo.lang.hitch(this, this.onGetError),
			mimetype: "text/json",
			preventCache: true,
			content: someQuery
		});
	},

	onGet@UCONTAINERNAME@: function(type, data, e) {

		dojo.event.topic.publish("ambassador.loading", {state: "IDLE"});
		for (var @CLASSNAME@ in data) {
			var new@UCLASSNAME@ = new ambassador.data.@UCLASSNAME@(@CLASSNAME@);
			this.@CONTAINERNAME@.push(new@UCLASSNAME@);
		}
	}
});'''
		return c
