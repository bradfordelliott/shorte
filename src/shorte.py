#!/usr/bin/env python
#+------------------------------------------------------------------------------
#|
#| SCRIPT:
#|    shorte.py
#|
#| FILE DESCRIPTION:
#|    This the entry point of the shorte shorthand parser. It takes input
#|    shorthand files and converts them into an output document.
#|
#+-------------------------------------------------------------------------------
#|
#| Copyright (c) Brad Elliott
#|
#+------------------------------------------------------------------------------
import sys
import os
import re
import platform
import shutil
from optparse import OptionParser
import string
from string import Template;
import time
import datetime
import ConfigParser, os
from types import *

from shorte_defines import *
from shorte_source_code import *
from src.parsers.shorte_parser import *
from src.parsers.cpp_parser import *
from shorte_code_executor import *
from src.templates.template_html import template_html_t
from src.templates.template_odt  import template_odt_t
from src.templates.template_word import template_word_t
from src.templates.template_text import template_text_t
from src.templates.template_twiki import template_twiki_t
from src.templates.template_c import template_c_t
from src.templates.template_vera import template_vera_t
from src.templates.template_shorte import template_shorte_t
from src.templates.template_swig import template_swig_t
from src.templates.template_labview import template_labview_t
from src.templates.template_mergefile import template_mergefile_t
from src.templates.template_sql import template_sql_t
from src.templates.template_mediawiki import template_mediawiki_t


#+------------------------------------------------------------------------------
#|
#| CLASS: engine_t
#|
#| DESCRIPTION:
#|    This is the main implementation class of the shorte parser. It parses
#|    the input source files and generates the output documentation.
#|
#+------------------------------------------------------------------------------
class engine_t:
    def __init__(self, output_path, config_file, parser):
        self.m_theme = "cortina"
        self.m_snippets = {}
        self.m_urls = {}
        self.m_example_id = 0

        if(output_path == None):
            output_path = "build-output"
        self.m_output_directory = output_path
        
        self.m_pages = []
        self.m_images = []

        # A list of imagemaps associated with images
        self.m_imagemaps = {}
        self.m_macros = {}

        self.m_docsubtitle = ""
        self.m_docversion = None
        self.m_package = ""
        self.m_docnumber = None
        self.m_revision_history = None

        self.m_output_filename = None

        self.m_include_queue = []

        self.m_search_and_replace = None

        # Create the output directory if it doesn't exist already
        #print "OUTPUT_DIR: %s" % self.m_output_directory
        if(not os.path.exists(self.m_output_directory)):
            os.makedirs(self.m_output_directory)

        self.m_date = datetime.datetime.now().strftime("%d %B %Y")

        if(parser == "cpp"):
            self.m_parser = cpp_parser_t(self)
        else:
            self.m_parser = shorte_parser_t(self)
            self.m_parser.set_cpp_parser(cpp_parser_t(self))

        # Read the configuration file
        self.m_config = ConfigParser.ConfigParser()
        self.m_config.read([config_file])

    def get_doc_revision_history(self):
        return self.m_revision_history

    def set_theme(self, theme):
        self.m_theme = theme

    def get_theme(self):
        return self.m_theme

    def set_title(self, title):
        self.m_parser.set_title(title)
    def get_title(self):
        return self.m_parser.get_title()

    def get_file_name(self):
        return self.m_output_filename

    def set_subtitle(self, subtitle):
        self.m_parser.set_subtitle(subtitle)

    def get_subtitle(self):
        return self.m_parser.get_subtitle()

    def set_version(self, version):
        self.m_docversion = version

    def set_package(self, package):
        self.m_package = package

    def set_template(self, template):
        self.m_template = template
        self.m_template.m_title = self.m_parser.get_title()



    def get_version(self):

        if(self.m_docversion == None):
            return "N/A"
        return self.m_docversion

    def get_date(self):
        return self.m_date

    def get_doc_number(self):
        if(self.m_docnumber == None):
            return ""

        return self.m_docnumber

    def get_output_dir(self):
        return self.m_output_directory

    def set_output_dir(self, path):
        self.m_output_directory = path
        if(not os.path.exists(self.m_output_directory)):
            os.makedirs(self.m_output_directory)

    def set_working_dir(self, path):
        os.chdir(path)
    
    def _expand_url(self, matches):
        return self.m_parser.m_urls[matches.groups()[0]]


    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    ()
    #|
    #| DESCRIPTION:
    #|    
    #| 
    #| PARAMETERS:
    #|    
    #| 
    #| RETURNS:
    #|    
    #|
    #+-----------------------------------------------------------------------------
    def _mkdir(self, newdir):
        """works the way a good mkdir should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                self._mkdir(head)
            #print "_mkdir %s" % repr(newdir)
            if tail:
                os.mkdir(newdir)
    
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    ()
    #|
    #| DESCRIPTION:
    #|    
    #| 
    #| PARAMETERS:
    #|    
    #| 
    #| RETURNS:
    #|    
    #|
    #+-----------------------------------------------------------------------------
    def install_support_files(self, outputdir):

        self.m_template.install_support_files(outputdir)
    
    def tag_is_source_code(self, tag_name):

        return self.m_parser.tag_is_source_code(tag_name)

    def tag_is_header(self, tag_name):
        
        return self.m_parser.tag_is_header(tag_name)

    def tag_is_executable(self, tag_name):

        return self.m_parser.tag_is_executable(tag_name)
                
    
    
    
    def create_tag(self, type, data):

        tag = {}
        tag["data"] = data
        tag["type"] = type

        return tag

    def get_keyword_list(self, language):

        code = source_code_t()
        keywords = code.get_keyword_list(language)

        return keywords

    def get_config(self, section, key):

        if(section == "shorte" and key == "scratchdir"):
            dir = self.m_config.get(section, key)
            dir = os.path.abspath(dir)
            return dir

        if(section == "c"):
            val = self.m_config.get(section, key)

            if(key == "comment_style"):
                if(val == "c"):
                    return COMMENT_STYLE_KERNEL
                else:
                    return COMMENT_STYLE_SHORTE

            if(key == "header_style"):
                if(val == "doxygen"):
                    return HEADER_STYLE_DOXYGEN
                elif(val == "kernel"):
                    return HEADER_STYLE_KERNEL
                else:
                    return HEADER_STYLE_SHORTE


        if(self.m_config.has_option(section, key)):
            return self.m_config.get(section, key)

        return None

    def set_config(self, section, key, val):
        if(self.m_config.has_option(section, key)):
            return self.m_config.set(section, key, val)



    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    parse_page()
    #| 
    #| DESCRIPTION:
    #|    This is a fairly simplistic parser used to parse the contents of an
    #|    input source document and convert it to output document.
    #|
    #| PARAMETERS:
    #|    source_file (I) - The path to the input source document to convert
    #|
    #| RETURNS:
    #|    None.
    #+-----------------------------------------------------------------------------
    def parse_page(self, source_file):

        print "Page: %s" % source_file
        self.m_parser.parse(source_file)

        #for link in self.m_parser.m_wiki_links:
        #    print "LINK: [%s]" % link

    def is_wiki_word(self, phrase):
        '''Returns the target link if the phrase is a wikiword
           or None if it does not exist'''
        link = None

        if(self.m_parser.m_wiki_links.has_key(phrase)):

            link = self.m_parser.m_wiki_links[phrase]

        return link

    def inkscape_to_png(self, name):
        '''This method is called to convert an inkscape
           SVG to PNG format for embedding in a document'''

        input = os.path.abspath(name)
        parts = os.path.splitext(input)
        basename = parts[0]

        #print "input = %s" % input
        #print "basename = %s" % basename
        dirname = os.path.dirname(basename) + os.path.sep
        #print "dirname = %s" % dirname
        filename = basename.replace(dirname, "")
        #print "filename = %s" % filename

        scratchdir = self.get_config("shorte", "scratchdir")
        output = scratchdir + os.path.sep + filename + ".png"
        #output = filename + ".png"
        #print "OUTPUT: %s" % output
        
        if(sys.platform == "cygwin" or sys.platform == "win32"):
            output = output.replace("/cygdrive/c/", "C:/")
            input = input.replace("/cygdrive/c/", "C:/")

        cmd = '''%s -e "%s" "%s"''' % (PATH_INKSCAPE, output, input)
        print cmd
        
        
        # Need a shorte delay after running inkscape because of
        # a race condition on windows
        result = os.popen(cmd).read()
        time.sleep(4)

        return output

    def convert_image(self, image):

        name = image["name"]
        converter = image["converter"]
        output = image["src"]

        if(converter == "inkscape"):
            input = image["src"]
            output = self.inkscape_to_png(input)
            image["src"] = output
            image["ext"] = ".png"

            print "output: %s" % output

            # If we've found the source image than remove it from
            # the list of images
            for i in self.m_images:
                if(i == input):
                    print "Removing %s from the list" % i
                    self.m_images.remove(i)

        self.m_images.append(output)

        return image

    def inline_image(self, image):

        handle = open(image["src"], "rb")
        name = "data:object/png;base64," + base64.encodestring(handle.read())
        name = name.replace("\n","")
        handle.close()

        return name


    def get_document_name(self):

        if(self.get_file_name() != None):
            name = self.get_file_name()
        else:
            name = self.get_title()

        name = name.lower()
        name = re.sub("[ -']", "_", name)
        name = re.sub("_+", "_", name)

        return name

    def get_macros(self):
        self.m_macros["SHORTE_DOC_TITLE"] = self.get_title()
        return self.m_macros
        

    def set_macros(self, macros):

        self.m_macros = macros

    def get_function_summary(self, tag=None):

        functions = []

        if(tag != None and tag.page_title):
            page_title = tag.page_title
        else:
            page_title = None

        #print "get_function_summary()->PAGE_TITLE = [%s]" % page_title
        #print tag

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        for page in pages:
            
            #print "    CHECKING [%s]" % page_title
            tags = page["tags"]
            #print "PAGE = %s" % page["title"]
            #print tag

            for tag in tags:

                #print tag
                
                if(tag.name == "prototype"):
                    
                    if(page_title == "" or (not tag.page_title)):
                        #print "DO I GET HERE? page_title = %s" % (page_title)
                        #print tag
                        #sys.exit(-1)
                        hierarchy = os.path.basename(page["source_file"])
                        hierarchy = hierarchy.replace("leeds_", "")
                        hierarchy = hierarchy.replace(".c", "")
                        hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")
                        hierarchy = hierarchy.replace("leeds", "cs4321")

                        if(tag.modifiers):
                            if(isinstance(tag.modifiers, DictType) and tag.modifiers.has_key("hierarchy")):
                                hierarchy = tag.modifiers["hierarchy"]

                        tag.hierarchy = hierarchy
                        tag.page = page["source_file"]
                        functions.append(tag)

                    elif(tag.page_title == page_title):
                        hierarchy = page["source_file"]
                        #print tag
                        if(tag.modifiers and tag.modifiers.has_key("hierarchy")):
                            hierarchy = tag.modifiers["hierarchy"]
                        hierarchy = os.path.basename(hierarchy)
                        hierarchy = hierarchy.replace("leeds_", "")
                        hierarchy = hierarchy.replace(".c", "")
                        hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")
                        hierarchy = hierarchy.replace("leeds", "cs4321")

                        tag.hierarchy = hierarchy
                        tag.page = page["source_file"]
                        functions.append(tag)
                    #else:
                    #    print "tag['page'] = %s, page_title = %s" % (tag["page_title"], page_title) 
        
        functions = sorted(functions, key=lambda k: k.hierarchy, reverse=False)

        return functions

    def get_types_summary(self, tag=None):

        types = []

        if(tag != None):
            page_title = tag.page_title
        else:
            page_title = None

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        for page in pages:
            
            #print "    CHECKING [%s]" % page_title
            tags = page["tags"]
            #print "PAGE = %s" % page["title"]
            #print tag

            for tag in tags:

                #print tag
                
                if(tag.name == "struct" or tag.name == "vector" or tag.name == "enum"):
                    
                    if(page_title == "" or (not tag.page_title)):
                        hierarchy = os.path.basename(page["source_file"])
                        hierarchy = hierarchy.replace("leeds_", "")
                        hierarchy = hierarchy.replace(".c", "")
                        hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")
                        hierarchy = hierarchy.replace("leeds", "cs4321")

                        if(tag.modifiers):
                            if(isinstance(tag.modifiers, DictType) and tag.modifiers.has_key("hierarchy")):
                                hierarchy = tag.modifiers["hierarchy"]

                        tag.hierarchy = hierarchy
                        tag.page = page["source_file"]
                        types.append(tag)

                    elif(tag.page_title == page_title):
                        hierarchy = page["source_file"]
                        if(tag.modifiers.has_key("hierarchy")):
                            hierarchy = tag.modifiers["hierarchy"]
                        
                        hierarchy = os.path.basename(hierarchy)
                        hierarchy = hierarchy.replace("leeds_", "")
                        hierarchy = hierarchy.replace(".c", "")
                        hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")
                        hierarchy = hierarchy.replace("leeds", "cs4321")

                        tag.hierarchy = hierarchy
                        tag.page = page["source_file"]
                        types.append(tag)
        
        types = sorted(types, key=lambda k: k.hierarchy, reverse=False)

        return types
    
    
    def get_testcase_summary(self, tag=None):

        types = []

        if(tag != None):
            page_title = tag.page_title
        else:
            page_title = None

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        for page in pages:
            
            #print "    CHECKING [%s]" % page_title
            tags = page["tags"]
            #print "PAGE = %s" % page["title"]
            #print tag

            for tag in tags:

                #print tag
                
                if(tag.name == "testcase"):
                    
                    if(page_title == "" or (not tag.page_title)):
                        category = os.path.basename(page["source_file"])
                        category = category.replace("leeds_", "")
                        category = category.replace(".c", "")
                        category = category.replace(".h", "")
                        category = category.replace(".tpl", "")
                        category = category.replace("leeds", "cs4321")

                        if(tag.modifiers):
                            if(isinstance(tag.modifiers, DictType) and tag.modifiers.has_key("category")):
                                category = tag.modifiers["category"]

                        tag.category = category
                        tag.page = page["source_file"]
                        types.append(tag)

                    elif(tag.page_title == page_title):
                        category = page["source_file"]
                        if(tag.modifiers.has_key("category")):
                            category = tag.modifiers["category"]
                        
                        category = os.path.basename(category)
                        category = category.replace("leeds_", "")
                        category = category.replace(".c", "")
                        category = category.replace(".h", "")
                        category = category.replace(".tpl", "")
                        category = category.replace("leeds", "cs4321")

                        tag.category = category
                        tag.page = page["source_file"]
                        types.append(tag)
        
        types = sorted(types, key=lambda k: k.category, reverse=False)

        return types

    def load_replace_strings(self, input_file):
        self.m_search_and_replace = input_file

    def search_and_replace(self, text):
        if(self.m_search_and_replace != None):
            #path = os.path.dirname(self.m_search_and_replace)
            ##print "PATH: %s" % path
            ##print "sys.path %s" % sys.path
            #if(sys.platform == "cygwin" or sys.platform == "win32"):
            #    path = path.replace("/cygdrive/c/", "C:\\")
            #    path = path.replace("/", "\\")
           
            snr = self.m_search_and_replace

            dirname = os.path.dirname(snr)
            path = os.path.basename(snr)
            module_name = os.path.splitext(path)[0]
            #print "DIRNAME: %s, MODULE=%s, CWD=%s" % (dirname, module_name, os.getcwd())
            sys.path.append(dirname)
            module = __import__("%s" % module_name)

            return module.search_and_replace(text)
        
        return text

    def generate(self, package):
        

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        version = options.version

        for page in pages:

            #print "NAME: %s" % page["source_file"]
            tags = page["tags"]

            for tag in tags:

                tag.result = None
            
                if(self.tag_is_executable(tag.name)):
                    source = tag.source 

                    executor = code_executor_t()
                    tag.result = executor.execute(tag.name, tag.source, tag.modifiers)
                
        # If the version number was not specified on the command
        # line then use any @docversion one specified in one of
        # the source files.
        if(version == None):
            version = self.m_docversion

        self.m_template.generate(options.theme, version, package)


parser = OptionParser()
parser.add_option("-f", "--files",
                  action="store", dest="files",
                  help="The list of files to generate")
parser.add_option("-l", "--list",
                  action="store", dest="file_list",
                  help="The list of files to generate in an input file")
parser.add_option("-o", "--output",
                  action="store", dest="output_dir",
                  help="The directory where output is generated")
parser.add_option("-v", "--version",
                  action="store", dest="version",
                  help="The version of the document")
parser.add_option("-t", "--theme",
                  action="store",type="string",dest="theme",default="cortina",
                  help="The output theme")
parser.add_option("-n", "--name",
                  action="store",type="string",dest="name",
                  help="The document name or title")
parser.add_option("-p", "--package",
                  action="store",type="string",dest="package",default="html",
                  help="The output package. Supported types are html, odt, word, and pdf")
parser.add_option("-b", "--output_format",
                  action="store",dest="output_format",default="bitfields",
                  help="Set the output format in C generated code: bitfields, byte_array, or defines")
parser.add_option("-y", "--diagnostic_code",
                  action="store_true",dest="allow_diagnostic_code",default=False,
                  help="Generate diagnostic code in generate code")
parser.add_option("-c", "--config",
                  action="store",type="string",dest="config",
                  help="The config file to load")
parser.add_option("-s", "--settings",
                  action="store",type="string",dest="settings",
                  help="A list of settings to use that overrides the standard config file")
parser.add_option("-x", "--parser",
                  action="store",type="string",dest="parser",
                  help="The parser to use",default="shorte")
parser.add_option("-a", "--about",
                  action="store_true",dest="about",
                  help="About this program")
parser.add_option("-m", "--macros",
                  action="store",type="string",dest="macros",
                  help="Macro substitution")
parser.add_option("-d", "--define",
                  action="store",type="string",dest="define",
                  help="Macro substitution")
parser.add_option("-r", "--search_and_replace",
                  action="store",type="string",dest="replace",
                  help="An input search and replace module that is loaded to pre-process input files and replace any references")
parser.add_option("-w", "--working_directory",
                  action="store",type="string",dest="working_directory",
                  help="The working directory")
parser.add_option("-i", "--info",
                  action="store",type="string",dest="info",
                  help="List info about the document, for example, --info=wikiwords will show the list of scanned wikiwords")

#parser.add_option("-I", "--include",
#                  action="store",type="string",dest="include",
#                  help="Include paths to search for include files")

(options, args) = parser.parse_args()

output_dir = options.output_dir
if(output_dir == None):
    output_dir = "build-output"

if(options.about):
    version_string = "<<VERSION>>"
    print "Shorte Version %s" % version_string
    sys.exit(0)

if(not os.path.isabs(output_dir)):
    output_dir = "%s/%s" % (os.getcwd(), output_dir)

if(options.config != None):
    config = options.config
else:
    config = g_startup_path + os.path.sep + "shorte.cfg"


shorte = engine_t(output_dir, config, options.parser)

if(options.replace):
    shorte.load_replace_strings(options.replace)

# Override any global configuration options that the
# user specified on the command line. Settings are
# specified in the format:
#    -s "html.inline_toc=1;html.xxx=2"
if(options.settings):
    settings = options.settings.split(";")

    for s in settings:
        matches = re.search("(.*?)\.(.*?)=(.*)", s)

        if(matches != None):
            sect = matches.groups()[0]
            key = matches.groups()[1]
            val = matches.groups()[2]
           
            shorte.set_config(sect, key, val)

# Setup any macros the user specified
#    -m "macro1=1;macro2=2"
# or
#    -d "macro1=2;macro2=2"
if(options.macros):
    fields = options.macros.split(";")
    macros = {}

    for field in fields:
        matches = re.search("(.*?)=(.*)", field)

        if(matches != None):
            key = matches.groups()[0]
            val = matches.groups()[1]
           
            macros[key] = val

    shorte.set_macros(macros)
if(options.define):
    fields = options.define.split(";")
    defines = {}

    for field in fields:
        matches = re.search("(.*?)=(.*)", field)

        if(matches != None):
            key = matches.groups()[0]
            val = matches.groups()[1]
           
            defines[key] = val

    shorte.set_macros(defines)


scratchdir = shorte.get_config("shorte", "scratchdir")
if(not os.path.exists(scratchdir)):
    os.makedirs(scratchdir)

shorte.set_theme(options.theme)

if(options.name != None):
    shorte.set_title(options.name)
    shorte.set_subtitle(options.name)

if(options.working_directory != None):
    shorte.set_working_dir(options.working_directory)

# Save the version number of the document
# if it was specified.
shorte.set_version(options.version)

packages = []

include_pdf = False
inline = False

package_list = options.package.split("+")

# Handle any modifications required by the
# input package selection. For example html+pdf
# needs some modifications in order to include
# a PDF link in the HTML documentation.
for package in package_list:
    if(package == "html"):
        packages.append(PACKAGE_TYPE_HTML)
        if('pdf' in package_list):
            include_pdf = True

    elif(package == "html_inline"):
        inline = True
        packages.append("html_inline")
        if('pdf' in package_list):
            include_pdf = True

    else:
        packages.append(package)

if(options.info):

    # This target is used to base64 encode a list of images
    # passed via the -t flag. This is useful when generating
    # inline HTML documents.
    if(options.info == "encode_images"):
        files = options.files.split(" ")
        for file in files:
            handle = open(file, "rb")
            name = "data:object/png;base64," + base64.encodestring(handle.read())
            name = name.replace("\n","")
            handle.close()
            print "FILE %s:\n%s" % (file, name)

    sys.exit(0)

# If the user specified the -l option then an input
# file containing a list of shorte files is being
# passed. In this case the file needs to be parsed
# to retrieve the list of input template files being
# used in the generation of the document. The file
# supports conditional defines so they need to be
# expanded first to handle any files that should be
# conditionally included.
if(options.file_list):
    handle = open(options.file_list, "rt")
    contents = handle.read()
    handle.close()
        
    tmp_macros = {}
    if(options.macros):
        macros = shorte.get_macros()
        for macro in macros:
            tmp_macros[macro] = macros[macro]

    contents = '''
def exists(s):
    if(globals().has_key(s)):
        return 1
    return 0

%s
''' % contents

    #print "[%s]" % contents

    eval(compile(contents, "example2.py", "exec"), tmp_macros, tmp_macros)
    contents = tmp_macros["result"]
    #print "CONTENTS = [%s]" % contents
    #sys.exit(-1)

    handle = open("tmp.tpf", "wt")
    handle.write("result += '''\n")
    files = contents.strip().split("\n")

    for fname in files:

        fname = fname.strip()
        if(fname == ""):
            continue
        elif(fname[0] == "#"):
            continue

        #print "FNAME: %s" % fname

        if(os.path.isdir(fname)):

            for root, dirs, paths in os.walk(fname):
                for path in paths:
                    (base, ext) = os.path.splitext(path)
                    if(ext == ".tpl"):
                        print "PATH: %s" % path

        else:
            tmp = fname
            tmp = shorte.get_output_dir() + os.sep + os.path.basename(tmp)
            tmp = re.sub("\.c$", ".tpl", tmp)
            tmp = re.sub("\.h$", ".h.tpl", tmp)
            tmp = re.sub("\\\\", "/", tmp)
            handle.write("%s\n" % tmp)
            shorte.parse_page(fname)
    handle.write("'''\n")
    handle.close()

else:
    files = options.files.split(" ")
    for file in files:
        rgx = re.compile("(\.tpl|\.txt|\.ste)")
        output = rgx.sub(".html", file)

        #print("output file: %s" % shorte.get_output_dir() + "/" + output);
        shorte.parse_page(file)


if(options.info):

    if(options.info == "wikiwords"):
        print "Summary of wiki words:"
        print "----------------------"
        links = shorte.m_parser.m_wiki_links
        for link in links:
            print '''  %-24s
    - wikiword: %s,
    - label:    %s,
    - bookmark: %s''' % (link, links[link].wikiword, links[link].label, links[link].is_bookmark)

    sys.exit(0)

# The caller may have selected multiple packages
# in the output, for example, html+pdf. Step through
# the list of packages and generate the output.
for pkg in packages:

    #print "Package = %s" % pkg

    shorte.set_package(pkg)
    
    indexer = indexer_t()
    
    # Associate an output template with the engine. This is used
    # to format the output into a particular document type
    if(pkg == PACKAGE_TYPE_WORD):
        template = template_word_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_ODT):
        template = template_odt_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_PDF):
        template = template_odt_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_TEXT):
        template = template_text_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_TWIKI):
        template = template_twiki_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_MEDIAWIKI):
        template = template_mediawiki_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_C):
        template = template_c_t(shorte, indexer)
        template.set_output_format(options.output_format)
        template.allow_diagnostic_code(options.allow_diagnostic_code)
    elif(pkg == PACKAGE_TYPE_VERA):
        template = template_vera_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_SHORTE):
        template = template_shorte_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_SWIG):
        template = template_swig_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_LABVIEW):
        template = template_labview_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_SQL):
        template = template_sql_t(shorte, indexer)
    elif(pkg == PACKAGE_TYPE_MERGEFILE):
        template = template_mergefile_t(shorte, indexer)
    else:
        template = template_html_t(shorte, indexer)
        template.m_inline = inline
        template.set_template_dir(pkg)
        template.m_include_pdf = include_pdf
    
    # Set the output template and generate the
    # contents in the output directory
    shorte.set_template(template)
    shorte.generate(pkg)

