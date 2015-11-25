import platform
import os
import sys
import string

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
        self.source_file = None

    def __str__(self):
        output = '''wikiword_t
  word:        %s
  is_bookmark: %d
  label:       %s
  link:        %s
  source:      %s
''' % (self.wikiword, self.is_bookmark, self.label, self.link, self.source_file)
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
        self.line = None
        self.line2 = None
        self.is_header = False
        self.is_prototype = False
        self.hierarchy = ""
        self.category = ""
        self.page = None
        self.modifiers = None

        self.result = None

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

    def has_result(self):
        if(None != self.result):
            return True
        return False
    def set_result(self, result):
        self.result = result
    def get_result(self):
        return self.result

    def has_image(self):
        if(None != self.result_image):
            return True
        return False
    def get_image(self):
        return self.result_image
    def set_image(self, image):
        self.result_image = image

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
        data += "  name: %s\n" % self.name
        data += "  file: %s\n" % self.file
        data += "  line: %s\n" % self.line
        data += "  page: %s\n" % self.page
        if(not short_form):
            data += "  source:\n"

            lines = self.source.split("\n")
            for line in lines:
                data += "    [" + line + "]\n"

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

    def __str__(self):
        output =  'Topic:\n'
        output += '------------\n'
        output += '  name: %s\n' % self.name
        output += '  file: %s\n' % self.file

        return output
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
                          "You can disable this error by passing -s \"shorte.duplicate_headers=ignore;\" at the shorte command line." % (data, tag.file, tag.line))
                elif(duplicate_headers == "warn"):
                    WARNING("A topic with the name '%s' already exists in %s on line %d.\n"
                          "You can disable this warning by passing -s \"shorte.duplicate_headers=ignore;\" at the shorte command line." % (data, tag.file, tag.line))


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


class checklist_item_t(object):

    def __init__(self):
        self.value = None
        self.status = None
        self.caption = None
        self.comments = None

    def has_caption(self):
        if(None != self.caption):
            return True
        return False
    def get_caption(self):
        return self.caption
    def set_caption(self, caption):
        self.caption = caption

    def get_name(self):
        return self.value
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value

    def get_checked(self):
        if(self.status == None):
            return False
        elif(self.status.upper() in ("CHECKED", "FINISHED", "CLOSED")):
            return True
        return False
    def set_status(self, status):
        self.status = status

    def set_field(self, fname, value):
        if(fname == "value"):
            self.value = value
        elif(fname == "comments"):
            self.comments = value
        elif(fname == "status"):
            self.status = value
        elif(fname == "who"):
            self.who = value

    def get_field(self, fname):
        if(fname == "value"):
            return self.value
        elif(fname == "comments"):
            return self.comments
        elif(fname == "status"):
            return self.status
        elif(fname == "who"):
            return self.who

        return None


class checklist_t(object):
    def __init__(self):
        self.columns = ["value"]
        self.items = []
        self.name = None
        self.caption = None

    def get_name(self):
        if(self.name == None):
            return "Checklist"

        return self.name
    def set_name(self, name):
        self.name = name

    def get_caption(self):
        return self.caption
    def has_caption(self):
        if(self.caption != None):
            return True
        return False
    def set_caption(self, caption):
        self.caption = caption

    def set_columns(self, columns):
        self.columns = []
        for col in columns:
            self.columns.append(col.strip())

    def get_columns(self):
        return self.columns

    def get_items(self):
        return self.items
    def set_items(self, items):
        self.items = items



class table_t:
    def __init__(self):
        self.rows = []
        self.modifiers = {}
        self.max_cols = 1
        self.widths = None
        self.width = None
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
        if(self.title != None and len(self.title) > 0):
            return True
        return False

    def get_widths(self):
        return self.widths
    def has_widths(self):
        if(self.widths != None and len(self.widths) > 0):
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

    def set_caption(self, caption):
        self.caption = caption
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
PACKAGE_TYPE_WKPDF       = "wpdf"
PACKAGE_TYPE_DOCBOOK     = "docbook"
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
        pname = platform.system()
        if(pname == "Linux"):
            key += ".linux"
        elif("CYGWIN" in pname):
            key += ".linux"
        elif(pname == "Darwin"):
            key += ".osx"
        else:
            key += ".win32"

    try:
        val = g_config.get(section, key)
    except:
        val = None

    # Expand any shorte variables in the config file
    if(val != None and ("$" in val)):
        vars = {}
        vars["SHORTE_STARTUP_DIR"] = shorte_get_startup_path()
        val = string.Template(val)
        val = val.safe_substitute(vars)

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
        pname = platform.system()
        if(pname == "Linux"):
            key += ".linux"
        elif(pname == "Darwin"):
            key += ".osx"
        else:
            key += ".win32"

    #print "  %s.%s = %s" % (section, key, val)

    if(key.endswith("*")):
        pname = platform.system()
        if(pname == "Linux"):
            key = key.replace("*", "linux")
        elif(pname == "Darwin"):
            key = key.replace("*", "osx")
        else:
            key = key.replace("*", "win32")
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
        sys.stdout.write("ERROR: ")
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
        sys.stdout.write("FATAL: ")
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


def shorte_get_os():
    import platform
    osname = platform.system().lower()

    if("windows" == osname):
        return "win32"
    elif("cygwin" in osname):
        return "cygwin"
    elif("darwin" in osname):
        return "osx"
    return "unix"

def shorte_import_cairo():
    osname = shorte_get_os()

    try:
        startup_path = shorte_get_startup_path()
        if("win32" == osname):
            sys.path.append(startup_path + "/libs/win32")
            import libs.win32.cairo_access as cairo_access
        elif("cygwin" == osname):
            sys.path.append(startup_path +"/libs/cygwin")
            import libs.cygwin.cairo_access as cairo_access
        elif("osx" == osname):
            sys.path.append(startup_path + "/libs/osx")
            import libs.osx.cairo_access as cairo_access
        elif("unix" == osname):
            sys.path.append(startup_path + "/libs/unix")
            import libs.unix.cairo_access as cairo_access

    except: 
        print sys.exc_info()
        FATAL("ERROR: Failed importing cairo, try running make cairo_plugin to generate it")


def shorte_mkdir(newdir):
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
            shorte_mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)
       
def shorte_parse_modifiers(modifiers):
    STATE_TAG = 0
    STATE_VALUE = 2
    STATE_STRING = 1
    STATE_TRIPLE_QUOTES = 3

    tag = ""
    value = ""
    string = []

    #WARNING("MODIFIERS: [%s]" % modifiers)

    tags = {}
    states = []
    states.append(STATE_TAG)

    i = 0
    while i < len(modifiers):

        state = states[-1]

        #print "STATE: %d, char: %c" % (state, modifiers[i])

        if(modifiers[i] == '\\'):
            i += 1
            continue

        if(state == STATE_TAG):

            if(modifiers[i] == "="):
                value = ""
                states.append(STATE_VALUE)
            else:
                tag += modifiers[i]
                #print "building tag: %s" % tag
        
        elif(state == STATE_TRIPLE_QUOTES):
            FATAL("Ooops, can I ever get here?")
            if((modifiers[i:i+3] == start_sequence) and modifiers[i-1] != '\\'):
                states.pop()
                i += 2
            else:
                string.append(modifers[i])

        elif(state == STATE_STRING):
            
            if(modifiers[i] == start_sequence and modifiers[i-1] != '\\'):
                states.pop()
            else:
                string.append(modifiers[i])


        elif(state == STATE_VALUE):
           
            value += ''.join(string)
            string = []

            
            if(modifiers[i:i+3] in ("'''", '"""')):
                FATAL("Ooops, can I ever get here?")
                states.append(STATE_TRIPLE_QUOTES)
                start_sequence = modifiers[i:i+3]
                i += 2
            elif(modifiers[i] in ('"', "'")):
                states.append(STATE_STRING)
                start_sequence = modifiers[i]
            elif(modifiers[i] == " "):

                tags[tag.strip()] = value.strip()

                #print "Adding tag: %s" % tag
                tag = ""
                value = ""
                states.pop()

            else:
                value += modifiers[i]

        i += 1

    if(value != "" or len(string) != 0):
        value += ''.join(string)
        #print "tag = %s, value = %s" % (tag, value)
        tags[tag.strip()] = value.strip()
    elif(tag != ""):
        tags[tag.strip()] = ""


    #for tag in tags:
    #    print "TAG: [%s] = [%s]" % (tag, tags[tag])

    return tags

def shorte_get_version_stamp():
    version = shorte_get_version()

    return '''
This file was generated by version %s of the shorte shorthand tool.
For more information refer to:
    https://github.com/bradfordelliott/shorte
''' % version

