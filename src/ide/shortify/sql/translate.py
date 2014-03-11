#!/usr/bin/python
import re
import sys

handle = open(sys.argv[1], "rt")
contents = handle.read()
handle.close()


keywords = {
    "leedsa" : 0,
    "leedsb" : 1,
    "t100"   : 2,
    "villa3" : 3,
    "k2"     : 4,
    "t41"    : 5,
    "ov3"    : 6,
    "mx00"   : 7,
    "k3"     : 8}

def replace_keyword(matches):
    match = matches.group(1)
    #print "match: %s" % match

    if(keywords.has_key(match)):
        return "%s" % keywords[match]
    else:
        print "ERROR: Keyword %s not found" % match
    return "ERROR"

def replace_includes(matches):
    include_file = matches.group(2)

    include_handle = open(include_file, 'rt')
    contents = include_handle.read()
    include_handle.close()

    #print "include: %s" % include
    return contents

contents = re.sub("(@include \"(.*?)\")", replace_includes, contents)
contents = re.sub("\$\{(.*?)\}", replace_keyword, contents)

print contents


