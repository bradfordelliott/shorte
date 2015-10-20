# -*- coding: iso-8859-15 -*-
"""This is a basic parser implementation for markdown support. This
   is not fully completely but can parse basic markdown text
"""
import re
import sys
import os
from src.shorte_source_code import *
from src.shorte_includes import *
import platform
import time
import random
try:
    from PIL import Image
except:
    WARNING("Failed to load Image library. Try installing it using the command 'pip install Pillow'")

from shorte_parser_base import parser_t
from shorte_images import *

from src.templates.template_shorte import template_shorte_t

import src.shorte_defines


class markdown_parser_t(parser_t):
    def __init__(self, engine):

        parser_t.__init__(self)

        self.m_pages = []
        
        self.m_engine = engine

        self.m_include_queue = []
        self.m_snippets = {}
        self.m_urls = {}
        self.m_links = []

        self.m_title = None
        self.m_subtitle = None

        # Rough parser position of current
        # tag
        self.m_current_file = None
        self.m_current_tag = None
        self.m_current_line = 0

        self.m_lines = {}
        self.m_line_info = {}

        self.m_active_file = []

        self.m_headers = []

    def get_pages(self):
        return self.m_pages

    def get_title(self):
        
        if(self.m_title == None):
            return "untitled"

        return self.m_title
    
    def get_subtitle(self):

        if(self.m_subtitle == None):
            return "untitled"

        return self.m_subtitle
    
    def parse(self, source_file):
        """This method opens a markdown source file and parses its
           contents
        """

        if(source_file == "result"):
            return None

        #print "PARSE: %s" % source_file
        source = open(source_file, "r")
        input = source.read()
        source.close()

        self.m_active_file.append(source_file)
        #print "  Setting current file to %s, stack.len = %d" % (source_file, len(self.m_active_file))
        self.m_current_file = self.m_active_file[-1]
        result = self.parse_string(input, source_file)
        if(len(self.m_active_file) > 1):
            self.m_active_file.pop()
        self.m_current_file = self.m_active_file[-1]
        #print "  Setting current file to %s" % self.m_current_file

        return result
    
    def parse_buffer(self, data):

        output = ""
        start = 0
        end = len(data)

        STATE_NORMAL = 0
        STATE_HEADER = 1

        states = []
        states.append(STATE_NORMAL)

        i = start
        output = ""
            
        tag = tag_t()
        tag.file = source_file
        tag.line = 1

        while(i < end):
            state = states[-1]

            if(state == STATE_NORMAL):

                if((i == 0 or data[i-1] == "\n") and data[i] == "#"):
                    states.append(STATE_HEADER)
                    i += 1

                else:
                    tag.source += data[i]

            elif(state == STATE_HEADER):

                i += 1

        return output

    def parse_string(self, input, source_file="default.tpl", is_include=False):

        if(None == self.m_current_file):
            self.m_current_file = source_file

        # Strip any illegal characters
        #input = re.sub("[]", "'", input)
        #input = re.sub("", "", input)
        
        # Replace any references to Leeds
        #input = self.__search_and_replace(input)

        # Perform any preprocessing/expansion
        # of macros
        #macros = self.m_engine.get_macros()
        #tmp_macros = {}
        #for macro in macros:
        #    tmp_macros[macro] = macros[macro]
        #
        #expr = re.compile("<\?(.*?)\?>", re.DOTALL)
        #input = expr.sub(self._evaluate_macros, input)

        #if(not is_include):
        #    source_file = self.m_engine.search_and_replace(source_file)

        try:

            # Strip any \r characters
            input = input.replace("\r", "")

            # Replace any tabs
            input = input.replace("\t", TAB_REPLACEMENT)
            
            page = {}
            page["title"] = "TBD" #title
            page["subtitle"] = "TBD" # subtitle
            page["tags"] = []
            page["source_file"] = source_file
            page["links"] = self.m_links
            page["file_brief"] = ""
            page["file_author"] = ""
            #page["header"] = header

            end = len(input)

            lines = input.split("\n")
            i = 0

            tag = tag_t()
            tag.source = ""
            tag.file = source_file
            tag.line = 1
            tag.modifiers = {}

            num_lines = len(lines)

            i = 0
            while i < num_lines:
                line = lines[i] + "\n"
                
                # If the next line starts with ====== or ----- then this
                # might be a markdown header.
                if(i+1 < num_lines):
                    next_line = lines[i+1] + "\n"

                    if(next_line.startswith("====")):
                        if(len(tag.source) > 0):
                            tag.name = "text"
                            tag.contents = textblock_t(tag.source)
                            page["tags"].append(tag)
                    
                        tag = tag_t()
                        tag.name = "h1"
                        tag.contents = lines[i]
                        tag.source = lines[i]
                        tag.modifiers = {}
                        tag.page_title = page["title"]
                        tag.is_header = True
                        tag.file = source_file
                        tag.line = i-1

                        self.m_headers.append(tag)
                        
                        page["tags"].append(tag)

                        tag = tag_t()
                        tag.modifiers = {}
                        tag.page_title = page["title"]
                        tag.is_header = False
                        tag.source = ""
                        tag.file = source_file
                        tag.line = i

                        i += 2
                        continue

                    if(next_line.startswith("----")):
                        if(len(tag.source) > 0):
                            tag.name = "text"
                            tag.contents = textblock_t(tag.source)
                            page["tags"].append(tag)
                    
                        tag = tag_t()
                        tag.name = "h2"
                        tag.contents = lines[i]
                        tag.source = lines[i]
                        tag.modifiers = {}
                        tag.page_title = page["title"]
                        tag.is_header = True
                        tag.file = source_file
                        tag.line = i-1

                        self.m_headers.append(tag)
                        
                        page["tags"].append(tag)

                        tag = tag_t()
                        tag.modifiers = {}
                        tag.page_title = page["title"]
                        tag.is_header = False
                        tag.source = ""
                        tag.file = source_file
                        tag.line = i

                        i += 2
                        continue


                if(line.startswith("#")):

                    if(len(tag.source) > 0):
                        tag.name = "text"
                        tag.contents = textblock_t(tag.source)
                        page["tags"].append(tag)

                    name = lines[i].strip()
                    j = 0
                    level = 0
                    while(name[j] == "#"):
                        level += 1
                        j += 1

                    name = name[j:]

                    tag = tag_t()
                    tag.name = "h%d" % level
                    tag.contents = name
                    tag.source = name
                    tag.modifiers = {}
                    tag.page_title = page["title"]
                    tag.is_header = True
                    tag.file = source_file
                    tag.line = i-1

                    self.m_headers.append(tag)
                    
                    page["tags"].append(tag)

                    tag = tag_t()
                    tag.modifiers = {}
                    tag.page_title = page["title"]
                    tag.is_header = False
                    tag.source = ""
                    tag.file = source_file
                    tag.line = i

                else:
                    tag.source += line

                i += 1

            
            if(tag.source != ""):
                tag.name = "text"
                tag.contents = textblock_t(tag.source)
                tag.line = i
                tag.file = source_file
                page["tags"].append(tag)

            #for tag in page["tags"]:
            #    print tag
            #    print tag.contents

            if(not is_include):
                self.m_pages.append(page)
                return None
            else:
                return page

        except:
            import traceback
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)

            FATAL("Failed parsing markdown file")

        return None
