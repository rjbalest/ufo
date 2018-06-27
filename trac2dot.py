#!/usr/bin/env python
import string
import re
import sys

class TracEdge:
    def __init__(self, fromNode, toNode):
	self.fromNode = fromNode
	self.toNode = toNode

class TracNode:
    def __init__(self, name):
	self.name = name
	self.component = None
	self.version = None
	self.owner = 'unknown'
	self.summary = ''
	self.type = ''
	self.status = ''
	self.priority = ''

class TracTicketParser:

    def __init__(self, infile):

	self.rank = { '1.0' : [0] }
	self.nodes = []
	self.edges = []
	self.components = {}

	self.owners = {}
	self.owners[""] = 0
	self.nOwners = 1

	self.componentMap = {}
	self.componentMap[""] = 0
	self.nComponents = 1

	self.shapes = ['pentagon','ellipse','egg','rect','diamond','triangle','hexagon','house','trapezium','invtriangle','parallelogram','Mcircle','Mdiamond','Msquare']

	self.colors = ['black','blue','green','red','yellow','orange','wheat','violet','grey','cadetblue','firebrick','magenta','saddlebrown','burlywood','yellow','orange','green','violet','grey','red','white','blue']

	self.peripheries = {}
	self.peripheries['trivial'] = 0
	self.peripheries['minor'] = 1
	self.peripheries['major'] = 2
	self.peripheries['critical'] = 3
	self.peripheries['blocker'] = 4

	self.rootNode = TracNode("0")

        self.deprex = re.compile('(?P<dep>#(?P<id>[0-9]+))')

	#dirname = os.path.dirname(infile)

	inf = open(infile, 'r')
	linecount=0
    
	for line in inf.readlines():
	    linecount = linecount + 1
	    # Skip the header line
	    if linecount == 1:
		continue
	    try:
		(color,id,keywords,summ,comp,vers,milestone,type,owner,created,modified,description,reporter,priority,status) = string.split(line, ',')

		print "Got ticket: %s" % id
		n = TracNode(id)

		# Clean up the owners.  WTF doesn't Trac have real Users?
		n.owner = string.split(owner)[0]
		print "Got owner: %s" % n.owner

		n.summary = summ
		n.component = comp
		n.type = type
		n.priority = priority
		n.status = status

		self.nodes.append(n)

		if self.owners.has_key(owner):
		    None
		else:
		    self.owners[owner] = self.nOwners
		    self.nOwners = self.nOwners + 1

		if self.componentMap.has_key(comp):
		    None
		else:
		    self.componentMap[comp] = self.nComponents
		    self.nComponents = self.nComponents + 1


		if milestone != '':
		    if self.rank.has_key(milestone):
			self.rank[milestone].append(id)
		    else:
			self.rank[milestone] = [id]
		else:
		    if self.rank.has_key('0.9'):
			self.rank['0.9'].append(id)
		    else:
			self.rank['0.9'] = [id]


		# Catalog Nodes by Component as well
		if self.components.has_key(comp):
		    self.components[comp].append(n)
		else:
		    self.components[comp] = [n]

		reo = self.deprex.search(keywords)
		if reo and reo.group('id'):
		    depId = reo.group('id') 
		    # Add an Edge
		    e = TracEdge(id, depId)
		    print "Got dependency %s => %s" % (id, depId)
		    self.edges.append(e)
		else:
		    print "No Deps"
		    e = TracEdge(self.rootNode.name, id)
		    self.edges.append(e)
	    except:
		print "Exception while parsing line: %d" % linecount
		raise

	inf.close()

    def writeNodesAsSubgraph(self, component ):

	outf = self.outf

	for n in self.components[component]:

	    if n.name == "0":
		url = "http://ambassador.sitepen.com"
	    else:
		url = "http://projects.sitepen.com/trac/ambassador_cap/ticket/%s" % n.name

	    if self.owners.has_key(n.owner):
		ownerId = self.owners[n.owner]
	    else:
		ownerId = 0

	    #color = self.colors[ownerId]
	    color = 'red'

	    print "owner: %s" % n.owner

	    shape = self.shapes[ownerId]

	    compId = self.componentMap[component]
	    fillColor = self.colors[compId]

	    peripheries = self.peripheries[n.priority]

	    #label = "%s %s" % (n.name,n.owner)
	    label = n.name
	    tooltip = n.summary

	    if ownerId == 0:
		fontcolor = 'white'
	    else:
		fontcolor = 'black'

	    outf.write('\t\t%s [shape = %s, peripheries=%d, label="%s", color = %s, fillcolor=%s, fontcolor = %s, URL = "%s", tooltip="%s",target="trac"];\n' % (n.name,shape,peripheries,label,color,fillColor,fontcolor,url,tooltip))


    def makeDOT(self, outfile):

	outf = open(outfile, 'w')
	self.outf = outf

	linecount=0
	
	print "Nowners = %d" % self.nOwners

	outf.write('''digraph ayp {
	graph [	fontname = "Times-Roman",
		fontsize = 48,
		labelfontsize = 48,
		label = "\\n\\n\\n\\nTicket Dep Graph",
		size = "14,14",
		ratio = "0.45",
		overlap = False ];
	node [	shape = polygon,
		sides = 5,
		distortion = "0.0",
		orientation = "0.0",
		skew = "0.0",
		color = black,
		style = filled,
		fontsize = 48,
		labelfontsize = 48,
		fontname = "Times-Roman" ];\n''')

	# Define All the Nodes
	# Timeline Nodes
	rk = self.rank.keys()
	rk.sort()
	for r in rk:
	    outf.write('\t"%s" [shape = plaintext, color=white];\n' % r)


	# Ticket Nodes
	for c in self.components:
	    cc = string.replace(c, ' ', '_')
	    outf.write('\tsubgraph %s {\n' % cc)
	    outf.write('\t\tlabel = %s;\n' % cc)
	    self.writeNodesAsSubgraph( c )
	    outf.write('\t}\n')


	# Rank definitions
	for r in rk:
	    outf.write('\t{rank=same; "%s"' % r)
	    for n in self.rank[r]:
		None
		outf.write(" %s" % n)
	    outf.write(';}\n')

	for n in self.nodes:
	    None

	for e in self.edges:
	    outf.write("\t%s -> %s;\n" % ( e.fromNode, e.toNode ))

	# Write invisible edges for timeline nodes.
	outf.write('\tedge [style=invis];\n')
	prev = None
	for r in rk:
	    if prev:
		outf.write('\t"%s" -> "%s";\n' % (prev, r))
	    prev = r

	outf.write("}\n")

if len(sys.argv) < 3:
    print "trac2dot.py <trac csv report>  <dot output file>"
    sys.exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]

tp = TracTicketParser( infile )
tp.makeDOT( outfile )

