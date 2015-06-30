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

from src.shorte_defines import *
from template import *


# This class is used to format the document as a shorte
# output file. Only certain tags are currently supported. This
# is currently intended mostly for converting C code into
# a shorte document.
class template_shorte_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = []
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
    
    def format_list_child(self, elem, indent=""):
        source = ''
        if(elem.children != None):
            if(elem.type == "checkbox"):
                if(elem.checked):
                    prefix = '[x]'
                else:
                    prefix = '[ ]'

                source += "%s-%s %s\n" % (indent, prefix, elem.get_text())
            else:
                source += "%s-%s\n" % (indent,elem.get_text())

            num_children = len(elem.children)
            #print "num_children = %d" % num_children
            for i in range(0, num_children):
                source += self.format_list_child(elem.children[i], indent + "    ")
        else:
            if(elem.type == "checkbox"):
                if(elem.checked):
                    prefix = "[x]"
                else:
                    prefix = "[ ]"
                source += "%s-%s %s\n" % (indent, prefix, elem.get_text())
            else:
                source += "%s-%s\n" % (indent,elem.get_text())

        return source
    
    def format_list(self, list, ordered=False, indent=0):

        source = ''

        for elem in list:
            source += self.format_list_child(elem)

        source += "\n"

        return source

    def format_textblock(self, input_data):

        txt = ''

        if(isinstance(input_data, textblock_t)):
            input_data = input_data.paragraphs

        if(is_array(input_data)):
            for p in input_data:
                indent  = p["indent"]
                text    = p["text"]
                is_code = p["code"]
                is_list = p["list"]

                #print "Indent: [%d], text: [%s]" % (indent, text)

                if(is_list):
                    txt += self.format_list(p["text"], False)
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

        enum = tag.contents
        
        title = enum.name
        title = re.sub("[ \n]+", " ", title).strip()

        description = self.format_textblock(enum.description)

        values = ''

        for row in enum.values:

            name = row["cols"][0]["text"]
            val  = row["cols"][1]["text"]
            desc = row["cols"][2]["text"]
            desc = re.sub("\|", "\\\\\\|", desc)
            val = re.sub("\|", "\\\\\\|", val)
            
            if(row["cols"][2].has_key("textblock")):
                lines = desc.split("\n") 
                desc = '\n'
                for line in lines:
                    desc += "   " + line + "\n"

            values += '''- %s | %s | %s
''' % (name, val, desc)

        template = string.Template("""
$heading
@enum: name="$name" private="$private" deprecated="$deprecated" deprecated_msg="$deprecated_msg" file="$file" line="$line" description='''
$description
'''
--values:
- Enum Name | Enum Value | Enum Description
$values
$example
$see_also
""")
        add_heading = shorte_get_config("shorte", "header_add_to_enum")
        if(tag.heading == None and ("None" != add_heading)):
            heading = '@%s %s' % (add_heading, title)
        else:
            heading = ''
        heading = ''
            
        vars = {}
        
        vars["example"] = self.format_object_example(enum)
        vars["see_also"] = self.format_object_see_also(enum)
        vars["name"] = title
        vars["heading"] = heading
        vars["description"] = description
        vars["values"] = values
        vars["private"] = enum.private
        vars["deprecated"] = enum.deprecated
        vars["deprecated_msg"] = enum.deprecated_msg
        vars["file"] = enum.get_file()
        vars["line"] = enum.get_line()

        return template.substitute(vars)

    def format_define(self, tag):

        template = string.Template("""
$heading
@define: private="$private" deprecated="$deprecated" file="$file" line="$line"
--name:
    $name
--value:
    $value
--description:
    $description
""")

        vars = {}

        define = tag.contents

        add_heading = shorte_get_config("shorte", "header_add_to_define")
        if(tag.heading == None and ("None" != add_heading)):
            heading = '@%s %s' % (add_heading, define.name)
        else:
            heading = ''

        heading = ''

        vars["name"] = define.name
        vars["heading"] = heading
        val = self.format_textblock(define.description)
        vars["description"] = indent_lines(trim_leading_indent(val), '    ')
            
        val = self.format_textblock(define.value)
        val = re.sub("\|", "\\\\\\|", val)
        vars["value"] = escape_string(val)
        vars["private"] = define.private
        vars["deprecated"] = define.deprecated
        vars["file"] = define.get_file()
        vars["line"] = define.get_line()

        return template.substitute(vars)


    
    def format_struct(self, tag):
        
        self.m_num_structs += 1
        
        struct = tag.contents

        title = struct.get_name()
        title = re.sub("[ \n]+", " ", title).strip()


        caption = self.format_textblock(struct.get_description())

        values = ''


        # DEBUG BRAD: Need to figure out how to deal with this
        fields = "rows"
        attributes = "cols"

        fields = "fields"
        attributes = "attrs"

        for field in struct.get_fields():

            bits = field.get_type() #field.get_bits()
            name = field.get_name()
            desc = indent_lines(self.format_textblock(field.get_description()), '    ')
            
            values += '''- %s | %s |\n%s
''' % (bits, name, desc)

        template = string.Template("""
$heading
@struct: private="$private" deprecated="$deprecated" file="$file" line="$line"
--name:
$name
--description:
$description
--fields:
- Type | Name | Description
$values
$example
$see_also
""")

        vars = {}

        add_heading = shorte_get_config("shorte", "header_add_to_struct")
        if(tag.heading == None and ("None" != add_heading)):
            heading = '@%s %s' % (add_heading,title)
            parent = ''
        else:
            heading = ''
            parent = tag.heading
        heading = ''

        #print "HEADING: %s" % heading

        vars["example"] = self.format_object_example(struct)
        vars["see_also"] = self.format_object_see_also(struct)

        vars["name"] = title
        vars["parent"] = parent
        vars["heading"] = heading
        vars["description"] = indent_lines(caption, '    ')
        vars["values"] = values
        vars["deprecated"] = "False"
        vars["private"] = "False"
        vars["file"] = struct.get_file()
        vars["line"] = struct.get_line()

        return template.substitute(vars)

    def format_object_see_also(self, obj):
        if(not obj.has_see_also()):
            return ''
        else:
            return '''
--see:
    %s
''' % obj.get_see_also()

    def format_object_example(self, obj):
        example = ''

        if(obj.example != None):
            example = '''
--example:
%s
''' % self.format_source_code(obj.example.get_unparsed())

        return example

    def format_class(self, tag):
        cls = tag.contents
        
        template = string.Template('''$title
@class: file="${file}" line="${line}"
--name: $name
--description:
$desc
''')
        
        add_heading = shorte_get_config("shorte", "header_add_to_prototype")
        if(tag.heading == None and ("None" != add_heading)):
            title = '@%s %s' % (add_heading,cls.get_name())
        else:
            title = ''
        title = ''

        vars = {}
        vars["title"] = title
        vars["name"] = cls.get_name()
        vars["desc"] = trim_blank_lines(cls.get_description(textblock=False))
        vars["file"] = cls.get_file()
        vars["line"] = cls.get_line()
        
        topic = topic_t({"name"   : cls.get_name(),
                         "file"   : tag.file, 
                         "indent" : 3,
                         "tag"    : tag})

        index.append(topic)
        
        return template.substitute(vars)
    

    def format_prototype(self, tag):

        prototype = tag.contents

        self.m_num_prototypes += 1
       
        template = string.Template('''
$title
@prototype: file="${file}" line="${line}"
--function:
    $name
$prototype
--description:
$desc
$params
--returns:
    $returns
$example
$pseudocode
$seealso
$deprecated
$heading
$class
''')
        add_heading = shorte_get_config("shorte", "header_add_to_prototype")
        if(tag.heading == None and ("None" != add_heading)):
            title = '@%s %s' % (add_heading,prototype.get_name())
        else:
            title = ''
        title = ''

        function = {}
        function["title"] = title
        function["name"] = prototype.get_name()
        function["example"] = ''
        function["prototype"] = ''
        function["desc"] = trim_blank_lines(prototype.get_description(textblock=False))
        function["params"] = ''
        function["returns"] = prototype.get_returns()
        function["pseudocode"] = ''
        function["heading"] = ''
        function["file"] = prototype.get_file()
        function["line"] = prototype.get_line()
        function["class"] = ''

        if(prototype.has_prototype()):
            function["prototype"] = '''
--prototype:
    %s
''' % prototype.get_prototype().get_unparsed()

        if(prototype.has_params):
            output = ''
            params = prototype.get_params()
            
            for param in params:

                output += '''-- %s | %s | %s\n    ''' % (param.get_name(), param.get_io(), param.get_description(textblock=False))


            function["params"] = '''
--params:
    %s
''' % output


        if(prototype.has_example()):
            import src.shorte_source_code
            func = src.shorte_source_code.prototype_t()
            func.example = prototype.get_example()
            function["example"] = self.format_object_example(func)
        
        if(prototype.has_pseudocode()):
            function["pseudocode"] = '''
--pseudocode:
%s
''' % self.format_source_code(prototype.get_pseudocode().get_unparsed())

        if(prototype.has_see_also()):
            function["seealso"] = '''
--see:
%s
''' % (prototype.get_see_also())
        else:
            function["seealso"] = ''
        
        if(prototype.get_deprecated()):
            function["deprecated"] = '''
--deprecated:
%s
''' % (self.format_textblock(prototype.get_deprecated_msg()))
        else:
            function["deprecated"] = ''

        if(prototype.has_class()):
            function['class'] = prototype.get_class().get_name()
        
# DEBUG BRAD: Should I continue supporting this?
#        if(prototype.has_key("heading") and prototype["heading"] != ""):
#            function["heading"] = '''
#-- heading:
#%s
#''' % (prototype["heading"])
#        else:
#            function["heading"] = ''

        topic = topic_t({"name"   : prototype.get_name(),
                         "file"   : tag.file, 
                         "indent" : 3,
                         "tag"    : tag})

        index.append(topic)
        
        return template.substitute(function)

    def format_header(self, tag):
        
        output = "@%s" % tag.get_name()
        if(tag.has_modifiers()):
            output += ": %s\n" % tag.get_modifiers_as_string()
        else:
            output += " "

        heading = tag.get_contents().strip()

        if(heading.startswith("@")):
            output += "\\"

        output += heading + "\n"

        return output

    def format_tag(self, tag):
        #print "NAME: %s" % tag.name
        if(tag.name in "text"):
            if(0 == len(tag.source.strip())):
                return ''

        output = "@%s" % tag.name
        if(tag.modifiers):
            modifiers = []
            for mod in tag.modifiers:
                modifiers.append("%s='''%s'''" % (mod, tag.modifiers[mod]))

            output += ": %s" % ' '.join(modifiers)
        else:
            pass

        output += "\n"
        output += tag.source + "\n"

        return output

    
    def append(self, tag):
        
        #print tag
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        elif(name == "prototype"):
            self.m_contents.append(self.format_prototype(tag))
        elif(name == "class"):
            self.m_contents.append(self.format_class(tag))
        elif(name == "enum"):
            self.m_contents.append(self.format_enum(tag))
        elif(name == "struct"):
            self.m_contents.append(self.format_struct(tag))
        elif(name == "define"):
            self.m_contents.append(self.format_define(tag))
        elif(name in ("h1", "h2", "h3", "h4", "h5")):
            self.m_contents.append(self.format_header(tag))
        else:
            #print "name: %s" % name
            self.m_contents.append(self.format_tag(tag))

    def get_contents(self):
        
        return ''.join(self.m_contents)
        
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

        vars["header"] = ''
        
#        auto_summary = self.m_engine.get_config("shorte", "auto_summarize")
#
#        if("1" == auto_summary):
#            vars["header"] = '''
#@h2 %s
#@text
#%s
#'''% (title, file_brief)
#
#            if(self.m_num_prototypes > 0):
#                vars["header"] += '''
#@h3 Function Summary
#@text
#This section summarizes the methods exported by this module
#
#@functionsummary
#'''
#            
#            if(self.m_num_structs > 0 or self.m_num_enums > 0):
#                vars["header"] += '''
#@h3 Types Summary
#@text
#This section summarizes the types exported by this module
#
#@typesummary
#'''
#    
#            if(self.m_num_prototypes > 0 or self.m_num_enums > 0 or self.m_num_structs > 0):
#                vars["header"] += '''
#@h3 Methods and Structures
#@text
#The following section describes the methods and structures
#exported by this module in greater detail.
#'''

        self.m_contents = []

        self.m_num_prototypes = 0
        self.m_num_structs = 0
        self.m_num_enums = 0

        return template.substitute(vars)

    
    def generate(self, theme, version, package):

        self.m_package = package
        self.m_inline = True

        #print "template_shorte.py::generate()"
        
        page_names = {}
        
        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = []

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            file_brief = ''
            if("file_brief" in page):
                file_brief = page["file_brief"]
            file_author = ''
            if("file_author" in page):
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

        #print "template_shorte.py::generate_buffer()"
        
        page_names = {}
        
        # Format the output pages
        self.m_contents = []

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

