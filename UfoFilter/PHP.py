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

import string

class Context ( Filter.Context ):
        def __init__(self, atts=None, name=None, parent=None):
                Filter.Context.__init__(self, name, parent)

                if atts:
                        self.persistenceDelegate = atts.persistenceDelegate
                        self.persistenceDelegate.setContext(self)               
                
                        self.tagDefine('CLASSNAME', atts.className)
                        self.tagDefine('CONTAINERNAME', atts.containerName)
                        self.tagDefine('PREFIX', atts.prefix)
                        self.vars = atts.vars
                        self.indices = atts.indices
                        self.facets = atts.facets
                        self.owner = atts.owner
                        self.className = atts.className
                        self.table_prefix = atts.prefix
                        self.oid = atts.oid
                        self.readOnly = atts.readOnly
                        self.atts = atts

        # Only in PHP5
        def PUBLIC(self):
                return "var"

        # Only in PHP5
        def PRIVATE(self):
                return "var"

        # Only in PHP5
        def PROTECTED(self):
                return "var"

        # Only in PHP4
        def RETURN_BY_REFERENCE(self):
                return "&"

        # Only in PHP4
        def PASS_BY_REF(self):
                return "&"

        # Only in PHP4
        def ASSIGN_BY_REF(self):
                return "=&"

	# No f-chaining in PHP4
	def FCHAIN(self, var, strchain='food'):
		return "chain( %s, '%s' )" % ( var, strchain )
		
        
        def ATTRIBUTES(self):
                c = ""
                # Declare hidden varibles.
                c = c + "@PUBLIC@ $%s;\n\t" % 'oid'
                c = c + "@PUBLIC@ $%s;\n\t" % 'uid'
                c = c + "@PUBLIC@ $%s;\n\t" % 'gid'
                c = c + "@PUBLIC@ $%s;\n\t" % 'cid'
                
                if self.atts.is_interface:
                        # Declare hidden vptr
                        c = c + "@PUBLIC@ $%s;\n\t" % 'vptr_class'
                        c = c + "@PUBLIC@ $%s;\n\t" % 'vptr'

                        # Declare delegate
                        c = c + "@PROTECTED@ $%s;\n\t" % '_delegate'
                        
                        # Ignore out own attributes
                        return c
                
                if self.atts.extends:
                        # Add a metadata for the parent class id
                        c = c + "@PUBLIC@ $%s;\n\t" % 'pid'
                        
                # Inherit the base class attributes
                # assumed to have been done already.
                # and available in the list of vars.
                for v in self.vars:
                        c = c + "@PUBLIC@ " + v.declaration()

                return c

        # Turn a name into upper camel case.
        def UCCNAME(self, name):
                ucname = string.capwords( name, '_' )
                ucname = string.replace( ucname, '_', '')
                return ucname

        def APOSTROPHE(self):
                return "'"
        
        # For extends classes only define parent()
        def GETPARENT(self):
                c = ""
                if self.atts.extends:
                        parent = self.atts.extends
                        c = c + """
        function @RETURN_BY_REFERENCE@parent() {
                global $ufoSession;

                $oid = $this->pid;
                $parent @ASSIGN_BY_REF@ $ufoSession->lookupContainer('%s', $oid);
                return $parent;
        }
                        """ % ( parent )
                return c

        # For interface classes only define delegate()
        def GETDELEGATE(self):
                c = ""
                if self.atts.is_interface:
                        c = c + """
        function @RETURN_BY_REFERENCE@delegate() {
                global $ufoSession;
                if ( is_object($this->_delegate) ) {
                   return $this->_delegate;
                }
                $suboid = $this->vptr;
                $subclass = $this->vptr_class;
                $this->_delegate @ASSIGN_BY_REF@ $ufoSession->lookupContainer($subclass, $suboid);
                return $this->_delegate;
        }
                        """
                return c
                
                
        def CLASS_ACCESSORS(self):
                c = ""
                for v in self.vars:
                        if v.is_inherited:
                                containerKey = 'pid'
                        else:
                                containerKey = 'oid'
                        if v.type == 'collection':
                                w = v.vars[0]
                                if w.type == 'object':
                                        if w.className == self.className:
                                                containerName = self.atts.containerName
                                        else:
                                                ctx = self.getContext(w.className)
                                                containerName = ctx.atts.containerName
                                        ucname = string.capwords( v.name, '_' )
                                        ucname = string.replace( ucname, '_', '')
                                        c = c + """
        function @RETURN_BY_REFERENCE@get%s($argv=Null) {
                global $ufoEncoding;
                global $ufoSession;
                // A hack to be sure.  Look at the global obj and method being called
                // remotely to distinguish between a server side call to this method.
                global $method;
                global $obj;
                
                // The container id is this object's oid.
                $cid = $this->%s;
                $clname = '%s'; 
                $lobj = $ufoSession->lookupContainer($clname,-1,-1,$cid);
                $this->%s = $lobj;
                if ( $argv != Null && isset( $argv['view'] ) ) {
                    $lobj->setViewable( $argv['view'] );
                }
                // Here we detect that this method was the target of a client request
                // and set the obuffer appropriately.
                if ( $method == 'get%s' && $obj == '@CLASSNAME@') {
                    $this->obuffer = $lobj->view( $ufoEncoding );
                }
                return $this->%s;
        }  """ % (ucname,containerKey,containerName,v.name,ucname,v.name)

                        elif v.type == 'object':
                                ucname = string.capwords( v.name, '_' )
                                ucname = string.replace( ucname, '_', '')
                                className = "'%s'" % v.className
                                if v.is_reference:
                                        if v.reference.is_polymorphic:
                                                className = "$this->%s_class" % v.name
                                if not v.select == 'multiple':
                                        c = c + """
        function @RETURN_BY_REFERENCE@get%s($argv=Null) {
                global $ufoEncoding;
                global $ufoSession;
                // A hack to be sure.  Look at the global obj and method being called
                // remotely to distinguish between a server side call to this method.
                global $method;
                global $obj;
                
                // Check if it's an object or an object id.
                if ( is_object( $this->%s ) ) {
                   $lobj = $this->%s;
                } else {
                   $id = $this->%s;
                   $clname = %s;
                   $lobj = $ufoSession->lookupContainer($clname, $id);
                   $this->%s = $lobj;
                }
                if ( $argv != Null && isset( $argv['view'] ) ) {
                    $lobj->setViewable( $argv['view'] );
                }
                if ( $method == 'get%s' && $obj == '@CLASSNAME@') {
                    $this->obuffer = $lobj->view( $ufoEncoding );
                }
                return $this->%s;
        }  """ % (ucname,v.name,v.name,v.name,className,v.name,ucname,v.name)

                                elif v.select=="multiple":
                                        ctx = self.getContext(v.className)
                                        containerName = ctx.atts.containerName
                                        c = c + """
        function @RETURN_BY_REFERENCE@get%s($argv=Null) {
                global $ufoEncoding;
                global $ufoSession;
                // A hack to be sure.  Look at the global obj and method being called
                // remotely to distinguish between a server side call to this method.
                global $method;
                global $obj;
                
                // Check if an array of objects or object ids.
                if ( count($this->%s) && is_object( $this->%s[0] ) ) {
                   $lobj = $this->%s;
                } else {
                   $id = $this->%s;
                   $clname = '%s';
                   $lobj = $ufoSession->lookupContainer($clname, 0);
                   $oids = implode(',', $this->%s);
                   $lobj->select( array('oids' => $oids ) );
                   $this->%s = $lobj->items();
                }
                if ( $argv != Null && isset( $argv['view'] ) ) {
                    $lobj->setViewable( $argv['view'] );
                }
                if ( $method == 'get%s' && $obj == '@CLASSNAME@') {
                    $this->obuffer = $lobj->view( $ufoEncoding );
                }
                return $this->%s;
        }  """ % (ucname,v.name,v.name,v.name,v.name,containerName,v.name,v.name,ucname,v.name)

                                        
                return c

        def CLASS_SETTERS(self):
                c = ""
                for v in self.vars:
                        if v.is_inherited:
                                containerKey = 'pid'
                        else:
                                containerKey = 'oid'
                        if v.type == 'collection':
                                None
                                # For now at least.
                        elif v.type == 'object':
                                ucname = string.capwords( v.name, '_' )
                                ucname = string.replace( ucname, '_', '')
                                className = "'%s'" % v.className
                                if v.is_reference:
                                        if v.reference.is_polymorphic:
                                                # Nothing special
                                                None
                                        c = c + """
        function @RETURN_BY_REFERENCE@set%s($argv=Null) {
                global $ufoStatus;
                
                // Check if it's an object or an object id.
                if ( is_object( $argv ) ) {
                   $this->%s = $argv;
                } else {
                   // Error
                   // Too complicated due to polymorphic references.
                   $ufoStatus->invalid_parameter_type('Required argument is not an object');
                   return 0;
                }
                return $this->%s;
        }  """ % (ucname,v.name,v.name)
                                else:
                                        # Nonreference object.  Unimplemented but the intent
                                        # would be to make a copy of it but keep our oid the same.
                                        None
                                
                return c

        def NUM_VIEWABLE_ATTRS(self):
                n = 0
                for v in self.vars:
                        # TBD: Check visibility of var
                        if v.visibility == True or v.visibility == 'read':
                                n = n + 1
                return "%d" % (n)

        def GETCOLLECTIONNAMES(self):
                name = []
                names = ''
                c = ''
                for v in self.vars:
                        if v.type == 'collection':
                                w = v.vars[0]
                                if w.type == 'object':
                                        if w.className == self.className:
                                                containerName = self.atts.containerName
                                        else:
                                                ctx = self.getContext(w.className)
                                                containerName = ctx.atts.containerName
                                        name.append( '"' + containerName + '"' )

                names = string.join( name, ',')
                c = c + """
        function getCollectionNames($argv=Null) {
                $names = array(%s);
                return $names;
        }  """ % (names)
                return c

        def GETREFERENCENAMES(self):
                name = []
                names = ''
                c = ''
                for v in self.vars:
                        if v.type == 'object':
                                if v.is_reference == True:
                                        name.append( '"' + self.UCCNAME(v.name) + '"' )

                names = string.join( name, ',')
                c = c + """
        function getReferenceVarNames($argv=Null) {
                $names = array(%s);
                return $names;
        }  """ % (names)
                return c
                        
        def MEMBERS_VIEWABLE(self):
                # The way that objects are implemented is exactly like reference except by default
                # they are viewable, to express that they are an intrinsic part of their containing object.
                c = "$viewable = array("
                first = True
                for v in self.vars:
                        if v.type == 'object' and not v.is_reference and not v.select=='multiple':
                                if first:
                                        c = c + "'%s' => True" % v.name
                                        first = False
                                else:
                                        c = c + ",\n\t'%s' => True" % v.name
                c = c + ");\n"                                  
                return c
        
        def METHOD_VISIBILITY(self):
                c = "$visibility = array(\n\t"
                c = c + "'view' => 'session',\n\t"
                c = c + "'select' => 'session',\n\t"
                c = c + "'submit' => 'session',\n\t"
                c = c + "'edit' => 'session',\n\t"
                c = c + "'copy' => 'session',\n\t"
                c = c + "'delete' => 'admin',\n\t"
                c = c + "'add' => 'session',\n\t"
                c = c + "'control' => 'admin'"

                if self.atts.enum:
                        c = c + ",\n\t'%s' => '%s'" % ('getEnumValues', 'public')
                        
                for v in self.vars:
                        if v.type == 'method':
                                c = c + ",\n\t'%s' => '%s'" % (v.name, v.visibility_roles)
                        if v.type == 'collection':
                                w = v.vars[0]
                                if w.type == 'object':
                                        ucname = string.capwords( v.name, '_' )
                                        ucname = string.replace( ucname, '_', '')
                                        c = c + ",\n\t'get%s' => 'public'" % (ucname)
                        if v.type == 'object':
                                ucname = string.capwords( v.name, '_' )
                                ucname = string.replace( ucname, '_', '')
                                c = c + ",\n\t'get%s' => 'public'" % (ucname)

                c = c + "\n\t);\n"
                return c

        def GLOBALOBJECT(self):
                #return "@PREFIX@Globals"
                return "ufoGlobals"
        def DBOBJECTDECL(self):
                c = ""
                c = """
                global $ufoDbPool;
                $@DBOBJECT@ = $ufoDbPool->getInstance('@CLASSNAME@');
                """
                return c
        def DBOBJECT(self):
                #return "@PREFIX@Db"
                return "ufoDb"
        def SESSIONOBJECT(self):
                #return "@PREFIX@Session"
                return "ufoSession"
        def GETOBJECT(self, className, oid, cid=None, uid=None, gid=None):
                return "$@SESSIONOBJECT@->lookupContainer('%s', %s);" % ( className, oid )
        def ALLOCATEOBJECT(self, className):
                return "$@SESSIONOBJECT@->allocate('%s');" % ( className )
        def TABLENAME(self):
                return "@PREFIX@_%s" % self.className
	def ASSIGN_OID(self):
		c = ''
		if self.atts.oid != 'foreign':
			c = '''
                /* Get the auto increment Id of the last insert. */
                $this->oid = $@DBOBJECT@->insert_id("@DBSEQNAME@");'''
		else:
			c = ''
		return c
        def INITIMPL(self):
                c = ""
                c = c + 'global $@SESSIONOBJECT@, $@GLOBALOBJECT@;\n\t\t'
                c = c + '$this->oid = "0";\n\t\t'
                c = c + '$this->uid = "0";\n\t\t'
                c = c + '$this->gid = "0";\n\t\t'
                c = c + '$this->cid = "0";\n\t\t'

                if self.atts.extends:
                        c = c + '$this->pid = "0";\n\t\t'

                for v in self.vars:
                        if v.default != None:
                                if v.type == 'enum':
                                        deflt = """'%s'""" % v.default
                                        print "Default is: %s" % deflt
                                elif v.type == 'string':        
                                        deflt = """'%s'""" % v.default
                                elif v.type == 'date':
                                        deflt = """$@GLOBALOBJECT@->unix_timestamp('%s')""" % v.default
                                elif v.type == 'timestamp':
                                        deflt = """$@GLOBALOBJECT@->unix_timestamp('%s')""" % v.default
                                elif v.type == 'real_timestamp':
                                        None
                                else:
                                        deflt = '%s' % v.default
                        elif v.select == 'multiple':
                                deflt = 'array()';
                        else: 
                                if v.type == 'string':
                                        deflt = "Null" 
                                elif v.type == 'int':
                                        deflt = "0"
                                elif v.type == 'object':
                                        if v.is_reference:
                                                deflt = "0"
                                        else:
                                                deflt = "@ALLOCATEOBJECT(%s)@" % ( v.className )
                                elif v.type == 'bool':
                                        deflt = "false"
                                elif v.type == 'date':
                                        deflt = 'time()'                                        
                                elif v.type == 'timestamp':
                                        deflt = 'time()'
                                elif v.type == 'real_timestamp':
                                        None
                                else:
                                        deflt = 'Null'

                        c = c + "$this->%s = %s;\n\t\t" % (v.name, deflt)
                return c

        def SQLCOLSPEC(self):
                c = ""
                if self.atts.extends:
                        c = c + "id, uid, gid, cid, pid"
                        nvars = 4
                else:
                        c = c + "id, uid, gid, cid"
                        nvars = 3
                        
                if self.atts.is_interface:
                        c = c + ", vptr, vptr_class"
                        # That's all
                else:   
                        for v in self.vars:
                                if v.type == 'collection':
                                        continue
                                if v.persistence == 'transient' or v.transient:
                                        continue
                                if v.is_reference:
                                        if v.reference.is_polymorphic:
                                                # Hidden variable
                                                if nvars > 0:
                                                        c = c + ", "
                                                c = c + "%s_class" % (v.name)
                                                nvars = nvars + 1
                                if nvars > 0:
                                        c = c + ", "
                                nvars = nvars + 1

                                # Used to handle the UNIX_TIMESTAMP conversion in PHP
                                # Changed back to handle it on DB in/out
                                if v.type == 'date' or v.type == 'timestamp' or v.type == 'real_timestamp':
                                        c = c + "UNIX_TIMESTAMP(%s) as %s" % (v.name,v.name)
                                else:
                                        c = c + v.name
                return c
                
        def SELECTIMPL(self,where=None):
                c = "$query = \"SELECT @SQLCOLSPEC@"

                if not where:
                        sqlwhere = 'WHERE id=$oid'
                else:
                        sqlwhere = 'WHERE %s' % ( where )

                c = c + " FROM @TABLENAME@ %s\";" % (sqlwhere)
                return c

        def IDENTIFIABLE_NAME_IMPL(self):
                c = 'return $this->UUID();'
                return c

        def UUID_IMPL(self):
                c = 'return "{$this->className}-{$this->oid}";'
                return c

        def INITROWIMPL(self):
                i = ""
                c = ""
                c = c + "global $@SESSIONOBJECT@;\n\t\t"
                c = c + "global $ufoGlobals;\n\t\t"
                c = c + "$this->oid = $row['id'];\n\t\t"
                c = c + "$this->uid = $row['uid'];\n\t\t"
                c = c + "$this->gid = $row['gid'];\n\t\t"
                c = c + "$this->cid = $row['cid'];\n\t\t"
                if self.atts.extends:
                        c = c + "$this->pid = $row['pid'];\n\t\t"
                if self.atts.is_interface:
                        c = c + "$this->vptr = $row['vptr'];\n\t\t"
                        c = c + "$this->vptr_class = $row['vptr_class'];\n\t\t"
                for v in self.vars:
                        if self.atts.is_interface:
                                break
                        if v.persistence == 'transient' or v.transient:
                                continue
                        if v.select == 'multiple':
                                delim = ':'
                                if v.type == 'enum':
                                        delim = ','
                                c = c + "$%s = explode('%s', $row['%s']);\n\t\t" % (v.name, delim, v.name)
                                c = c + "$this->%s = $%s;\n\t\t" % (v.name,v.name)
                        else:
                                # Currently treating all single objects as reference.
                                if v.type == 'date' or v.type == 'timestamp' or v.type == 'real_timestamp':
                                        c =  c + "$this->%s = $row['%s'];\n\t\t" % (v.name,v.name)
                                elif v.type == 'currency':
                                        c =  c + "$this->%s = number_format($row['%s'], 2, '.', '');\n\t\t" % (v.name,v.name)
                                elif v.type == 'object':
                                        if v.is_reference:
                                                # Reference
                                                c = c + "$this->%s = $row['%s'];\n\t\t" % (v.name,v.name)
                                                if v.reference.is_polymorphic:
                                                        c = c + "$this->%s_class = $row['%s_class'];\n\t\t" % (v.name,v.name)
                                        else:
                                                # Non-reference
                                                c = c + "$this->%s =& $ufoSession->lookupContainer('%s',$row['%s']);\n\t\t" % (v.name, v.className, v.name)
                                elif v.type == 'collection':
                                        for w in v.vars:
                                                if w.type == 'object':
                                                        # Inherited collections are owned by the parent class
                                                        # so we need to look them up by our parent class id.
                                                        if v.is_inherited:
                                                                containerKey = 'pid'
                                                        else:
                                                                containerKey = 'oid'
                                                        if w.className == self.className:
                                                                containerName = self.atts.containerName
                                                        else:
                                                                ctx = self.getContext(w.className)
                                                                containerName = ctx.atts.containerName
                                                        #c = c + "$this->%s = @GETOBJECT(%s,0)@\n\t\t" % ( v.name, containerName )
                                                        c = c + "$this->%s = Null;\n\t\t" % ( v.name )
                                                        # check constraint type
                                                        c = c + "// Don't initialize until this is accessed with items() \n\t\t"
                                                        c = c + "// $this->%s->selectByContainer($this->oid);\n\t\t" % ( v.name )
                                                        #c = c + '$this->%s->filter = "cid={$this->%s}";\n\t\t' % (v.name,containerKey)
                                else:
                                        c = c + "$this->%s = $row['%s'];\n\t\t" % (v.name,v.name)

                return i + c

        def COPYIMPL(self):

                c = ""

                # 
                for v in self.vars:
                        if self.atts.is_interface:
                                break
                        if v.type == 'object':
                                if v.is_reference:
                                        c = c + "$obj->%s = $this->%s;\n\t\t" % ( v.name, v.name )
                                elif v.select == 'multiple':
                                        # Need to deal with select = multiple type objects.
                                        None
                                else:
                                        c = c + "// Copy nested object.\n\t\t"
                                        c = c + "$subthis = $this->get@UCCNAME(%s)@();\n\t\t" % ( v.name )
                                        c = c + "$subobj = $obj->get@UCCNAME(%s)@();\n\t\t" % ( v.name )
                                        c = c + "$subthis->_copy($subobj, $recurse);\n\t\t"

                        elif v.type == 'collection':
                                None
                        else:
                                # Need to deal with select = multiple types and whether they should be cloned as well.
                                c = c + "$obj->%s = $this->%s;\n\t\t" % ( v.name, v.name )

                # At this point, save it to aquire an oid.
                c = c + "$obj->save();\n\t\t\t"

                c = c + "if ($recurse) {\n\t\t\t"
                nvars = 0
                # After creating object, it has an oid, and now we can copy collections to it.
                for v in self.vars:
                        if self.atts.is_interface:
                                break                   
                        if v.type == 'collection':
                                c = c + "// Copy owned collection, but do not retain a reference to it in memory.\n\t\t\t"
                                c = c + "$coll = $obj->get@UCCNAME(%s)@();\n\t\t\t" % ( v.name )
                                c = c + "$thiscoll = $this->get@UCCNAME(%s)@();\n\t\t\t" % ( v.name )
				c = c + "$thiscoll->_copy($coll, $recurse);\n\t\t\t"
                                nvars = nvars + 1
                if nvars == 0:
                        c = c + "// No subobjects to copy\n\t\t"
                else:
                        c = c + "// End subobjects copy\n\t\t"
                      
                c = c + "}\n\t\t"

                c = c + "return $obj;\n\t\t"

                if self.atts.is_interface:
                        # Clone our delegate
                        c = c + "$delegate = $this->delegate();\n\t\t"
                        c = c + "$newdelegate = $obj->delegate();\n\t\t"
                        c = c + "if ($delegate) { \n\t\t\t"
                        c = c + "$delegate->pid = $obj->oid;\n\t\t\t"
                        c = c + "$delegate->_copy($newdelegate, $recurse);\n\t\t\t"
                        c = c + "$obj->vptr = $newdelegate->oid;\n\t\t\t"
                        c = c + "$obj->save(True);\n\t\t\t"
                        c = c + "}\n\t\t"

                if self.atts.extends:
                        # Clone our parent
                        c = c + "$parent = $this->parent();\n\t\t"
                        c = c + "$newparent = $obj->parent();\n\t\t"
                        c = c + "if ($parent) { \n\t\t\t"
                        c = c + "$newparent->vptr = $obj->oid;\n\t\t\t"
                        c = c + "$parent->_copy($newparent, $recurse);\n\t\t\t"
                        c = c + "$obj->pid = $newparent->oid;\n\t\t\t"
                        c = c + "}\n\t\t"

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
                ctx = self.getContext(v.className)
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

		# Make a function that returns labels for an enum value.
		c = c + """
        function %sEnumLabel( $v ) {
	       return $v;
	}
                                       \t""" % (v.name)

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
			$name = $this->%sEnumLabel( $v );
                        $c .= "<option value=\\"{$v}\\" {$select}>{$name}</option>";
                }
                return $c;
        }
                                        \t""" % (v.name, arrvals, v.name, v.name)
                                        
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

        def UPDATESQLMETA(self):
                return self.persistenceDelegate.updateSqlMeta()

        def LOG_THE_QUERY_BOOL(self):
                # If this ufo has any blobs in it, don't log the query please!
                for v in self.vars:
                        if v.type == 'blob':
                                # forget about it
                                return 'FALSE'
                return 'TRUE'

        def VALIDATEIMPL(self):
                c = ""
                constraint = "array()"
                for v in self.vars:
                        if v.type == 'bool':
                                c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateBool($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                        if v.type == 'string':
                                if v.constraint:
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateString($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                                else:
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateString($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                        if v.type == 'int':
                                c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateInt($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                        if v.type == 'float':
                                c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateFloat($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                        if v.type == 'currency':
                                c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateCurrency($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)

                        if v.type == 'date' or v.type == 'timestamp' or v.type == 'real_timestamp':
                                c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateDate($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                        if v.type == 'enum':
                                if v.select == 'multiple':
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateSet($ufo['%s'], %s)) { return False; } }\n\t\t" % (v.name, v.name, constraint)
                                else:
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateEnum($ufo['%s'], %s)) { return False; } }\n\t\t" % (v.name, v.name, constraint)
                        if v.type == 'object':
                                if v.select == 'multiple':
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateObject($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)
                                else:
                                        c = c + "if (isset($ufo['%s'])) { if ( ! $@GLOBALOBJECT@->validateObject($ufo['%s'])) { return False; } }\n\t\t" % (v.name, v.name)

                return c

        def CHOWNIMPL(self):
                c = ""
                nvars = 0
                if self.atts.extends:
                        None
                        # FIXME: chown our parent class as well.

                if self.atts.is_interface:
                        None
                        # That's all for interface classes
                        

                for v in self.vars:
                        # For interfaces, skip these things
                        if v.type == 'object':
                                if v.is_reference:
                                        None
                                else:
                                        c = c + "// Chown nested object.\n\t\t\t"
                                        c = c + "$obj = $this->get@UCCNAME(%s)@();\n\t\t\t" % ( v.name )
                                        c = c + "if (is_object($obj)) $obj->chown($uid, $gid, $recurse)\n\t\t\t;"
                                        c = c + "$obj = null;\n\t\t\t"
                                        nvars = nvars + 1
                        elif v.type == 'collection':
                                c = c + "// Chown owned collection.\n\t\t\t"
                                c = c + "$obj = $this->get@UCCNAME(%s)@();\n\t\t\t" % ( v.name )
                                c = c + "if (is_object($obj)) $obj->chown($uid, $gid, $recurse);\n\t\t\t"
                                c = c + "$obj = null;\n\t\t\t"
                                nvars = nvars + 1

                if nvars == 0:
                        c = c + "// No subobjects to chown"
                else:
                        c = c + "// End of subobjects to chown"
                        
                return c
                
        def DELETEIMPL(self):
                c = ""
                c = "if ($recurse) {\n\t\t\t"
                
                nvars = 0
                
                # Delete subobjects first in order to prevent accidentally leaked objects.
                for v in self.vars:
                        if v.type == 'object':
                                if v.is_reference:
                                        None
                                elif v.select == 'multiple':
                                        None
                                else:
                                        c = c + "// Delete nested object.\n\t\t\t"
					c = c + "$tmpobj = $this->get@UCCNAME(%s)@();\n\t\t\t" % (v.name)
					c = c + "$tmpobj->_delete($recurse);\n\t\t\t"
                                        nvars = nvars + 1
                        elif v.type == 'collection':
                                c = c + "// Delete owned collection.\n\t\t\t"
                                c = c + "$tmpobj = $this->get@UCCNAME(%s)@();\n\t\t\t" % (v.name)
				c = c + "$tmpobj->_delete($recurse);\n\t\t\t"
                                nvars = nvars + 1

                if nvars == 0:
                        c = c + "// No subobjects to delete\n\t\t"
                else:
                        c = c + "// End subobjects delete\n\t\t"
                        
                c = c + "}\n\t\t";

                if self.atts.is_interface:
                        # Delete our delegate
                        c = c + "$delegate = $this->delegate();\n\t\t"
                        c = c + "if ($delegate) { $delegate->_delete($recurse); }\n\t\t"

                if self.atts.extends:
                        # Delete our parent
                        c = c + "$parent = $this->parent();\n\t\t"
                        c = c + "if ($parent) { $parent->_delete($recurse); }\n\t\t"

                c = c + '$query = "@DELETESQL@";\n\t\t'
                c = c + '$result = @EXEC_QUERY@\n\t\t'
        
                return c
        
        def SUBMITIMPL(self):
                c = ""
                c = c + "if ( $this->oid == 0 ) {\n\t\t\t"
                c = c + "// changing metadata must be explicit through specialized methods\n\t\t\t"
                c = c + "if (isset($ufo['uid'])) { $this->uid = $ufo['uid']; }\n\t\t\t"
                c = c + "if (isset($ufo['gid'])) { $this->gid = $ufo['gid']; }\n\t\t\t"
                c = c + "if (isset($ufo['cid'])) { $this->cid = $ufo['cid']; }\n\t\t"
                c = c + "}\n\t\t"
                
                if self.atts.extends:
                        c = c + "if (isset($ufo['pid'])) { $this->pid = $ufo['pid']; }\n\t\t"

                for v in self.vars:
                        if v.visibility == False or v.visibility == 'read':
                                continue
                        # For bool, interpret string.
                        if v.type == 'bool':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = anyToBool($ufo['%s']); }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'string':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'int':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'float':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'currency':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'date' or v.type == 'timestamp':
                                c = c + "if (isset($ufo['%s'])) { $this->%s = $@GLOBALOBJECT@->unix_timestamp($ufo['%s']); }\n\t\t" % (v.name, v.name, v.name)
                        if v.type == 'real_timestamp':
                                # never write to a DB-generated timestamp, regardless of our visibility="foo" attribute
                                continue
                        if v.type == 'enum':
                                if v.select == 'multiple':
                                        c = c + "if (isset($ufo['%s'])) { $this->%s = is_array($ufo['%s']) ? $ufo['%s'] : array_combine(array($ufo['%s']), array($ufo['%s'])); }\n\t\t" % (v.name, v.name, v.name, v.name, v.name, v.name)
                                else:
                                        c = c + "if (isset($ufo['%s'])) { $this->%s = $ufo['%s']; }\n\t\t" % (v.name, v.name, v.name)
                        # Treat all single objects as references.
                        if v.type == 'object':
                                if v.select == 'multiple':
                                        c = c + """if (isset($ufo['%s'])) {
                        if ( is_array( $ufo['%s'] ) ) {
                           $tmparr = $ufo['%s'];
                        } else {
                           $tmparr = explode(':', $ufo['%s']);
                        }
                        $newarr = array();
                        foreach ( $tmparr as $elem ) {
                           if ( is_numeric( $elem ) ) {
                              $newarr[] = $elem;
                           } else {
                              error_log("WARNING: RECEIVED NONNUMERIC REFERENCE: $elem");
                           }
                        }
                        $this->%s = $newarr;
                }
                """ % (v.name, v.name, v.name, v.name, v.name)
                                else:
                                        if v.is_reference:
                                                # Object reference
                                                if v.reference.is_polymorphic:
                                                        ucname = string.capwords( v.name, '_' )
                                                        ucname = string.replace( ucname, '_', '')
                                                        c = c + "if (isset($ufo['%s_class'])) { $this->%s_class = $ufo['%s_class'];\n\t\t }\n\t\t" % (v.name, v.name, v.name)
                                                        c = c + "if (isset($ufo['%s'])) { \n\t\t\t$this->%s = $ufo['%s'];\n\t\t\t$this->get%s();\n\t\t}\n\t\t" % (v.name, v.name, v.name, ucname)
                                                else:
                                                        c = c + "if (isset($ufo['%s'])) { $this->%s = $@SESSIONOBJECT@->lookupContainer('%s', $ufo['%s']); }\n\t\t" % (v.name, v.name, v.className, v.name)
                                        else:
                                                # Non-reference: Ignore changes to this index.
                                                c = c + """if (isset($ufo['%s']) && is_array( $ufo['%s'] ) ) {
                        $this->%s->submit ( $ufo['%s'] );
                } elseif ( $this->%s->oid == 0 ) {
                        $this->%s->submit (array());
                }
                """ % (v.name,v.name,v.name,v.name,v.name,v.name)

                        if v.type == 'blob':
                                c = c + """global $_FILES;
                if (isset($_FILES['%s'])) { 
                        $data = $_FILES['%s'];
                           $this->wasUpload = True;
                           $tmpfile = $data['tmp_name'];

                           // Get image related data
                           list($width, $height, $imgtype, $imgattr) = getimagesize($tmpfile);
                           $this->width = $width;
                           $this->height = $height;
                           
                           $size = $data['size'];
                           $fh = fopen($tmpfile, "r");
                           $content = fread($fh, $size);
                           $this->%s = addslashes($content);
                           $ufo['mime_type'] = $data['type'];
                           $ufo['name'] = $data['name'];
                           // This is a hack.
                           $this->mime_type = $ufo['mime_type'];
                           $this->name = $ufo['name'];
                           $this->size = $size;
                }
                        """ % (v.name,v.name,v.name)

                c = c + "$this->save();\n\t\t"
                c = c + "$this->readOnly = TRUE;\n"
                return c

        def TABLE_HEADERS(self):
                c = ""
                for v in self.vars:
                        if v.visibility == False:
                                continue
                        if v.type == 'collection' or v.type == 'object' or v.is_reference == True or v.select == 'multiple':
                                continue
                        c = c + '\n<td>\n'
                        c = c + v.text
                        c = c + '\n</td>'
                return c

        def CLASS_VIEWJSONIMPL(self):
                c = ""
                c = c + "\tglobal $ufoSession;\n"
                c = c + "\t$obj = array();\n"
                c = c + "\t$obj['className'] = $this->className;\n"
                c = c + "\t$obj['version'] = $this->version;\n"
                c = c + "\t$obj['oid'] = $this->oid;\n"
                c = c + "\t$obj['uid'] = $this->uid;\n"
                c = c + "\t$obj['gid'] = $this->gid;\n"
                c = c + "\t$obj['cid'] = $this->cid;\n"

                c = c + "\t// add this object to the remote cache\n\t"
                c = c + """if ( $addToRemoteCache ) {
                $ufoSession->addRemoteObjects($this->className, array($this->oid));
        }"""

                if self.atts.extends:
                        c = c + "\t$obj['pid'] = $this->pid;\n"
                        
                for v in self.vars:
                        if v.persistence == 'transient':
                                None
                                # Just return it for now anyway.
                        elif v.type == "object" or v.type == "collection" or v.type == "blob":
                                ucname = string.capwords( v.name, '_' )
                                ucname = string.replace( ucname, '_', '')
                                if v.type == "object" and v.is_reference:
                                        if v.reference.is_polymorphic:
                                                c = c + "\t$obj['%s_class'] = $this->%s_class;\n" % (v.name,v.name)
                                        else:
                                                c = c + """
                                if ( array_key_exists( '%s', $this->viewable ) ) {
                                     // Acess this member via getter in case it's not instantiated yet.
                                     $temp = $this->get%s();
                                     $obj['%s'] = $temp->viewJSON();
                                } else {
                                     $obj['%s'] = is_object($this->%s)?$this->%s->oid:$this->%s;
                                }
                                """ % ( v.name, ucname, v.name, v.name, v.name, v.name, v.name )

                                elif v.type=="object" and v.select=="multiple":
                                        c = c + """
                                if ( array_key_exists( '%s', $this->viewable ) ) {
                                     // Acess this member via getter in case it's not instantiated yet.
                                     $temp = $this->get%s();
                                     $obj['%s'] = $temp;
                                } else {
                                     $obj['%s'] = $this->%s;
                                }
                                """ % ( v.name, ucname, v.name, v.name, v.name )
                                else:           
                                        c = c + """
                                if ( array_key_exists( '%s', $this->viewable ) ) {
                                     // Acess this member via getter in case it's not instantiated yet.
                                     $temp = $this->get%s();
                                     $obj['%s'] = $temp->viewJSON();
                                } else {
                                     $obj['%s'] = Null;
                                }
                                """ % ( v.name, ucname, v.name, v.name )
                        else:   
                                c = c + "\t$obj['%s'] = $this->%s;\n" % (v.name,v.name)
                c = c + "\treturn $obj;\n"
                return c

        def CONTAINER_VIEWJSONIMPL(self):
                c = r'''
                global $ufoSession;
                // lazy initialization
                // $this->initialize();

                $output = array();
                $output['uid'] = $this->uid;
                $output['gid'] = $this->gid;
                $output['cid'] = $this->cid;
                $items = array();
                $oids = array();
                foreach ( $this->items() as $item ) {
                    $oids[] = $item->oid;
                    $item->setViewable( $this->viewable );
                    $items[] = $item->viewJSON(False);
                }
                $output['items'] = $items;

                // add this object to the remote cache
                if ( $addToRemoteCache ) {
                   $ufoSession->addRemoteObjects('@CLASSNAME@', $oids);
                }

                // If we're selecting a set of items, just
                // return the raw items and not the container.
                if ( FALSE ) {
                   return $items;
                } else {
                   return $output;
                }
                '''
                return c

        def VIEWROIMPL(self):
                c = ""                  
                c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\">'
                for v in self.vars:
                        if v.visibility == False or v.visibility == 'write':
                                continue
                        if v.type == 'collection' :
                                continue
                        if v.type == 'object':
                                if v.is_reference:
                                        continue
                                else:
                                        c = c + v.viewRO()
                        else:
                                c = c + v.viewRO()
                c = c + '\n</table>'
                return c

        def INITVIEWIMPL(self):
                c = ""
                if self.readOnly:
                        return c

                encoding = "";

                # Look for any blob data which implies an upload.
                for v in self.vars:
                        if v.type == 'blob':
                                encoding = 'enctype=\\"multipart/form-data\\"';
                                break;

                # c = c + '\n<form %s action=\\"" . $this->getSubmitLink() . "\\" method=\\"post\\">' % (encoding)
                c = c + '\n<form %s dojoType=\\"dijit.form.Form\\" id=\\"form_%s\\" action=\\"" . $this->getSubmitLink() . "\\" method=\\"post\\">' % (encoding, self.className)
                c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\">'

                for v in self.vars:
                        if v.visibility == False or v.visibility == 'read':
                                continue
                        # Variable knows how to present itself.
                        if v.type == 'collection':
                                continue
                        c = c + v.formInput()
                c = c + '\n</table>'

                #c = c + '\n<input type=\\"hidden\\" name=\\"ufo[oid]\\" value=\\"{$this->oid}\\">'
                c = c + '\n<!-- <input type=\\"hidden\\" name=\\"ufo[gid]\\" value=\\"{$this->gid}\\"> -->'
                c = c + '\n<!-- <input type=\\"hidden\\" name=\\"ufo[cid]\\" value=\\"{$this->cid}\\"> -->'
                c = c + '\n<!-- <input type=\\"hidden\\" name=\\"method\\" value=\\"submit\\"> -->'
                c = c + '\n<button dojoType=\\"dijit.form.Button\\" iconClass=\\"formNext\\" onclick=\\"dijit.byId(\'form_%s\').submit()\\">Next</button>' % ( self.className )
                #c = c + '\n<input type=\\"submit\\" name=\\"submit\\" value=\\"submit\\">'
                c = c + '\n</form>'
                return c

        def OBJECT_REF_INCLUDES(self):
                c = ""
                # Include explicitly declared base classes
                for parent in self.atts.parent_classes:
                        c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix, parent)

                # For now don't include other classes.
                # Attempt to access everything through the session cache.
                return c
        
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
                                                        print "Getting context %s" % w.className
                                                        ctx = self.getContext(w.className)
                                                        containerName = ctx.atts.containerName
                                                if containerName:
                                                        c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,containerName)
                                                else:
                                                        c = c + "include_once('%s_%s.php');\n" % (self.atts.prefix,w.className)
        
                        if v.type == 'object':
                                # Include its container if it has one.
                                ctx = self.getContext(v.className)
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
                                c = c + "@PRIVATE@ $facets = array(\n\t"
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
                                c = c + "@PROTECTED@ $selected = array(\n\t"
                                lfirst = False
                        else:
                                c = c + ","
                        c = c + "'%s' => False\n\t" % f
                if lfirst:
                        c = "@PROTECTED@ $selected = False;"
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
                        if v.type == 'collection' or v.type == 'object' or v.is_reference == True or v.select == 'multiple':
                                continue
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

        def INITIALIZE_ALL_MEMBERS(self):
                c = ""
                for v in self.vars:
                        if v.type == 'object':
                                if v.is_reference:
                                        c = c + '$this->get@UCCNAME(%s)@();\n\t\t' % (v.name)
                return c
                
        def VIEWIMPL(self):
                c = ""
                page = self.atts.containerName
                if self.readOnly:
                        return c

                encoding = "";

                # Look for any blob data which implies an upload.
                for v in self.vars:
                        if v.type == 'blob':
                                encoding = 'enctype=\\"multipart/form-data\\"';
                                break;

                #c = c + '\n<form %s action=\\"" . $this->getSubmitLink() . "\\" method=\\"post\\">' % (encoding)
		c = c + '\n<form %s dojoType=\\"dijit.form.Form\\" id=\\"form_%s\\" action=\\"" . $this->getSubmitLink() . "\\" method=\\"post\\">' % (encoding, self.className)
                c = c + '\n<table class=\\"stats\\" border cellpadding=\\"0\\" style=\\"border-collapse: collapse\\">'

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

                c = c + '\n<!-- <input type=\\"hidden\\" name=\\"ufo[oid]\\" value=\\"$this->oid\\"> -->'
                c = c + '\n<!-- <input type=\\"hidden\\" name=\\"method\\" value=\\"submit\\"> -->'
                c = c + '\n<button dojoType=\\"dijit.form.Button\\" iconClass=\\"formNext\\" onclick=\\"dijit.byId(\'form_%s\').submit()\\">Next</button>' % ( self.className )
                #c = c + '\n<input type=\\"submit\\" name=\\"submit\\" value=\\"submit\\">'
                c = c + '\n</form>'
                return c
                
        def CONTAINER_FUNCTION_ADD_SIGNATURE(self):
                if self.atts.is_interface:
                        return '$obj=Null,$classname="@CLASSNAME@"';
                else:
                        return '$obj=Null';

        def CONTAINER_FUNCTION_ADD_CLASSNAME(self):
                if self.atts.is_interface:
                        return '$classname';
                else:
                        return '"@CLASSNAME@"';

        def CONTAINER_FUNCTION_COPY_IMPL(self):
                if self.atts.is_interface:
                        return '$obj = $toContainer->add(Null, $item->className);';
                else:
                        return '$obj = $toContainer->add();';                   


        def PARENT_CLASS_DECL(self):
                c = ""
                if self.atts.parent_classes:
                        # PHP only support single inheritance in general - use the first one.
                        for p in self.atts.parent_classes:
                                c = c + "extends ayp_%s" % p
                                break
                return c
        
        def MAJORVERSION(self):
                (major,minor) = string.split(self.atts.version, '.')
                return major

        def MINORVERSION(self):
                (major,minor) = string.split(self.atts.version, '.')
                return minor

        def CONSTRUCTIMPL(self):
                c = ""
                c = """
                // Handle mixed args, possibly an array.
                if ( is_array($argv) ) {
                        if ( isset($argv['oid']) ) {
                                $oid = $argv['oid'];
                        } else {
                                $oid = -1;
                        }
                } else {
                        $oid = $argv;
                }

                if ( $oid != -1 ) {
                        // load it
                        if ( $oid == 0 ) {
                                // return empty
                                $this->initialized = False;
                        } else {                   
                                if ( is_numeric( $oid ) ) {
                                   $this->load( $oid );
                                } """

                if self.atts.enum:
                        c = c + """else {
                                   $this->loadByName( $oid );
                                }"""
                else:
                        c = c + """else {
                                   global $ufoStatus;
                                   $ufoStatus->invalid_parameter_range("@CLASSNAME@ constructor: $oid not a numeral");
                                }"""
                        
                c = c + """
                        } 
                }
                """
                return c

        def GETENUMVALUES(self):
                c = ""
                if self.atts.enum:
                        enumkey = self.atts.enum
                else:
                        return c
                
                c = c + """
        function getEnumValues() {
                $c = "";
                @DBOBJECTDECL@

                global $ufoEncoding;
                global $obj;
                global $method;
                $values = array();
                $query = "SELECT %s FROM @PREFIX@_@CLASSNAME@";
                $result = @EXEC_QUERY@
                while ($row = @EXEC_FETCH_ASSOC@) {
                        $values[] = $row['%s'];
                }
                if ($obj == '@CLASSNAME@' && $method == 'getEnumValues') {
                   $jsarray = "[";
                   $first = True;
                   foreach ($values as $value) {
                      if ( ! $first ) {
                         $jsarray .= ", ";
                      } else {
                         $first = False;
                      }
                      $jsarray .= '"' . $value . '"';
                   }
                   $jsarray .= "]";
                   $this->obuffer = $jsarray;
                }
                return $values;
        }""" % (enumkey,enumkey)
                return c

        # When a container fetches its items, if they are abstract (interface) objects, follow the vptr
        # and instantiate the concrete derived class.  The end result can be a heterogeneous array of objects.
        def CONTAINER_CAST_ITEM(self):
                c = ""
                if self.atts.is_interface:
                        c = c + """
                        // overwrite the $to variable with the subclass instance before adding to items.
                        $suboid = $to->vptr;
                        $subclass = $to->vptr_class;
                        $to = $ufoSession->lookupContainer($subclass, $suboid);
                        """
                return c

        # When a derived class is created, it must be create its parent class object at the same time.
        def CREATEPARENTCLASS(self):
                c = ""
                if self.atts.extends:
                        parent = self.atts.extends
                        c = c + """
                        $parent = $ufoSession->allocate('%s');
                        $parent->uid = $this->uid;
                        $parent->gid = $this->gid;
                        $parent->cid = $this->cid;
                        $parent->vptr = $this->oid;
                        $parent->vptr_class = "@CLASSNAME@";
                        $parent->save();
                        $this->pid = $parent->oid;
                        $this->save();
                        """ % ( parent )
                return c
                
        def LOADBYNAME(self):
                c = ""

                if self.atts.enum:
                        enumkey = self.atts.enum
                else:
                        return c
                
                c = """
        function loadByName( $name ) {
                @DBOBJECTDECL@

                @SELECTIMPL(%s=@APOSTROPHE@$name@APOSTROPHE@)@

                $result = @EXEC_QUERY@
                $row = @EXEC_FETCH_ASSOC@;
                if (! $row ) {
                        // ok if foreign key
                        $this->initialized = False;

                } else {
                        $this->initRow( $row );
                }
                return $this;
        }
        """ % ( enumkey )
                return c
        
        def ENUMTEMPLATE(self):
                c = r'''<?php
class @PREFIX@_@CLASSNAME@ {

        var $values = array();


}'''
                return c

        def CLASSBASETEMPLATE(self):    
                c = r'''<?php
@OBJECT_REF_INCLUDES@
class @PREFIX@_@CLASSNAME@_base @PARENT_CLASS_DECL@ {
        // public attributes
        @ATTRIBUTES@

        // facets - subviews
        @FACETS@

        // selectors 
        @SELECTOR@

        // private attributes
        @PROTECTED@ $readOnly;
        @PROTECTED@ $initialized;
        @PROTECTED@ $edit_link;
        @PROTECTED@ $submit_link;
        @PUBLIC@ $wasUpload;
        
        @PUBLIC@ $className;
        @PROTECTED@ $version = "@MAJORVERSION@.@MINORVERSION@";

        // output buffer to override view
        @PROTECTED@ $obuffer = Null;
        @PROTECTED@ @MEMBERS_VIEWABLE@
        
        // Security
        @PUBLIC@ @METHOD_VISIBILITY@

        function @PREFIX@_@CLASSNAME@_base( $argv=-1 ) {
                @DBOBJECTDECL@
                global $@SESSIONOBJECT@;
                $this->readOnly = 1;
                $this->wasUpload = False;
                // hopefully this isn't necessary.
                $this->className = "@CLASSNAME@";
                $this->link_edit = "main.php?obj=@CLASSNAME@&ufo[oid]={\$this->oid}&method=edit";
                $this->link_submit = Null;

                // initialize to reasonable defaults.
                $this->initialize();

                @CONSTRUCTIMPL@
        }
        function identifiableName() {
                @IDENTIFIABLE_NAME_IMPL@
        }
        function version() { return $this->version; }
        function UUID() {
                @UUID_IMPL@
        }
        @CLASS_ACCESSORS@
        @CLASS_SETTERS@
        @GETENUMVALUES@
        @GETDELEGATE@
        @GETPARENT@
        @GETCOLLECTIONNAMES@
        @GETREFERENCENAMES@
        function getEditLink() {
	        return $this->link_edit;
                // return "main.php?obj=@CLASSNAME@&ufo[oid]={$this->oid}&method=edit";
        }
        // not generated currently
        function getViewLink() {
                return "main.php?obj=@CLASSNAME@&ufo[oid]={$this->oid}";
        }
        // not generated currently
        function getSubmitLink() {
                global $page;
		if ( $this->link_submit ) {
                   $link_submit = $this->link_submit;
	        } else {
                   $link_submit = "main.php?obj={$this->className}&method=submit&ufo[oid]={$this->oid}&page={$page}";
	        }
		return $link_submit;
        }
        // not generated currently
        function getDeleteLink() {
                global $page;
                return "main.php?obj=@CLASSNAME@&ufo[oid]={$this->oid}&method=delete&ufo[recurse]=1&page={$page}";
        }
        // not generated currently
        function setEditLink( $url ) {
                $this->link_edit = $url;
        }
        function setSubmitLink( $url ) {
                $this->link_submit = $url;
        }
        @MENUOPTIONFUNCTIONS@
        @SELECTMETHODS@

        // Array of member you want to see if the view output.
        function setViewable ( $argv ) {
                $this->viewable = array_merge( $this->viewable, $argv );
        }
        function edit() {
                $this->setReadWrite();
        }
        function setReadOnly() { $this->readOnly = TRUE; }
        function setReadWrite() { 
                //global $Log;
                $this->readOnly = 0; 
                //$Log->append("In ufo::setReadWrite()");
        }
        function getReadState() {
                //global $Log;
                //$Log->append("In ufo::getReadState($this->readOnly)");
                return $this->readOnly;
        }
        function initialize() {
                @INITIMPL@
        }
        function initRow( $row ) {
                // Initialize through SQL row.
                @INITROWIMPL@
                $this->initialized = True;
        }

        // Lifecycle operations
        function copy($argv) {
           //
           // NOOP currently.
           // Override this in subclass.  For example:
           //
           // $to = Null;
           // # or:
           // $to = some_container_object;
           //
           // if (isset( $argv['recurse'] )) {
           //   return $this->_copy($to, $argv['recurse'] );
           // } else {
           //   return $this->_copy($to);
           // } 
           //
        }
        function _copy($to, $recurse=False) {
           global $ufoLog;
           global $ufoSession;
           if ( ! $to ) {
              $obj = $ufoSession->allocate('@CLASSNAME@');
              $ufoLog->debug("Copying " . $this->identifiableName());
              // retain metadata
              $obj->uid = $this->uid;
              $obj->gid = $this->gid;
           } else {
              // Need to assert that $to is the right type of object.
              $ufoLog->debug("Copying " . $this->identifiableName() . " to: " . $to->identifiableName() );
              $obj = $to;
           }
           // To prevent copy loops
           // I'm reusing my deleteLock variable here.
           if ( isset( $this->deleteLock ) ) {
              $ufoLog->oddity("Multiple attempts to copy " . $this->identifiableName()); 
              return $this->deleteLock;
           } else {
              $this->deleteLock = $obj;
           }
                @DBOBJECTDECL@  
                @COPYIMPL@
        }
        function move($oid) {
                $this->cid = $oid;
                $this->save(True);
        }
        function chown($uid, $gid, $recurse=False) {
          if ($recurse) {
                @CHOWNIMPL@
          }
          $this->uid=$uid;
          $this->gid=$gid;
          $this->save();
        }
        function delete( $argv ) {
           if (isset( $argv['recurse'] )) {
              return $this->_delete( $argv['recurse'] );
           } else {
              return $this->_delete();
           }
        }
        function _delete($recurse=False) {
           global $ufoLog;
           $ufoLog->debug("Deleting " . $this->identifiableName());
           // To prevent delete loops and avoid deleting oid=0 objects
           if ( $this->oid == 0 || isset( $this->deleteLock ) ) {
              return True;
           } else {
              $this->deleteLock = True;
           }
                @DBOBJECTDECL@  
                @DELETEIMPL@
        }
        function create() {
                // create it in the DB
                global $@SESSIONOBJECT@;
                @DBOBJECTDECL@

                $link = $@DBOBJECT@->getLink();
                $this->uid = $@SESSIONOBJECT@->getUID();

                // insert
                $query = @INSERTSQL@;

                $result = @EXEC_QUERY@

		@ASSIGN_OID@

                $this->initialized = True;
                @CREATEPARENTCLASS@
        }
        function post_create() {
            global $@GLOBALOBJECT@;
            // Add it to the dirty object cache under certain conditions, which are currently all conditions ...
            $@GLOBALOBJECT@->addDirtyObject($this->className, array($this->oid));
        }
        function post_update($metadata=False) {
            global $@GLOBALOBJECT@;
            // Add it to the dirty object cache under certain conditions, which are currently all conditions ...
            $@GLOBALOBJECT@->addDirtyObject($this->className, array($this->oid));
        }
        function save($metadata=False) {
                global $@GLOBALOBJECT@;
                @DBOBJECTDECL@
                // update it in the DB
                $link = $@DBOBJECT@->getLink();
                $oid = $this->oid;
                if ($this->initialized == True) {
                        if ($metadata) {
                           $query = @UPDATESQLMETA@
                        } else {
                           $query = @UPDATESQL@;
                        }
                        if ( $query ) {
                           $result = @EXEC_QUERY@
                        }
                        $this->post_update($metadata);
                } else {
                        $this->create();
                        $this->post_create();
                }
                
        }
        function load( $oid ) {
                @DBOBJECTDECL@

                @SELECTIMPL@

                $result = @EXEC_QUERY@
                $row = @EXEC_FETCH_ASSOC@;
                if (! $row ) {
                        // ok if foreign key
                        $this->initialized = False;

                } else {
                        $this->initRow( $row );
                        $this->oid = $oid;
                }
                return $this;
        }
        @LOADBYNAME@
        function validate( $ufo ) {
                global $ufoStatus;
                @DBOBJECTDECL@
                @VALIDATEIMPL@
        }
        function submit( $ufo ) {
                // update state
                // assert the oid is correct.
                global $@GLOBALOBJECT@;
                global $@SESSIONOBJECT@;

                // validate the checksum first
                // FIXME

                // validate the data next
                //if ( ! $this->validate($ufo) ) {
                //     return;
                //}

                @SUBMITIMPL@
        }
        function link( $name="@CLASSNAME@" ) {
                global $@GLOBALOBJECT@;
                $c = "<a href=\"http://{$@GLOBALOBJECT@->domain}/main.php?obj=@CLASSNAME@&ufo[oid]={$this->oid}\">{$name}</a>";
                return $c;
        }
        function table_headers() {
                $c = "";
                $c .= "
                @TABLE_HEADERS@
                ";
                return $c;
        }
        function viewAsTableRow($encoding='html') {
                global $@GLOBALOBJECT@;
                global $page;
                global $CHECKED;
                global $BOOLSTR;
                @INITIALIZE_ALL_MEMBERS@

                $c = "";
                if ($this->readOnly == TRUE) {
                $c = "
                @VIEW_ROW_ROIMPL@
                "; 
                } else {
                  if ($this->initialized == TRUE) {
                $c = "
                @VIEW_ROW_IMPL@
                ";
                  } else {
                $c = "
                @INITVIEW_ROW_IMPL@
                ";
                  }
                }
                return $c;
        }
        function viewJSON($addToRemoteCache=True) {
                @CLASS_VIEWJSONIMPL@
        }
        function viewXML() {
                return "viewXML Not Implemented";
        }
        function viewHTML() {
                global $@GLOBALOBJECT@;
                global $page;
                global $CHECKED;
                global $BOOLSTR;
                @INITIALIZE_ALL_MEMBERS@
                $c = "";
                if ($this->readOnly == TRUE) {
                $c = "
                @VIEWROIMPL@
                "; 
		$edit_link = $this->getEditLink();
		if ( $edit_link ) {
                $c .= "[<a href=\"{$edit_link}\">edit</a>]";
		}
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
        function view($encoding='html') {

                // The implication of this is that some function call happened that changed what we want to view.
                // For example, maybe just a subset of the object.
                if ( $this->obuffer != Null ) {
                   return $this->obuffer;
                }

                if ($encoding == 'xml') {
                        return $this->viewXML();
                }
                if ($encoding == 'json') {
                        return $this->viewJSON();
                }
                if ($encoding == 'html') {
                        return $this->viewHTML();
                }
                // else
                return "";
        }
}
?>'''
                return c

        def CLASSTEMPLATE(self):
                c = r'''<?php
include_once('@PREFIX@_@CLASSNAME@_base.php');

class @PREFIX@_@CLASSNAME@ extends @PREFIX@_@CLASSNAME@_base {

        function @PREFIX@_@CLASSNAME@( $argv=-1 ) {
                // Override default method here.
                parent::@PREFIX@_@CLASSNAME@_base( $argv );
        }
        function extendsVersions() {
              return array('@MAJORVERSION@.@MINORVERSION@');
        }
        function identifiableName() {
                // Override default method here.
                return parent::identifiableName();
        }
        // not generated currently
        function setEditLink( $url ) {
                // Override default method here.
                return parent::setEditLink( $url );
        }
        function setSubmitLink( $url ) {
                // Override default method here.
                return parent::setSubmitLink( $url );
        }
        function initialize() {
                // Override default method here.
                return parent::initialize();
        }
        function delete($argv) {
                // Override default method here.
                return parent::delete($argv);
        }
        function copy($argv) {
                // Override default method here.
                // See the comment in parent::copy()
                return parent::copy($argv);
        }

        function create() {
                // Override default method here.
                return parent::create();
        }
        function save() {
                // Override default method here.
                return parent::save();
        }
        function validate( $ufo ) {
                // Override default method here.
                return parent::validate( $ufo );
        }
        function link() {
                // Override default method here.
                return parent::link();
        }
        function table_headers() {
                // Override default method here.
                return parent::table_headers();
        }
        function viewAsTableRow($encoding='html') {
                // Override default method here.
                return parent::viewAsTableRow();
        }
        function view($encoding='html') {
                // Override default method here.
                return parent::view($encoding);
        }
}
?>'''
                return c

        def CONTAINERBASETEMPLATE(self):
                c = r'''<?php
include_once('@PREFIX@_@CLASSNAME@.php');

class @PREFIX@_@CONTAINERNAME@_base {
        // public attributes
        @PUBLIC@ $uid;
        @PUBLIC@ $gid;
        @PUBLIC@ $cid;

        @PROTECTED@ $@CLASSNAME@ = array();
        @PUBLIC@ $addedObject = 0;

        // Types of pseudo-persistent containers:
        // uid, gid, cid

        // Types of transient containers:
        // query

        @PROTECTED@ $pseudoType;

        // private attributes
        @PUBLIC@ $className;
        @PROTECTED@ $initialized;

        // default selection criteria
        @PUBLIC@ $maxItems;
        @PUBLIC@ $startIdx;
        @PUBLIC@ $orderBy;
        @PUBLIC@ $filter;

        // output buffer to override view
        @PROTECTED@ $obuffer = Null;
        @PROTECTED@ $viewable = array();

        // Security
        @PUBLIC@ @METHOD_VISIBILITY@

        function @PREFIX@_@CONTAINERNAME@_base ( $argv=0 ) {
                global $@SESSIONOBJECT@;
                global $ufoLog;

                // hopefully this isn't necessary.
                $this->className = "@CONTAINERNAME@";
                $this->pseudoType = Null;
                
                $this->maxItems = 999;
                $this->startIdx = 0;
                $this->orderBy = 'id';
                $this->filter = '';

                // initialize uid/gid to session values
                $this->uid = $ufoSession->getUID();
                $this->gid = $ufoSession->getGID();
                
                $this->initialized=False;

                // Handle mixed args, possibly an array.
                if ( is_array($argv) ) {
                        if  ( isset($argv['cid']) ) {
                                $this->cid = $argv['cid'];
                        }
                        if  ( isset($argv['gid']) ) {
                                $this->gid = $argv['gid'];
                        }
                        if  ( isset($argv['uid']) ) {
                                $this->uid = $argv['uid'];
                        } else {
                                $this->uid = $ufoSession->getUID();
                        }

                        //$ufoLog->info("@CLASSNAME@::CLASSNAME::ARGV");
                        if  ( isset($argv['cid']) ) {
                                //$ufoLog->info("@CLASSNAME@::CLASSNAME::CID");
                                $this->selectByContainer($this->cid);
                        } elseif  ( isset($argv['gid']) ) {
                                //$ufoLog->info("@CLASSNAME@::CLASSNAME::GID");
                                $this->selectByGroups($this->gid);
                        } elseif ( isset($argv['uid']) ) {
                                //$ufoLog->info("@CLASSNAME@::CLASSNAME::UID");
                                $this->selectByUser($this->uid);
                        }
                } else {
                        // Do nothing.
                        // $ufoLog->oddity("@CLASSNAME@::CLASSNAME::ARGV={$argv}");
                }
        }
        // Wipe out any objects in this container and reset initialized to False.
        function clear() {
                $this->@CLASSNAME@ = array();
                $this->initialized = False;
        }
        function initialize($argv=0) {
                // Find the member data.
                if ($this->initialized) { 
                        return; 
                } else {
                        // wipe out the existing array
                        $this->@CLASSNAME@ = array();
                }

                @DBOBJECTDECL@
                global $ufoSession;
                global $ufoLog;

                $ufoLog->debug("@CLASSNAME@::initialize()");

                if (isset($argv['uid'])) {
                        $this->uid = $argv['uid'];
                } else {
                        $this->uid = $ufoSession->getUID();
                }

                $where = is_array($this->filter) ? implode(' and ', $this->filter) : $this->filter;
                
                //do not restrict admin from selecting items
                if (in_array('root', $ufoSession->getRoles())) {
                   $isAdminUser = true;
                } elseif (in_array('admin', $ufoSession->getRoles())) {
                   $isAdminUser = true;
                } elseif (in_array('manager', $ufoSession->getRoles())) {
                   //FIXME: make manager an admin user for this purpose temporarily
                   $isAdminUser = true;
                } else {
                    $isAdminUser = false;
                }
                if (strlen($where)>0) {
                   if ($isAdminUser) {
                      $where = "and $where";
                   }
                   else {
                      $where = "and $where";
                   }
                }
                $limit = $this->maxItems + 1;
                if ($isAdminUser) {
                   $uidInWhere = "1";
                }
                else {
                   $uidInWhere = "uid=" . $this->uid;
                }

                $query = "SELECT @SQLCOLSPEC@ from @PREFIX@_@CLASSNAME@ where $uidInWhere $where ORDER BY {$this->orderBy}"; // limit {$this->startIdx},{$limit}";


                $result = @EXEC_QUERY@

                $idx = 0;
                while ($row = @EXEC_FETCH_ASSOC@ ) {
                        $to = new @PREFIX@_@CLASSNAME@(0);
                        $to->initRow( $row );
                        @CONTAINER_CAST_ITEM@
                        $this->@CLASSNAME@[] = $to;
                        $idx += 1;
                }

                 /* Free resultset */
                @EXEC_FREE_RESULT@
        }

        // Generic way of accessing the list of objects in a container
        // allowing for lazy retrieval of the actual items.
        function items($argv=0) {
                $this->initialize($argv);
                return $this->@CLASSNAME@;
        }
        
        function version() { return $this->version; }

        function selectByUser($id=Null) {
                // Find the member data.
                @DBOBJECTDECL@
                global $ufoSession;
                global $ufoLog;
                
                if ($id == Null ) {
                        $this->uid = $ufoSession->getUID();
                } else {
                        $this->uid = $id;
                }

                $limit = $this->maxItems + 1;
                $query = "SELECT @SQLCOLSPEC@ from @PREFIX@_@CLASSNAME@ where uid=$this->uid ORDER BY {$this->orderBy}"; // limit {$this->startIdx},{$limit}";
                $result = @EXEC_QUERY@

                $idx = 0;
                while ($row = @EXEC_FETCH_ASSOC@ ) {
                        $to = new @PREFIX@_@CLASSNAME@(0);
                        $to->initRow( $row );
                        @CONTAINER_CAST_ITEM@
                        $this->@CLASSNAME@[] = $to;
                        $idx += 1;
                }

                 /* Free resultset */
                @EXEC_FREE_RESULT@
                $this->initialized = True;
        }
        function selectByGroups($id=Null) {
                global $ufoLog;
                $ufoLog->debug("@CLASSNAME@::selectByGroup()");
        }
        function selectByOids($oids=Null) {
                // Find the member data.
                @DBOBJECTDECL@
                global $ufoSession;
                global $ufoLog;

                // reset
                $this->@CLASSNAME@ = array();
                
                $this->pseudoType = 'explicit';
                if ( $oids != Null ) {
                        // Great
                } else {
                        // This is quite important.  Otherwise, when items() is called, it thinks it hasn't been initialized
                        // and falls back to implicit rules to initialize the container.  Bad.
                        $this->initialized = True;
                        return;
                }
                
                if ( is_array( $oids ) ) {
                        $oids = implode(',', $oids);
                }

                // limit to the session user id
                $uid = $ufoSession->getUID();
                
                $limit = $this->maxItems + 1;

                //do not restrain admin from selecting items
                if (in_array('admin', $ufoSession->getRoles())) {
                    $uidInWhere = "";
                }
                else {
                    // FIXME: disabled uid constraint entirely
                    //$uidInWhere = "AND uid=" . $uid;
                    $uidInWhere = "";
                }
                $query = "SELECT @SQLCOLSPEC@ from @PREFIX@_@CLASSNAME@ where id in ($oids) $uidInWhere ORDER BY {$this->orderBy}"; // limit {$this->startIdx},{$limit}";
                $result = @EXEC_QUERY@

                $idx = 0;
                while ($row = @EXEC_FETCH_ASSOC@ ) {
                        // $ufoLog->info("Got item: {$idx}");
                        $to = new @PREFIX@_@CLASSNAME@(0);
                        $to->initRow( $row );
                        @CONTAINER_CAST_ITEM@
                        $this->@CLASSNAME@[] = $to;
                        $idx += 1;
                }

                 /* Free resultset */
                @EXEC_FREE_RESULT@
                $this->initialized = True;
        }
        function selectByContainer($cid) {
                // Find the member data.
                @DBOBJECTDECL@
                global $ufoSession;
                global $ufoLog;

                $this->cid = $cid;
                $this->pseudoType = 'container';

                $limit = $this->maxItems + 1;
                $query = "SELECT @SQLCOLSPEC@ from @PREFIX@_@CLASSNAME@ where cid=$this->cid ORDER BY {$this->orderBy}"; // limit {$this->startIdx},{$limit}";
                $result = @EXEC_QUERY@

                $idx = 0;
                while ($row = @EXEC_FETCH_ASSOC@ ) {
                        // $ufoLog->info("Got item: {$idx}");
                        $to = new @PREFIX@_@CLASSNAME@(0);
                        $to->initRow( $row );
                        @CONTAINER_CAST_ITEM@
                        $this->@CLASSNAME@[] = $to;
                        $idx += 1;
                }

                 /* Free resultset */
                @EXEC_FREE_RESULT@
                $this->initialized = True;
        }
        function link() {
                global $ufoGlobals;
                global $page;
                $c = "";
                if ( $this->pseudoType == 'container') {
                        $c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?obj=@CONTAINERNAME@&ufo[cid]={$this->cid}&page=@CONTAINERNAME@\">@CONTAINERNAME@</a>";
                } elseif ( $this->pseudoType == 'group') {
                        $c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?obj=@CONTAINERNAME@&ufo[gid]={$this->gid}&page=@CONTAINERNAME@\">@CONTAINERNAME@</a>";
                } else {
                        $c = "<a href=\"http://{$ufoGlobals->domain}/{$ufoGlobals->rootdir}/main.php?obj=@CONTAINERNAME@&ufo[uid]={$this->uid}&page=@CONTAINERNAME@\">@CONTAINERNAME@</a>";

                }
                return $c;
        }
        function @RETURN_BY_REFERENCE@add(@CONTAINER_FUNCTION_ADD_SIGNATURE@) {
                global $ufoLog;
                global $ufoSession;

                // check if we have quota.
                if ($obj != Null) {
                   if ( is_array($obj) ) {
                        // append the whole array
                        $this->@CLASSNAME@ = array_merge( $this->@CLASSNAME@, $obj );
                        return $obj;
                   } elseif ( is_object($obj) ) {                 
                        // just add this to items
                        // FIXME: really should assert the type is correct.
                        $this->@CLASSNAME@[] @ASSIGN_BY_REF@ $obj;
                        return $obj;
                   } else {
                        // not know what to do with this thing.
                        return Null;
                   }
                } else {

                        
                        // create an empty @CLASSNAME@.
                        $o = $ufoSession->allocate( @CONTAINER_FUNCTION_ADD_CLASSNAME@ );
                
                        // initialize to defaults
                        $o->initialize();
                        
                        $ufoLog->debug("Setting uid to {$this->uid}");
                        $ufoLog->debug("Setting gid to {$this->gid}");
                        $ufoLog->debug("Setting cid to {$this->cid}");
                        $o->uid = $this->uid;
                        $o->gid = $this->gid;
                        $o->cid = $this->cid;

                        $this->addedObject @ASSIGN_BY_REF@ $o;

                        // This is so the state of the new object is editable for gui view.
                        $o->edit();

                        // add it to the @CLASSNAME@ array.
                        $this->@CLASSNAME@[] @ASSIGN_BY_REF@ $o;

                        // Return the new object
                        return $o;
                }
        }
        // asking a container to copy its members.  kind of only makes sense if we tell it WHERE to 
        // copy its members.  i.e. to another container.   So, $to should be another container.
        function _copy($toContainer, $recurse=False ) {
               foreach ( $this->items() as $item ) {
                       @CONTAINER_FUNCTION_COPY_IMPL@
                       $item->_copy($obj, $recurse);
               }
        }
        function move($oid) {
               $this->cid = $oid;
               foreach ( $this->@CLASSNAME@ as $item ) {
                       $item->move($oid);
               }
        }
        function chown($uid, $gid, $recurse=False) {
               $this->uid = $uid;
               $this->gid = $gid;
               foreach ( $this->@CLASSNAME@ as $item ) {
                       $item->chown($uid, $gid, $recurse);
               }
        }
        function delete($argv) {
           if ( isset($argv['recurse']) ) {
              $this->_delete( $argv['recurse'] );
           } else {
              $this->_delete();
           }
        }
        function _delete($recurse=False) {
               // This obviously needs work.
               while ( ($item = array_pop($this->@CLASSNAME@)) != Null ) {
                       $item->_delete($recurse);
                       // Check if delete worked, if not put it back on.
               }
        }
        function control( $argv ) {

                $this->initialize();

                if ( isset($argv['method'])) { 
                        $method = $argv['method'];
                }

                if ( isset($argv['oids']) && is_array( $argv['oids'] ) ) {
                        $oids = $argv['oids'];
                        $idx = 0;

                        // PHP4-safe iterate references
                        foreach ( array_keys($this->@CLASSNAME@) as $key ) {
                                $r =& $this->@CLASSNAME@[$key];
                                if ( array_key_exists($r->oid, $oids ) ) {

                                        if ( !strcasecmp($method,'delete') ) {
                                                $this->initialized = False;
                                                $r->delete($argv);
                                                unset($this->@CLASSNAME@[$idx]);
                                        }
                                }
                                $idx++;
                        }

                }
        }

        /* Select a subset of items, given a filter clause, owner id, 
         * starting index, max items, and order by column name.
         */
        function select($argv) {
                $this->initialized = false;
                if (isset($argv['maxItems'])) {
                        $this->maxItems = $argv['maxItems'];
                }
                if (isset($argv['startIdx'])) {
                        $this->startIdx = $argv['startIdx'];
                }
                if (isset($argv['filter'])) {
                        $this->filter = $argv['filter'];
                }
                if (isset($argv['owner'])) {
                        $this->owner = $argv['owner'];
                }
                if (isset($argv['orderBy'])) {
                        $this->orderBy = $argv['orderBy'];
                }
                if (isset($argv['oids'])) {
                        $this->selectByOids( $argv['oids'] );
                }
        }

        // Array of members you want to emit during view.
        function setViewable($argv) {
                $this->viewable = array_merge( $this->viewable, $argv );
        }
        
        function viewAsMenuOptions() {
                $c = "";
                foreach ($this->items() as $item ) {
                        $oid = $item->oid;
                        $name = $item->identifiableName();
                        if (False) {
                                $select = "selected";
                        } else {
                                $select = "";
                        }
                        $c .= "<option value=\"{$oid}\" {$select}>{$name}</option>";
                }
                return $c;
        }
        function view_@CLASSNAME@($encoding='html') {
                $c = "";

                $c .= "<br><h3>@CONTAINERNAME@:</h3>";

                $c .= "
                <table class=\"@CLASSNAME@Listing\" cellspacing=\"0\">
                <form action=\"main.php?obj=@CONTAINERNAME@&method=control&ufo[recurse]=1&ufo[cid]={$this->cid}\" method=\"post\">
                ";
                $lfirst = True;
                $idx = 0;
                $numColumns = @NUM_VIEWABLE_ATTRS@ + 2;
                foreach ( $this->@CLASSNAME@ as $r ) {
                        $idx++;
                        // Only display maxItems
                        if ($idx >= $this->maxItems) {
                                break;
                        }
                        $oid = $r->oid;
                        if ( $lfirst ) {
                                $table_headers = "<td></td>";
                                $table_headers .= $r->table_headers();
                                $c .= "
                        <thead>
                        <tr>
                        {$table_headers}
                        <td>
                        Action
                        </td>
                        </tr>
                        </thead>
                        <tfoot>
                        <tr>
                        <td colspan=\"${numColumns}\">
                        <span style=\"margin-left:5px\">Selected:</span> 
                        <input type=\"submit\" name=\"ufo[method]\" value=\"delete\"></td>
                        </tr>
                        </tfoot>
                        <tbody>
                                ";
                                $lfirst = False;
                        }

                        // Alternate color of rows
                        if ( $idx % 2 ) {
                                $c .= "<tr class=\"alt\">";
                        } else { 
                                $c .= "<tr>";
                        }

                        $c .= "<td><input type=\"checkbox\" name=\"ufo[oids][{$oid}]\" value=\"{$oid}\"/></td>";
                        $c .= $r->viewAsTableRow();
                        $c .= "
                        <td>
                        <a href=\"" . $r->getViewLink() . "\">View</a> / <a href=\"" . $r->getDeleteLink() . "\">Delete</a>
                        </td>
                        </tr>";
                }
                if ( $lfirst ) {
                        $table_headers = "No @CLASSNAME@ objects created currently";
                        $c .= "
                        <tr>
                        {$table_headers}
                        </tr>
                        ";
                        $lfirst = False;
                }
                $c .= "</tbody></table></form>";
                return $c;
                
        }
        function viewJSON($addToRemoteCache=True) {
                @CONTAINER_VIEWJSONIMPL@
        }
        function viewXML() {
                return "viewXML Not Implemented";
        }
        function viewHTML() {
                $c = "";

                if ( $this->addedObject ) {
                        $c .= $this->addedObject->view();
                        return $c;
                }

                // lazy initialization
                $this->initialize();
                $c .= "<div id=\"@CONTAINERNAME@\">";
                $c .= $this->view_@CLASSNAME@();

                // Paging functions
                if ( $this->startIdx > 0 ) {
                        $prevIdx = $this->startIdx - $this->maxItems;
                        if ( $prevIdx < 0 ) {
                                $prevIdx = 0;
                        }
                        $c .= "<br>
                        <a href=\"main.php?page=@CONTAINERNAME@&obj=@CONTAINERNAME@&method=select&ufo[startIdx]={$prevIdx}&ufo[maxItems]={$this->maxItems}\">Previous {$this->maxItems}</a>";
                }
                if ( count($this->@CLASSNAME@) > $this->maxItems ) {
                        $nextIdx = $this->startIdx + $this->maxItems;
                        $c .= "<br>
                        <a href=\"main.php?page=@CONTAINERNAME@&obj=@CONTAINERNAME@&method=select&ufo[startIdx]={$nextIdx}&ufo[maxItems]={$this->maxItems}\">Next {$this->maxItems}</a>";
                }

                // If we have quota
                $c .= "<br>";
                if (True) {
                $c .= "
                <form action=\"main.php?page=@CONTAINERNAME@&obj=@CONTAINERNAME@&method=add&ufo[gid]={$this->gid}&ufo[cid]={$this->cid}\" method=\"post\">
                <input type=\"submit\" name=\"submit\" value=\"Add Entry\">
                </form>
                ";

                }
                $c .= "</div>";
                return $c;
        }
        function view($encoding='html') {
                // The implication of this is that some function call happened that changed what we want to view.
                // For example, maybe just a subset of the object.
                if ( $this->obuffer != Null ) {
                   return $this->obuffer;
                }
                if ($encoding == 'xml') {
                        return $this->viewXML();
                }
                if ($encoding == 'json') {
                        return $this->viewJSON();
                }
                if ($encoding == 'html') {
                        return $this->viewHTML();
                }
                // else
                return "";
        }
}
?>'''
                return c

        def CONTAINERTEMPLATE(self):
                c = r'''<?php
include_once('@PREFIX@_@CONTAINERNAME@_base.php');

class @PREFIX@_@CONTAINERNAME@ extends @PREFIX@_@CONTAINERNAME@_base {

        function @PREFIX@_@CONTAINERNAME@( $argv=0 ) {
                parent::@PREFIX@_@CONTAINERNAME@_base( $argv );
        }
        function initialize($argv=0) {
                // Override default method here.
                parent::initialize($argv);
        }
        // Generic way of accessing the list of objects in a container.
        function items($argv=0) {
                // Override default method here.
                return parent::items($argv);
        }
        function selectByUser($id=Null) {
                // Override default method here.
                return parent::selectByUser($id);
        }
        function selectByGroups($id=Null) {
                // Override default method here.
                return parent::selectByGroups($id);
        }
        function selectByContainer($id=Null) {
                // Override default method here.
                return parent::selectByContainer($id);
        }
        function link() {
                // Override default method here.
                return parent::link();
        }
        function control( $argv ) {
                // Override default method here.
                return parent::control($argv);
        }
        function add( $argv ) {
                // Override default method here.
                return parent::add();
	}
        function view_@CLASSNAME@($encoding='html') {
                // Override default method here.
                return parent::view_@CLASSNAME@();
        }
        function view($encoding='html') {
                // Override default method here.
                return parent::view($encoding);
        }
}
?>'''
                return c



