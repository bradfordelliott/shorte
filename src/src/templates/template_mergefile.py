#!/usr/bin/env python
#+------------------------------------------------------------------------------
#|
#| SCRIPT:
#|    template_mergefile.py
#|
#| FILE DESCRIPTION:
#|    This module contains the mergefile template. This is used to merge a
#|    list of input shorte files into one large book for easier distribution.
#|
#+-------------------------------------------------------------------------------
#|
#| Copyright (c) Brad Elliott
#|
#+------------------------------------------------------------------------------
import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from shorte_defines import *
from template import *


class template_mergefile_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_inline = False
        self.m_num_prototypes = 0
        self.m_num_structs = 0
        self.m_num_enums = 0
    
    def generate(self, theme, version, package):

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()

        source = '''
@doctitle Merge File
@docsubtitle Merge File
@docversion 1.0

@body
'''
        
        for page in pages:

            #print "PAGE: %s" % page["title"]
            
            tags = page["tags"]

            for tag in tags:

                #print "TAG = %s" % tag.name

                source += "@" + tag.name
                if(tag.modifiers != None and (len(tag.modifiers) > 0)):

                    source += ":"
                    for modifier in tag.modifiers:

                        name = modifier
                        value = tag.modifiers[name]

                        source += ' %s="%s"' % (name, value)

                    source += "\n" + tag.source + "\n\n"

                elif(tag.name in ("h1", "h2", "h3", "h4", "h5", "h")):
                    source += " " + tag.source + "\n\n"
                else:
		    if(tag.source != None):
                        source += "\n" + tag.source + "\n\n"

        
        file = open(self.m_engine.m_output_directory + "/book.tpl", "w")
        file.write(source)
        file.close()

