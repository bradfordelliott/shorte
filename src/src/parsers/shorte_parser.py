# -*- coding: iso-8859-15 -*-
#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   shorte_parser.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a parser class used to
#|   parse shorte documents in order to convert them into another output
#|   format.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import sys
import os
from src.shorte_source_code import *
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

import src.graphing.sequence_diagram as sequence_diagram
import src.shorte_defines

from libs.records import *

#class cell_t():
#    def __init__(self):
#        self.span = 1
#        self.text = ""
#        self.textblock = ""

class col_t():
    '''This class is used to manage a column within a table
       row which is used by declarations such as @struct, @register
       and @table
    '''

    def __init__(self):
        self.text = ""
        self.span = 1

class row_t():
    '''This class is used to manage a table row which is used
       by declarations such as @struct, @register, and @table
    '''

    def __init__(self):
        '''The constructor for the class'''

        self.cols = []
        self.is_heading = False
        self.is_subheading = False
        self.is_title = False
        self.is_spacer = False
        self.is_crossed = False
        self.is_reserved = False

    def __str__(self):
        '''Convert the row object into a human readable string
           for debug purposes'''

        output =  "ROW\n"
        output += "  is_spacer     = %s\n" % self.is_spacer
        output += "  is_heading    = %s\n" % self.is_heading
        output += "  is_subheading = %s\n" % self.is_subheading
        output += "  is_title      = %s\n" % self.is_title
        output += "  is_crossed    = %s\n" % self.is_crossed
        output += "  is_reserved   = %s\n" % self.is_reserved

        output += "  cols          = %d\n" % len(self.cols)
        for col in self.cols:
            output += indent_lines(col, "    > ")
        return output 

class shorte_header_t():
    def __init__(self):
        self.start = 0
        self.title = ""
        self.subtitle = ""
        self.version = ""
        self.toc = False
        self.numbered = False
        self.number = ""
        self.revision_history = None
        self.filename = None
        self.sourcedir = None
        self.outdir = None
        self.line = 0
        self.footer_title = None
        self.footer_subtitle = None
        self.doc_info = None
        self.author = None
        self.csource = None
        self.template = None
    def get_start(self):
        return self.start
    def get_line(self):
        return self.line
    def get_title(self):
        return self.title
    def get_subtitle(self):
        return self.subtitle
    def get_toc(self):
        return self.toc
    def get_numbered(self):
        return self.numbered
    def get_version(self):
        return self.version
    def get_number(self):
        return self.number
    def get_revision_history(self):
        return self.revision_history
    def get_author(self):
        return self.author
    def has_author(self):
        if(self.author != None):
            return True
        return False
    def has_filename(self):
        if(self.filename != None):
            return True
        return False
    def get_filename(self):
        return self.filename

    def has_csource(self):
        if(self.csource != None):
            return True
        return False
    def get_csource(self):
        return self.csource

    def __str__(self):
        print "Heading"
       

class shorte_parser_t(parser_t):
    def __init__(self, engine):

        self.m_pages = []
        
        self.m_engine = engine

        self.m_uid = 0

        # The list of valid tags supported by the language
        self.m_valid_tags = {
            "h1"              : True,
            "h2"              : True,
            "h3"              : True,
            "h4"              : True,
            "h5"              : True,
            "h"               : True,
            "p"               : True,
            "text"            : True,
            "note"            : True,
            "warning"         : True,
            "question"        : True,
            "tbd"             : True,
            "pre"             : True,
            "ul"              : True,
            "table"           : True,
            "struct"          : True,
            "define"          : True,
            "vector"          : True,
            "register"        : True,
            "ol"              : True,
            "image"           : True,
            "gallery"         : True,
            "inkscape"        : True,
            "gnuplot"         : True,
            "graph"           : True,
            "shell"           : True,
            "prototype"       : True,
            "class"           : True,
            "imagemap"        : True,

            "java"            : True,
            "verilog"         : True,
            "tcl"             : True,
            "vera"            : True,
            "python"          : True,
            "c"               : True,
            "cpp"             : True,
            "sql"             : True,
            "perl"            : True,
            "code"            : True,
            "batch"           : True,
            "d"               : True,
            "bash"            : True,
            "shorte"          : True,
            "xml"             : True,
            "swift"           : True,
            "go"              : True,
            "javascript"      : True,
            "include"         : True,
            "include_child"   : True,

            "checklist"       : True,
            "enum"            : True,
            "acronyms"        : True,
            "questions"       : True,
            "sequence"        : True,

            "functionsummary" : True,
            "typesummary"     : True,

            "embed"           : True,

            # Tags used to support test cases
            "testcase"        : True,
            "testcasesummary" : True,

            "doctitle"        : True,
            "doc.title"       : True,
            "footertitle"     : True,
            "docsubtitle"     : True,
            "doc.subtitle"    : True,
            "docnumber"       : True,
            "docauthor"       : True,
            "csource"         : True,
            "docrevisions"    : True,
            "docversion"      : True,
            "doc.version"     : True,
            "docfilename"     : True,
            "outdir"          : True,
            "sourcedir"       : True,
            "template"        : True,
            "doc.config"      : True,
            "doc.info"        : True,

            "doc.footer.title" : True,
            "doc.footer.subtitle" : True,

            # Layout tags
            "columns"         : True,
            "column"          : True,
            "endcolumns"      : True,

            # Form tags
            "input"           : True,

            # Just for doxygen compatibility
            "cond"            : True,
            "endcond"         : True,
        }

        # The tag hierarchy is used to determine
        # what tags belong to other tags. It is used
        # to cascade "if" modifiers so that child tags
        # are automatically excluded if a parent tag
        # is excluded.
        self.m_tag_hierarchy = {
            "body"    : 0,
            "include" : 1, # @include and @h1 should have same include priority
            "h1"      : 1,
            "h2"      : 3,
            "h3"      : 4,
            "h4"      : 5,
            "h5"      : 6,
            "h"       : 7,
            "include_child" : 8,
            "least"   : 100
        }

        # The list of tags that qualify as source code elements
        self.m_source_code_tags = {
            "python"     : True,
            "perl"       : True,
            "shell"      : True,
            "c"          : True,
            "cpp"        : True,
            "sql"        : True,
            "code"       : True,
            "batch"      : True,
            "vera"       : True,
            "bash"       : True,
            "java"       : True,
            "verilog"    : True,
            "tcl"        : True,
            "shorte"     : True,
            "xml"        : True,
            "swift"      : True,
            "go"         : True,
            "javascript" : True,
            }

        self.m_include_queue = []
        self.m_snippets = {}
        self.m_urls = {}
        self.m_links = []

        self.m_title = None
        self.m_subtitle = None

        # Track WikiWords in the document
        #self.m_wiki_links = {}

        # Rough parser position of current
        # tag
        self.m_current_file = None
        self.m_current_tag = None
        self.m_current_line = 0

        self.m_lines = {}
        self.m_line_info = {}

        self.m_active_file = []

        self.m_headers = []

    #def get_wiki_links(self):
    #    return self.m_wiki_links

    #def add_wiki_links(self, links):
    #    self.m_wiki_links = dict(self.m_wiki_links.items() + links.items())

            
    def reset(self):
        self.m_headers = []
        self.m_engine.m_wiki_links = {}
        self.m_links = []
        self.m_urls = {}
        self.m_snippets = {}
        self.m_include_queue = []
        self.m_pages = []

    def __search_and_replace(self, text):

        return self.m_engine.search_and_replace(text)

    def get_header(self, name):
        
        for header in self.m_headers:
            if(header.contents == name):
                return header

        return None

    def get_pages(self):
        return self.m_pages

    def get_title(self):
        
        if(self.m_title == None):
            return "untitled"

        return self.m_title

    def set_title(self, title):
        self.m_title = title
   
    def get_subtitle(self):

        if(self.m_subtitle == None):
            return "untitled"

        return self.m_subtitle
    
    def set_subtitle(self, subtitle):
        self.m_subtitle = subtitle

    def __parse_header(self, data):

        attr = {}

        header = ""

        start = data.find("@body")

        #print "START = %d" % start

        if(start == -1 or start == 0):
            attr = shorte_header_t()

            if(start == 0):
                attr.start = 5
            else:
                attr.start = 0
            
            attr.line = 1

            return attr

        tags = self._parse_header_tags("title", data[0:start-1], 0)
        if(tags == None):
            FATAL("Failed parsing header")

        line = 1
        for i in range(0, start):
            if(data[i] == '\n'):
                line += 1

        header = shorte_header_t()
        header.start = start + 5
        header.line = line + 1
        header.toc = False
        header.numbered = False
        header.title = "undefined"
        header.subtitle = ""
        header.version = "undefined"
        header.number = ""
        header.author = None
        header.revision_history = None
        header.filename = None
        header.outdir = None
        header.sourcedir = None
        header.footer_title = None
        header.footer_subtitle = None
        header.doc_info = None

        for tag in tags:
            if(tag.name in ("title", "doctitle", "doc.title")):
                header.title = tag.contents
            elif(tag.name in ("docfilename", "doc.filename")):
                header.filename = tag.contents
            elif(tag.name in ("docsubtitle", "doc.subtitle")):
                header.subtitle = tag.contents
            elif(tag.name in ("docauthor", "doc.author")):
                header.author = tag.contents
            elif(tag.name == "csource"):
                header.csource = tag.contents
            elif(tag.name in ("docversion", "doc.version")):
                header.version = tag.contents
            elif(tag.name in ("docnumber", "doc.number")):
                header.number = tag.contents
            elif(tag.name in ("docrevisions", "doc.revisions")):
                header.revision_history = self.parse_table(tag.contents, tag.modifiers)
            elif(tag.name in ("docinfo", "doc.info")):
                header.doc_info = tag.contents
            elif(tag.name == "sourcedir"):
                header.sourcedir = tag.contents
                self.m_engine.set_working_dir(header["sourcedir"])
            elif(tag.name == "template"):
                header.template = tag.contents
                name = tag.modifiers["name"]
                self.m_engine.get_doc_info().add_template(name, tag.contents)
            elif(tag.name == "outdir"):
                header.outdir = tag.contents
                self.m_engine.set_output_dir(header["outdir"])

            elif(tag.name in ("footertitle", "doc.footer.title")):
                header.footer_title = tag.contents
                self.m_engine.get_doc_info().set_footer_title(tag.contents)
            elif(tag.name in ("footersubtitle", "doc.footer.subtitle")):
                header.footer_subtitle = tag.contents
                self.m_engine.get_doc_info().set_footer_subtitle(tag.contents)
            elif(tag.name == "doc.config"):
                config_string = tag.contents
                parts = tag.contents.strip().split("=")
                (section,key) = parts[0].split(".")
                val = parts[1]
                shorte_set_config(section, key, val)
            else:
                WARNING("Unknown tag %s" % tag)

        return header

    def is_valid_tag(self, tag):
        
        if(self.m_valid_tags.has_key(tag)):
            return True

        return False
    
    def tag_is_source_code(self, tag_name):

        if(self.m_source_code_tags.has_key(tag_name)):
            return True

        #if(tag_name in ("python", "perl", "shell", "d", "c", "cpp", "sql", "code", "batch", "vera", "bash", "java", "verilog", "tcl", "shorte", "xml", "swift", "go", "javascript")):
        #   return True

        return False
    
    def tag_is_header(self, tag_name):
        
        if(tag_name in ("h1", "h2", "h3", "h4", "h5", "h")):
            return True

        return False

    def tag_is_executable(self, tag_name):

        if(tag_name in ("python", "perl", "d", "c", "cpp", "vera", "bash", "java", "verilog", "tcl", "batch", "swift", "go", "javascript")):
            return True

        return False
    
    def _parse_tag_data(self, tag_name, input, i, line_no):

        tag_data = []
        tag_modifier = []

        STATE_NORMAL     = 0
        STATE_COMMENT    = 1
        STATE_MCOMMENT   = 2
        STATE_MODIFIER   = 3
        STATE_MULTILINE_STRING = 4

        states = []
        states.append(STATE_NORMAL)

        # Skip any leading whitespace
        while(input[i] == ' ' or input[i] == '\t'):
            i = i + 1

        if(input[i] == ':'):
            states.append(STATE_MODIFIER)
            i += 1
        elif(input[i] == '\n'):
            line_no += 1
            i += 1

        while i < len(input):

            state = states[-1]
            
            if(input[i] == '\n'):
                line_no += 1
                
            if(input[i:i+4] == '<!--'):
                states.append(STATE_MCOMMENT)
                i += 4
                continue

            if(state == STATE_NORMAL):

                if(not self.tag_is_source_code(tag_name) and tag_name != "gnuplot"):
                    
                    # parse any comments
                    if(input[i] == '#'):
                        states.append(STATE_COMMENT)
                        i = i + 1
                        continue
                    
                # DEBUG BRAD: This is an attempt to skip
                #             inline @ so they don't need to
                #             be escaped
                #if(input[i] == '@'):
                if((i == 0 and input[i] == '@') or (input[i] == '@' and input[i-1] == '\n')):
                    if(input[i+1] == '{'):
                        tag_data.append(input[i])
                    else:
                        break 
                   
                # If we hit an escape sequence then skip it and
                # the next character
                elif(input[i] == '\\'):

                    # DEBUG BRAD: This is an attempt to strip
                    #             escape sequence backslashes
                    if(self.tag_is_source_code(tag_name)):
                        tag_data.append(input[i])
                    # DEBUG BRAD: Added this on Oct 19, 2013
                    else:
                        tag_data.append(input[i])

                    tag_data.append(input[i+1])
                    i+=2
                    continue


                else:
                    tag_data.append(input[i])

            elif(state == STATE_MODIFIER):
                
                if(input[i] == '\n'):
                    states.pop()
                elif(input[i:i+3] == "'''"):
                    #print "DO I GET HERE?"
                    tag_modifier.append('"')
                    states.append(STATE_MULTILINE_STRING )
                    i = i + 3
                    continue
                else:
                    tag_modifier.append(input[i])

            elif(state == STATE_MULTILINE_STRING):
                if(input[i:i+3] == "'''"):
                    states.pop()
                    i = i + 2
                    #print "MODIFIER: [%s]" % tag_modifier
                    tag_modifier.append('"')
                else:
                    tag_modifier.append(input[i])

            elif(state == STATE_MCOMMENT):
                if(input[i:i+3] == '-->'):
                    states.pop()
                    i += 2
            elif(state == STATE_COMMENT):
                if(input[i] == '\n'):
                    states.pop()


            i = i + 1

        #print "TAG:\n  DATA: [%s]\n  MODIFIERS: [%s]" % (tag_data, tag_modifier)

        return (i, line_no, ''.join(tag_data), ''.join(tag_modifier))
    
    def parse_inline_image_str(self, data):
        tags = self.parse_modifiers(data)
        return self.parse_inline_image_data(tags)

    def parse_inline_image(self, matches):

        name = matches.groups()[0]

        tags = {}
        tags["src"] = name
        
        if(len(matches.groups()) > 1):
            tags = self.parse_modifiers(matches.groups()[3])
            if(not tags.has_key("caption")):
                tags["caption"] = matches.groups()[1]

        return self.parse_inline_image_data(tags)


    def parse_inline_image_data(self, tags):
            
        image = {}
        src = os.path.abspath(tags["src"])
        dirname = os.path.dirname(src) + os.path.sep

        name = src.replace(dirname, "")
        parts = os.path.splitext(name)
        basename = parts[0]
        ext = parts[1]
        
        image["src"] = src
        image["name"] = basename
        image["ext"] = ext
        
        if(tags.has_key("height")):
            image["height"] = tags["height"]
        if(tags.has_key("width")):
            image["width"] = tags["width"]
        if(tags.has_key("caption")):
            image["caption"] = tags["caption"]
        if(tags.has_key("center")):
            image["center"] = True
        if(tags.has_key("href")):
            image["href"] = tags["href"]

        image["reference"] = self.m_current_file

        self.m_engine.m_images.append(src)

        return image
                            
    def is_reserved_text(self, value):
        
        if(value == "Reserved" or value == 'reserved' or value == 'Rsvd' or value == 'rsvd'):
            return True

        return False


    def parse_questions(self, data, modifiers):

        lines = re.split("\n", data)

        question = ''
        answer   = ''

        questions = []

        for line in lines:
            if(line[0:2] == "Q:"):
                if(question != ''):

                    if(answer != ''):
                        answer = answer[2:].strip()

                    questions.append({
                        "question" : question[2:].strip(),
                        "answer"   : answer
                        })
                    question = ''
                
                question += line + ' '
                answer = ''

            elif(line[0:2] == "A:"):
                answer += line + ' '

            elif(answer == ''):
                question += line + ' '
            else:
                answer += line + ' '

        if(question != ''):

            if(answer != ''):
                answer = answer[2:].strip()

            questions.append({
                "question" : question[2:].strip(),
                "answer"   : answer
                })

        return questions


    def parse_sequence_old(self, source, modifiers):
        '''This method is called to parse the @sequence tag
           and generate a sequence diagram from it'''

        table = self.parse_table(source, modifiers).dict

        xml = '''<xml>
   <diagram>
      <title>%s</title>
      <desc>%s</desc>
''' % (xmlize(table["title"]), xmlize(table["caption"]))
        
        index = 0
        for row in table["rows"]:

            if(index == 0):
                index += 1
                continue
            index += 1

            cols = row["cols"]

            type = cols[0]["text"]
            src  = cols[1]["text"]
            dst  = cols[2]["text"]
            name = cols[3]["text"]
            desc = cols[4]["text"]

            if(len(cols) >= 5):
                action = cols[4]["text"]
            else:
                action = ""

            attributes = name.split(",")

            matches = re.search("\[\[(.*)\]\]", name, re.DOTALL)
            if(matches != None):
                link = "<link>%s</link>" % matches.groups()[0]
                name = matches.groups()[0]
            else:
                link = ""

            if(type == "message"):
                xml += '''
      <event type="message" from="%s" to="%s">
         <name>%s</name>
         <desc>%s</desc>
         %s
      </event>
''' % (xmlize(src), xmlize(dst), xmlize(name), xmlize("<b>" + name + "</b><br/>" + desc + "</b>"), link)
            elif(type == "action"):
                xml += '''
      <event type="action" src="%s">
         <name>%s</name>
         <desc>%s</desc>
      </event>
''' % (xmlize(src), xmlize(name), xmlize("<b>" + name + "</b><br/>" + desc + "</b>"))

        xml += '''
    </diagram>
</xml>
'''
        if(table.has_key("title")):
            name = table["title"]
        if(table.has_key("name")):
            name = table["name"]

        path = pathize(name)
        
        parts = os.path.splitext(path)
        basename = parts[0]
        ext = parts[1]
        dirname = os.path.dirname(basename) + os.path.sep

        DEBUG("PATH: %s" % path)

        handle = open(path, "wb")
        handle.write(xml)
        handle.close()

        os.popen("sequencediagram.pl %s %s" % (path, basename))

        handle = open("image.map", "rb")
        image_map = handle.read()
        handle.close()

        handle = open("events.html", "rb")
        event_html = handle.read()
        handle.close()

        image = {}
        image["src"] = os.path.abspath(basename + ".png")
        image["name"] = basename
        image["ext"]  = ".png"
        image["imagemap"] = image_map
        image["imagemap_name"] = basename
        image["html"] = event_html
        image["reference"] = self.m_current_file

        self.m_engine.m_images.append(image["src"])

        return image
    
    
    def parse_sequence(self, source, modifiers):
        '''This method is called to parse the @sequence tag
           and generate a sequence diagram from it'''

        table = self.parse_table(source, modifiers)

        title = table.title
        desc = table.caption
        width = 800
        height = 600
        svg_file = "test.svg"


        events = []
        index = 0
        for row in table.rows:

            #print "ROW[%d]:" % index
            #print row

            if(index == 0):
                index += 1
                continue
            index += 1

            cols = row["cols"]

            type = cols[0]["text"]
            src  = cols[1]["text"]
            dst  = cols[2]["text"]
            name = cols[3]["text"]
            desc = cols[4]["text"]

            if(len(cols) >= 5):
                action = cols[4]["text"]
            else:
                action = ""

            attributes = name.split(",")

            matches = re.search("\[\[(.*)\]\]", name, re.DOTALL)
            if(matches != None):
                link = matches.groups()[0]
                name = matches.groups()[0]
            else:
                link = ""

            event = {}
            event["type"] = type
            event["from"] = src
            event["to"] = dst
            event["name"] = name
            event["desc"] = desc

            events.append(event)

        name = table.title
        #print "Name: [%s]" % name

        path = pathize(name)
        parts = os.path.splitext(path)
        basename = parts[0]
        ext = parts[1]
        dirname = os.path.dirname(basename) + os.path.sep
        
        if(sys.platform == "cygwin" or sys.platform == "win32"):
            basename = basename.replace("/cygdrive/c/", "C:/")
        
        (sequence_img, image_map, event_html) = sequence_diagram.generate_diagram(
            events=events,
            title=title,
            description=desc,
            target_width=800,
            target_height=600,
            base_file_name=basename)

        table = self.parse_table(event_html, modifiers)
        table.widths = [8,10,10,20,52]
        image = {}
        image["src"] = sequence_img
        image["name"] = basename
        image["ext"]  = ".png"
        image["imagemap"] = image_map
        image["imagemap_name"] = basename
        image["html"] = table
        image["reference"] = self.m_current_file

        self.m_engine.m_images.append(image["src"])

        return image


    def parse_table(self, source, modifiers, col_separators=['|']):
        '''This method is called to parse the contents of a table
           declaration
        '''

        table = {}
        table2 = table_t()

        table["rows"] = []

        for modifier in modifiers:
            if(modifier in ("caption", "description")):
                table[modifier] = textblock_t(modifiers[modifier])
                table2.modifiers[modifier] = table[modifier]

                if(modifier == "caption"):
                    table2.set_caption(table[modifier])
            else:
                table[modifier] = modifiers[modifier]

                if(modifier in ("name", "title")):
                    table2.title = table[modifier]

                table2.modifiers[modifier] = modifiers[modifier]

        
        if(modifiers.has_key("mark_reserved")):
            mark_reserved = True
        else:
            mark_reserved = False

        if(modifiers.has_key("widths")):
            vals = modifiers["widths"].split(",")
            total = 0
            widths = []
            for i in range(0, len(vals)):
                total += int(vals[i])
                widths.append(int(vals[i]))

            if(total != 100):
                #FATAL("Table widths do not add up to 100%% at %s:%d" % (self.m_current_file, self.m_current_line[self.m_current_file]))
                FATAL("Table widths do not add up to 100%% at %s:%d" % (self.m_current_file, -1))

            table["widths"] = widths
            table2.widths = widths

        if(modifiers.has_key("width")):
            table["width"] = modifiers["width"]
            table2.width = modifiers["width"]

        if(modifiers.has_key("style")):
            table2.style = modifiers["style"]


        rows = []
        buffer = ""

        if(source.startswith("--")):
            FATAL("Can't parse this table yet!")

        rows = self._parse_rows(source)

        row_num = 0

        for row in rows:
            table_row = {}
            table_row["cols"] = []
            table_row["is_header"] = row.is_heading
            table_row["is_subheader"] = row.is_subheading
            table_row["is_caption"] = False
            table_row["is_reserved"] = row.is_reserved
            table_row["is_spacer"] = row.is_spacer
            table_row["is_crossed"] = row.is_crossed
            table_row["is_title"] = row.is_title

            if(row_num == 0):
                table_row["is_header"] = True

            row_num = row_num + 1

            for col in row.cols:
                tmp = {}
                tmp["span"] = col.span
                tmp["text"] = col.text
                tmp["textblock"] = textblock_t(col.text)
                table_row["cols"].append(tmp)
            
            table2.rows.append(table_row)


        # Now step through the table and figure out how many
        # columns there actually are.
        max_cols = 0 
        for row in table2.rows:

            cols = row["cols"]
            colspan = 0
            for col in cols:
                colspan += col["span"]

            if(colspan > max_cols):
                max_cols = colspan
        
        table2.max_cols = max_cols
        #print "MAX COLS: %d" % max_cols

        # Now right expand any columns that are shorter
        # than the maximum number of columns
        for row in table2.rows:
            cols = row["cols"]

            if(row["is_spacer"]):
                continue

            # Sum the span of all columns
            span = 0
            for col in cols:
                span += col["span"]

            if(span < max_cols):
                col = row["cols"][-1]

                col["span"] = max_cols - len(row["cols"]) + 1

        table2.dict = table
        return table2


    def strip_formatting(self, input):

        input = re.sub("\*", "", input)

        return input
    
    
    def parse_define(self, source, modifiers):
        '''The parse_define method is called to parse
a C/C++ like define that looks like:

#define MY_DEFINE blah blah blah

@param source    [I] = The source of the define
@param modifiers [I] = The list of attributes associated
                       with the define.
'''

        define = define_t()
        #define.name = self.get_attribute_as_string(modifiers, "name")
        #define.description = textblock_t(self.get_attribute_as_string(modifiers, "description"))
        #define.value = textblock_t(self.get_attribute_as_string(modifiers, "value"))
        define.source = source

        define.private = self.get_attribute_as_bool(modifiers, "private")
        define.file = self.get_attribute_as_string(modifiers, "file")
        define.line = self.get_attribute_as_int(modifiers, "line")
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)
        
        language = "code"
        if(modifiers.has_key("language")):
            language = modifiers["language"]
        
        for section in sections:

            if(section == ""):
                continue

            elif(section.startswith("value:")):
                define.value = textblock_t(section[6:len(section)].strip())

        for section in sections:
            if(section.strip() != ""):
                self.parse_object_section(define, 'define', section)

        return define

    def parse_object_example(self, source, obj):
        code = self.m_engine.m_source_code_analyzer
        language = "code"
        example = code.parse_source_code(language, source, obj.file, obj.line)
        obj.example = code_block_t()
        obj.example.language = language
        obj.example.parsed = example
        obj.example.unparsed = source

    def parse_enum(self, source, modifiers):
        
        enum = enum_t()
        
        enum.name = self.get_attribute_as_string(modifiers, "name")
        enum.description = textblock_t(self.get_attribute_as_string(modifiers, "description"))
        enum.private = self.get_attribute_as_bool(modifiers, "private")
        enum.file = self.get_attribute_as_string(modifiers, "file")
        enum.line = self.get_attribute_as_int(modifiers, "line")
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        for section in sections:

            if(section == ""):
                continue

            elif(section.startswith("values:")):
                source = section[7:len(section)].strip()

                values = []

                table = self.parse_table(source, modifiers)
                enum.values = table.rows
                enum.max_cols = table.max_cols

                #print "BEFORE"
                #print enum.values

                # Remove the first row which just describes the enum
                # values.
                enum.values.pop(0)

                #print "AFTER"
                #print enum.values

                #sys.exit(-1)

                i = 0
                num_rows = len(enum.values)

                #table["rows"][0]["is_header"] = True

                # Create Wiki links for each of the enums
                for i in range(0, num_rows):

                    e = table.rows[i]["cols"][0]["text"]
                    #print "ENUM: [%s]" % e
                    
                    word = wikiword_t()
                    word.wikiword = e
                    word.label = e
                    word.is_bookmark = True

                    if(modifiers.has_key("wikiword")):
                        word.wikiword = modifiers["wikiword"]

                    word.link = os.path.basename(self.m_current_file)
                    word.source_file = self.m_current_file
                    self.m_engine.add_wikiword(word)

                for i in range(0, num_rows):
                    cols = table.rows[i]['cols']

                    ename  = cols[0]['text']
                    evalue = cols[1]['text']
                    edesc  = cols[2]['text']

                    e = enum_value_t()
                    e.set_name(ename)
                    e.set_value(evalue)
                    e.set_description(textblock_t(edesc))
                    values.append(e)

                enum.values2 = values

            #elif(section.startswith("name:")):
            #    source = section[5:len(section)].strip()
            #    enum.name = source
            #elif(section.startswith("description:")):
            #    source = section[12:len(section)].strip()
            #    enum.description = textblock_t(source)
            #elif(section.startswith("see:")):
            #    see_also = section[4:len(section)].strip()
            #    enum.set_see_also(see_also)
            #elif(section.startswith("since:")):
            #    since = section[6:len(section)].strip()
            #    enum.set_since(textblock_t(since))
            #elif(section.startswith("example:")):
            #    example = section[8:len(section)]
            #    enum.set_example(example, self.m_engine.m_source_code_analyzer, "code")

        for section in sections:
            if(section != ''):
                self.parse_object_section(enum, 'enum', section)
                

        return enum
    
    def parse_class(self, source, modifiers):
        
        cname = self.get_attribute_as_string(modifiers, "name")

        cdescription = textblock_t(self.get_attribute_as_string(modifiers, "description"))
        cprivate = self.get_attribute_as_bool(modifiers, "private")
        cfile = self.get_attribute_as_string(modifiers, "file")
        cline = self.get_attribute_as_int(modifiers, "line")
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        cprivfunc = ''
        cpubfunc  = ''
        cprivmembers = ''
        cpubmembers  = ''
        cproperties = ''

        for section in sections:

            if(section == ""):
                continue

            elif(section.startswith("name:")):
                source = section[5:len(section)].strip()
                cname = source
            elif(section.startswith("description:")):
                source = section[12:len(section)].strip()
                cdescription = textblock_t(source)
            elif(section.startswith("public.functions:")):
                source = section[17:].strip()
                cpubfunc = source
            elif(section.startswith('public.members:')):
                source = section[15:].strip()
                cpubmembers = source
            elif(section.startswith("private.functions:")):
                source = section[18:].strip()
                cprivfunc = source
            elif(section.startswith('private.members:')):
                source = section[16:].strip()
                cprivmembers = source
            elif(section.startswith('properties:')):
                source = section[11:].strip()
                cproperties = source
                

        cls = self.m_engine.class_get(cname)
        cls.set_name(cname)
        cls.set_description(cdescription)
        cls.private = cprivate
        cls.file = cfile
        cls.line = cline

        if(len(cpubmembers) > 0):
            types = cpubmembers.split("--")
            for t in types:
                t = t.strip()
                if(len(t) > 0):
                    cls.member_add(t, 'public')
        
        if(len(cprivmembers) > 0):
            types = cprivmembers.split("--")
            for t in types:
                t = t.strip()
                if(len(t) > 0):
                    cls.member_add(t, 'private')
        
        if(len(cproperties) > 0):
            types = cproperties.split("--")
            for t in types:
                t = t.strip()
                if(len(t) > 0):
                    cls.member_add(t, 'property')

        return cls

    def parse_gnuplot(self, source, modifiers):
        '''This method is called to parse a gnuplot tag
           @param self      [I] - The shorte parser instance
           @param source    [I] - The source code for the tag
           @param modifiers [I] - A list of modifiers associated with the tag.

           @return A dictionary defining the GNU Plot object
        '''
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)
        
            
        scratchdir = shorte_get_scratch_path()
        
        image = {}
        image["name"] = "gnuplot_%d" % self.m_uid
        self.m_uid += 1
        image["data"] = ""
        image["cmd"]  = ""
        
        if(modifiers.has_key("data")):
            # Open the plot data file
            handle = open(modifiers["data"], "rt")
            image["data"] = handle.read()
            handle.close()
        
        if(modifiers.has_key("cmd")):
            # Open the plot data file
            handle = open(modifiers["cmd"], "rt")
            image["cmd"] = handle.read()
            handle.close()

        for section in sections:

            if(section == ""):
                continue

            if(section.startswith("data:")):
                data = section[5:len(section)]
                image["data"] = data

            elif(section.startswith("cmd:")):
                cmd = section[4:]
                image["cmd"] = cmd
                    
        image["cmd"] = image["cmd"].replace("$OUTPUT_FILE", image["name"] + ".png")
        image["cmd"] = image["cmd"].replace("$DATA_FILE", "plot.dat")

        # Create the plot data file
        handle = open(scratchdir + "/plot.dat", "wt")
        handle.write(image["data"])
        handle.close()

        # Create the plot command file
        handle = open(scratchdir + "/plot.gnu", "wt")
        handle.write(image["cmd"])

        path_gnuplot = shorte_get_tool_path("gnuplot")

        cmd = 'cd "%s";%s %s' % (scratchdir, path_gnuplot, "plot.gnu")

        # DEBUG BRAD: Check the return here to ensure
        #             the image was actually generated
        output = os.popen(cmd)

        image["name"] = image["name"]
        image["ext"] = ".png"
        image["src"] = scratchdir + "/" + image["name"] + image["ext"]
        self.m_engine.m_images.append(image["src"])
        DEBUG(image["src"])

        return image
    
    
    def parse_graph(self, source, modifiers):
        '''This method is called to parse a graph tag
           @param self      [I] - The shorte parser instance
           @param source    [I] - The source code for the tag
           @param modifiers [I] - A list of modifiers associated with the tag.

           @return A dictionary defining the generated image object
        '''
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)
            
        scratchdir = shorte_get_scratch_path()
        
        image = {}
        image["name"] = "graph_%d" % self.m_uid
        self.m_uid += 1
        image["data"] = {}

        graph_type = "line"
        height = 600
        width = 800
        title = ""
        subtitle = ""
        max_x = 10
        max_y = 10
        bg_color = None
        frame = False
        filled = False
        
        if(modifiers.has_key("data")):
            # Open the plot data file
            handle = open(modifiers["data"], "rt")
            image["data"] = handle.read()
            handle.close()
        if(modifiers.has_key("type")):
            graph_type = modifiers["type"]
        if(modifiers.has_key("height")):
            height = int(modifiers["height"])
        if(modifiers.has_key("width")):
            width = int(modifiers["width"])
        if(modifiers.has_key("title")):
            title = modifiers["title"]
        if(modifiers.has_key("subtitle")):
            subtitle = modifiers["subtitle"]
        if(modifiers.has_key("max_x")):
            max_x = int(modifiers["max_x"])
        if(modifiers.has_key("max_y")):
            max_y = int(modifiers["max_y"])
        if(modifiers.has_key("bgcolor")):
            bg_color = modifiers["bgcolor"]
        if(modifiers.has_key("frame")):
            frame = to_boolean(modifiers["frame"]) 
        if(modifiers.has_key("filled")):
            filled = to_boolean(modifiers["filled"])
        
        for section in sections:

            if(section == ""):
                continue

            if(section.startswith("data:")):
                data = section[5:len(section)]

                #print data

                tmp_macros = {}
                eval(compile(data, "example.py", "exec"), tmp_macros, tmp_macros)
                image["data"] = tmp_macros["data"]
                #image["data"] = data
                #lines = data.split('\n')
                #
                #for line in lines:
                #    parts = line.split(" ")
                #    if(len(parts) == 2):
                #        x = float(parts[0])
                #        y = float(parts[1])
                #        image["data"][x] = y

        if(graph_type == "line"):
            import src.graphing.linegraph as linegraph
            graph = linegraph.line_graph_t(width,height,bg_color,bg_color)
            graph.set_title(title, subtitle)
            graph.set_xaxis("X-Axis", "red", 0, max_x, 1)
            graph.set_yaxis("Y-Axis", "red", 0, max_y, 1)
            graph.set_filled(filled)
        elif(graph_type == "bar"):
            import src.graphing.bargraph as bargraph
            graph = bargraph.bar_graph_t(width,height,bg_color,bg_color)
            graph.set_title(title, subtitle)
            graph.set_xaxis("X-Axis", "red", 0, max_x, 1)
            graph.set_yaxis("Y-Axis", "red", 0, max_y, 1)
        elif(graph_type == "pie"):
            import src.graphing.piegraph as piegraph
            graph = piegraph.pie_graph_t(width,height,bg_color,bg_color)
            graph.set_title(title,subtitle)
        elif(graph_type == "memorymap"):
            import src.graphing.memorymap as memorymap
            graph = memorymap.memorymap_graph_t(width,height,bg_color,bg_color)
            graph.set_title(title,subtitle)
        elif(graph_type == "timeline"):
            import src.graphing.timeline as timeline
            graph = timeline.timeline_graph_t(width,height)
            graph.set_title(title, subtitle)
            graph.set_xaxis("X-Axis", "red", 0, 10, 1)
            graph.set_yaxis("Y-Axis", "red", 0, 10, 1)

        graph.show_frame(frame)
            
        #d = {0:1, 1:3, 4:5, 6:4, 7:4, 8:3, 10:8}
        for dataset in image["data"]:
            graph.add_data_set(image["data"][dataset], dataset)

        image["name"] = image["name"]
        image["ext"] = ".png"
        image["src"] = scratchdir + "/" + image["name"] + image["ext"]
        image["caption"] = "This is a random caption"
        
        graph.draw_graph(image["src"])
        self.m_engine.m_images.append(image["src"])

        return image

    def _parse_columns(self, buffer, col_separators=["|"]):

        columns = []

        STATE_NORMAL = 0
        STATE_ESCAPE = 4

        states = []
        state = STATE_NORMAL
        states.append(state)

        column = ""
        pos = 0
        start = 0
        i = start
        indent_of_column = 0

        row = row_t()
        if(buffer[0:2] in ("h ", "* ")):
            row.is_heading = True
            buffer = buffer[2:]
        elif(buffer[0:2] in ("s ", "& ")):
            row.is_subheading = True
            buffer = buffer[2:]
        elif(buffer[0:2] == "t "):
            row.is_title = True
            buffer = buffer[2:]
        elif(buffer[0:2] in ("= ", "x ")):
            row.is_crossed = True
            buffer = buffer[2:]
        elif(buffer[0:2] == "r "):
            row.is_reserved = True
            buffer = buffer[2:]

        buffer = buffer.strip()
        end = len(buffer)

        colspan = 1

        while i < end:
            if(i < pos):
                i += 1
                continue

            if(state == STATE_NORMAL):
                if(buffer[i] == '\\'):
                    states.append(state)
                    column += buffer[i]
                    state = STATE_ESCAPE

                elif(buffer[i] == '@' and buffer[i+1] == '{'):
                    states.append(state)
                    state = STATE_INLINE_STYLING
                    column += buffer[i]
                    column += buffer[i+1]
                    indent_of_column += 1
                    i += 1
                    
                elif(buffer[i] in col_separators):

                    colspan = 1
                    # If we hit a || then we need to merge
                    # with the next column and increment our colspan
                    try:
                        while(buffer[i+1] in col_separators):
                            colspan += 1
                            i += 1
                    except:
                        pass
                    
                    data = trim_leading_indent(column)
                    col = col_t()
                    col.text = data
                    col.span = colspan
                    row.cols.append(col)
                    column = ""
                else:
                    column += buffer[i]

            elif(state == STATE_INLINE_STYLING):
                column += buffer[i]
                if(buffer[i] == '}'):
                    state = states.pop()

            elif(state == STATE_ESCAPE):
                column += buffer[i]
                state = states.pop()

            i += 1

        if(len(column) > 0 or (buffer[end-1] in col_separators)):
            column = trim_leading_indent(column)
            col = col_t()
            col.text = column
            col.span = 1
            row.cols.append(col)

        #for column in columns:
        #    print "COL: [%s]" % column
        if(len(row.cols) == 0):
            row.is_spacer = True

        return row

    def _parse_field_type(self, ftype):
        matches = re.search("(.*?)\[(.*?)\]", ftype)
        fnum = 1
        if(matches != None):
            ftype = matches.groups()[0] 
            fnum  = int(matches.groups()[1]) 

        if(ftype in ("char", "unsigned char", "int8_t", "uint8_t", "cs_uint8", "cs_int8", "boolean", "cs_boolean")):
            width = 8
        elif(ftype in ("unsigned short", "short", "int16_t", "uint16_t", "cs_uint16", "cs_int16")):
            width = 16
        elif(ftype in ("unsigned int", "int", "long", "unsigned long", "int32_t", "uint32_t", "cs_uint32", "cs_int32")):
            width = 32
        elif(ftype in ("unsigned long long", "int64_t", "uint64_t", "cs_uint64", "cs_int64")):
            width = 64
        else:
            WARNING("Cannot process this field type [%s]" % ftype)
            width = 0

        return (fnum * width)


    def _parse_rows(self, source):

        rows = []
        buffer = ''
        
        # Split the structure into individual rows. This is
        # done by looking for the \n- sequence which separates
        # each line
        for i in range(0, len(source)):
            if(source[i] == '-' and (i == 0 or source[i-1] == '\n')):
                if(buffer.strip() != ''):
                    row = self._parse_columns(buffer)
                    #print row
                    rows.append(row)
                    buffer = ''
            else:
                buffer += source[i]

        if(buffer.strip() != ''):
            row = self._parse_columns(buffer)
            #print row
            rows.append(row)
        
        return rows

               
    def _parse_register_fields(self, source, columns, mark_reserved):

        fields = []
        rows = []
        buffer = ''
        fields_are_bits = True
        fields_are_bytes = False
        max_cols = 0

        rows = self._parse_rows(source)

        rindex = 0
        start = 0
        end = 0

        for row in rows:

            #print "[%s]" % row
            cindex = 0

            # Skip spacers for now
            if(row.is_spacer == True):
                continue

            if(rindex > 0):
                field = field_t()

                if(row.is_spacer == True):
                    field.is_spacer = True
                    field.set_name("spacer")
                    field.set_type("spacer")
                else:
                    for col in row.cols:

                        col = col.text

                        column_id = columns[cindex]
                        #print "%s = %s" % (column_id, col)
                        cindex += 1

                        if(column_id in ("bits", "type")):
                            field.set_type(col)

                            bits = col

                            if("'b" in bits):
                                width = bits
                                width = int(bits.replace("'b", ""))

                            elif("-" in bits):
                                parts = bits.split("-")
                                min = int(parts[0].strip())
                                max = int(parts[1].strip())
                                width = (max - min)+1

                                #print "  MIN: %d" % min
                                #print "  END OF LAST: %d" % end

                                # If min > end of last field then
                                # insert a reserved block
                                if(min > end):
                                    len_reserved = min-end
                                    
                                    #print "  len reserved: %d" % len_reserved
                                    new_field = field_t()
                                    new_field.width = len_reserved
                                    new_field.start = end
                                    new_field.end   = start
                                    new_field.set_name("Reserved")
                                    new_field.set_description(textblock_t("Automatically generated"))
                                    new_field.is_reserved = True
                                    new_field.set_type("%d-%d" % (end, start))
                                    fields.append(new_field)

                                    start += len_reserved

                            elif(bits in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
                                #print "BITS: %s" % bits
                                type = bits

                                min = int(bits)

                                if(column_id == "bits"):
                                    #print "  MIN: %d" % min
                                    #print "  END OF LAST: %d" % end
                                    if(min > end):
                                        len_reserved = min - end
                                        #print "  len reserved: %d" % len_reserved
                                        
                                        new_field = field_t()
                                        new_field.width = len_reserved
                                        new_field.start = end
                                        new_field.end   = start
                                        new_field.set_name("Reserved")
                                        new_field.set_description(textblock_t("Automatically generated"))
                                        new_field.is_reserved = True
                                        new_field.set_type("%d-%d" % (end, start))
                                        fields.append(new_field)

                                        start += len_reserved

                                    width = 1

                                elif(column_id == "type"):
                                    width = (min * 8)

                            elif(None != (re.search("[0-9]+x[0-9]+", bits))):
                                parts = bits.split("x")
                                if(len(parts) != 2):
                                    FATAL("Cannot process type field %s" % bits)

                                bit_width = int(parts[0])
                                increment = int(parts[1])
                                width = bit_width*increment

                            else:
                                width = self._parse_field_type(bits)
                                
                            start += width
                            end += start

                            field.width = width
                            field.start = start
                            field.end = end

                        elif(column_id == "name"):
                            if(col.upper() in ("RSVD", "RESERVED", "RESV")):
                                field.is_reserved = True
                            field.set_name(col)

                        elif(column_id == "customer"):
                            field.set_customer(col)

                        elif(column_id == "description"):
                            field.set_description(textblock_t(col))

                        if(cindex > (max_cols-1)):
                            max_cols = cindex + 1

                fields.append(field)
            rindex += 1

        return (fields, max_cols)

    
    def parse_register(self, tag):
        '''This method is called to parse an @register tag containing a
           register definition.

           @param self      [I] - The shorte parser instance
           @param tag       [I] - The tag containing the register

           @return An object containing the register, currently mapped as a structure
        '''
        struct = struct_t()
        struct.fields = []

        modifiers = tag.modifiers
        source = tag.source

        mark_reserved = True

        for modifier in modifiers:
            if(modifier in ("caption", "description")):
                struct.set_description(textblock_t(modifiers[modifier]))

        rows = []
        buffer = ""

        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        struct.headings = {}
        
        struct.set_name(self.get_attribute_as_string(modifiers, "name"))
        struct_desc = self.get_attribute_as_string(modifiers, "description")
        
        struct.set_description(textblock_t(struct_desc))
        struct.private = self.get_attribute_as_bool(modifiers, "private")
        struct.file = self.get_attribute_as_string(modifiers, "file")
        struct.line = self.get_attribute_as_int(modifiers, "line")
        
        columns = ["bits", "name", "description", "attributes"]
        max_cols = 4

        for section in sections:

            if(section == ""):
                continue

            elif(section.startswith("columns:")):
                source = section[8:len(section)].strip()
                columns = source.strip().split(",")

            elif(section.startswith("fields:")):
                    
                source = section[7:len(section)].strip()

                (struct.fields, max_cols) = self._parse_register_fields(source, columns, mark_reserved)

        
        for section in sections:
            if(section != ""):
                self.parse_object_section(struct, 'struct', section)

        struct.max_cols = max_cols

        index = len(self.m_engine.m_images)
        image_name = "record_%d.png" % index

            
        # Generate a record describing the structure
        desc = struct.get_description().get_source()

        record = record_t(struct.get_name(), desc)

        for field in struct.fields:
            #print "FIELD = [%s]" % (field["name"]) # field["attrs"][1], field["attrs"][0])

            if(field.get_is_reserved()):
                record.append_reserved(field.width, field.is_array, 8, field.get_type())
            elif(not field.is_spacer):

                is_array = field.is_array
                array_elem_size = 8
                
                if(field.array_elem_size):
                    array_elem_size = int(field.array_elem_size)

                #print field
                desc = field.get_description().get_source()
                #print "FIELD: %s:" % field.get_name()
                #print "DESC:"
                #print desc
                #print ""
                record.append_field(field.get_name(), field.width, desc, field.is_reserved, is_array, array_elem_size, field.get_type())

        # Generate an record of the structure so that images
        # or source code can be generated from it.
        if(modifiers.has_key("diagram")):

            attributes = {}
            attributes["bitorder"] = "decrement"
            attributes["alignment"] = 64
            
            params = modifiers["diagram"].split(",")

            for param in params:
                parts = param.split(":")

                if(len(parts) == 2):
                    name = parts[0].strip()
                    val  = parts[1].strip()

                    if(name == "align"):
                        attributes["alignment"] = int(val)
                    elif(name == "bitorder"):
                        attributes["bitorder"] = val

            image_name = self.m_engine.get_config("shorte", "scratchdir") + "/" + image_name
            image_map = record.draw(image_name, attributes)

            self.m_engine.m_images.append(image_name)
            img = {}
            img["path"] = image_name
            img["map"] = image_map
            img["reference"] = self.m_current_file
            struct.image = img

        struct.record = record
        
        return struct


    def parse_struct(self, source, modifiers):
        '''This method is called to parse an @struct tag containing a structure
           definition.

           @param self      [I] - The shorte parser instance
           @param source    [I] - The source code for the tag
           @param modifiers [I] - A list of modifiers associated with the tag.

           @return A dictionary defining the structure
        '''
        struct = struct_t()
        struct.fields = []
        
        mark_reserved = True

        for modifier in modifiers:
            if(modifier in ("caption", "description")):
                struct.set_description(textblock_t(modifiers[modifier]))

        rows = []
        buffer = ""

        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        struct.headings = {}
        

        struct.set_name(self.get_attribute_as_string(modifiers, "name"))
        struct_desc = self.get_attribute_as_string(modifiers, "description")
        
        struct.set_description(textblock_t(struct_desc))
        struct.private = self.get_attribute_as_bool(modifiers, "private")
        struct.file = self.get_attribute_as_string(modifiers, "file")
        struct.line = self.get_attribute_as_int(modifiers, "line")
        
        columns = ["type", "name", "description", "attributes"]
        max_cols = 4

        for section in sections:

            if(section == ""):
                continue

            if(section.startswith("fields:")):
                source = section[7:len(section)].strip()
                (struct.fields, max_cols) = self._parse_register_fields(source, columns, mark_reserved) 
        
        for section in sections:
            if(section != ""):
                self.parse_object_section(struct, 'struct', section)

        struct.max_cols = max_cols

        index = len(self.m_engine.m_images)
        image_name = "record_%d.png" % index

            
        # Generate a record describing the structure
        desc = struct.get_description().get_source()

        record = record_t(struct.get_name(), desc)

        for field in struct.fields:

            #print "FIELD = [%s]" % (field["name"]) # field["attrs"][1], field["attrs"][0])

            if(field.get_is_reserved()):
                record.append_reserved(field.width, field.is_array, 8, field.get_type())
            elif(not field.is_spacer):

                is_array = field.is_array
                array_elem_size = 8
                
                if(field.array_elem_size):
                    array_elem_size = int(field.array_elem_size)

                desc = field.get_description().get_source()
                record.append_field(field.get_name(), field.width, desc, field.is_reserved, is_array, array_elem_size, field.get_type())

        # Generate an record of the structure so that images
        # or source code can be generated from it.
        if(modifiers.has_key("diagram")):

            attributes = {}
            attributes["bitorder"] = "decrement"
            attributes["alignment"] = 64
            
            params = modifiers["diagram"].split(",")

            for param in params:
                parts = param.split(":")

                if(len(parts) == 2):
                    name = parts[0].strip()
                    val  = parts[1].strip()

                    if(name == "align"):
                        attributes["alignment"] = int(val)
                    elif(name == "bitorder"):
                        attributes["bitorder"] = val

            image_name = self.m_engine.get_config("shorte", "scratchdir") + "/" + image_name
            image_map = record.draw(image_name, attributes)

            self.m_engine.m_images.append(image_name)
            img = {}
            img["path"] = image_name
            img["map"] = image_map
            img["reference"] = self.m_current_file
            struct.image = img

        struct.record = record
        
        return struct

    def set_if_valid(self, modifiers, name, callback):
        if(modifiers.has_key(name)):
            callback(modifiers[name])
   
    def parse_checklist(self, source, modifiers):

        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)
                
        column_splitter = ","
        if(modifiers.has_key("column_splitter")):
            column_splitter = modifiers["column_splitter"].strip()

        checklist = checklist_t()
        
        self.set_if_valid(modifiers, "name",  checklist.set_name)
        self.set_if_valid(modifiers, "title", checklist.set_name)
        self.set_if_valid(modifiers, "caption", checklist.set_caption)

        for section in sections:

            if(section == ""):
                continue

            elif(section.startswith("name:")):
                data = section[5:].strip()
                checklist.set_name(data)

            elif(section.startswith("columns:")):
                data = section[8:]
                checklist.set_columns(data.strip().split(column_splitter))
            
            else:
                if(section.startswith("items:")):
                    source = section[6:len(section)]
                else:
                    source = section
                
                splitter = re.compile("^-", re.DOTALL | re.MULTILINE)
                
                lines = splitter.split(source)

                items = []

                for line in lines:
                    
                    blank_line = re.compile("^[ \t]*\r?\n")
                    matches = blank_line.match(line)
                    if(matches or line==""):
                        continue

                    elements = line.strip().split(column_splitter)
                    columns = checklist.get_columns()

                    if(len(elements) != len(columns)):
                        FATAL("Number of elements %d does not match column count %d" % (len(elements), len(columns)))

                    elem = checklist_item_t()
                    for i in range(0, len(elements)):
                        fname = columns[i]
                        fvalue = elements[i].strip()

                        elem.set_field(fname, fvalue)

                    items.append(elem)

                checklist.set_items(items)


        return checklist
    

    def parse_testcase(self, source, modifiers):
        
        splitter = re.compile("^(:|--)[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        vars = {}
        vars["name"] = ""
        vars["desc"] = ""
        vars["status"] = ""
        vars["duration"] = ""

        for section in sections:

            if(section != ""):
                if(section.startswith("name:")):
                    vars["name"] = section[5:len(section)].strip()
                if(section.startswith("desc:")):
                    tag = tag_t()
                    tag.contents = trim_leading_indent(section[5:len(section)])
                    #print "contents: [%s]" % tag["contents"]
                    tag.source = tag.contents
                    tag.contents = textblock_t(tag.contents)

                    vars["desc"] = tag
                if(section.startswith("status:")):
                    vars["status"] = section[7:len(section)].strip()
                if(section.startswith("duration:")):
                    vars["duration"] = section[9:len(section)].strip()
                    #print "DURATION: %s" % vars["duration"]

        return vars

    def parse_object_section(self, obj, objtype, section):
        
        if(section.startswith("class:")):
            class_name = section[6:len(section)].strip()
            cls = self.m_engine.class_get(class_name)

            if(objtype == 'prototype'):
                cls.prototype_add(obj)

        elif(section.startswith("deprecated:")):
            msg = textblock_t(section[11:len(section)].strip())
            obj.set_deprecated(msg)
                
        elif(section.startswith("example:")):
            # Find the position of the first newline
            pos = section.find("\n")
            modifiers = section[8:pos]
            example = section[pos+1:len(section)]
            
            result = None
            rc     = None

            # If the example has any modifiers then parse them
            # to see if we should execute the code or not.
            if(len(modifiers) > 0):
                modifiers = self.parse_modifiers(modifiers)
                if(modifiers.has_key("exec")):
                    exec_example = to_boolean(modifiers["exec"])

                    if(exec_example):
                        tag = tag_t()
                        tag.file = obj.file
                        tag.name = "c"
                        tag.line = obj.line
                        tag.modifiers = modifiers
                        tag.source = example
                        self.m_engine.execute_code_block(tag)
                        result     = tag.get_result()
                        obj.set_example_result(result)
            
            obj.set_example(example, self.m_engine.m_source_code_analyzer, "code")

        elif(section.startswith("see:")):
            see_also = section[4:len(section)].strip()
            obj.set_see_also(see_also)
        elif(section.startswith("since:")):
            since = section[6:len(section)].strip()
            obj.set_since(textblock_t(since))
        elif(section.startswith("name:")):
            name = section[5:len(section)].strip()
            obj.set_name(name)
        elif(section.startswith("description:")):
            source = trim_leading_indent(section[12:len(section)].strip())
            obj.description = textblock_t(source)
        elif(section.startswith("requires:")):
            source = section[9:len(section)].strip()
            obj.set_requirements(textblock_t(source))

    
    def parse_prototype(self, source, modifiers):
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        p2 = prototype_t()

        vars = {}
        vars["name"]      = ""
        
        p2.file = self.get_attribute_as_string(modifiers, "file")
        p2.line = self.get_attribute_as_int(modifiers, "line")
        
        p2.private = self.get_attribute_as_bool(modifiers, "private")
        
        p2.set_name(self.get_attribute_as_string(modifiers, "name"))
        
        language = "code"
        if(modifiers.has_key("language")):
            language = modifiers["language"]

        class_name = None

        for section in sections:
            if(section != ""):

                if(section.startswith("function:")):
                    vars["name"] = section[9:len(section)].strip()
                    p2.set_name(vars["name"])
                #elif(section.startswith("name:")):
                #    vars["name"] = section[5:len(section)].strip()
                #    p2.set_name(vars["name"])

                elif(section.startswith("description:")):
                    vars["desc"] = section[12:len(section)].strip()
                    p2.set_description(vars["desc"],False)
                    tmp = section[12:len(section)]
                    vars["desc2"] = textblock_t(tmp)
                    p2.set_description(vars["desc2"])

                elif(section.startswith("prototype:")):
                    vars["prototype"] = section[10:len(section)].strip()

                    function_prototype = section[10:len(section)].strip()

                    p2.set_prototype(function_prototype, self.m_engine.m_source_code_analyzer, language)
                
                elif(section.startswith("called by:")):
                    vars["called_by"] = section[10:len(section)].strip()
                
                elif(section.startswith("calls:")):
                    vars["calls"] = section[6:len(section)].strip()
                
                elif(section.startswith("params:")):
                    params = '\n' + section[8:len(section)].strip() + '\n'
                    #params = re.sub('\n', ' ', params).strip()

                    vars["params"] = []
                
                    #print "Parsing [%s] = [%s]" % (vars["name"], params)
                    
                    rows = re.split("\n *--", params);
                    for row in rows:

                        matches = re.search("(.*?)\|(.*?)\|.*{(.*?)}", row, re.DOTALL)

                        if(0): #matches != None):
                            param_name = matches.groups()[0].strip()
                            param_io   = matches.groups()[1].strip()
                            param_value = matches.groups()[2]

                            #print "N:%s, I:%s, V:%s" % (param_name, param_io, param_value)
                            fields = {}
                            
                            fields["name"] = param_name
                            fields["io"]   = param_io

                            #desc = []
                            #cols = re.split(";", param_value)
                            #for col in cols:
                            #    #print "COL: %s" % col

                            #    parts = re.split("=", col)

                            #    name = parts[0].strip()
                            #    val  = parts[1].strip()

                            #    desc.append((name, val))

                            fields["desc"] = param_value
                            fields["desc2"] = textblock_t(trim_leading_blank_lines(desc))

                            p = param_t()
                            p.set_name(param_name)
                            p.set_io(param_io)
                            p.set_description(param_value, textblock=False)
                            p.set_description(textblock_t(trim_leading_blank_lines(param_value)), textblock=True)
                            #vars["params"].append(fields)
                            vars["params"].append(p)


                        else:
                            #row = re.sub('\n', ' ', row).strip()
#
                            if(row != ""):
                            
                                #print "PARAM: [%s]" % row

                                cols = row.split("|")

                                if(len(cols) > 1):
                                    fields = {}
                                    
                                    fields["name"] = cols[0]
                                    fields["io"]   = cols[1].strip()
                                    desc = []
                                    desc.append((cols[2]))
                                    #print "DESC2: [%s]" % trim_leading_blank_lines(trim_leading_indent(cols[2]))
                                    desc2 = cols[2]
                                    fields["desc"] = desc
                                    fields["desc2"] = textblock_t(trim_leading_blank_lines(trim_leading_indent(cols[2])))
                                    fields["desc2"] = textblock_t(cols[2]) 

                                    p = param_t()
                                    p.set_name(cols[0].strip())
                                    p.set_io(cols[1].strip())
                                    p.set_description(cols[2], textblock=False)
                                    p.set_description(textblock_t(cols[2]),textblock=True)

                                    #vars["params"].append(fields)
                                    vars["params"].append(p)

                    p2.set_params(vars["params"])
                
                elif(section.startswith("returns:")):
                    vars["returns"] = section[8:len(section)].strip()
                    p2.set_returns(vars["returns"])
                
                #elif(section.startswith("example:")):
                #    example = section[8:len(section)]
                #    p2.set_example(example, self.m_engine.m_source_code_analyzer, language)

                elif(section.startswith("pseudocode:")):
                    
                    pseudocode = section[11:len(section)]

                    # Now trim any leading lines

                    #print "PSEUDOCODE: [%s]" % pseudocode
                    
                    p2.set_pseudocode(pseudocode, self.m_engine.m_source_code_analyzer, language)

                #elif(section.startswith("see:")):
                #    vars["see_also"] = section[4:len(section)].strip()
                #    p2.set_see_also(vars["see_also"])
            
                elif(section.startswith("since:")):
                    since = section[6:len(section)].strip()
                    p2.set_since(textblock_t(since))
                
        for section in sections:
            if(section != ""):
                self.parse_object_section(p2, 'prototype', section)

        # This section attempts to search the prototype of the
        # method for the type of each argument and sets the type
        # associated with each parameter.
        matches = re.search("\((.*)\)", function_prototype, re.DOTALL)
        if(matches != None):
            args = matches.groups()[0].split(',')

            arg_types = {}
            for arg in args:
                # Strip any brackets since we won't count
                # that as the type
                arg = re.sub("\[.*\]", '', arg)
                arg = arg.strip()
                parts = arg.split(' ')

                # The last word must be the argument
                # name.
                arg_name = parts[-1]

                # Everthing before it is the argument
                # type.
                arg_type = ' '.join(parts[0:-1])

                arg_types[arg_name] = arg_type

        if(p2.has_params()):
            for param in p2.get_params():
                if(not param.has_type() and arg_types.has_key(param.get_name())):
                    param.set_type(arg_types[param.get_name()])

        return (vars, p2)

    

    def parse_image(self, tags):
        
        image = {}
        
        if(tags.has_key("name")):
            image["name"] = tags["name"]
       
        if(tags.has_key("src")):

            # First fetch the URL so that it can be converted
            if("http://" in tags["src"]):
                import urllib
                image_path = self.m_engine.get_config("shorte", "scratchdir") + "/" + os.path.basename(tags["src"])
                urllib.urlretrieve(tags["src"], image_path)
                tags["src"] = image_path

            #print "src = %s" % tags["src"]
            input = os.path.abspath(tags["src"])
            dirname = os.path.dirname(input) + os.path.sep

            name = input.replace(dirname, "")
            parts = os.path.splitext(name)
            basename = parts[0]
            ext = parts[1]
            
            image["src"] = os.path.abspath(tags["src"])
            #print "parse_image.src = %s" % image["src"]
            image["name"] = basename
            image["ext"] = ext
        
            src.shorte_defines.DEBUG('''Image:
    src:  %s
    name: %s
    ext:  %s
''' % (image["src"], image["name"], image["ext"]))
        
        if(tags.has_key("height")):
            image["height"] = tags["height"]
        if(tags.has_key("width")):
            image["width"] = tags["width"]
        if(tags.has_key("caption")):
            image["caption"] = tags["caption"]
        if(tags.has_key("center")):
            image["center"] = true
        if(tags.has_key("href")):
            image["href"] = tags["href"]
        if(tags.has_key("align")):
            image["align"] = tags["align"]
        if(tags.has_key("map")):
            image["imagemap"] = tags["map"]

        image["reference"] = self.m_current_file

        self.m_engine.m_images.append(image["src"])

        return image

    def parse_imagemap(self, source, modifiers):

        imagemap = self.parse_table(source, modifiers).dict
        self.m_engine.m_imagemaps[imagemap["id"]] = imagemap

        return imagemap

    def parse_gallery(self, source, modifiers):
        
        splitter = re.compile("^--[ \t]*", re.MULTILINE)
        sections = splitter.split(source)

        gallery = gallery_t()

        for section in sections:

            if(section == ""):
                continue

            if(section.startswith("images:")):
                text = section[8:len(section)]
                table = self.parse_table(text, modifiers)

                for row in table.rows:
                    if(row["is_header"] == False):
                        #for col in row["cols"]:
                        image = image_t()
                        image.height = 0
                        image.width = 0

                        height = int(row['cols'][1]['text'].strip())

                        image.caption = row["cols"][2]["text"]

                        image.parse_path(row["cols"][0]["text"])

                        #print "PATH: %s" % image.source
                        # Add the image to the list of managed photos
                        self.m_engine.m_images.append(image.source)

                        # Create a thumbnail for the image and add it to
                        # the list of managed photos
                        #height = 200 #random.choice([100,200,300])
                        width = None
                        self.m_engine.m_images.append(image.create_thumbnail(height=height,width=width))

                        gallery.add_image(image)

        return gallery

    def parse_embed(self, tags):
        
        obj = {}
        
        if(tags.has_key("name")):
            obj["name"] = tags["name"]
       
        if(tags.has_key("src")):

            #print "src = %s" % tags["src"]
            input = os.path.abspath(tags["src"])
            dirname = os.path.dirname(input) + os.path.sep

            name = input.replace(dirname, "")
            parts = os.path.splitext(name)
            basename = parts[0]
            ext = parts[1]
            
            obj["src"] = os.path.abspath(tags["src"])
            obj["name"] = basename
            obj["ext"] = ext
        
        if(tags.has_key("height")):
            obj["height"] = tags["height"]
        if(tags.has_key("width")):
            obj["width"] = tags["width"]
        if(tags.has_key("caption")):
            obj["caption"] = tags["caption"]
        if(tags.has_key("center")):
            obj["center"] = true
        if(tags.has_key("href")):
            obj["href"] = tags["href"]
        if(tags.has_key("align")):
            obj["align"] = tags["align"]

        obj["reference"] = self.m_current_file

        self.m_engine.m_images.append(obj["src"])

        return obj

    def parse_input(self, tags):

        form_input = {}

        form_input["name"] = tags["name"]
        form_input["type"] = tags["type"]
        form_input["form"] = tags["form"]
        form_input["value"] = ""
        form_input["label"] = tags["label"]
        form_input["caption"] = tags["caption"]

        return form_input
    
    def _parse_inkscape(self, source, tags):
        '''This method is called to parse the @inkscape tag
           and specify the image conversion program'''
        
        image = self.parse_image(tags)
        image["converter"] = "inkscape"

        return image

    
    def expand_snippet(self, matches):

        name = matches.groups()[0]

        #print "SNIPPET NAME: %s" % name

        if(self.m_snippets.has_key(name)):
            return self.m_snippets[name].strip()

        return "SNIPPET %s NOT FOUND" % name

    def _parse_tag(self, page_title, name, data, modifiers, line_no):
        '''This method is used to parse the tag itself and expand
           or modify it as necessary.
           
           Keyword arguments:
           page_title -- The title associated with the page being parsed
           name       -- The name of the tag
           data       -- The data associated with the tag
           modifiers  -- Any modifiers associated with the tag

           Returns:
           A list of tags
           '''

        tags = []

        #print "Parsing tag: [%s]" % name

        name = name.strip()
        self.m_current_tag = name
        self.m_current_line = line_no

        data = data.rstrip("\n")
        modifiers = modifiers.rstrip("\n")
        
        #print "Tag: [%s]" % (name)
        #print "Modifiers=[%s]" % modifiers
        #print "Data=[%s]" % data
        
        modifiers = self.parse_modifiers(modifiers)

        if(data == ""):
            if(modifiers.has_key("name")):
                data = modifiers["name"]
            elif(modifiers.has_key("title")):
                data = modifiers["title"]

        # Determine whether we should automatically add a header before
        # a function prototype
        prototype_add_header = self.m_engine.get_config("shorte", "prototype_add_header")

        # Determine whether we should automatically add a header before
        # a testcase definition
        testcase_add_header = self.m_engine.get_config("shorte", "testcase_add_header")


        #print "CURRENT_FILE = %s" % os.path.basename(self.m_current_file)

        if(not self.is_valid_tag(name)):
            FATAL("Invalid tag '%s' encountered at %s:%d" % (name, self.m_current_file, self.m_current_line))
            
        # Expand any PHP style embedded snippets
        data = re.sub("<\?=(\$[0-9])\?>", self.expand_snippet, data)

        if(modifiers.has_key("if")):
            define = modifiers["if"]
            macros = self.m_engine.get_macros()

            # Figure out the variables that are defined
            # in the define list
            expr = re.compile("([A-Za-z][A-Za-z0-9_]+)", re.DOTALL | re.IGNORECASE)

            # If a variable is not set then set it
            # to zero
            matches = expr.search(define)
            while(matches != None):
                var = matches.groups()[0]

                if(not (var == "and" or
                        var == "or" or
                        var == "not")):
                    if(not macros.has_key(var)):
                        #print "EXPR = %s" % var
                        macros[var] = 0

                matches = expr.search(define, matches.end() + 1)

            # Evalulate the if check in the tag and
            # exclude it if necessary
            tmp_macros = {}
            for macro in macros:
                tmp_macros[macro] = macros[macro]

            to_eval = '''
def exists(s):
    if(globals().has_key(s)):
        return 1
    return 0

def value(s):
    if(exists(s)):
        return s
    return 0

if(%s):
    result = 1
else:
    result = 0
''' % define

            #to_eval = "(" + define + ")"

            try:
                eval(compile(to_eval, "example.py", "exec"), tmp_macros, tmp_macros)
            except:
                FATAL(to_eval)

            result = tmp_macros["result"]
            #print "RESULT: %s = %s" % ("(" + define + ")", result)
            if(int(result) == 0):
                #print "DO I GET HERE?"
                return None

        tag = tag_t()
        tag.name = name
        tag.contents = data
        tag.source = data
        tag.modifiers = modifiers
        tag.page_title = page_title

        if(modifiers.has_key("break_before")):
            tag.break_before = bool(modifiers["break_before"])

        visible = True
        if(modifiers.has_key("visible")):
            visible = to_boolean(modifiers["visible"])

        filename = os.path.basename(self.m_current_file)

        tag.file = filename
        tag.line = line_no
            
        if(len(data) == 0):
            if(not tag.name in ('image', 'functionsummary', 'typesummary', 'embed', 'columns', 'column', 'endcolumns', 'inkscape')):
                # DEBUG BRAD: This uses the old way of dealing with line numbers. Need to figure out
                #             a way of fixing this.
                WARNING("Tag '%s' at %s:%d has no body, may cause parsing errors" % (tag.name, tag.file, tag.line))

        if(self.tag_is_header(name)):
            tag.is_header = True 

            # DEBUG BRAD: old way of dealing with headers
            #    tmp = data
            #    tmp = re.sub("\n", " ", tmp).strip()
            #    self.m_engine.m_wiki_links[tmp] = (os.path.basename(self.m_current_file), False)
            #    self.m_headers.append(tag)
            
            # DEBUG BRAD: This is the new way of dealing with
            #             headers where I automatically insert
            #             an @text after the first line of the header
            #             and assume the header doesn't span multiple lines.
            #
            # If the data contains multiple lines then treat everything after
            # the first line as a text block
            lines = data.split('\n')
            tmp = lines[0].strip()
            
            # If the header is of the format [[...,...]] then
            # treat the first part as a wikiword and the second
            # as the title
            matches = re.search("\[\[(.*),(.*)\]\]", tmp)
            if(None != matches):
                tmp = matches.groups()[1]
                modifiers["wikiword"] = matches.groups()[0]

            tag.contents = tmp
            tag.source = tmp

            if(name != "h"):
                #print "Adding wikiword %s" % tmp
                word = wikiword_t()
                word.wikiword = tmp
                word.label = tmp
                word.is_bookmark = False

                if(modifiers.has_key("wikiword")):
                    word.wikiword = modifiers["wikiword"]

                word.link = os.path.basename(self.m_current_file)
                word.source_file = self.m_current_file
                self.m_engine.add_wikiword(word)

            self.m_headers.append(tag)
        
            tags.append(tag)

            # Now create a new text tag with the remainder 
            lines.pop(0)
            tag = tag_t()
            tag.name = "text"
            tag.source = '\n'.join(lines)
            tag.contents = textblock_t(tag.source)
            tag.modifiers = modifiers
            tag.page_title = page_title
            tag.file = filename
            tag.line = line_no

            tags.append(tag)

            return tags

        elif(name == "doctitle" or
             name == "docsubtitle" or
             name == "docversion" or
             name == "docnumber" or
             name == "docauthor" or
             name == "title" or
             name == "csource"):
            tmp = data
            tmp = re.sub("\n", " ", tmp).strip()
            tag.source = data
            tag.contents = tmp


        elif(self.tag_is_source_code(name)):
            code = self.m_engine.m_source_code_analyzer
        
            tag.source = data
            tag.contents = code.parse_source_code(name, data, tag.file, tag.line)

        elif(name == "table"):
            tag.contents = self.parse_table(data, modifiers)

        elif(name == "include" or name == "include_child"):
            INFO("Parsing include(s) [%s]" % data)
            data = data.replace("\"", "")

            include_files = data.split("\n")
            tags = []
            for include in include_files:
                #print "  INCLUDE = [%s]" % include
                if(include != ""):
                    tags.extend(self.parse_include(include))

            return tags

        elif(name == "struct"):
            modifiers["treat_fields_as"] = "bytes"
            struct = self.parse_struct(data, modifiers)
            tag.contents = struct

        elif(name == "define"):
            tag.contents = self.parse_define(data, modifiers)
        
        elif(name == "vector"):
            modifiers["treat_fields_as"] = "bits"
            struct = self.parse_struct(data, modifiers)
            tag.contents = struct
            tag.name = "struct"
    
        elif(name == "register"):
            reg = self.parse_register(tag)
            tag.contents = reg
            tag.name = "register"

        elif(name in ("ol", "ul")):
            tag.contents = self.parse_list(data, modifiers)

        elif(name == "image"):
            tag.contents = self.parse_image(modifiers)

        elif(name == "gallery"):
            tag.contents = self.parse_gallery(data, modifiers)

        elif(name == "imagemap"):
            tag.contents = self.parse_imagemap(data, modifiers)

        elif(name == "embed"):
            tag.contents = self.parse_embed(modifiers)

        elif(name == "input"):
            tag.contents = self.parse_input(modifiers)

        elif(name in ("cond", "endcond")):
            return
        
        elif(name == "prototype"):

            if(len(data) == 0):
                ERROR("Prototype at %s:%d has no body, may cause parsing errors" % (tag.file, tag.line))

            (function,ptype) = self.parse_prototype(data, modifiers)

            if(prototype_add_header != None):

                # Automatically add a header before function prototypes

                header = tag_t()
                header.is_header = True
                header.is_prototype = True
                header.name = prototype_add_header
                header.contents = ptype.get_name()
                header.source = ptype.get_name()
                header.modifiers = modifiers
                header.file = ptype.get_file()
                header.line = ptype.get_line()
                
                # If a header with the same name already exists then don't
                # bother adding a new one
                #print "FUNC NAME: [%s]" % function["name"]
                hdr_tag = self.get_header(ptype.get_name())
                if(hdr_tag == None):
                    tmp = function["name"]
                    tmp = re.sub("\n", " ", tmp).strip()

                    word = wikiword_t()
                    word.wikiword = tmp
                    word.label = tmp
                    word.is_bookmark = False
                    if(modifiers.has_key("wikiword")):
                        word.wikiword = modifiers["wikiword"]

                    word.source_file = self.m_current_file
                    word.link = os.path.basename(self.m_current_file)
                    word.source_file = self.m_current_file

                    self.m_engine.add_wikiword(word)

                    tags.append(header)
                else:
                    hdr_tag.is_prototype = True
            
            tag.contents = ptype

        elif(name == "testcase"):
            testcase = self.parse_testcase(data, modifiers)

            # Automatically add a header before testcase definitions
            if(testcase_add_header != None):
                header = tag_t()
                header.is_header = True
                header.is_prototype = True
                header.name = testcase_add_header
                header.contents = testcase["name"]
                header.source = testcase["name"]
                header.modifiers = modifiers
                header.file = filename
                header.line = line_no
                
                # If a header with the same name already exists then don't
                # bother adding a new one
                #print "FUNC NAME: [%s]" % function["name"]
                hdr_tag = self.get_header(testcase["name"])
                if(hdr_tag == None):
                    tmp = testcase["name"]
                    tmp = re.sub("\n", " ", tmp).strip()
                    
                    word = wikiword_t()
                    word.wikiword = tmp
                    word.label = tmp
                    word.is_bookmark = False
                    if(modifiers.has_key("wikiword")):
                        word.wikiword = modifiers["wikiword"]

                    word.link = os.path.basename(self.m_current_file)
                    
                    word.source_file = self.m_current_file

                    self.m_engine.add_wikiword(word)

                    tags.append(header)
                else:
                    hdr_tag.is_prototype = True

            tag.contents = testcase


        elif(name == "functionlist"):
            vars = {}
            tag.contents = vars

        elif(name == "inkscape"):
            tag.contents = self._parse_inkscape(data, modifiers)
            tag.name = "image"

        elif(name == "gnuplot"):
            tag.contents = self.parse_gnuplot(data, modifiers)
            tag.name = "image"

        elif(name == "graph"):
            tag.contents = self.parse_graph(data, modifiers)
            tag.name = "image"

        elif(name == "pre"):
            tag.contents = data.strip()

        elif(name == "checklist"):
            tag.contents = self.parse_checklist(data, modifiers)

        elif(name == "enum"):
            tag.contents = self.parse_enum(data, modifiers)
            tag.name = "enum"

        elif(name == "class"):
            tag.contents = self.parse_class(data, modifiers)
            tag.name = "class"

        elif(name == "acronyms"):
            tag.contents = self.parse_table(data, modifiers)

            table = tag.contents

            i = 0
            num_rows = len(table.rows)

            # Create Wiki links for each of the acronyms
            for i in range(1, num_rows):

                acronym = table.rows[i]["cols"][0]["text"]

                word = wikiword_t()
                word.wikiword = acronym
                word.label = acronym
                word.is_bookmark = True

                if(modifiers.has_key("wikiword")):
                    word.wikiword = modifiers["wikiword"]

                word.link = os.path.basename(self.m_current_file)
                word.source_file = self.m_current_file
                self.m_engine.add_wikiword(word)
            
            # If the table has no title then default it
            if(table.title == None):
                table.title = "Acronyms"

        elif(name == "sequence"):
            tag.contents = self.parse_sequence(data, modifiers)

        elif(name == "questions"):
            tag.contents = self.parse_questions(data, modifiers)

        elif(name in ("text", "note", "warning", "question", "tbd")):
            tag.source = tag.contents
            tag.contents = textblock_t(tag.source)

        if(visible):
            tags.append(tag)

        return tags
    
    def load_source_file(self, source_file):
        try:
            source = open(source_file, "r")
            input = source.read()
            source.close()
        except:
            FATAL("Failed loading source file [%s]" % source_file)
        
        # Strip any \r characters
        input = input.replace("\r", "")

        # Replace any references to Leeds
        input = self.__search_and_replace(input)
        
        # Strip any illegal characters
        input = re.sub("[]", "'", input)

        # Replace any tabs
        input = input.replace("\t", TAB_REPLACEMENT)

        return input

    def is_child_tag(self, tag, predecessor):
        '''This method is called by the __append_tags_if_not_excluded
           method to cascade tag exclusion from headers to child
           topics'''
        rank_tag         = self.m_tag_hierarchy["least"]
        rank_predecessor = self.m_tag_hierarchy["least"]

        if(self.m_tag_hierarchy.has_key(predecessor)):
            rank_predecessor = self.m_tag_hierarchy[predecessor]

        if(self.m_tag_hierarchy.has_key(tag)):
            rank_tag = self.m_tag_hierarchy[tag]
        
        #print "COMPARING %s(%d) AGAINST %s(%d)" % (tag, rank_tag, predecessor, rank_predecessor)

        # If the tag has a higher rank then it is a child
        # of the predecessor.
        if(rank_tag > rank_predecessor):
            return True

        return False

    def __append_tags_if_not_excluded(self, tags, excluded, tag_name, tag_list):
        '''This method is used to add support for cascading excluded tags
           based on the 'if' modifier of a tag. For example, if a header
           supports exclusion then all child tags under the header will
           be excluded as well'''

        # If tags is None then the tag has been excluded by some rule. If it
        # is excluded we need to record it's name. This is done so that any
        # child tags can be excluded beneath this parent tag.
        if(tags == None):
            #print "TAG %s EXCLUDED" % tag_name
            excluded = tag_name
        else:
            if(excluded != None):

                if(self.is_child_tag(tag_name, excluded)):
                    #print "TAG %s EXCLUDED" % tag_name
                    pass
                else:
                    excluded = None
                    tag_list.extend(tags)
            else:
                tag_list.extend(tags)

        return excluded

    def set_cpp_parser(self, cpp_parser):
        self.m_cpp_parser = cpp_parser

    def parse_include(self, source_file):

        source = open(source_file, "r")
        input = source.read()
        source.close()
        
        #self.parse_line_info(source_file, input)

        parent_file = self.m_active_file[-1]

        self.m_active_file.append(source_file)
        self.m_current_file = self.m_active_file[-1]
        #print "  Setting current file to %s, stack.len = %d" % (source_file, len(self.m_active_file))
        
        # If the include is a source file then first convert it
        # to shorte format.
        if(source_file.endswith(".c") or source_file.endswith(".h")):

            indexer = indexer_t()
            page = self.m_cpp_parser.parse_buffer(input, source_file)
            template = template_shorte_t(self.m_engine, indexer)
            input = template.generate_buffer(page)

        elif(source_file.endswith('.py')):
            indexer = indexer_t()
            pyparse = src.parsers.python_parser.python_parser_t(self.m_engine)
            page = pyparse.parse_buffer(None, source_file)
            template = template_shorte_t(self.m_engine, indexer)
            input = template.generate_buffer(page)

        #result = self.parse_string(input, source_file, is_include=True)
        self.m_current_file = None
        result = self.parse_string(input, parent_file, is_include=True)

        if(len(self.m_active_file) > 1):
            self.m_active_file.pop()

        self.m_current_file = self.m_active_file[-1]
        #print "  Setting current file to %s" % self.m_current_file

        return result

    def _parse_header_tags(self, title, input, start):

        STATE_NORMAL     = 0
        STATE_INTAG      = 1
        STATE_INMTAGDATA = 2
        STATE_INTAGDATA  = 3
        STATE_ESCAPE     = 4
        STATE_COMMENT    = 5
        STATE_MCOMMENT   = 6
        STATE_MODIFIERS  = 7

        states = []
        states.append(STATE_NORMAL)
        
        tag_name = ""
        tag_data = ""
        tag_modifiers = ""

        tag_list = []

        line_no = 0

        #print "INPUT = [%s]" % input
       
        i = start
        excluded = None

        while i < len(input):

            state = states[-1]
                
            if(input[i:i+4] == '<!--'):
                states.append(STATE_MCOMMENT)
                i += 4
                continue

            if(state == STATE_INTAG):

                if(input[i] == ' ' or input[i] == ':' or input[i] == '\t' or input[i] == '\n'):

                    (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)

                    tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, line_no)
                        
                    excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, tag_list)
                    
                    tag_name = ""
                    tag_data = ""

                else:
                    tag_name += input[i];
                
            elif(state == STATE_NORMAL):

                if(input[i] == '#'):
                    states.append(STATE_COMMENT)
                    
                # DEBUG BRAD: Assume it's a tag only if it starts at the beginning of a line
                #elif(input[i] == '@'):
                elif((i == 0 and input[i] == '@') or (input[i] == '@' and input[i-1] == '\n')):
                
                    #print "Here"
                    if(tag_name != "" and tag_data != ""):
                        (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)
                        tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, line_no)
                    
                        excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, tag_list)
                    
                    tag_name = ""
                    tag_data = ""
                    
                    states.append(STATE_INTAG)
                    
                elif(input[i] == '\\'):
                    tag_data += '\\'
                    states.append(STATE_ESCAPE)
            
            elif(state == STATE_ESCAPE):
                
                tag_data += input[i];
                states.pop()

            elif(state == STATE_MCOMMENT):
                if(input[i:i+3] == '-->'):
                    states.pop()
                    i += 2
            
            elif(state == STATE_COMMENT):
                if(input[i] == '\n'):
                    states.pop()
            
            i = i+1
        
        
        if(tag_data != ""):
            if(tag_name != ""):

                (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)
                tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, line_no)
                        
                excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, tag_list)
                        

            else:
                
                (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data("p", input, i, line_no)
                tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, line_no)

                excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, tag_list)
                
        return tag_list

    def _evaluate_macros(self, matches):

        input = matches.groups()[0].strip()
        macros = self.m_engine.get_macros()
        tmp_macros = {}
        for macro in macros:
            tmp_macros[macro] = macros[macro]

        input = '''
def exists(s):
    if(globals().has_key(s)):
        return 1
    return 0

%s
''' % input

        #print "MACRO: [%s]" % input

        eval(compile(input, "example.py", "exec"), tmp_macros, tmp_macros)

        eval_result = ""

        try:
            if(tmp_macros.has_key("result")):
                eval_result = tmp_macros["result"]
        except Exception,e:
            WARNING("EXCEPTION: %s" % e)
            do_nothing=1

        return eval_result
    
    def parse_line_info(self, source_file, source):

        self.m_lines[source_file] = {}

        line = 0
        self.m_lines[source_file][line] = 0
        for i in range(0, len(source)):
            if(source[i] == '\n'):
                line += 1
                self.m_lines[source_file][line] = i+1

    def get_line_at(self, source_file, pos, name):
        line = 0

        if(not self.m_lines.has_key(source_file)):
            return -1

        while(pos > self.m_lines[source_file][line]):
            if(self.m_lines[source_file].has_key(line+1)):
                line += 1
            else:
                break

        #print "    LINE: %d (tag: %s, pos: %d)" % (line, name, pos)
        return line
        

    def parse(self, source_file):

        if(source_file == "result"):
            return None

        #print "PARSE: %s" % source_file
        source = open(source_file, "r")
        input = source.read()
        source.close()

        #self.parse_line_info(source_file, input)

        self.m_active_file.append(source_file)
        #print "  Setting current file to %s, stack.len = %d" % (source_file, len(self.m_active_file))
        self.m_current_file = self.m_active_file[-1]
        result = self.parse_string(input, source_file)
        if(len(self.m_active_file) > 1):
            self.m_active_file.pop()
        self.m_current_file = self.m_active_file[-1]
        #print "  Setting current file to %s" % self.m_current_file

        return result

    def parse_string(self, input, source_file="default.tpl", is_include=False):

        if(None == self.m_current_file):
            self.m_current_file = source_file

        # Strip any illegal characters
        input = re.sub("[]", "'", input)
        input = re.sub("", "", input)
        
        # Replace any references to Leeds
        input = self.__search_and_replace(input)

        # Perform any preprocessing/expansion
        # of macros
        macros = self.m_engine.get_macros()
        tmp_macros = {}
        for macro in macros:
            tmp_macros[macro] = macros[macro]
        
        expr = re.compile("<\?(.*?)\?>", re.DOTALL)
        input = expr.sub(self._evaluate_macros, input)

        if(not is_include):
            source_file = self.m_engine.search_and_replace(source_file)

        try:

            # Strip any \r characters
            input = input.replace("\r", "")

            # Replace any tabs
            input = input.replace("\t", TAB_REPLACEMENT)

            #print "ONE_A"

            start = 0
            header = self.__parse_header(input)

            start = header.get_start()
            title = header.get_title()
            subtitle = header.get_subtitle()
            toc   = header.get_toc()
            numbered = header.get_numbered()
            version = header.get_version()
            number = header.get_number()
            revision_history = header.get_revision_history()
            line_no = header.get_line() - 1

            #print "FILE %s starts at line %d" % (source_file, header.get_line())
            
            # If the title has not already been set
            # then use the version found in the input file
            if(self.m_title == None):
                self.m_title = title
            if(self.m_subtitle == None):
                self.m_subtitle = subtitle

            self.m_engine.get_doc_info().set_version(version)
            self.m_engine.get_doc_info().set_number(number)
            if(header.has_author()):
                self.m_engine.get_doc_info().set_author(header.get_author())

            self.m_engine.get_doc_info().set_revision_history(revision_history)

            if(self.m_engine.m_output_filename == None):
                if(header.has_filename()):
                    self.m_engine.m_output_filename = header.get_filename()


            page = {}
            page["title"] = title
            page["subtitle"] = subtitle
            page["tags"] = []
            page["source_file"] = source_file
            page["links"] = self.m_links
            page["header"] = header

            #self.m_links = []

            # Now parse the document body
            contents = ""
            
            STATE_NORMAL     = 0
            STATE_INTAG      = 1
            STATE_INMTAGDATA = 2
            STATE_INTAGDATA  = 3
            STATE_ESCAPE     = 4
            STATE_COMMENT    = 5
            STATE_MCOMMENT   = 6
            STATE_MODIFIERS  = 7

            states = []
            states.append(STATE_NORMAL)
            
            tag_name = ""
            tag_data = ""
            tag_modifiers = ""
            
            i = start

            excluded = None

            while i < len(input):

                state = states[-1]
                
                if(input[i:i+4] == '<!--'):
                    states.append(STATE_MCOMMENT)
                    i += 4
                    continue

                if(state == STATE_INTAG):

                    if(input[i] == ' ' or input[i] == ':' or input[i] == '\t' or input[i] == '\n'):

                        saved_i = i
                        saved_line = line_no

                        (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)

                        tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, saved_line)

                        #if(tags != None):
                        #    for tag in tags:
                        #        if(tag.line2 == None):
                        #            tag.line2 = self.get_line_at(self.m_current_file, saved_i, tag.name)

                        excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, page["tags"])

                        tag_name = ""
                        tag_data = ""

                    else:
                        tag_name += input[i];
                    
                elif(state == STATE_NORMAL):

                    if(input[i] == '#'):
                        states.append(STATE_COMMENT)

                    # DEBUG BRAD: Assume it's a tag only if it starts at the beginning of a line
                    #elif(input[i] == '@'):
                    elif((i == 0 and input[i] == '@') or (input[i] == '@' and input[i-1] == '\n')):
                    
                        #print "CHARS: %s,%s" % (input[i], input[i+1])
                        if(input[i+1] == '{'):
                            DEBUG("DO I GET HERE?")
                            pass
                        else:
                            #print "Here"
                            if(tag_name != "" and tag_data != ""):
                                saved_i = i
                                saved_line = line_no

                                (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)
                                tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, saved_line)

                                #if(tags != None):
                                #    for tag in tags:
                                #        if(tag.line2 == None):
                                #            tag.line2 = self.get_line_at(self.m_current_file, saved_i, tag.name)
                            
                                excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, page["tags"])

                            tag_name = ""
                            tag_data = ""
                            
                            states.append(STATE_INTAG)
                        
                    elif(input[i] == '\\'):
                        #tag_data += input[i]
                        states.append(STATE_ESCAPE)
                    
                    elif(input[i] == '\n'):
                        line_no += 1
                
                elif(state == STATE_ESCAPE):
                    
                    tag_data += input[i];
                    states.pop()
                
                elif(state == STATE_MCOMMENT):
                    if(input[i:i+3] == '-->'):
                        states.pop()
                        i += 2
                    elif(input[i] == '\n'):
                        line_no += 1

                elif(state == STATE_COMMENT):
                    if(input[i] == '\n'):
                        line_no += 1
                        states.pop()
                
                i = i+1
            
            #print "TWO"
            
            if(tag_data != ""):
                if(tag_name != ""):

                    saved_i = i
                    saved_line = line_no

                    (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data(tag_name, input, i, line_no)
                    tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, saved_line)

                    #if(tags != None):
                    #    for tag in tags:
                    #        if(tag.line2 == None):
                    #            tag.line2 = self.get_line_at(self.m_current_file, saved_i, tag.name)

                    excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, page["tags"])

                else:
                    
                    if(i < len(input)):
                        INFO("Snippet: %s, i = %d, len = %d" % (input[i:-1], i, len(input)))
                        saved_i = i
                        saved_line = line_no
                        (i, line_no, tag_data, tag_modifiers) = self._parse_tag_data("p", input, i, line_no)
                        tags = self._parse_tag(title, tag_name, tag_data, tag_modifiers, saved_line)

                        #if(tags != None):
                        #    for tag in tags:
                        #        if(tag.line2 == None):
                        #            tag.line2 = self.get_line_at(self.m_current_file, saved_i, tag.name)
                        
                        excluded = self.__append_tags_if_not_excluded(tags, excluded, tag_name, page["tags"])

            #print "THREE"
            
            # Check to see if there were any includes found. If there are then
            # pop them off one at a time and process them
            while(len(self.m_include_queue) != 0):
                path = self.m_include_queue.pop(-1)
                self.parse(path)


            # Now walk the list of tags and cascade conditionals on headers
            #for tag in page["tags"]:
            #    print "TAG: %s at %d" % (tag.name, tag.line)

            #print "Finished parsing"

            if(not is_include):
                self.m_pages.append(page)
                return None
            else:
                return page["tags"]

        except Exception,e:
            import traceback
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)

            print e

            #FATAL("\n\nEncountered exception parsing '%s' tag at line %d of %s" % (self.m_current_tag, self.m_current_line[self.m_current_file], self.m_current_file))
            FATAL("\n\nEncountered exception parsing '%s' tag" % (self.m_current_tag))

        return None
    
