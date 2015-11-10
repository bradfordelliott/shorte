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

from src.shorte_defines import *
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
    
    def get_index_name(self):
        '''This method is called to fetch the name to associate
           with the index file.

           @return The name of the index file which is something
                   like index.tpl
        '''

        if(self.m_engine.has_output_file()):
            index_name = self.m_engine.get_output_file()
            return index_name

        return "index.tpl"
    
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

                if(not tag.has_source()):
                    continue

                source += "@" + tag.get_name()
                if(tag.has_modifiers()):
                    source += ":"
                    for modifier in tag.get_modifiers():

                        name = modifier
                        value = tag.get_modifier(name)

                        source += ' %s="%s"' % (name, value)

                    source += '\n'

                    #source += "\n" + tag.source + "\n\n"

                if(tag.get_name() in ("h1", "h2", "h3", "h4", "h5", "h")):
                    source += " " + tag.get_source() + "\n\n"
                else:
                    if(tag.has_source()):
                        source += "\n" + tag.get_source() + "\n\n"

        
        file = open(self.m_engine.m_output_directory + os.sep + self.get_index_name(), "w")
        file.write(source)
        file.close()

