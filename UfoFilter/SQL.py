import Filter
import string
from re import sub
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

def makeGenerator( dialect, version=None ):
    if dialect == 'postgres':
        return PostgresDialect(version)
    elif dialect == 'mysql' or dialect == 'mysqli':
        return MySqlDialect(version)
    else:
        print "%s dialect not implemented" % dialect
        return None

# Generic Sql - abstract class
class Dialect(Filter.Context) :
    def __init__(self, atts=None):
        Filter.Context.__init__(self)
        self.ctx = atts

    # Need to implement this in concrete subclass 
    def insertSql(self):
        return "Not implemented"

    # Need to implement this in concrete subclass 
    def updateSql(self):
        return "Not implemented"

    def setContext ( self, context ):
        self.ctx = context
        # Add replacements to context
        # self.ctx.tagDefine('CREATETABLE', self.CREATETABLE)
        # self.ctx.tagDefine('EXEC_QUERY', self.EXEC_QUERY)
        # self.ctx.tagDefine('EXEC_FETCH_ASSOC', self.EXEC_FETCH_ASSOC)

# Concrete MySql implementation.
class MySqlDialect ( Dialect ):
    def __init__(self, version, atts=None):
        Dialect.__init__(self, atts)
        self.version = version
        #self.tagDefine('CLASSNAME', atts.className)
        #self.vars = atts.vars
        #self.className = atts.className
        #self.oid = atts.oid
        #self.table_prefix = atts.prefix

    def setContext ( self, context ):
        self.ctx = context

    def EXEC_QUERY( self ):

        # return '''mysql_query($query) or die("Query failed : " . mysql_error());'''
        return '''$@DBOBJECT@->query($query, @LOG_THE_QUERY_BOOL@);'''

    def EXEC_FETCH_ASSOC( self ):
        #return '''mysql_fetch_array($result, MYSQL_ASSOC)'''
        return '''$@DBOBJECT@->fetch($result)'''

    def EXEC_FREE_RESULT( self ):
        return ""

    def DBSEQNAME(self):
        """This is empty because MySql uses the auto increment 
           modifier to imply a sequence.
        """
        return ""

    def CREATETABLE(self):
        c = "CREATE TABLE IF NOT EXISTS %s_%s (" % (self.ctx.table_prefix, self.ctx.className)
        if self.ctx.oid == 'foreign':
            c = c + "id INT UNSIGNED NOT NULL PRIMARY KEY, uid INT UNSIGNED, gid INT UNSIGNED, cid INT UNSIGNED"
        elif self.ctx.atts.is_interface:
            c = c + "id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY, uid INT UNSIGNED, gid INT UNSIGNED, cid INT UNSIGNED, vptr INT UNSIGNED, vptr_class VARCHAR(64) );"
            return c
        else:
            if self.ctx.atts.extends:
                c = c + "id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY, uid INT UNSIGNED, gid INT UNSIGNED, cid INT UNSIGNED, pid INT UNSIGNED"
            else:
                c = c + "id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY, uid INT UNSIGNED, gid INT UNSIGNED, cid INT UNSIGNED"
        for v in self.ctx.vars:
            if v.transient:
                continue
            elif v.type == 'collection':
                continue
            elif v.type == 'method':
                continue
            else:
                None
                
            if v.type == "object" and v.is_reference:
                print "%s is an object reference" % v.name,
                if v.reference.is_polymorphic:
                    print "And it's polymorphic"
                    # Add a column for the derived type
                    c = c + ", "
                    c = c + "%s_class %s" % (v.name, self.sqlType( v.reference.repr ))
                    
            c = c + ", "
            c = c + "%s %s" % (v.name, self.sqlType( v ))

            if v.default != None:
                # Look closely, bool needs quotes whereas enum does not.
                # doh!  mysql 5 chokes on quoted 'false'.  removed quotes on bools.
                if v.type == 'bool':
                    if self.version == "5":
                        c = c + " default %s" % (v.default)
                    else:
                        cdef = string.lower(v.default)
                        if cdef == 'true':
                            cval = '1'
                        else:
                            cval = '0'
                        c = c + " default %s" % (cval)

                elif v.type == 'string':
                    c = c + " default '%s'" % (v.default)
                elif v.type == 'enum':
                    c = c + " default '%s'" % (v.default)
                elif v.type == 'timestamp':
                    # MySQL can take ISO-8601 datetimes, but only if there isn't any punctuation.
                    # e.g., "19700101T000000" works, but not "1970-01-01T00:00:00"
                    c = c + " default '%s'" % (sub("[^0123456789T]", "", v.default))
                elif v.type == 'object':
                    if v.select == 'multiple':
                        None
                else:
                    c = c + " default %s" % (v.default)
            else:
                if v.type == 'object':
                    if v.select == 'multiple':
                        None
                        # No defaults on text/blob columns
                    else:
                        c = c + " default 0"

        for v in self.ctx.indices:
            c = c + ", "
            if v.unique:
                c = c + "UNIQUE "
            c = c + "INDEX %s ( %s )" % (v.name, ','.join(v.columns))
        c = c + ");"
        
        return c

    # Map ufo types to MySql types
    def sqlType(self, v):
        
        if v.select == 'multiple':
            return 'TEXT'
        
        if v.type == 'string':
            if int(v.width) < 256:
                return "VARCHAR(%s)" % (v.width)
            else:
                return "TEXT"
        elif v.type == 'blob':
            return 'longblob'
        elif v.type == 'object':
            return "int"
        elif v.type == 'bool':
            return 'bool'
        elif v.type == 'currency':
            return 'decimal(10,2)'
        elif v.type == 'timestamp':
            return 'datetime'
        elif v.type == 'real_timestamp':
            return 'timestamp'
        elif v.type == 'date':
            if v.constraint == 'day':
                return 'date'
            else:
                return 'date'
        elif v.type == 'enum':
            if v.constraint.source == 'enumerated':
                vals = ""
                first = True
                for val in v.constraint.values:
                    val = "'%s'" % val
                    if not first:
                        vals = vals + ','
                    else:
                        first = False
                    vals = vals + val
                kw = "enum"
                if v.select == 'multiple':
                    kw = "set"
                return "%s (%s)" % (kw, vals)
            elif v.constraint.source == 'table':
                return "varchar(255)"
            elif v.constraint.source == 'range':
                None
            else:
                print "Unknown constraint source: %s" % v.constraint.source
        else:
            return v.type

    def insertSql(self):
        c = ""
        if self.ctx.oid == 'foreign':
            vars = "id,uid,gid,cid"
            ss = "%s,%s,%s,%s"
            values = "$this->oid,$this->uid,$this->gid,($this->cid!=null)?$this->cid:0"
            nvars = 4
        else:
            if self.ctx.atts.extends:
                vars = "uid,gid,cid,pid"
                ss = '%s,%s,%s,%s'
                values = "$this->uid,$this->gid,($this->cid!=null)?$this->cid:0,($this->pid!=null)?$this->pid:0"
                nvars = 4
            elif self.ctx.atts.is_interface:
                vars = "uid,gid,cid,vptr,vptr_class"
                ss = "%s,%s,%s,%s,'%s'"
                values = "$this->uid,$this->gid,($this->cid!=null)?$this->cid:0,($this->vptr!=null)?$this->vptr:0,$this->vptr_class"
                nvars = 5
            else:
                vars = "uid,gid,cid"
                ss = '%s,%s,%s'
                values = "$this->uid,$this->gid,($this->cid!=null)?$this->cid:0"
                nvars = 3

        # Ignore member variables on interface classes
        if self.ctx.atts.is_interface:
            classvars = []
        else:
            classvars = self.ctx.vars
            
        for v in classvars:
            if v.persistence == 'transient' or v.transient == True:
                continue
            if v.type == 'collection':
                continue
            if v.type == 'method':
                continue
            if v.type == 'real_timestamp':
                continue
            if nvars > 0:
                vars = vars + ", "
                ss = ss + ", "
                values = values + ", "

            nvars = nvars + 1
            vars = vars + v.name

            if v.select == 'multiple':
                delim = ':'
                if v.type == 'enum':
                    delim = ','
                values = values + "$@DBOBJECT@->quote(implode('%s',array_values($this->%s)))" % (delim, v.name)
                ss = ss + "'%s'"
            else:
                if v.type == 'string':
                    values = values + "$@DBOBJECT@->quote($this->%s)" % v.name
                    ss = ss + "'%s'"
                elif v.type == 'blob':
                    values = values + "$this->%s" % v.name
                    ss = ss + "'%s'"
                elif v.type == 'date':
                    values = values + "$@DBOBJECT@->quote($this->%s)" % v.name
                    ss = ss + "FROM_UNIXTIME(%s)"
                elif v.type == 'timestamp':
                    values = values + "$this->%s?$this->%s:0" % (v.name, v.name)
                    ss = ss + "FROM_UNIXTIME(%s)"
                elif v.type == 'enum':
                    values = values + "$@DBOBJECT@->quote($this->%s)" % v.name
                    ss = ss + "'%s'"
                elif v.type == 'bool':
                    values = values + "$this->%s?'1':'0'" % v.name
                    ss = ss + "%s"
                elif v.type == 'int':
                    values = values + "$this->%s?$this->%s:0" % (v.name, v.name)
                    ss = ss + "%s"
                elif v.type == 'float':
                    values = values + "$this->%s?$this->%s:0.0" % (v.name, v.name)
                    ss = ss + "%s"
                elif v.type == 'currency':
                    values = values + "$this->%s?$this->%s:0.0" % (v.name, v.name)
                    ss = ss + "%s"
                elif v.type == 'object':
                    values = values + "is_object($this->%s)?$this->%s->oid:'0'" % (v.name, v.name)
                    ss = ss + "%s"
                    if v.is_reference:
                        if v.reference.is_polymorphic:
                            # update the classname column
                            nvars = nvars + 1
                            vars = vars + ", "
                            ss = ss + ", "
                            values = values + ", "
                            vars = vars + "%s_class" % v.name
                            values = values + "$this->%s_class" % (v.name)
                            ss = ss + "%s"
                else:
                    values = values + "$this->%s" % v.name
                    ss = ss + "%s"

        c = c + 'sprintf("INSERT INTO @TABLENAME@ (%s) VALUES (%s)", %s)' % (vars,ss,values)
        return c

    def updateSqlMeta(self):
        c = ""
        state = "SET uid=%s, gid=%s, cid=%s"
        vals = "$this->uid, $this->gid, $this->cid"
        where = 'id=$this->oid'

        c = c + 'sprintf("UPDATE @TABLENAME@ %s WHERE %s", %s);' % (state, where, vals)
        return c
    
    def updateSql(self):
        c = ""
        state = "SET "
        
        vals = ""
        where = 'id=$this->oid'
        nmutable = 0

        # Ignore member variables on interface classes
        if self.ctx.atts.is_interface:
            state = state + "%s=%s" % ("vptr", '%s')
            vals = vals + "$this->vptr"
            nmutable = nmutable + 1
            classvars = []
        else:
            # Need to update our pid because we don't know it on creation
            if self.ctx.atts.extends:
                state = state + "%s=%s" % ("pid", '%s')
                vals = vals + "$this->pid"
                nmutable = nmutable + 1
                
            classvars = self.ctx.vars

        for v in classvars:
            if v.persistence == 'transient' or v.transient == True:
                continue
            if v.mutable == False or v.mutable == 'onInit':
                continue
            if v.type == 'collection':
                continue
            if v.type == 'method':
                continue
            if v.type == 'real_timestamp':
                continue
            if v.const == False:
                if nmutable > 0:
                    state = state + ", "
                    vals = vals + ", "
                nmutable = nmutable + 1
                if v.select == 'multiple':
                    state = state + "%s='%s'" % (v.name, '%s')
                    delim = ':'
                    if v.type == 'enum':
                        delim = ','
                    vals = vals + "$@DBOBJECT@->quote(implode('%s',array_values($this->%s)))" % (delim, v.name)
                else:
                    if v.type == 'object':
                        if v.is_reference:
                            state = state + "%s=%s" % (v.name, '%s')
                            vals = vals + "is_object($this->%s)?$this->%s->oid:$this->%s" % (v.name,v.name,v.name)
                            if v.reference.is_polymorphic:
                                state = state + ", "
                                vals = vals + ", "
                                state = state + "%s_class=%s" % (v.name, '%s')
                                vals = vals + "is_object($this->%s)?$this->%s->className:$this->%s_class" % (v.name,v.name,v.name)
                        else:
                            state = state + "%s=%s" % (v.name, '%s')
                            vals = vals + "$this->%s->oid" % v.name
                    elif v.type == 'string':
                        state = state + "%s='%s'" % (v.name, '%s')
                        vals = vals + "$@DBOBJECT@->quote($this->%s)" % v.name
                    elif v.type == 'blob':
                        # Don't update blobs for now.
                        #state = state + "%s='%s'" % (v.name, '%s')
                        #vals = vals + "$this->%s" % v.name
                        None
                    elif v.type == 'int':
                        state = state + "%s=%s" % (v.name, '%s')
                        vals = vals + "$this->%s?$this->%s:0" % (v.name, v.name)
                    elif v.type == 'float':
                        state = state + "%s=%s" % (v.name, '%s')
                        vals = vals + "$this->%s?$this->%s:0.0" % (v.name, v.name)
                    elif v.type == 'currency':
                        state = state + "%s=%s" % (v.name, '%s')
                        vals = vals + "$this->%s?$this->%s:0.0" % (v.name, v.name)
                    elif v.type == 'bool':
                        state = state + "%s=%s" % (v.name, '%s')
                        vals = vals + "$this->%s?'1':'0'" % v.name
                    elif v.type == 'enum':
                        state = state + "%s='%s'" % (v.name, '%s')
                        vals = vals + "$@DBOBJECT@->quote($this->%s)" % v.name
                    elif v.type == 'date':
                        state = state + "%s=FROM_UNIXTIME(%s)" % (v.name, '%s')
                        vals = vals + "$@DBOBJECT@->quote($this->%s)" % v.name
                    elif v.type == 'timestamp':
                        state = state + "%s=FROM_UNIXTIME(%s)" % (v.name, '%s')
                        vals = vals + "$this->%s?$this->%s:0" % (v.name, v.name)
                    else:
                        state = state + "%s=%s" % (v.name,'%s')
                        vals = vals + "$this->%s" % v.name

        if nmutable > 0:
            c = c + 'sprintf("UPDATE @TABLENAME@ %s WHERE %s", %s)' % (state, where, vals)
        else:
            c = 'Null'
        return c

    def deleteSql(self):
        # Technically, there should be some kind of check on 
        # reference counting going on here, before deleting.
        return "delete from %s_%s where id = {$this->oid}" % (self.ctx.table_prefix, self.ctx.className)

# Concrete Postgres implementation.
class PostgresDialect ( Dialect ):
    def __init__(self, version, atts=None):
        Dialect.__init__(self, atts)
        self.version = version
        #self.tagDefine('CLASSNAME', atts.className)
        #self.vars = atts.vars
        #self.className = atts.className
        #self.oid = atts.oid
        #self.table_prefix = atts.prefix

    def setContext ( self, context ):
        self.ctx = context

    def EXEC_QUERY( self ):

        return '''pg_query($query) or die("Query failed : " . pg_last_error());'''

    def EXEC_FETCH_ASSOC( self ):
        return '''pg_fetch_assoc($result)'''

    def EXEC_FREE_RESULT( self ):
        return ""

    def DBSEQNAME(self):
        return "%s_%s_seq" % (self.ctx.table_prefix, self.ctx.className)

    def CREATETABLE(self):
        seq = ""
        constraint = ""

        c = "CREATE TABLE %s_%s (\n" % (self.ctx.table_prefix, self.ctx.className)
        if self.ctx.oid == 'foreign':
            c = c + " id INT UNSIGNED NOT NULL PRIMARY KEY,\n uid INT UNSIGNED"
        else:
            if self.ctx.owner:
                c = c + " id INT PRIMARY KEY DEFAULT nextval('%s_%s_seq')" % (self.ctx.table_prefix,self.ctx.className)
            else:
                c = c + " id INT PRIMARY KEY DEFAULT nextval('%s_%s_seq'),\n uid INT UNSIGNED" % (self.ctx.table_prefix,self.ctx.className)

            seq = "CREATE SEQUENCE %s_%s_seq;\n\n" % (self.ctx.table_prefix,self.ctx.className)

        for v in self.ctx.vars:
            c = c + ",\n "
            c = c + "%s %s" % (v.name, self.sqlType( v.type ))
            if v.default:
                if v.type == "string":
                    c = c + ' DEFAULT "%s"' % (v.default)
                else:
                    c = c + " DEFAULT %s" % (v.default)

            # Build constraints
            if v.constraint:
                vc = v.constraint
                if vc.source == 'table':
                    if vc.column:
                        constraint = constraint + """\nALTER TABLE ONLY "%s_%s ADD CONSTRAINT %s_cons FOREIGN KEY ("%s") REFERENCES "%s"("%s");""" % (self.ctx.table_prefix,self.ctx.className,v.name,v.name,vc.table,vc.column)
                    else:
                        constraint = constraint + """\nALTER TABLE ONLY "%s ADD CONSTRAINT %s FOREIGN KEY ("%s") REFERENCES "%s"("%s");""" % (self.ctx.table_prefix,self.ctx.className,v.name,v.name,vc.table,"value")

        c = c + ");\n"
        c = seq + c + constraint
        return c

    # Map ufo types to pgsql types
    def sqlType(self, t):
        if t == 'string':
            return "text"
        else:
            return t

    def insertSql(self):
        c = ""
        if self.ctx.oid == 'foreign':
            vars = "uid"
            values = "$this->uid"
            nvars = 1
        else:
            vars = "uid"
            values = "$this->uid"
            nvars = 1
        for v in self.ctx.vars:
            if nvars > 0:
                vars = vars + ", "
                values = values + ", "
            nvars = nvars + 1
            vars = vars + v.name
            if v.select == 'multiple':
                delim = ':'
                if v.type == 'enum':
                    delim = ','
                values = values + "'\" . $@DBOBJECT@->quote(implode('%s',array_keys($this->%s))) . \"'" % (delim, v.name)
            else:
                if v.type == 'string':
                    values = values + "'$this->%s'" % v.name
                else:
                    values = values + "$this->%s" % v.name

        c = c + "INSERT INTO @TABLENAME@ (%s) VALUES (%s)" % (vars,values)
        return c

    def updateSql(self):
        c = ""
        state = "set "
        nmutable = 0
        for v in self.ctx.vars:
            if v.const == False:
                if nmutable > 0:
                    state = state + ", "
                nmutable = nmutable + 1
                if v.select == 'multiple':
                    delim = ':'
                    if v.type == 'enum':
                        delim = ','
                    state = state + "%s='\" . $@DBOBJECT@->quote(implode('%s',array_keys($this->%s))) . \"'" % (v.name, delim, v.name)
                else:
                    state = state + "%s='$this->%s'" % (v.name,v.name)
        c = c + "UPDATE @TABLENAME@ %s WHERE id=$oid" % (state)
        return c

    def deleteSql(self):
        return "delete from %s_%s where id = {$this->oid}" % (self.ctx.table_prefix, self.ctx.className)

