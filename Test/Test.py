#!/usr/bin/env python

import sys
import Filter

class TestContext( Filter.Context ):
	def __init__(self):
		Filter.Context.__init__(self)

	def FOO(self, a, b, c=None):
		return "@_" + a + b + c + "@"
		
if __name__ == '__main__':

    # A trivial but useful implementation of configure
    def usage():
        print "usage: Filter.py <tagfile> <infile> <outfile>"

    argc = len(sys.argv)
    if argc < 3:
        print "Not enough arguments"
        usage()
        sys.exit(1)
    
    tagfile = sys.argv[1]
    infile = sys.argv[2]
    outfile = sys.argv[3]

    # Load a context from tagfile
    ctx = TestContext()
    ctx.ENABLE_TAG_APPENDS = 1
    ctx.loadTagDefs(tagfile)

    # Parse the infile for tags!!
    Filter.Parser(infile, outfile, ctx)
    
    sys.exit(0)
