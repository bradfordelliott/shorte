#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   template_python.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a template class that is used
#|   to generate shorte documents from another input form such as a
#|   C source file.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from shorte_defines import *
from template import *


# This class is used to format the document as a python
# output file. Only certain tags are currently supported. This
# is currently intended mostly for converting C code into
# function calls
class template_python_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_inline = False
        self.m_num_prototypes = 0

    def format_source_code(self, code):

        code = re.sub("@", "\\@", code)
        code = re.sub("#", "\\#", code)

        return code

    def format_enum(self, tag):

        table = tag["contents"]
        
        if(table.has_key("title")):
            title = table["title"]
        else:
            title = ""

        title = re.sub("[ \n]+", " ", title).strip()

        if(table.has_key("caption")):
            caption = table["caption"]
        else:
            caption = ""

        caption = re.sub("[ \n]+", " ", caption).strip()

        values = ''

        for row in table["rows"]:

            name = row["cols"][0]["text"]
            val  = row["cols"][1]["text"]
            desc = row["cols"][2]["text"]


            values += '''- %s | %s | %s
''' % (name, val, desc)

        template = string.Template('''
@h4 $name
@enum: name="$name" caption="$caption"
- Name | Value | Description
$values
        ''')

        vars = {}
        vars["name"] = title
        vars["caption"] = caption
        vars["values"] = values

        return template.substitute(vars)
    
    
    def format_struct(self, tag):

        table = tag["contents"]
        
        if(table.has_key("title")):
            title = table["title"]
        else:
            title = ""

        title = re.sub("[ \n]+", " ", title).strip()

        if(table.has_key("caption")):
            caption = table["caption"]
        else:
            caption = ""

        caption = re.sub("[ \n]+", " ", caption).strip()

        values = ''

        for row in table["rows"]:

            bits = row["cols"][0]["text"]
            name = row["cols"][1]["text"]
            desc = row["cols"][2]["text"]

            values += '''- %s | %s | %s
''' % (bits, name, desc)

        template = string.Template('''
@h4 $name
@struct: name="$name" title="$title" caption="$caption"
- Width/Type | Name | Description
$values
        ''')

        vars = {}
        vars["name"] = title
        vars["title"] = title
        vars["caption"] = caption
        vars["values"] = values

        return template.substitute(vars)

    def format_prototype(self, tag):

        prototype = tag["contents"]

        self.m_num_prototypes += 1
       
        template = string.Template('''
@h4 $function_name
@prototype
- function:
    $function_name
$prototype
- description:
    $function_desc
$params
- returns:
    $function_returns
$function_example
$pseudocode
''')
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["prototype"] = ''
        function["function_desc"] = prototype["function_desc"]
        function["function_params"] = ''
        function["function_returns"] = prototype["function_returns"]
        function["pseudocode"] = ''

        if(prototype.has_key("function_prototype")):
            function["prototype"] = '''
- prototype:
    %s
''' % prototype["function_prototype"]["unparsed"]

        if(prototype.has_key("function_params")):
            output = ''
            params = prototype["function_params"]
            
            for param in params:

                output += '''- %s | %s | %s\n    ''' % (param["param_name"], param["param_io"], param["param_desc"])


            function["params"] = '''
- params:
    %s
''' % output



        if(prototype.has_key("function_example")):
            function["function_example"] = '''
- example:
%s
''' % self.format_source_code(prototype["function_example"]["unparsed"])
        
        if(prototype.has_key("function_pseudocode")):
            function["pseudocode"] = '''
- pseudocode:
%s
''' % self.format_source_code(prototype["function_pseudocode"]["unparsed"])


        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3})

        index.append(topic)
        
        return template.substitute(function)
    
    def append(self, tag):
        
        name = tag["name"]

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        elif(name == "prototype"):
            self.m_contents += self.format_prototype(tag)
        elif(name == "enum"):
            self.m_contents += self.format_enum(tag)
        elif(name == "struct"):
            self.m_contents += self.format_struct(tag)

    def get_contents(self):
        
        return self.m_contents
        
    def _load_template(self):
        
        handle = open(shorte_get_startup_path() + "/templates/shorte/%s.tpl" % self.m_engine.get_theme(), "r")
        contents = handle.read()
        handle.close()

        return contents
    
    def format_page(self, title, name, file_brief, file_author):

        template = string.Template(self._load_template())

        vars = {}
        vars["filename"] = name
        vars["title"] = title
        vars["subtitle"] = title
        vars["project"] = "Your project here"
        vars["description"] = file_brief
        vars["code" ] = self.get_contents()
        vars["header"] = '''
@h2 %s
@h3 File Description
@text
%s

@h3 File Author
@text
%s
'''% (title, file_brief, file_author)

        if(self.m_num_prototypes > 0):
            vars["header"] += '''
@h3 Function Summary
@text
This section describes the methods and types
exported by this module

@functionsummary
'''
        vars["header"] += '@h3 Methods and Structures\n'

        self.m_contents = ''

        return template.substitute(vars)

    
    def generate(self, theme, version, package):

        self.m_package = package
        self.m_inline = True
        
        page_names = {}
        
        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = ""

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            file_brief = page["file_brief"]
            file_author = page["file_author"]

            # Strip off the extension
            title = os.path.basename(source_file)
            output_file = re.sub("\.c", "", source_file)
            output_file = os.path.basename(output_file)

            base = output_file

            #print "BASE1: %s" % base

            # Now see if the page name already exists and modify
            # it as necessary
            cnt = 1
            while(page_names.has_key(base)):
                base = "%s_%d" % (output_file,cnt)
                cnt += 1

            page_names[base] = base
            output_file = base + ".tpl"

            #print "BASENAME: %s" % base

            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                self.append(tag)

            output = open(path, "w")
            output.write(self.format_page(title, output_file, file_brief, file_author))
            output.close

