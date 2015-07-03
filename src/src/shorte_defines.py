import platform
import os
import sys

# Track the number of warnings or errors
# encountered during processing
g_shorte_warning_count = 0
g_shorte_error_count   = 0

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

    def __str__(self):
        output = '''wikiword_t
  word:        %s
  is_bookmark: %d
  label:       %s
  link:        %s
''' % (self.wikiword, self.is_bookmark, self.label, self.link)
        return output


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
        self.modifiers = None

        # The heading that this tag belongs to (if applicable)
        self.heading = None

    def has_source(self):
        if(self.source != None and len(self.source) > 0):
            return True

        # Text blocks shouldn't be blank
        if(self.name in ("text")):
            return False

        # It is ok for an image to not have any source
        if(self.name in ("image")):
            return True

        WARNING("Tag %s has no source, should it?" % self.name)
        return True

    def get_source(self):
        return self.source

    def get_contents(self):
        return self.contents

    def has_modifiers(self):
        if(self.modifiers != None and (len(self.modifiers) > 0)):
            return True
        return False
    def get_modifiers(self):
        return self.modifiers
    def get_modifiers_as_string(self):
        mods = ''
        for key in self.modifiers:
            mods += " %s='%s'" % (key, self.modifiers[key])

        return mods

    def has_modifier(self, name):
        if(self.modifiers.has_key(name)):
            return True
        return False

    def get_modifier(self, name):
        if(self.modifiers.has_key(name)):
            return self.modifiers[name]
        return None
    
    def get_name(self):
        return self.name

    def __str__(self, short_form=False):
        data = "Tag:\n"
        data += "  name %s\n" % self.name
        data += "  file %s\n" % self.file
        data += "  line %s\n" % self.line
        data += "  page %s\n" % self.page
        if(not short_form):
            data += "  source\n"
            data += self.source

            if(self.has_modifiers()):
                data += self.get_modifiers_as_string()

        return data

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

    # If shorte.py doesn't exist then try the PATH_SHORTE
    # environment variable
    if(not os.path.exists(startup_path + "/shorte.py")):
        if(not os.path.exists(startup_path + "/shorte.exe")):
            WARNING("shorte.py not found at %s, trying PATH_SHORTE environment variable" % startup_path)

            if(not os.environ.has_key("PATH_SHORTE")):
                FATAL("Unable to determine shorte startup directory. I would recommend you "
                      "define the PATH_SHORTE environment variable to the location of "
                      "shorte.py")

            startup_path = os.environ["PATH_SHORTE"]

    #print "STARTUP PATH: %s" % startup_path
    
    # Replace any Cygwin path references
    g_startup_path = startup_path.replace("/cygdrive/c/", "C:/")

    sys.path.append(g_startup_path)

    return g_startup_path

def shorte_get_scratch_path():
    scratch_dir = shorte_get_config("shorte", "scratchdir")
    scratch_dir = os.path.abspath(scratch_dir)

    if(not os.path.exists(scratch_dir)):
        os.mkdir(scratch_dir)

    return scratch_dir


def shorte_get_tool_path(tool):
        
    tool_uc = tool.upper()
    path_tool = None

    if(os.environ.has_key("PATH_%s" % tool_uc)):
        path_tool = os.environ["PATH_%s" % tool_uc]
    else:
        if(sys.platform == "cygwin" or sys.platform == "win32"):
            osname = "win32"
        elif(sys.platform == "darwin"):
            osname ="osx"
        else:
            osname ="linux"
        path_tool = shorte_get_config("shorte", "path.%s.%s" % (tool.lower(), osname))

    if(not path_tool):
        FATAL("%s not found at %s. Try setting PATH_%s" % (tool, path_tool, tool_uc))

    return path_tool


class topic_t:
    def __init__(self, vars):
        self.m_vars = vars

        self.name = vars["name"]
        self.level = vars["indent"]
        #self.parent = self.m_vars["parent"]
        self.file   = vars["file"]
        self.tag    = vars["tag"]

    def get_file(self):
        return self.file
    def get_tag(self):
        return self.tag
    def get_name(self):
        return self.name
    def get_indent(self):
        return self.level
    def get_level(self):
        return self.level

    #def __str__(self):
    #    return self.m_vars.__str__()


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

    def __str__(self):
        output = 'Index:\n'
        output += "==============\n"
        
        last_level = 1 

        index = {}

        for i in range(0, 6):
            index[i] = 1

        for topic in self.m_topics:
            prefix = ' ' * topic.get_indent()

            level = topic.get_level()
            
            last_level = level
            lindex = index[level]
            
            if(level < last_level):
                index[level] = 1
            else:
                index[level] += 1

                for i in range(level+1,6):
                    index[i] = 1
            
            l = []
            for i in range(1, level+1):
                l.append("%d" % (index[i] - 1))
            l = ".".join(l)
                
            output += "%s%s. %s\n" % (prefix, l, topic.get_name())


        return output

    def level(self, tag, data, file, inc=True):

        level = None
        parent = None

        topics = []
        for topic in self.m_topics:
            if(topic.name == data):
                duplicate_headers = shorte_get_config("shorte", "duplicate_headers")
                if(duplicate_headers == "error"):
                    ERROR("A topic with the name '%s' already exists in %s on line %d.\n"
                          "Change the shorte.duplicate_headers to change this behavior." % (data, tag.file, tag.line))
                elif(duplicate_headers == "warn"):
                    WARNING("A topic with the name '%s' already exists in %s on line %d.\n"
                          "Change the shorte.duplicate_headers to change this behavior." % (data, tag.file, tag.line))


            topics.append(topic)
            
        if(tag.name == "h1"):
            if(len(topics) > 0):
                topics.reverse()
                for topic in topics:
                    if(topic.level == 1):
                        parent = topic
                        break
            level = self.level1(tag, data, file, inc)
        elif(tag.name == "h2"):
            if(len(topics) > 0):
                topics.reverse()
                for topic in topics:
                    if(topic.level == 1):
                        parent = topic
                        break
            level = self.level2(tag, data, file, inc)
        elif(tag.name == "h3"):
            if(len(topics) > 0):
                topics.reverse()
                for topic in topics:
                    if(topic.level == 2):
                        parent = topic
                        break
            level = self.level3(tag, data, file, inc)
        elif(tag.name == "h4"):
            if(len(topics) > 0):
                topics.reverse()
                for topic in topics:
                    if(topic.level == 3):
                        parent = topic
                        break
            level = self.level4(tag, data, file, inc)
        elif(tag.name == "h5"):
            if(len(topics) > 0):
                topics.reverse()
                for topic in topics:
                    if(topic.level == 4):
                        parent = topic
                        break
            level = self.level5(tag, data, file, inc)

        return (level,parent)
    
    def level1(self, tag, data, file, inc=True):
        
        if(inc):
            self.m_index_l1 += 1
            self.m_index_l2 = 0
            self.m_index_l3 = 0
            self.m_index_l4 = 0
            self.m_index_l5 = 0

        topic = topic_t({"tag"    : tag,
                         "name"   : data,
                         "file"   : file,
                         "indent" : 1})

        self.m_topics.append(topic)
        
        return "%d" % self.m_index_l1
        
    
    def level2(self, tag, data, file, inc=True):
       
        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1

            self.m_index_l2 += 1
            self.m_index_l3 = 0
            self.m_index_l4 = 0
            self.m_index_l5 = 0
        
        topic = topic_t({"tag"    : tag,
                         "name"   : data,
                         "file"   : file,
                         "indent" : 2})

        self.m_topics.append(topic)
        
        return "%d.%d" % (self.m_index_l1, self.m_index_l2)
   
    def level3(self, tag, data, file, inc=True):

        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1
            if(self.m_index_l2 == 0):
                self.m_index_l2 = 1

            self.m_index_l3 += 1
            self.m_index_l4 = 0
            self.m_index_l5 = 0
        
        topic = topic_t({"tag"    : tag,
                         "name"   : data,
                         "file"   : file,
                         "indent" : 3});
        self.m_topics.append(topic)
        
        return "%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3)

    def level4(self, tag, data, file, inc=True):

        if(inc):

            if(self.m_index_l1 == 0):
                self.m_index_l1 = 1
            if(self.m_index_l2 == 0):
                self.m_index_l2 = 1
            if(self.m_index_l3 == 0):
                self.m_index_l3 = 1

            self.m_index_l4 += 1
            self.m_index_l5 = 0
        
        topic = topic_t({"tag"    : tag,
                         "name"   : data,
                         "file"   : file,
                         "indent" : 4});
        self.m_topics.append(topic)
        
        return "%d.%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3, self.m_index_l4)

    def level5(self, tag, data, file, inc=True):

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
        
        topic = topic_t({"tag"    : tag,
                         "name"   : data,
                         "file"   : file,
                         "indent" : 5});
        self.m_topics.append(topic)
        
        return "%d.%d.%d.%d.%d" % (self.m_index_l1, self.m_index_l2, self.m_index_l3, self.m_index_l4, self.m_index_l5)


    def image(self, inc=True):
        
        if(inc):
            self.m_image_index += 1
        
        return self.m_image_index


class table_t:
    def __init__(self):
        self.rows = []
        self.modifiers = {}
        self.max_cols = 1
        self.widths = []
        self.width = 0
        self.title = None
        self.caption = None

        # Attributes primarily for ODT
        self.table_style_name = None
        self.column_styles = None

        self.style = None

        pass

    def get_title(self):
        return self.title
    def has_title(self):
        if(self.title != None):
            return True
        return False

    def get_widths(self):
        return self.widths
    def has_widths(self):
        if(len(self.widths) > 0):
            return True
        return False

    def has_style(self):
        if(self.style != None):
            return True
        return False
    def get_style(self):
        return self.style

    def get_max_cols(self):
        return self.max_cols

    def get_caption(self):
        return self.caption
    def has_caption(self):
        if(self.caption != None):
            return True
        return False

    def add_row(self, row):
        self.rows.append(row)

    def get_rows(self):
        return self.rows
    def get_num_rows(self):
        return len(self.rows)

    def has_column_styles(self):
        if(self.column_styles != None):
            return True
        return False

    def get_column_styles(self):
        return self.column_styles


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
TAG_TYPE_PREPROCESSOR = 7

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
PACKAGE_TYPE_MARKDOWN    = "markdown"

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

def indent_lines(source, prefix):
    lines = source.split('\n')

    output = ''
    for line in lines:
        output += prefix + line + '\n'
    return output

def trim_leading_indent(source, allow_second_line_indent_check=True):
    '''This method is called to trim the leading indent from a string.
    
       @param source                         [I] - The string to strip
       @param allow_second_line_indent_check [I] - If every line after the
                                                   first is indented by the same amount
                                                   then strip it. This doesn't make sense
                                                   for source code elements but it probably does for
                                                   normal text paragraphs.
    '''

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
            if(allow_second_line_indent_check and all_indented):
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

def to_boolean(val):
    if(isinstance(val, (str,unicode))):
        val = val.lower()
        if(val == "true"):
            return True
        elif(val == "false"):
            return False
        elif(val == "0"):
            return False
        elif(val == "1"):
            return True
        else:
            FATAL("Unsupported values, cannot convert to boolean: %s" % val)
    elif(isinstance(val,int)):
        val = int(val)
        if(val == 0):
            return False
        return True
    return False


g_config = None

def shorte_get_config(section, key, expand_os=False):
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
    if(section == "paths" or True == expand_os):
        if(platform.system() == "Linux"):
            key += ".linux"
        elif("CYGWIN" in platform.system()):
            key += ".linux"
        elif(platform.system() == "Darwin"):
            key += ".osx"
        else:
            key += ".win32"

    try:
        val = g_config.get(section, key)
    except:
        val = None

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
STATE_PREPROCESSOR = 9

def zipper(dir, zip_file):
    import zipfile, os

    DEBUG("%s" % zip_file)

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
    
def shorte_get_version():
    path_version = shorte_get_startup_path() + "/version.inc"

    if(not os.path.exists(path_version)):
        FATAL("Version file version.inc not found")

    handle = open(path_version, 'rt')
    contents = handle.read()
    contents = contents.replace("version \:= ", "")
    matches = re.search("version := ([0-9]+\.[0-9]+\.[0-9]+)", contents)
    version = "???"
    if(matches != None):
        version = matches.groups()[0]
    else:
        FATAL("Version not found in %s" % path_version)

    return version

g_verbose = False
def shorte_set_verbosity(enable):
    global g_verbose
    g_verbose = enable

g_logfile = None
g_logfile_path = "log.html"

def shorte_get_log_file_path():
    return g_logfile_path
def shorte_set_log_file_path(path):
    global g_logfile_path
    g_logfile_path = path

def shorte_get_log_file():
    global g_logfile
    if(g_logfile == None):
        path = shorte_get_log_file_path()
        dirname = os.path.dirname(path)
        if((0 != len(dirname)) and not os.path.exists(dirname)):
            print "PATH: %s" % path
            print "DIR:  %s" % dirname
            os.makedirs(dirname)
        g_logfile = open(path, "wt")
        g_logfile.write('''<html>
<head>
  <style>
    div.log     {width:100%;vertical-align:text-top;border-top:1px solid #ccc;clear:both;}
    div.log div {float:left;}
    div.fatal   {font-weight:bold;color:red;   width:100px;float:left;}
    div.status  {font-weight:bold;color:#ccc;  width:100px;float:left;}
    div.error   {font-weight:bold;color:red;   width:100px;float:left;}
    div.warning {font-weight:bold;color:orange;width:100px;float:left;}
  </style>
</head>
<body>
''')
    return g_logfile


def DEBUG(message):
    '''This method is used to manage debug statements in the log file'''
    if(g_verbose):
        import inspect
        frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
        message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 
        print "DEBUG: %s" % message
    
        message = message.replace('\n', '<br/>')
        message = message.replace(' ', '&nbsp')
        shorte_get_log_file().write("<div class='log'><div class='debug'>DEBUG:</div><div>%s</div></div>" % message)

def STATUS(message):
    '''This method is used to manage import status messages in the log file'''
    import inspect
    frame,filename,line_number,function_name,lines,index = inspect.stack()[1]
    message += " (%s:%s @ %d)" % (os.path.basename(filename), function_name, line_number) 

    if(g_verbose):
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

    message = message.replace('\n', '<br/>')
    message = message.replace(' ', '&nbsp')
    shorte_get_log_file().write("<div class='log'><div class='status'>STATUS:</div><div>%s</div></div>" % message)

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
    
        message = message.replace('\n', '<br/>')
        message = message.replace(' ', '&nbsp')
        shorte_get_log_file().write("<div class='log'><div class='info'>INFO:</div>%s</div>" % message)


def WARNING(message):
    '''This method is used to manage warning mesages messages in the log file'''
    import inspect
    global g_shorte_warning_count
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
    
    message = message.replace('\n', '<br/>')
    message = message.replace(' ', '&nbsp')
    shorte_get_log_file().write("<div class='log'><div class='warning'>WARNING:</div><div>%s</div></div>" % message)

    g_shorte_warning_count += 1

def ERROR(message):
    '''This method is used to manage error mesages messages in the log file'''
    import inspect
    global g_shorte_error_count

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
    
    message = message.replace('\n', '<br/>')
    message = message.replace(' ', '&nbsp')
    shorte_get_log_file().write("<div class='log'><div class='error'>ERROR:</div><div>%s</div></div>" % message)

    g_shorte_error_count += 1

def FATAL(message):
    '''This method is used to manage fatal error mesages messages in the log file for which there is no recovery'''
    import inspect
    import traceback
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
        for line in traceback.format_stack():
            print "    >> %s" % line.strip()

        print "\033[91mFATAL:\033[0m %s" % message

    message = message.replace('\n', '<br/>')
    message = message.replace(' ', '&nbsp')
    
    shorte_get_log_file().write("<div class='log'><div class='fatal'>FATAL:</div>%s</div>" % message)
    sys.exit(-1)

def shorte_get_error_count():
    return g_shorte_error_count
def shorte_get_warning_count():
    return g_shorte_warning_count

class list_item_t:

    def __init__(self):

        self.text = None
        self.indent = 0
        self.children = None
        self.type = "list"
        self.checked = False
        self.starred = False
        self.priority = 0

    def set_text(self, text):

        #print "LIST ITEM TEXT: %s" % text

        # See if it starts with an action [] but make sure
        # it isn't a hyperlink
        if(not text.startswith("[[") and text.startswith("[")):
            self.type = "checkbox"
            self.checked = False

            pos = 1
            modifier = ''
            for i in range(0,len(text)):
                if(text[i] == ']'):
                    pos = i+1
                    break
                else:
                    modifier += text[i]
            
            text = text[pos:]
            start_tag = ""
            end_tag = ""

            for i in range(0, len(modifier)):
                
                if(modifier[i] == 'x'):
                    self.checked = True
                    start_tag += "@{cross,"
                    end_tag += "}"

                elif(modifier[i] == 'a'):
                    self.type = "action"
                    start_tag = "*ACTION:*" + start_tag

                elif(modifier[i] in ('0', '1', '2', '3', '4', '5')):
                    self.priority = int(modifier[i])

                elif(modifier[i] == '*'):
                    self.starred = True


            text = start_tag + text + end_tag
            text = text.strip()

            #print "ITEM:"
            #print "  TEXT: %s" % text
            #print "  PRIORITY: %d" % self.priority

        self.text = text

    def get_text(self):

        return self.text.strip()

class textblock_t:

    def __init__(self, data=""):
        self.source = ""
        self.paragraphs = []

        self.parse(data)
    
    def get_indent_of_line(self, data, start_of_line):

        i = start_of_line
        indent = []
        len_data = len(data)

        while(i < len_data and data[i] == ' '):
            indent.append('0')
            i += 1
        
        return ''.join(indent)
    
    def strip_indent(self, input, indent):
        
        #print "\n\nINPUT=[%s], indent=%d" % (input, indent)

        if(indent == 0):
            return input

        len_input = len(input)

        for i in range(0, indent+1):
            if(i >= (len_input-1)):
                break

            if(input[i] != ' '):
                break

        return input[i:]

    def parse_block(self, text):

        lines = text.split("\n")
        
        # Remove any leading blank lines
        for line in lines:
            if(len(line) == 0):
                lines.remove(line)
            else:
                break

        # Figure out the indent of the first line
        indent = 0
        for i in range(0, len(lines[0])):
            if(lines[0][i] == ' '):
                indent += 1
            else:
                break

        #print "Indent = %d" % indent
        
        lines_out = []
        for line in lines:
            if(len(line) == 0):
                continue
            lines_out.append(self.strip_indent(line, indent))
            #lines_out.append(line)

        if(len(lines_out) == 0):
            return ""

        #print "DO I get here? len=%d" % len(lines_out)
        #print lines_out
        return "\n".join(lines_out)
    
    
    def parse_list_child(self, i, items, x=1):
        
        #print "%*sparsing text=%s, i=%d" % (x*3, " ", items[i][0].strip(), i)
        nodes = []

        while(i < len(items)):
            item   = items[i]
            indent = item.indent
            text   = item.get_text()
            children = None

            #print "%*sitem=%s, indent=%d" % (x*3, " ", text, indent)

            # Check to see if the next element has a greater
            # indent, if it is then it's a child
            if(i+1 < len(items)):
                next_item = items[i+1]
                next_indent = next_item.indent
                next_text = next_item.get_text()
                
                # If the next node in the list has a smaller
                # indent then we've hit the end of this branch
                if(next_indent < indent):
                    #print "%*sstopping at %s, curr_text = %s" % (x*3, " ", next_text, text)
                    #print "%*sAdding node %s" % (x*3, " ", text)
                    node = list_item_t()
                    node.checked = item.checked
                    node.type = item.type
                    node.children = item.children
                    node.starred = item.starred
                    node.priority = item.priority
                    node.set_text(text)
                    nodes.append(node)
                    return (i+1, nodes)
                # If the next node is indented more than it's
                # a child of this node.
                elif(next_indent > indent):
                    #print "%*sWalking children of %s" % (x*3, " ", text)
                    (i, children) = self.parse_list_child(i+1, items, x+1)

                # Otherwise we're at the same level so continue
                # adding elements.
                else:
                    #print "%*sContinue at text=%s,next_text=%s" % (x*3, " ", text, next_text)
                    i += 1
            else:
                i += 1
              
            #print "%*sAdding node %s" % (x*3, " ", text)
            node = list_item_t()
            node.checked = item.checked
            node.type = item.type
            node.starred = item.starred
            node.priority = item.priority
            node.set_text(text)
            node.children = item.children
            if(children != None):
                if(len(children) > 0):
                    node.children = children
                    children = []

            nodes.append(node)

            # Check the next item in the list and make sure it's not
            # then end of this level
            if(i < len(items)):
                next_item = items[i]
                next_indent = next_item.indent
                if(next_indent < indent):
                    #print "Next item %s is up one level" % next_item[0].strip()
                    i -= 1
                    break

        return (i+1,nodes)

    def parse_list(self, source, modifiers):

        items = []
        item = []
        item_indent = 0
        #print "PARSING LIST: [%s]" % source

        STATE_NORMAL = 0
        STATE_INLINE_FORMATTING = 1

        state = STATE_NORMAL

        for i in range(0, len(source)):

            if(state == STATE_INLINE_FORMATTING):
                if(source[i] == '}'):
                    state = STATE_NORMAL

                item.append(source[i])
            
            elif(state == STATE_NORMAL):
                if(source[i] == '@' and source[i+1] == '{'):
                    item.append(source[i])
                    state = STATE_INLINE_FORMATTING
                    continue
                
                elif(source[i] in ('-')):

                    # Look backwards till the first newline
                    # to ensure this is a list item and not
                    # a dash between two words:
                    j = i-1
                    is_list_item = True
                    while(j > 0):
                        if(source[j] == "\n"):
                            break
                        elif(source[j] != " "):
                            is_list_item = False
                        j -= 1

                    if(not is_list_item):
                        item.append(source[i])
                        continue

                    # Output the last item if it exists
                    if(len(item) != 0):
                        litem = list_item_t()
                        litem.set_text(''.join(item))
                        litem.indent = item_indent
                        items.append(litem)
                    item = []

                    # Figure out the indent level of this item
                    item_indent = 0
                    j = i
                    while(j >= 0):
                        if(source[j] == '\n'):
                            break
                        j -= 1
                        item_indent += 1
                    

                else:
                    item.append(source[i])

        if(len(item) != 0):
            litem = list_item_t()
            litem.text = ''.join(item)
            litem.indent = item_indent
            items.append(litem)

        (i, list) = self.parse_list_child(0, items)

        #for elem in list:
        #    print elem

        return list

    def parse(self, data):
        #print "PARSING TEXTBLOCK: [%s]" % data

        data = trim_leading_indent(data)

        STATE_NORMAL = 0
        STATE_LIST = 1
        STATE_CODE = 2
        STATE_INLINE = 3
        STATE_ESCAPE = 4
        states = []
        states.append(STATE_NORMAL)

        segments = []
        segment = {}
        segment["type"] = "text"
        segment["text"] = ""
        i = 0

        #print "DATA: [%s]" % data

        while(i < len(data)):

            state = states[-1]

            if(state == STATE_ESCAPE):
                segment["text"] += data[i]
                states.pop()
                i += 1
                continue
                
            if(data[i] == '\\'):
                i += 1
                states.append(STATE_ESCAPE)
                continue

            if(state == STATE_NORMAL):

                # If the line starts with - or * then treat it
                # as a list. If it is ** then it is actually bold text
                if(data[i] == "-"): #  or (data[i] == "*" and (i+1 < len(data) and data[i+1] != "*"))):
                    if(i == 0 or data[i-1] == "\n"):
                        #print "Starting a list, last seg=%s" % segment
                        i += 1 
                        segments.append(segment)
                        segment = {}
                        segment["type"] = "list"
                        segment["text"] = "-"
                        states.append(STATE_LIST)
                    else:
                        segment["text"] += data[i]
                        i += 1

                # Start of a new segment
                elif(data[i] == "\n" and (i < len(data)-1) and data[i+1] == "\n"):
                    #print "SEGMENT [%s]" % segment["text"]
                    #print "Start of new segment"
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    i += 1 
                # DEBUG BRAD: This is not implemented
                #  If a line is indented then we should treat all consecutive lines
                #  that have the same indent level as an indented block.
                #elif(data[i] == "\n" and (i < len(data)-1) and data[i+1] in (" ")):
                elif(data[i] == "\n" and data[i+1] == " "):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    
                    #print "\n\nParsing Indented text [%s]\n" % data[i+1:]

                    j = i+1

                    block = ""

                    same_indent = True
                    while(same_indent):
                        prefix = ""

                        while((j <= len(data)-1) and data[j] == ' '):
                            prefix += "0"
                            block += " "
                            j += 1
                        
                        if(j >= (len(data)-1)):
                            break

                        # Add the rest of the text to the end of the line
                        while((j <= len(data)-1) and data[j] != '\n'):
                            block += data[j]
                            j += 1
                        #print "data[%d] = [%s]" % (j, data[j])
                        block += "\n"

                        # Now that I've hit the newline get the indent
                        # level of the next line. If it is the same then
                        # continue adding this line to the current paragraph
                        # If it is different then stop processing
                        j += 1
                        #print "REMAINDER: [%s]" % data[j:]
                        indent = self.get_indent_of_line(data, j)

                        if(indent != prefix):
                            same_indent = False
                            #print "indent [%s] != prefix [%s]" % (indent,prefix)
                            break

                    segment["text"] = block

                    #print "   TEXT: [%s]" % segment["text"]
                    i = j+1
                    
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""

                    #i += 2

                elif(data[i] == "{" and data[i+1] == "{"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "code"
                    segment["text"] = ""
                    i += 2
                    states.append(STATE_CODE)

                elif(data[i] == '@' and data[i+1] == "{"):
                    #segments.append(segment)
                    #segment = {}
                    #segment["type"] = "text"
                    segment["text"] += "@"
                    i += 1
                    states.append(STATE_INLINE)

                else:
                    #print "In Else block"
                    segment["text"] += data[i]
                    i += 1

            elif(state == STATE_INLINE):
                if(data[i] == "}"):
                    segment["text"] += "}"
                    i += 1
                    #segments.append(segment)
                    #segment = {}
                    #segment["type"] = "text"
                    #segment["text"] = ""
                    states.pop()
                else:
                    segment["text"] += data[i]
                    i += 1

            elif(state == STATE_CODE):
                #print "PARSING CODE"
                
                if(data[i] == "}" and data[i+1] == "}"):
                    segment["text"] += ""
                    i += 2
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    states.pop()
                else:
                    segment["text"] += data[i]
                    i += 1

            elif(state == STATE_LIST):
                #print "PARSING LIST"
                if(data[i] == "\n" and (i > len(data)-2 or data[i+1] == "\n")):
                    segment["text"] += data[i]
                    i += 2 
                    segments.append(segment)
                    states.pop()
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                else:
                    segment["text"] += data[i]
                    i += 1
                #print "  [%s]" % segment["text"]

        if(segment["text"] != ""):
            segments.append(segment)

        #s = 0
        #for segment in segments:
        #    print "SEGMENT[%d]: [%s]" % (s,segment)
        #    s+=1
        paragraphs = []

        for segment in segments:
            indent = 0
            text = segment["text"]
            type = segment["type"]

            #print "Segment [%s]" % segment

            for i in range(0, len(text)):
                if(text[i] == ' '):
                    indent += 1
                else:
                    break

            is_code = False
            is_list = False
            is_table = False
            
            # Handle any code blocks detected within the
            # textblock. Code blocks are represented by {{ }}
            if(type == "code"):
                #print "TEXT = [%s]" % text
                text = self.parse_block(text)
                is_code = True
            elif(type == "list"):

                #print "LIST: [%s]" % text

                elements = self.parse_list(text, "")

                text = elements
                is_list = True
            elif(type == "table"):
                elements = self.parse_table(text, "")

                text = elements
                is_table = True

            paragraphs.append({
                "indent":indent,
                "text":text,
                "code":is_code,
                "list":is_list,
                "table":is_table})
        
        self.paragraphs = paragraphs
        return paragraphs
