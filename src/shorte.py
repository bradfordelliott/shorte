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
import argparse
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



parser = argparse.ArgumentParser(description="""Shorte is a
shorthand documentation generation tool similar to formats
like markdown or RST.""")
parser.add_argument("-f", "--files",
                  action="store", dest="files",
                  help="""The list of files to analyze separated by comma or semicolon.
Spaces can currently be used but they will eventually be deprecated
to allow for installation paths that have spaces""")
parser.add_argument("-l", "--list",
                  action="store", dest="file_list",
                  help="The list of files to generate in an input file")
parser.add_argument("-o", "--output",
                  action="store", dest="output_dir",
                  help="The directory where output is generated")
parser.add_argument("--of", "--output_file",
                  action="store", dest="output_file",
                  help="The main output file to generate")
parser.add_argument("-v", "--version",
                  action="store", dest="version",
                  help="The version of the document")
parser.add_argument("-t", "--theme",
                  action="store",dest="theme",
                  help="The output theme")
parser.add_argument("-n", "--name",
                  action="store",dest="name",
                  help="The document name or title")
parser.add_argument("-p", "--package",
                  action="store",dest="package",default="html",
                  help="The output package. Supported types are html, odt, word, and pdf")
parser.add_argument("-b", "--output_format",
                  action="store",dest="output_format",default="bitfields",
                  help="Set the output format in C generated code: bitfields, byte_array, or defines")
parser.add_argument("-y", "--diagnostic_code",
                  action="store_true",dest="allow_diagnostic_code",default=False,
                  help="Generate diagnostic code in generate code")
parser.add_argument("-c", "--config",
                  action="store",dest="config",
                  help="The config file to load")
parser.add_argument("-s", "--settings",
                  action="store",dest="settings",
                  help="A list of settings to use that overrides the standard config file")
parser.add_argument("-x", "--parser",
                  action="store",dest="parser",
                  help="The parser to use",default="shorte")
parser.add_argument("-a", "--about",
                  action="store_true",dest="about",
                  help="About this program")
parser.add_argument("-m", "--macros",
                  action="store",dest="macros",
                  help="Macro substitution")
parser.add_argument("-D", "--define",
                  action="store",dest="define",
                  help="Macro substitution")
parser.add_argument("-I", "--include",
                  action="store",dest="include",
                  help="Include paths - currently only used for Clang")
parser.add_argument("-r", "--search_and_replace",
                  action="store",dest="replace",
                  help="An input search and replace module that is loaded to pre-process input files and replace any references")
parser.add_argument("-w", "--working_directory",
                  action="store",dest="working_directory",
                  help="The working directory")
parser.add_argument("-i", "--info",
                  action="store",dest="info",
                  help="List info about the document, for example, --info=wikiwords will show the list of scanned wikiwords")

parser.add_argument("--srv", "--server",
                  action="store_true",dest="server",
                  help="Run a background XML-RPC server to process remote requests")
parser.add_argument("--port", "--port",
                  action="store",dest="server_port", default="8300",
                  help="The port number to start the XML-RPC server listening on")
parser.add_argument("--zip", "--zip",
                  action="store", dest="zip",default=None,
                  help="Create an archive of the output")
parser.add_argument("--resize", "--resize_image",
                  action="store", dest="resize", default=None,
                  help="Resize an input image")
parser.add_argument("--verbose", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbosity of the output log")
parser.add_argument("--ierr", "--ignore_errors",
                 action="store_true", dest="ignore_errors", default=False,
                 help="Ingore errors")
parser.add_argument("--werr", "--warnings_as_errors",
                 action="store_true", dest="warnings_as_errors", default=False,
                 help="Treat warnings as errors")
parser.add_argument("--profile", "--profile",
                  action="store", dest="profile", default=False,
                  help="Turn on profiling")
parser.add_argument("--build_index", "--build_index",
                    action="store", dest="build_index", help="Scan a directory and generate an index file")

#parser.add_argument("-I", "--include",
#                  action="store",type="string",dest="include",
#                  help="Include paths to search for include files")

options = parser.parse_args()

if(options.verbose):
    shorte_set_verbosity(True)

output_dir = options.output_dir
if(output_dir == None):
    output_dir = "build-output"
shorte_set_log_file_path(output_dir + "/shorte_log.html")

from src.shorte_server import shorte_server_start

# Run shorte as an XML-RPC server process instead of a command
# line utility. This is required for web-server integration
if(options.server):
    shorte_server_start("127.0.0.1", int(options.server_port))
    sys.exit(0)

#args = ' '.join(sys.argv)
#print ""
#print "======================================================"
#print "Shorte:"
#print "  version: %s" % shorte_get_version()
#print "======================================================"
#STATUS("Command Line:\n  %s" % args)


if(options.about):
    version = shorte_get_version()
    print "Shorte Version:"
    print "==============="
    print version
    sys.exit(0)

if(options.resize):
    shorte_image_resize(options.resize, "%s/%s" % (output_dir, os.path.basename(options.resize)), 50, 50)
    sys.exit(0)

if(not os.path.isabs(output_dir)):
    output_dir = "%s/%s" % (os.getcwd(), output_dir)

if(options.config != None):
    config = options.config
else:
    config = shorte_get_startup_path() + os.path.sep + "shorte.cfg"


shorte = engine_t(output_dir, config, options.parser)

if(options.output_file):
    shorte.set_output_file(options.output_file)

if(options.replace):
    shorte.load_replace_strings(options.replace)

if(options.theme):
    shorte_set_config("shorte", "theme", options.theme)

shorte.set_theme(shorte_get_config("shorte", "theme"))

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
           
            shorte_set_config(sect, key, val)

# Setup any macros the user specified
#    -m "macro1=1;macro2=2"
# or
#    -d "macro1=2;macro2=2"
if(options.macros):
    #print "MACROS: %s" % options.macros
    fields = options.macros.split(";")
    macros = {}

    for field in fields:
        matches = re.search("(.*?)=(.*)", field)


        if(matches != None):
            key = matches.groups()[0]
            val = matches.groups()[1]

            #print "%s = %s" % (key, val)
           
            macros[key] = val
        # If there was no equal sign then assume
        # the macro has the value 1
        else:
            key = field.strip()
            if(len(key) > 0):
                macros[key] = "1"

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
        # If there was no equal sign then assume
        # the macro has the value 1
        else:
            key = field.strip()
            if(len(key) > 0):
                defines[key] = "1"

    shorte.set_macros(defines)

if(options.include):
    includes = options.include.split(";")
    shorte.set_includes(includes)

scratchdir = shorte.get_config("shorte", "scratchdir")
if(not os.path.exists(scratchdir)):
    os.makedirs(scratchdir)

if(options.name != None):
    shorte.set_title(options.name)
    shorte.set_subtitle(options.name)

if(options.working_directory != None):
    shorte.set_working_dir(options.working_directory)


# Save the version number of the document
# if it was specified.
shorte.set_version(options.version)

if(options.info):

    # This target is used to base64 encode a list of images
    # passed via the -t flag. This is useful when generating
    # inline HTML documents.
    if(options.info == "encode_images"):

        shorte.encode_images(options.files)

        sys.exit(0)


# See if we should just use shorte to generate an index file
if(options.build_index != None):
    output = '''@doctitle Index Page
@body
@h1 Document Index
This is the document index page.
@table
- Page
'''
    for root, dirs, paths in os.walk(options.build_index):
        for path in paths:
            if("index.html" in path):
                link = root + os.sep + path
                link = link.replace(options.build_index, "")
                if(link.startswith("/")):
                    link = link[1:]

                output += "- [[%s]]\n" % link 
                #print "PATH: %s" % link
    shorte.parse_string(output)
    shorte.generate_packages(options.package, shorte_get_config("shorte", "theme"), options, options.zip)
    sys.exit(0)


# If profiling is enabled then profile the parsing task
if(options.profile):
    import cProfile, pstats, StringIO
    profiler = cProfile.Profile()
    profiler.enable()


shorte.parse_pages(options.file_list, options.files, options.macros)

#sortby = 'cumulative'
sortby = 'time'
if(options.profile):
    profiler.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    poutput = s.getvalue()
    phandle = open(output_dir + "/" + options.profile + "_parse.txt", "wt")
    phandle.write(poutput)
    phandle.close()
    profiler.clear()
    profiler.enable()


# Print any information that the user requested and
# exit
if(options.info):

    print shorte.info(options)
    sys.exit(0)

shorte.generate_packages(options.package, shorte_get_config("shorte", "theme"), options, options.zip)

if(options.profile):
    profiler.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    poutput = s.getvalue()
    phandle = open(output_dir + "/" + options.profile + "_generate.txt", "wt")
    phandle.write(poutput)
    phandle.close()


warnings = shorte_get_warning_count()
errors   = shorte_get_error_count()

print "\nShorte finishined processing"

error_on_exit = False

if(warnings != 0):
    print "  - %d warnings found during processing" % warnings
    if(True == options.warnings_as_errors):
        error_on_exit = True

if(errors != 0):
    print "  - %d errors found during processing (set --ignore_errors to ignore)" % errors
    if(not options.ignore_errors):
        error_on_exit = True

print "  - See %s for more detail" % shorte_get_log_file_path()

# Before we exit make sure we cleanup the scratch directory
if(os.path.exists(scratchdir)):
    try:
        shutil.rmtree(scratchdir)
    except:
        print "Failed removing scratchdir %s" % scratchdir
   
if(error_on_exit):
    sys.exit(-1)
