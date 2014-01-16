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

    def clear(self):
        self.m_pages = []
        self.m_images = []
        self.m_include_queue = []
        self.m_imagemaps = {}
        self.m_macros = {}

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

            
