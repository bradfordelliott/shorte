import os
import datetime
import string
from string import Template;

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
from src.templates.template_revealjs import template_revealjs_t

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
        self.m_docauthor = None
        self.m_revision_history = None

        self.m_output_filename = None

        self.m_include_queue = []

        self.m_search_and_replace = None
        
        self.m_source_code_analyzer = source_code_t()

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
        import ConfigParser
        self.m_config = ConfigParser.ConfigParser()
        self.m_config.read([config_file])

    def set_output_directory(self, output_dir):
        self.m_output_directory = output_dir

        if(not os.path.exists(self.m_output_directory)):
            os.makedirs(self.m_output_directory)


    def reset(self):
        self.m_pages = []
        self.m_images = []
        self.m_include_queue = []
        self.m_imagemaps = {}
        self.m_macros = {}

        if(self.m_parser != None):
            self.m_parser.reset()

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

    def get_author(self):
        if(self.m_docauthor == None):
            return "N/A"
        return self.m_docauthor

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

        code = self.m_source_code_analyzer
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

    def parse_string(self, contents):
        self.m_parser.parse_string(contents)

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

        if(not os.path.exists(output)):
            print "ERROR: %s does not exist" % output
            sys.exit(-1)
        else:
            print "PATH %s exists" % output
            sys.exit(-1)

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

    def encode_images(self, files):
        files = files.split(" ")
        for file in files:
            handle = open(file, "rb")
            name = "data:object/png;base64," + base64.encodestring(handle.read())
            name = name.replace("\n","")
            handle.close()
            print "FILE %s:\n%s" % (file, name)
        
    
    def info(self, keys):
        output = []

        if("wikiwords" in keys):
            output.append("Summary of wiki words:")
            output.append("----------------------")
            links = self.m_parser.m_wiki_links
            for link in links:
                output.append('''  %-24s
    - wikiword: %s,
    - label:    %s,
    - bookmark: %s''' % (link, links[link].wikiword, links[link].label, links[link].is_bookmark))

        elif("deprecated" in keys):
            pages = self.m_parser.get_pages()

            for page in pages:
                print page["source_file"]
                tags = page["tags"]

                for tag in tags:
                    if(tag.name == "prototype"):
                        prototype = tag.contents
                        if(prototype.has_key("deprecated")):
                            output.append("%s is deprecated" % prototype["name"])


        return '\n'.join(output)
            

    def generate(self, package):
        

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        version = self.get_version()

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

        self.m_template.generate(self.get_theme(), version, package)

    def eval_expr(self, clause):
            macros = self.get_macros()

            # Figure out the variables that are defined
            # in the define list
            expr = re.compile("([A-Za-z][A-Za-z0-9_]+)", re.DOTALL | re.IGNORECASE)

            # If a variable is not set then set it
            # to zero
            matches = expr.search(clause)
            while(matches != None):
                var = matches.groups()[0]

                if(not (var == "and" or
                        var == "or" or
                        var == "not")):
                    if(not macros.has_key(var)):
                        #print "EXPR = %s" % var
                        macros[var] = 0

                matches = expr.search(clause, matches.end() + 1)

            # Evalulate the if check in the tag and
            # exclude it if necessary
            tmp_macros = {}
            for macro in macros:
                tmp_macros[macro] = macros[macro]

            to_eval = '''
def exists(s):
    if(globals().has_key(s)):
        return 1
    return 0

def value(s):
    if(exists(s)):
        return s
    return 0

if(%s):
    result = 1
else:
    result = 0
''' % clause

            try:
                eval(compile(to_eval, "example.py", "exec"), tmp_macros, tmp_macros)
            except:
                print to_eval
                sys.exit(-1)

            result = tmp_macros["result"]
            #print "RESULT: %s = %s" % ("(" + define + ")", result)
            if(int(result) == 0):
                #print "DO I GET HERE?"
                return False
            
            return True

    def generate_string(self, package):
        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        version = self.get_version()

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

        output = self.m_template.generate_string(self.get_theme(), version, package)

        return output

    def parse_pages(self, file_list, files, macros):
        # If the user specified the -l option then an input
        # file containing a list of shorte files is being
        # passed. In this case the file needs to be parsed
        # to retrieve the list of input template files being
        # used in the generation of the document. The file
        # supports conditional defines so they need to be
        # expanded first to handle any files that should be
        # conditionally included.
        if(file_list):
            handle = open(file_list, "rt")
            contents = handle.read()
            handle.close()
                
            tmp_macros = {}
            if(macros):
                macros = self.get_macros()
                for macro in macros:
                    tmp_macros[macro] = macros[macro]
        
            contents = '''
def exists(s):
    if(globals().has_key(s)):
        return 1
    return 0

%s
        ''' % contents

            contents = trim_blank_lines(contents)
        
            #print "[%s]" % contents
        
            try:
                eval(compile(contents, "example2.py", "exec"), tmp_macros, tmp_macros)
            except:
                print "ERROR parsing example2.py in %s" % os.getcwd()
                sys.exc_info()
                raise

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
                    tmp = self.get_output_dir() + os.sep + os.path.basename(tmp)
                    tmp = re.sub("\.c$", ".tpl", tmp)
                    tmp = re.sub("\.h$", ".h.tpl", tmp)
                    tmp = re.sub("\\\\", "/", tmp)
                    handle.write("%s\n" % tmp)
                    self.parse_page(fname)
            handle.write("'''\n")
            handle.close()
        
        else:
            files = files.split(" ")
            for file in files:
                rgx = re.compile("(\.tpl|\.txt|\.ste)")
                output = rgx.sub(".html", file)
        
                #print("output file: %s" % shorte.get_output_dir() + "/" + output);
                self.parse_page(file)
        

    def generate_packages(self, package_list, theme_list, options, zip_output=None):

        inline = False
        include_pdf = False

        #print "package_list: %s" % package_list
        #print "theme_list:   %s" % theme_list

        package_list = package_list.split("+")
        packages = []

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
    
        for pkg in packages:
            self.set_package(pkg)

            if("=" in theme_list):
                theme = theme_list
                themes = theme.split(";")
                for theme in themes:
                    parts = theme.split("=")

                    package = parts[0]
                    theme = parts[1]

                    if(package == pkg):
                        self.set_theme(theme)
            else:
                self.set_theme(theme_list)

            indexer = indexer_t()

            # Associate an output template with the engine. This is used
            # to format the output into a particular document type
            if(pkg == PACKAGE_TYPE_WORD):
                template = template_word_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_ODT):
                template = template_odt_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_PDF):
                template = template_odt_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_TEXT):
                template = template_text_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_TWIKI):
                template = template_twiki_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_MEDIAWIKI):
                template = template_mediawiki_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_C):
                template = template_c_t(self, indexer)
                template.set_output_format(options.output_format)
                template.allow_diagnostic_code(options.allow_diagnostic_code)
            elif(pkg == PACKAGE_TYPE_VERA):
                template = template_vera_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_SHORTE):
                template = template_shorte_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_SWIG):
                template = template_swig_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_LABVIEW):
                template = template_labview_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_SQL):
                template = template_sql_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_MERGEFILE):
                template = template_mergefile_t(self, indexer)
            elif(pkg == PACKAGE_TYPE_REVEALJS):
                template = template_revealjs_t(self, indexer)
            else:
                template = template_html_t(self, indexer)
                template.m_inline = inline
                template.set_template_dir(pkg)
                template.m_include_pdf = include_pdf
            
            # Set the output template and generate the
            # contents in the output directory
            self.set_template(template)
            self.generate(pkg)

        if(zip_output != None):
            zip_output = "test.zip"
            print "ZIP_OUTPUT: %s" % zip_output
            print "OUTPUT: %s" % self.m_output_directory
            #zipper("%s/." % self.m_output_directory, zip_output)
            zipper(self.m_output_directory, zip_output)

            
