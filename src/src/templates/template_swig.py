import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from src.shorte_defines import *
from template import *


class template_swig_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_inline = False
        self.m_comment_style = COMMENT_STYLE_SHORTE
        self.m_allow_bitfields = True
        self.m_allow_diagnostic_code = True

    
    def format_source_code(self, language, tags, prefix='    // '):

        output = ''

        for tag in tags:

            type = tag["type"]
            source = tag["data"]
        
            if(type == TAG_TYPE_WHITESPACE):
                output += ' '
            elif(type == TAG_TYPE_NEWLINE):
                output += ''
            else:
                output += source

        lines = output.split('\n')
        output = ''

        for line in lines:
            output += '%s%s\n' % (prefix, line)

        return output

    def _format_desc(self, desc):
    
        if(self.m_comment_style == COMMENT_STYLE_SHORTE):
            desc = self.format_comment(desc, "//|     ")
        else:
            desc = self.format_comment(desc, " * ")

        return desc

    def _format_pseudocode(self, prototype):

        pseudocode = ''
    
        if(prototype.has_key("function_pseudocode")):

            if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                pseudocode = '''
    // FUNCTION PSEUDOCODE:
%s
''' % self.format_source_code(prototype["function_pseudocode"]["language"], prototype["function_pseudocode"]["parsed"], '    // ')

            else:
                pseudocode = '''
    /* FUNCTION PSEUDOCODE:
%s     */
''' % self.format_source_code(prototype["function_pseudocode"]["language"], prototype["function_pseudocode"]["parsed"], '     * ')

        return pseudocode

    
    def format_prototype(self, tag):

        templates = {}
        templates["prototype"] = {}
        templates["param"] = {}
        
        templates["prototype"][COMMENT_STYLE_SHORTE] = string.Template("""
//+----------------------------------------------------------------------------
//|
//| Function:
//|     ${function_name}
//| 
//| Description:
//|     ${function_desc}
//|                     
//| Params:
//|     ${function_params}
//|                 
//| Returns:
//|     ${function_returns}
//|     
//+----------------------------------------------------------------------------
${prototype}
{${pseudocode}}
""")
        templates["prototype"][COMMENT_STYLE_KERNEL] = string.Template("""
/**
 * ${function_name}
 *${function_params}
 *
 * ${function_desc}
 */
${prototype}
{${pseudocode}}
""")

        templates["param"][COMMENT_STYLE_KERNEL] = string.Template("""
 *  @${param_name} ${param_io} - ${param_desc}""")

        templates["param"][COMMENT_STYLE_SHORTE] = string.Template("""
//|     ${param_name} ${param_io} - ${param_desc}""")

    
        template_prototype = string.Template("""${function_prototype}
""");

        prototype = tag["contents"]
        
        file = "blah"
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["prototype"] = ''
        function["function_desc"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''
        function["pseudocode"] = ''

        if(prototype.has_key("function_desc")):
            function["function_desc"] = self._format_desc(prototype["function_desc"])

        if(prototype.has_key("function_prototype")):

            # Replace any semicolons
            code = prototype["function_prototype"]
            code = re.sub(";", "", code)

            function["prototype"] = code

        if(prototype.has_key("function_params")):
            params = prototype["function_params"]

            output = ''
            for param in params:

                #if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                #    param["param_desc"] = self.format_comment(param["param_desc"], "//|     ")
                #else:
                #    param["param_desc"] = self.format_comment(param["param_desc"], " *     ")

                output += templates["param"][self.m_comment_style].substitute(param)

            function["function_params"] = output

        if(prototype.has_key("function_returns")):
            function["function_returns"] = prototype["function_returns"]

        function["pseudocode"] = self._format_pseudocode(prototype)

                


        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)
        
        return templates["prototype"][self.m_comment_style].substitute(function)
    
   
    def format_enum(self, tag):

        enums = tag["contents"]
        modifiers = tag["modifiers"]
        fields = ''
        val = 0

        for enum in enums:

            tmp = '''    %s = %d, ''' % (enum["enum"], val)
             
            if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                tmp += '''// %s\n''' % (self.format_comment(enum["desc"], "%*s// " % (len(tmp), " "), len(tmp)))
            else:
                tmp += '''/* %s */\n''' % (self.format_comment(enum["desc"], "%*s* " % (len(tmp)+1, " "), len(tmp)))

            fields += tmp


            val += 1

        templates = {}
        templates[COMMENT_STYLE_KERNEL] = string.Template('''
/**
 * enum $name
 *
$desc
 */
enum $name
{
$fields
};
''')
        templates[COMMENT_STYLE_SHORTE] = string.Template('''
// enum $name
//
$desc
enum $name
{
$fields
};
''')

        vars = {}
        vars["name"] = modifiers["name"]
        vars["fields"] = fields

        if(self.m_comment_style == COMMENT_STYLE_SHORTE):
            vars["desc"] = '// ' + self.format_comment(modifiers["caption"], "// ")
        else:
            vars["desc"] = ' * ' + self.format_comment(modifiers["caption"], " * ")

        return templates[self.m_comment_style].substitute(vars)

    
    def format_struct(self, tag):
        
        struct = tag["contents"]

        code = ''
        if(self.m_allow_bitfields):
            code += struct["record"].to_c(True, self.m_comment_style, self.m_comment_style)
        else:
            code += struct["record"].to_c(False, self.m_comment_style, self.m_comment_style)

        if(self.m_allow_diagnostic_code):
            code += struct["record"].to_c_support_routines()

        return code

   
    def format_comment(self, data, prefix, start=0):

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)

        # Replace any bold
        data = re.sub(r'\*(.*?)\*', r'\1', data)


        # Collapse any newlines and multiple whitespace
        data = re.sub(r'\n', ' ', data)
        data = re.sub(r' +', ' ', data)
        
        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "\n%s    " % prefix, data)
       
        words = re.split(r' ', data)

        line_length = start
        output = ''

        for word in words:

            output += word + ' '
            line_length += (len(word) + 1)
            
            if(line_length > (80 - len(prefix))):
                line_length = 0
                output += '\n' + prefix

        return output


    def format_text(self, data):

        # Collapse multiple spaces
        data = re.sub('\n', " ", data)
        data = re.sub(" +", " ", data)

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)
       
        words = re.split(r' ', data)

        line_length = 0
        output = ''

        for word in words:

            output += word + ' '
            line_length += (len(word) + 1)
            
            if(line_length > 80):
                line_length = 0
                output += '\n'

        return output


    
    def append_source_code(self, tag):

        rc = ''
        rc += self.format_source_code(tag["name"], tag["contents"])
        result = tag["result"]

        if(result != None):

            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            nl = re.compile("\n")
            ws = re.compile(" ")

            result = lt.sub("&lt;", result)
            result = gt.sub("&gt;", result)
            result = nl.sub("<br>", result)
            result = ws.sub("&nbsp;", result)

            self.m_contents += code_template.substitute(
                    {"contents" : rc,
                     "result"   : result,
                     "source"   : "blah"});
        else:
            self.m_contents += code_template_no_result.substitute(
                    {"contents" : rc,
                     "source"   : "blah"});

    
    def append(self, tag):
        
        name = tag["name"]

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name == "struct"):
            self.m_contents += self.format_struct(tag)
        elif(name == "prototype"):
            self.m_contents += self.format_prototype(tag)
        elif(name == "enum"):
            self.m_contents += self.format_enum(tag)


    def get_contents(self):
        
        return self.m_contents
        
    def _load_template(self):
        
        handle = open(shorte_get_startup_path() + "/templates/swig/%s.i" % self.m_engine.get_theme(), "r")
        contents = handle.read()
        handle.close()

        return contents
    
    def format_page(self, name):

        template = string.Template(self._load_template())

        vars = {}
        vars["filename"] = name
        vars["project"] = "Your project here"
        vars["description"] = "Automatically generated by shorte"
        vars["code" ] = self.get_contents()
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

            # Strip off the extension
            output_file = re.sub(".tpl", "", source_file)
            output_file = os.path.basename(output_file)

            base = output_file

            # Now see if the page name already exists and modify
            # it as necessary
            cnt = 1
            while(page_names.has_key(base)):
                base = "%s_%d" % (output_file,cnt)
                cnt += 1

            page_names[base] = base
            output_file = base + ".c"

            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                self.append(tag)

            output = open(path, "w")
            output.write(self.format_page(output_file))
            output.close

