import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from shorte_defines import *
from template import *
from src.parsers.cpp_parser import *


class template_c_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_header = {}
        self.m_header["structs"] = ""
        self.m_header["prototypes"] = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_inline = False
        self.m_format = self.m_engine.get_config("c", "format")
        self.m_comment_style = self.m_engine.get_config("c", "comment_style")
        self.m_header_style = self.m_engine.get_config("c", "header_style")

        self.m_prototypes = {}

        self.m_index_header_structs = ""
        self.m_index_header_prototypes = ""
        self.m_index_module = ""

    def set_output_format(self, record_format):
        self.m_format = record_format

    def allow_diagnostic_code(self, allow):
        self.m_allow_diagnostic_code = allow
   
    def load_source(self, path):

        parser = cpp_parser_t(self.m_engine)
        parser.parse(path)
        pages = parser.get_pages()

        for page in pages:

            tags = page["tags"]

            for tag in tags:
                if(tag["name"] == "prototype"):
                    prototype = tag["contents"]
                    name = prototype["function_name"]
                    self.m_prototypes[name] = prototype

        
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
    
    def _format_desc_header(self, desc):
    
        if(self.m_comment_style == COMMENT_STYLE_SHORTE):
            desc = self.format_comment(desc, "// ")
        else:
            desc = self.format_comment(desc, " * ")

        return desc

    def _format_pseudocode(self, prototype, comment=True):

        pseudocode = ''
        prefix = '    '

        if(prototype.has_key("function_pseudocode")):
       
            start = ''
            end = ''

            name = prototype["function_name"]
            code = prototype["function_pseudocode"]["parsed"]
            language = prototype["function_pseudocode"]["language"]
            has_prefix = True

            if(self.m_prototypes.has_key(name)):
                comment = False
                code = self.m_prototypes[name]["function_pseudocode"]["parsed"]

            if(self.m_comment_style == COMMENT_STYLE_SHORTE):

                if(comment):
                    prefix = '    // '

                start = '''
    // FUNCTION PSEUDOCODE:
'''
            else:
                if(comment):
                    prefix = '     * '
                
                    start = '''
    /* FUNCTION PSEUDOCODE:
'''
                    end = '''    */'''
                    
                else:
                    start = '''
    /* FUNCTION PSEUDOCODE: */
'''

            if(self.m_prototypes.has_key(name)):
                start = ''
                end = ''
        
            pseudocode = '''%s
%s%s
''' % (start, self.format_source_code(language, code, prefix), end)

        return pseudocode

    
    def format_prototype(self, tag):

        modifiers = tag["modifiers"]
        prototype = tag["contents"]

        comment_pseudocode = True

        # Check to see if the user has requested not to export this method
        if(modifiers.has_key("export")):
            export = modifiers["export"]

            if(export == "0"):
                #print "Skipping exporting prototype %s" % prototype["function_name"]
                contents = {}
                contents["header"] = ""
                contents["module"] = ""
                return contents

        if(modifiers.has_key("comment_pseudocode")):

            if(modifiers["comment_pseudocode"] == "0"):
                comment_pseudocode = False

        templates = {}
        templates["module"] = {}
        templates["param"] = {}
        templates["header"] = {}

        templates["header"][HEADER_STYLE_KERNEL] = string.Template('''
/* ${function_desc_header} */
${prototype};
''')
        templates["header"][HEADER_STYLE_DOXYGEN] = string.Template('''
/* ${function_desc_header} */
${prototype};
''')
        templates["header"][HEADER_STYLE_SHORTE] = string.Template('''
// ${function_desc_header}
${prototype};
''')
        
        templates["module"][HEADER_STYLE_SHORTE] = string.Template("""
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
        templates["module"][HEADER_STYLE_KERNEL] = string.Template("""
/**
 * ${function_name}
 *${function_params}
 *
 * ${function_desc}
 */
${prototype}
{${pseudocode}}
""")
        
        templates["module"][HEADER_STYLE_DOXYGEN] = string.Template("""
/**
 * ${function_desc}
 *
 *${function_params}
 *
 */
${prototype}
{${pseudocode}
    return CS_ERROR;
}
""")

        templates["param"][HEADER_STYLE_KERNEL] = string.Template("""
 *  @${param_name} [${param_io}] - ${param_desc}""")

        templates["param"][HEADER_STYLE_SHORTE] = string.Template("""
//|     ${param_name} [${param_io}] - ${param_desc}""")
        
        templates["param"][HEADER_STYLE_DOXYGEN] = string.Template("""
 *  @param ${param_name} [${param_io}] - ${param_desc}""")

    
        template_prototype = string.Template("""${function_prototype}
""");

        
        file = "blah"
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["prototype"] = ''
        function["function_desc"] = ''
        function["function_desc_header"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''
        function["pseudocode"] = ''

        if(prototype.has_key("function_desc")):
            function["function_desc"] = self._format_desc(prototype["function_desc"])
            function["function_desc_header"] = self._format_desc_header(prototype["function_desc"])

        if(prototype.has_key("function_prototype")):

            # Replace any semicolons
            code = prototype["function_prototype"]["unparsed"]
            code = re.sub(";", "", code)

            function["prototype"] = code

        if(prototype.has_key("function_params")):
            params = prototype["function_params"]

            output = ''
            for param in params:
                
                if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                    prefix = "//|      "
                else:
                    prefix = " *      "

                tmp = ''
                for val in param["param_desc"]:
                    if(len(val) == 2):
                        tmp += self.format_comment("%s = %s" % (val[0], val[1]), prefix)
                    else:
                        tmp += self.format_comment("%s" % (val), prefix)


                param["param_desc"] = tmp

                output += templates["param"][self.m_header_style].substitute(param)

            function["function_params"] = output

        if(prototype.has_key("function_returns")):
            function["function_returns"] = prototype["function_returns"]

        function["pseudocode"] = self._format_pseudocode(prototype, comment_pseudocode)
                
        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)

        contents = {}
        contents["header"] = templates["header"][self.m_header_style].substitute(function)
        contents["module"] = templates["module"][self.m_header_style].substitute(function)

        return contents
    
   
    def format_enum(self, tag):

        table = tag["contents"]
        modifiers = tag["modifiers"]
        fields = ''

        i = 0
        
        for row in table["rows"]:

            if i == 0:
                i += 1
                continue

            #if(row["is_subheader"] or row["is_header"] or row["is_reserved"] or i == 0):
            #    continue

            cols = row["cols"]

            enum = cols[0]["text"]

            #print "i = %d, VAL = %s" % (i, cols[1]["text"])
            val  = int(cols[1]["text"], 16)
            desc = cols[2]["text"]

            tmp = ''
             
            if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                tmp += '''    // %s\n''' % (self.format_comment(desc, "%*s// " % (len(tmp), " "), len(tmp)))
            else:
                tmp += '''    /* %s */\n''' % (self.format_comment(desc, "%*s* " % (len(tmp)+1, " "), len(tmp)))

            tmp += '''    %s = 0x%x,\n''' % (enum, val)

            fields += tmp

            i += 1

        templates = {}
        templates[COMMENT_STYLE_KERNEL] = string.Template('''
/**
$desc
 */
typedef enum
{
$fields
}$name;
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
        vars["desc"] = ""

        if(self.m_comment_style == COMMENT_STYLE_SHORTE):
            vars["desc"] = '// ' + self.format_comment(modifiers["caption"], "// ")
        else:
            vars["desc"] = ' * ' + self.format_comment(modifiers["caption"], " * ")

        return templates[self.m_comment_style].substitute(vars)

    
    def format_struct(self, tag):
        
        struct = tag["contents"]

        define_prefix = ''
        if(tag["modifiers"].has_key('define_prefix')):
            define_prefix = tag["modifiers"]["define_prefix"]

        header = ''
        module = ''

        header = struct["record"].to_c(self.m_format, define_prefix, self.m_comment_style, self.m_header_style)
        #header = struct["record"].to_c("native", define_prefix, self.m_comment_style, self.m_header_style)

        if(self.m_allow_diagnostic_code):
            module = struct["record"].to_c_support_routines()

        struct = {}
        struct["header"] = header
        struct["module"] = module

        return struct

   
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
            contents = self.format_struct(tag)
            self.m_contents += contents["module"]
            self.m_header["structs"] += contents["header"]
        elif(name == "prototype"):
            contents = self.format_prototype(tag)
            self.m_contents += contents["module"]
            self.m_header["prototypes"] += contents["header"]
        elif(name == "enum"):
            self.m_header["structs"] += self.format_enum(tag)
        else:
            print "WARNING: Skipping %s for now" % name


    def get_contents(self, what):

        if(what == "module"):
            return self.m_contents

        return self.m_header

        
    def _load_template(self, what="module"):
       
        if(what == "module"):
            ext = ".c"
        else:
            ext = ".h"

        handle = open(shorte_get_startup_path() + "/templates/c/%s%s" % (self.m_engine.get_theme(), ext), "r")
        contents = handle.read()
        handle.close()

        return contents
    
    def format_page(self, name, basename, what):

        template = string.Template(self._load_template(what))

        vars = {}
        vars["filename"] = name
        vars["project"] = "Your project here"
        vars["description"] = "Automatically generated by shorte"

        contents = self.get_contents(what)

        if(what == "header"):
            vars["code"] = contents["structs"] + contents["prototypes"]

            
            if(contents["structs"].strip() != ""):
                name = name.replace("leeds", "cs4321")
                name = name.replace(".h.h", ".h")
                self.m_index_header_structs += '''
/******************************************************************************
 * API Structures from %s
 ******************************************************************************/
''' % (name)
                self.m_index_header_structs += contents["structs"]
            
            if(contents["prototypes"].strip() != ""):
                name = name.replace("leeds", "cs4321")
                name = name.replace(".h.h", ".h")
                self.m_index_header_prototypes += '''
            
/******************************************************************************
 * API Methods from %s
 ******************************************************************************/
''' % name
                self.m_index_header_prototypes += contents["prototypes"]
        else:
            vars["code" ] = contents
            self.m_index_module += contents

        define = name
        define = re.sub("\.", "_", define)
        vars["define"] = "%s" % define.upper()

        if(what == "module"):
            vars["includes"] = '#include "%s.h"' % basename
        else:
            vars["includes"] = ''

        return template.substitute(vars)

    def generate_index(self, theme):
        
        template = string.Template(self._load_template("header"))
        
        vars = {}
        vars["filename"] = "cs4321_api.h"
        vars["project"] = "CS4321"
        vars["description"] = "Customer API for the CS4321 family of devices"
        vars["code"] = self.m_index_header_structs + self.m_index_header_prototypes
        vars["define"] = "CS4321_API"

        handle = open(self.m_engine.get_output_dir() + "/cs4321_api.h", "wt")
        handle.write(template.substitute(vars))
        handle.close()

    
    def generate(self, theme, version, package):

        self.m_package = package
        self.m_inline = True
        
        page_names = {}
        
        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = ""
        self.m_header = {}
        self.m_header["structs"] = ""
        self.m_header["prototypes"] = ""

        txt_structs = ""
        txt_prototypes = ""

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]

            # Check to see if a source file was associated
            # with this module. If so load it to get any
            # function definitions
            if(page.has_key("header")):
                header = page["header"]
                if(header.has_key("csource")):
                    self.load_source(header["csource"])


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

            # Generate the .c file
            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                self.append(tag)

            output = open(path, "w")
            output.write(self.format_page(output_file, base, "module"))
            self.m_contents = ''
            output.close

            # Generate the .h file
            output_file = base + ".h"
            path = self.m_engine.get_output_dir() + "/" + output_file

            output = open(path, "w")
            output.write(self.format_page(output_file, base, "header"))
            output.close

            self.m_header = {}
            self.m_header["structs"] = ""
            self.m_header["prototypes"] = ""
    
        self.generate_index(theme)


