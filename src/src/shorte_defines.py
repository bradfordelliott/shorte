import platform
import os
import sys

if(platform.system() == "Linux"):
    python = "python"
    perl   = "perl"
    gdc    = "/work/gdc/bin/gdc"
    gpp    = "g++"
else:
    python = "python.exe"
    perl   = "perl.exe"
    gdc    = "/work/gdc/bin/gdc"

class tools_t:

    def get_c_compiler(self):

        if(platform.system() == "Linux"):
            return "g++"
        else:
            return "g++"

    def get_perl(self):
        return "perl"

    def get_python(self):
        return "python"

    def get_tcl(self):
        return "tclsh"

class wikiword_t:

    def __init__(self):
        self.wikiword = ""
        self.is_bookmark = False
        self.label = ""
        self.link = ""

class tag_t:
    def __init__(self):
        self.source = ""
        self.attributes = {}
        self.name = ""
        self.contents = None
        self.page_title = None
        self.break_before = False
        self.file = ""
        self.line = 0
        self.is_header = False
        self.is_prototype = False
        self.result = None
        self.hierarchy = ""
        self.category = ""
        self.page = None

        # The heading that this tag belongs to (if applicable)
        self.heading = None

g_tools = tools_t()
g_startup_path = None
def shorte_get_startup_path():
    global g_startup_path
    if(g_startup_path != None):
        return g_startup_path

    argv0 = sys.argv[0]
    argv0 = argv0.replace("\\", "/")
    
    startup_path = os.path.dirname(argv0)
    if(startup_path == ""):
        startup_path = os.getcwd()

    #print "STARTUP PATH: %s" % startup_path
    
    # Replace any Cygwin path references
    g_startup_path = startup_path.replace("/cygdrive/c/", "C:/")

    return g_startup_path

class topic_t:
    def __init__(self, vars):
        self.m_vars = vars

    def get_name(self):
        return self.m_vars["name"]


class identity_t:
    def __init__(self):
        self.m_identity = 0
    
    def next_id(self):
        self.m_identity += 1
        return self.m_identity


class indexer_t:
    
    def __init__(self):
        self.m_index_l1 = 0 
        self.m_index_l2 = 0
        self.m_index_l3 = 0
        self.m_index_l4 = 0
        self.m_index_l5 = 0
        self.m_image_index = 0

        self.m_topics = []
    
    def level1(self, name, data, file, inc=True):
        
        if(inc):
            self.m_index_l1 += 1
            self.m_index_l2 = 0
            self.m_index_l3 = 0
            self.m_index_l4 = 0
            self.m_index_l5 = 0

        topic = topic_t({"name"   : data,
                         "file"   : file,
                         "indent" : 1});
        self.m_topics.append(topic)
        
        return "%d" % self.m_index_l1
        
    
    def level2(self, name, data, file, inc=True):
       
        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1

            self.m_index_l2 += 1
            self.m_index_l3 = 0
            self.m_index_l4 = 0
            self.m_index_l5 = 0
        
        topic = topic_t({"name"   : data,
                         "file"   : file,
                         "indent" : 2});
        self.m_topics.append(topic)
        
        return "%d.%d" % (self.m_index_l1, self.m_index_l2)
   
    def level3(self, name, data, file, inc=True):

        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1
            if(self.m_index_l2 == 0):
                self.m_index_l2 = 1

            self.m_index_l3 += 1
            self.m_index_l4 = 0
            self.m_index_l5 = 0
        
        topic = topic_t({"name"   : data,
                         "file"   : file,
                         "indent" : 3});
        self.m_topics.append(topic)
        
        return "%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3)

    def level4(self, name, data, file, inc=True):

        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1
            if(self.m_index_l2 == 0):
                self.m_index_l2 = 1
            if(self.m_index_l3 == 0):
                self.m_index_l3 = 1

            self.m_index_l4 += 1
            self.m_index_l5 = 0
        
        topic = topic_t({"name"   : data,
                         "file"   : file,
                         "indent" : 4});
        self.m_topics.append(topic)
        
        return "%d.%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3, self.m_index_l4)

    def level5(self, name, data, file, inc=True):

        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1
            if(self.m_index_l2 == 0):
                self.m_index_l2 = 1
            if(self.m_index_l3 == 0):
                self.m_index_l3 = 1
            if(self.m_index_l4 == 0):
                self.m_index_l4 = 1

            self.m_index_l5 += 1
        
        topic = topic_t({"name"   : data,
                         "file"   : file,
                         "indent" : 5});
        self.m_topics.append(topic)
        
        return "%d.%d.%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3, self.m_index_l4, self.m_index_l5)


    def image(self, inc=True):
        
        if(inc):
            self.m_image_index += 1
        
        return self.m_image_index


g_images  = []
index = []


import base64
import re
import sys


def encode_image(image):
    handle = open(image, "rb")
    contents = handle.read()
    handle.close()

    return base64.b64encode(contents)

def xmlize(data):
    data = re.sub("&", "&amp;", data)
    data = re.sub("->", "#", data)
    data = re.sub("<", "&lt;", data)
    data = re.sub(">", "&gt;", data)

    return data

def pathize(data):

    data = re.sub(" ", "_", data)

    return data


TAG_TYPE_CODE = 0
TAG_TYPE_STRING = 1
TAG_TYPE_COMMENT = 2
TAG_TYPE_MCOMMENT = 3
TAG_TYPE_WHITESPACE = 4
TAG_TYPE_NEWLINE = 5
TAG_TYPE_XMLCOMMENT = 6

if(sys.platform == "win32"):
    PATH_INKSCAPE = "c:\\usr\\tools\\InkscapePortable\\InkscapePortable"
elif(sys.platform == "cygwin"):
    PATH_INKSCAPE = "c:/usr/tools/InkscapePortable/InkscapePortable"
else:
    PATH_INKSCAPE = "/usr/bin/inkscape"

# The output package formats that are supported
PACKAGE_TYPE_HTML        = "html"
PACKAGE_TYPE_HTML_INLINE = "html_inline"
PACKAGE_TYPE_ODT         = "odt"
PACKAGE_TYPE_WORD        = "word"
PACKAGE_TYPE_PDF         = "pdf"
PACKAGE_TYPE_TEXT        = "txt"
PACKAGE_TYPE_TWIKI       = "twiki"
PACKAGE_TYPE_MEDIAWIKI   = "mediawiki"
PACKAGE_TYPE_C           = "c"
PACKAGE_TYPE_VERA        = "vera"
PACKAGE_TYPE_SHORTE      = "shorte"
PACKAGE_TYPE_SWIG        = "swig"
PACKAGE_TYPE_LABVIEW     = "labview"
PACKAGE_TYPE_MERGEFILE   = "mergefile"
PACKAGE_TYPE_SQL         = "sql"
PACKAGE_TYPE_REVEALJS    = "reveal.js"

TAB_REPLACEMENT = "    "

COMMENT_STYLE_KERNEL = 0
COMMENT_STYLE_SHORTE = 1
COMMENT_STYLE_DEFAULT = COMMENT_STYLE_KERNEL

HEADER_STYLE_KERNEL  = 0
HEADER_STYLE_SHORTE  = 1
HEADER_STYLE_DOXYGEN = 2
HEADER_STYLE_DEFAULT = HEADER_STYLE_DOXYGEN

is_array = lambda var: isinstance(var, (list, tuple))
is_dict  = lambda var: isinstance(var, (dict))

def trim_leading_blank_lines(source):
    lines = source.split("\n")

    if(len(lines) == 1):
        return source

    output = ''

    # Find the index of first non-blank line
    start = 0
    for i in range(0, len(lines)):
        tmp = lines[i].strip()
        if(tmp != ""):
            break
        start += 1

    #print "Start = %d" % start

    # Find the index of the last non-blank line
    end = len(lines)-1

    #print "End = %d" % end

    for i in range(start, end+1):
        output += (lines[i] + "\n")

    return output

def trim_blank_lines2(source):
    
    lines = source.split('\n')

    if(len(lines) == 1):
        return source

    output = []

    # Find the index of first non-blank line
    start = 0
    for i in range(0, len(lines)):
        tmp = lines[i].strip()
        if(len(tmp) != 0):
            break
        start += 1

    #print "Start = %d" % start

    # Find the index of the last non-blank line
    end = len(lines)-1
    for i in range(len(lines)-1, 0, -1):
        tmp = lines[i].strip()
        if(len(tmp) != 0):
            break
        end -= 1 

    #print "End = %d" % end

    for i in range(start, end+1):
        output.append(lines[i])

    return '\n'.join(output)

def trim_blank_lines(source):
    
    lines = source.split('\n')

    if(len(lines) == 1):
        return source

    output = ''

    # Find the index of first non-blank line
    start = 0
    for i in range(0, len(lines)):
        tmp = lines[i].strip()
        if(len(tmp) != 0):
            break
        start += 1

    #print "Start = %d" % start

    # Find the index of the last non-blank line
    end = len(lines)-1
    for i in range(len(lines)-1, 0, -1):
        tmp = lines[i].strip()
        if(len(tmp) != 0):
            break
        end -= 1 

    #print "End = %d" % end

    for i in range(start, end+1):
        output += (lines[i] + '\n')

    return output


def trim_leading_indent(source):

    source = trim_blank_lines(source)

    # Trim any leading indent from each line
    lines = source.split("\n")
    lines_out = []

    # Now figure out the indent of the first line
    i = 0
    leading_indent = ''
    while i < len(lines[0]) and lines[0][i] == " ":
        leading_indent += lines[0][i]
        i += 1

    #print "Source: [%s]" % source
    
    #print "leading indent: [%s]" % leading_indent
    
    if(len(lines) > 1):
        second_line_indent = ''
        i = 0

        l = 1
        while((l < len(lines)-1) and len(lines[l]) == 0):

        #    print "L: %d, len(lines) = %d" % (l,len(lines))
        #    if(l+1 >= len(lines)):
        #        return source

            l+=1

        #print "L: %d" % l

        while i < len(lines[l]) and lines[l][i] == " ":
            second_line_indent += lines[l][i]
            i += 1

        #print "second line indent: [%s]" % second_line_indent

        # If every line has an indent > second_line_indent
        # then strip the second line indent from every line
        all_indented = True
        i = 0
        for line in lines:
            if(i > 0 and len(line) > 0):
                if(not line.startswith(second_line_indent)):
                    #print "line [%s] not indented, index=%d" % (line, i)
                    all_indented = False
                    break
            i+=1

        #if(all_indented):
        #    print "All lines have same indent"
        #    print "[%s]" % source

        j = 0
        for line in lines:
            if(all_indented):
                if(j == 0):
                    line = re.sub("^%s" % leading_indent, "", line)
                    lines_out.append(line)
                else:
                    line = re.sub("^%s" % second_line_indent, "", line)
                    lines_out.append(line)
            else:
                line = re.sub("^%s" % leading_indent, "", line)
                lines_out.append(line)
            j+=1

    else: 
        for line in lines:
            line = re.sub("^%s" % leading_indent, "", line)
            lines_out.append(line)
    
    source = "\n".join(lines_out).strip()
    #print "OUTPUT\n[%s]" % source.strip()

    return source

def escape_string(source):
    source = source.replace('"', '\\"')
    source = source.replace('\n', '<br/>')
    return source

def unescape_string(source):
    #print "Source: %s" % source
    source = source.replace('\\"', '"')
    source = source.replace("<br/>", '\n')
    return source

g_config = None

def shorte_get_config(section, key):
    global g_config
    #print "GET CONFIG ", g_config
    if(g_config == None):
        import ConfigParser
        g_config = ConfigParser.ConfigParser()
        g_config.read(shorte_get_startup_path() + "/shorte.cfg")
    #config.read("../../shorte.cfg")

    # If searching for a path then make sure
    # to append the OS to get the correct
    # path
    if(section == "paths"):
        if(platform.system == "Linux"):
            key += ".linux"
        else:
            key += ".win32"


    val = g_config.get(section, key)

    #print "  %s.%s = %s" % (section, key, val)
    return val

def shorte_set_config(section, key, val):
    global g_config

    #print "SET CONFIG ", g_config

    if(g_config == None):
        import ConfigParser
        g_config = ConfigParser.ConfigParser()
        g_config.read(shorte_get_startup_path() + "/shorte.cfg")

    # If searching for a path then make sure
    # to append the OS to get the correct
    # path
    if(section == "paths"):
        if(platform.system == "Linux"):
            key += ".linux"
        else:
            key += ".win32"

    #print "  %s.%s = %s" % (section, key, val)
        
    g_config.set(section, key, val)
    #config.write(shorte_get_startup_path() + "/shorte.cfg")

        

STATE_NORMAL   = 1
STATE_COMMENT  = 2
STATE_STRING   = 3
STATE_MSTRING  = 4
STATE_MCOMMENT = 5
STATE_MODIFIER = 6
STATE_INLINE_STYLING = 7
STATE_XMLCOMMENT = 8

def zipper(dir, zip_file):
    import zipfile, os

    print "%s" % zip_file

    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(dir))
    for root, dirs, files in os.walk(dir):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            #print f
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
    zip.close()
    return zip_file

def shorte_image_resize(input_path, output_path, height, width):
    import Image
    im = Image.open(input_path)

    output = im.resize((width,height), Image.ANTIALIAS)

    output.save(output_path) 

g_verbose = False
def shorte_set_verbosity(enable):
    global g_verbose
    g_verbose = enable

def DEBUG(message):
    '''This method is used to manage debug statements in the log file'''
    if(g_verbose):
        import inspect
        frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
        message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
        print "DEBUG: %s" % message

def STATUS(message):
    '''This method is used to manage import status messages in the log file'''
    import inspect
    frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
    message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
    if(sys.platform == "win32"):
        import console_utils as con
        default_colors = con.get_text_attr()
        con.set_text_attr(con.FOREGROUND_MAGENTA)
        sys.stdout.write("STATUS: ")
        con.set_text_attr(default_colors)
        sys.stdout.flush()
        sys.stdout.write("%s\n" % message)
        sys.stdout.flush()
    else:
        print "\033[90mSTATUS:\033[0m %s" % message

def INFO(message):
    '''This method is used to manage informational messages in the log file that are more import than debug statements'''
    if(g_verbose):
        import inspect
        frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
        message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
        if(sys.platform == "win32"):
            import console_utils as con
            default_colors = con.get_text_attr()
            con.set_text_attr(con.FOREGROUND_MAGENTA)
            sys.stdout.write("INFO: ")
            con.set_text_attr(default_colors)
            sys.stdout.flush()
            sys.stdout.write("%s\n" % message)
            sys.stdout.flush()
        else:
            print "\033[90mINFO:\033[0m %s" % message

def WARNING(message):
    '''This method is used to manage warning mesages messages in the log file'''
    import inspect
    frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
    message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
    if(sys.platform == "win32"):
        import console_utils as con
        default_colors = con.get_text_attr()
        con.set_text_attr(con.FOREGROUND_YELLOW)
        sys.stdout.write("WARNING: ")
        con.set_text_attr(default_colors)
        sys.stdout.flush()
        sys.stdout.write("%s\n" % message)
        sys.stdout.flush()
    else:
        print "\033[93mWARNING:\033[0m %s" % message

def ERROR(message):
    '''This method is used to manage error mesages messages in the log file'''
    import inspect
    frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
    message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
    if(sys.platform == "win32"):
        import console_utils as con
        default_colors = con.get_text_attr()
        con.set_text_attr(con.FOREGROUND_RED)
        sys.stdout.write("WARNING: ")
        con.set_text_attr(default_colors)
        sys.stdout.flush()
        sys.stdout.write("%s\n" % message)
        sys.stdout.flush()
    else:
        print "\033[91mERROR:\033[0m %s" % message

def FATAL(message):
    '''This method is used to manage fatal error mesages messages in the log file for which there is no recovery'''
    import inspect
    frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
    message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 

    if(sys.platform == "win32"):
        import console_utils as con
        default_colors = con.get_text_attr()
        con.set_text_attr(con.FOREGROUND_RED)
        sys.stdout.write("WARNING: ")
        con.set_text_attr(default_colors)
        sys.stdout.flush()
        sys.stdout.write("%s\n" % message)
        sys.stdout.flush()
    else:
        print "\033[91mFATAL:\033[0m %s" % message

    sys.exit(-1)

