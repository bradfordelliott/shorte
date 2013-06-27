#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   shorte_template.py
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


# This class is used to format the document as a shorte
# output file. Only certain tags are currently supported. This
# is currently intended mostly for converting C code into
# a shorte document.
class template_shorte_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_inline = False
        self.m_num_prototypes = 0
        self.m_num_structs = 0
        self.m_num_enums = 0

    def format_source_code(self, code):

        code = re.sub("@", "\\@", code)
        code = re.sub("#", "\\#", code)

        return code

    def format_textblock(self, input_data):

        txt = ''

        if(is_array(input_data)):
            for p in input_data:
                indent  = p["indent"]
                text    = p["text"]
                is_code = p["code"]
                is_list = p["list"]

                #print "Indent: [%d], text: [%s]" % (indent, text)

                if(is_list):
                    for elem in p["text"]:
                        txt += "- %s\n" % elem["text"]
                else:
                    txt += text

                #if(is_code):
                #    style = "margin-left:%dpx;background-color:#eee;border:1px solid #ccc;" % (30 )
                #else:
                #    style = "margin-left:%dpx;" % (20 + (indent * 10))

                #if(is_code):
                #    html += "<pre style=\"%s\">" % style + self.format_text(text) + "</pre>\n"
                #elif(is_list):
                #    html += self.format_list(p["text"], False, indent)
                #else:
                #    html += "<p style=\"%s\">" % style + self.format_text(text) + "</p>\n"
        else:
            txt = input_data

        return txt

    def format_enum(self, tag):

        self.m_num_enums += 1

        table = tag["contents"]
        
        if(table.has_key("title")):
            title = table["title"]
        else:
            title = ""

        title = re.sub("[ \n]+", " ", title).strip()

        if(table.has_key("caption")):
            caption = self.format_textblock(table["caption"])
        else:
            caption = ""

        caption = re.sub("[ \n]+", " ", caption).strip()

        values = ''

        for row in table["rows"]:

            name = row["cols"][0]["text"]
            val  = row["cols"][1]["text"]
            desc = row["cols"][2]["text"]
            desc = re.sub("\|", "\\\\\\|", desc)
            val = re.sub("\|", "\\\\\\|", val)

            values += '''- %s | %s | %s
''' % (name, val, desc)

        template = string.Template('''
@h4 $name

@enum: name="$name" caption="$caption"
- Enum Name | Enum Value | Enum Description
$values
        ''')

        vars = {}
        vars["name"] = title
        vars["caption"] = caption
        vars["values"] = values

        return template.substitute(vars)

    def format_define(self, tag):

        template = string.Template('''
@h4 $name

@define: name="$name" caption="$caption" value="$value"
        ''')

        vars = {}
        vars["name"] = tag["contents"]["name"]
        vars["caption"] = escape_string(tag["contents"]["desc"])
        vars["value"] = escape_string(tag["contents"]["value"])

        return template.substitute(vars)


    
    def format_struct(self, tag):
        
        self.m_num_structs += 1

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
            desc = desc.replace("#", "\#")

            values += '''- %s | %s | %s
''' % (bits, name, desc)

        template = string.Template('''
@h4 $name

@struct: name="$name" title="$title" caption="$caption"
- Type | Name | Description
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
$seealso
$deprecated
''')
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["prototype"] = ''
        function["function_desc"] = trim_blank_lines(prototype["function_desc"])
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

                output += '''-- %s | %s | %s\n    ''' % (param["param_name"], param["param_io"], param["param_desc"])


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

        if(prototype.has_key("function_see_also") and prototype["function_see_also"] != None):
            function["seealso"] = '''
- see also:
%s
''' % (prototype["function_see_also"])
        else:
            function["seealso"] = ''
        
        if(prototype.has_key("function_deprecated") and prototype["function_deprecated"] != None):
            function["deprecated"] = '''
- deprecated:
%s
''' % (prototype["function_deprecated"])
        else:
            function["deprecated"] = ''

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
        elif(name == "define"):
            self.m_contents += self.format_define(tag)

    def get_contents(self):
        
        return self.m_contents
        
    def _load_template(self):
        
        handle = open(g_startup_path + "/templates/shorte/%s.tpl" % self.m_engine.get_theme(), "r")
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
@text
%s
'''% (title, file_brief)

        if(self.m_num_prototypes > 0):
            vars["header"] += '''
@h3 Function Summary
@text
This section summarizes the methods exported by this module

@functionsummary
'''
        
        if(self.m_num_structs > 0 or self.m_num_enums > 0):
            vars["header"] += '''
@h3 Types Summary
@text
This section summarizes the types exported by this module

@typesummary
'''

        if(self.m_num_prototypes > 0 or self.m_num_enums > 0 or self.m_num_structs > 0):
            vars["header"] += '''
@h3 Methods and Structures
@text
The following section describes the methods and structures
exported by this module in greater detail.
'''

        self.m_contents = ''

        self.m_num_prototypes = 0
        self.m_num_structs = 0
        self.m_num_enums = 0

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

            # DEBUG BRAD: Rolling back this change for now
            output_file = re.sub("\.c", "", source_file)
            #output_file = source_file
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
    
    def generate_buffer(self, page):

        self.m_package = "tpl"
        self.m_inline = True
        
        page_names = {}
        
        # Format the output pages
        self.m_contents = ""

        tags = page["tags"]
        source_file = page["source_file"]
        file_brief = page["file_brief"]
        file_author = page["file_author"]

        # Strip off the extension
        title = os.path.basename(source_file)

        for tag in tags:
            self.append(tag)

        output_file = "tbd"

        return self.format_page(title, output_file, file_brief, file_author)

