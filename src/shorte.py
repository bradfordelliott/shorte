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

from src.shorte_defines import *
from src.shorte_source_code import *
from src.parsers.shorte_parser import *
from src.parsers.cpp_parser import *
from src.shorte_code_executor import *
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
from src.shorte_engine import *



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

parser.add_option("--srv", "--server",
                  action="store_true",dest="server",
                  help="Run a background XML-RPC server to process remote requests")
parser.add_option("--port", "--port",
                  action="store",dest="server_port",
                  help="The port number to start the XML-RPC server listening on")


#parser.add_option("-I", "--include",
#                  action="store",type="string",dest="include",
#                  help="Include paths to search for include files")

(options, args) = parser.parse_args()
from src.shorte_server import shorte_server_start

# Run shorte as an XML-RPC server process instead of a command
# line utility. This is required for web-server integration
if(options.server):
    shorte_server_start("127.0.0.1", 8300)
    sys.exit(0)

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
    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"


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

        shorte.encode_images(options.files)

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


# Print any information that the user requested and
# exit
if(options.info):

    print shorte.info(options.info)
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

