<html>
<body>
<br>
<h1>UFO: a declarative object system for the web.</h1>
<span style="font-weight: bold;">Author: Russell Balest<br>
E-mail: russell@balest.com<br>
Copyright (C) 2004 Russell Balest<br>
<br>
</span>
<hr style="width: 100%; height: 2px;"><span style="font-weight: bold;"></span><br>
<big><big><span style="font-weight: bold;">
Forward:<br>
</span></big></big>
Generically referred to as 'UFO', this is a system for writing
object-oriented frameworks for web applications using a declarative
model based on XML.&nbsp; The main function of UFO is to generate code
artifacts derived from XML declarations.&nbsp; These artifacts are
things like PHP code and SQL statements for inserts, updates, and table
creation in a database, which together implement a simple object model
for web applications.&nbsp; This version of
UFO is written in
Python and while simple usage requires no knowledge of Python, more
advanced usage does require Python programming.&nbsp; The system is
extensible and currently has support for PHP, Postgres, and
MySql.&nbsp; The
main use of UFO has been, for me, in generating large amounts of PHP
and Sql in order to reduce the amount of manual coding and
duplication - thus reducing errors.&nbsp; Currently, UFO provides me a
good starting point by generating alot of initial PHP and SQL code
which I can then customize manually where I need to.&nbsp; The ongoing
goal is to refine UFO and improve its declarative capabilities in order
to reduce the amount of manual coding.<br>
<br>
I began using the term UFO in Summer of 2003, but the basic idea had
been evolving since 1997 or earlier, written in various languages along
the way from Perl to Tcl/Tk.&nbsp; The term became thoroughly congealed
when, in 2004, I wrote a web application for a startup called
'Uffinity'.&nbsp; Much of my code was using the prefix 'uf_', and my
base object class was 'uf_object'.&nbsp; So, I started thinking of
'ufo' as short for 'Uffinity Objects', which only reinforced the
acronym.&nbsp; 
UFO is an application of the <a href="Docs/Filter.html"><span
 style="font-weight: bold;">Filter</span></a>
system.<span style="font-style: italic;"></span><br>
&nbsp; <br>

<h2>Simple Usage<br>
</h2>
<br>
&nbsp;UFO comes with a simple implementation of a program to read an
XML file
containing a &lt;ufo&gt; definition, and output the PHP class and Sql
table creation code.<br>
This program is called parseUfo.py and the simplest usage is:<br>
<span style="font-weight: bold;">parseUfo.py &lt;ufoFile&gt;</span><br>
<br>
where:<br>
&lt;ufoFile&gt; is an XML file containing the definition of a UFO such
as:<br>
<br>
---------------<br>
<span style="font-weight: bold;">&lt;ufo&gt;</span><br
 style="font-weight: bold;">
<span style="font-weight: bold;">&lt;class name="device"
oid="foreign"&gt;</span><br style="font-weight: bold;">
<span style="font-weight: bold;">&lt;var name="type" type="enum"
constraint="gps_device" label="Device Type"&gt; gps_device &lt;/var&gt;</span><br
 style="font-weight: bold;">
<span style="font-weight: bold;">&lt;var name="carrier" type="enum"
constraint="wireless_carrier" label="Carrier"&gt; carrier &lt;/var&gt;</span><br
 style="font-weight: bold;">
<span style="font-weight: bold;">&lt;var name="phone_number"
type="string" constraint="phone_number" label="Phone Number"&gt; phone
&lt;/var&gt;</span><br style="font-weight: bold;">
<span style="font-weight: bold;">&lt;/class&gt;</span><br
 style="font-weight: bold;">
<span style="font-weight: bold;">&lt;/ufo&gt;</span><br>
---------------<br>
<br>
The above example will produce 3 additional output files:
<span style="font-weight: bold;">ufo_device.php, ufo_device_base.php</span>,
and <span style="font-weight: bold;">ufo_device.mysql</span>.&nbsp;&nbsp;
The prefix 'ufo' is
configurable and may be set to something more meaningful
to your project.&nbsp;&nbsp; Generally speaking, the
<span style="font-weight: bold;">ufo_device_base.php</span> file should
never be edited manually.&nbsp; Manual
implementations are reserved for the user subclass defined in
<span style="font-weight: bold;">ufo_device.php</span>, in this example.<br>
The contents of the mysql file is simply the SQL necessary for creation
of a table called 'ufo_device', predictably.&nbsp; The contents of the
.php file are much more complicated.&nbsp; But, basically, a PHP class
called ufo_device is defined along with several methods like:&nbsp;
create, load, edit, submit, view, update, and a constructor.&nbsp;

The persistence methods are created in the <span
 style="font-weight: bold;">ufo_device_base.php</span> file and
act to synchronize the PHP object with it's persistent
form in the database.&nbsp; The view method returns html code suitable
for viewing, and editing an object.&nbsp; These methods are callable
from http GET and POST methods using the UFO mapping specified
later.&nbsp; In addition, these objects will be instantiated and
invoked within a larger framework that includes a security model and a
layout model.<br>
</body>
</html>