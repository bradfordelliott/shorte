import os
import datetime
import string
import shutil
from string import Template;
from src.shorte_defines import *

try:
    from PIL import Image
except:
    WARNING("Failed to load Image library. Try installing it using the command 'pip install Pillow'")

from src.shorte_source_code import *
from src.parsers.shorte_parser import *
from src.parsers.cpp_parser import *
from src.parsers.clang_parser import *
from src.parsers.python_parser import *
from src.parsers.markdown_parser import *
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
from src.templates.template_markdown import template_markdown_t

class document_info_t:
    '''This class is used to manage the attributes associated
       with a shorte document'''

    def __init__(self):
        '''Class constructor'''

        self.m_docnumber = None
        self.m_docversion = None
        self.m_docsubitle = ""
        self.m_doctitle = ""
        self.m_docauthor = None
        self.m_revision_history = None
        self.m_footer_title = None
        self.m_footer_subtitle = None
        self.m_templates = {}

    def version(self):
        if(self.m_docversion == None):
            return "N/A"

        return self.m_docversion

    def set_version(self, version):
        if(self.m_docversion == None):
            self.m_docversion = version

    def author(self):
        if(self.m_docauthor == None):
            return "N/A"

        return self.m_docauthor

    def set_author(self, author):
        if(self.m_docauthor == None):
            self.m_docauthor = author

    def copyright_date(self):
        return "%d" % datetime.date.today().year

    def customer(self):
        return ""

    def footer_title(self):
        if(self.m_footer_title == None):
            return ""
        return self.m_footer_title

    def set_footer_title(self, title):
        if(self.m_footer_title == None):
            #INFO("set_footer_title: %s" % title)
            self.m_footer_title = title

    def set_footer_subtitle(self, title):
        if(self.m_footer_subtitle == None):
            #DEBUG("set_footer_subtitle: %s" % title)
            self.m_footer_subtitle = title

    def footer_subtitle(self):
        if(self.m_footer_subtitle == None):
            return ""
        return self.m_footer_subtitle
    
    def revision_history(self):
        return self.m_revision_history

    def set_revision_history(self, revision_history):
        if(self.m_revision_history == None):
            self.m_revision_history = revision_history

    def number(self):
        if(self.m_docnumber == None):
            return ""
        return self.m_docnumber

    def set_number(self, number):
        if(self.m_docnumber == None):
            self.m_docnumber = number

    def title(self):
        return self.m_doctitle

    def subtitle(self):
        return self.m_docsubtitle
   
    def add_template(self, key, value):
        # DEBUG BRAD: This is a temporary way of dealing with comments
        #             in snippets
        if(self.m_templates.has_key(key)):
            FATAL("Template %s already exists" % key)
        value = value.replace("\\#", "#")
        self.m_templates[key] = value

    def has_template(self, key):
        if(self.m_templates.has_key(key)):
            return True
        return False

    def get_template(self, key):
        return self.m_templates[key]


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
        self.m_theme = "shorte"
        self.m_snippets = {}
        self.m_urls = {}
        self.m_example_id = 0
        self.m_image_id = 0

        if(output_path == None):
            output_path = "build-output"
        self.m_output_directory = output_path
        self.m_output_file = None
        
        self.m_pages = []
        self.m_images = []

        # A list of imagemaps associated with images
        self.m_imagemaps = {}
        self.m_macros = {}
        self.m_includes = []

        self.m_package = ""
        self.m_doc_info = document_info_t()

        self.m_output_filename = None

        self.m_include_queue = []

        self.m_search_and_replace = None
        
        self.m_source_code_analyzer = source_code_t()

        self.m_wiki_links = {}

        # Create the output directory if it doesn't exist already
        #print "OUTPUT_DIR: %s" % self.m_output_directory
        if(not os.path.exists(self.m_output_directory)):
            os.makedirs(self.m_output_directory)

        self.m_date = datetime.datetime.now().strftime("%d %B %Y")

        if(parser == "cpp"):
            self.m_parser = cpp_parser_t(self)
        elif(parser == "clang"):
            self.m_parser = clang_parser_t(self)
        elif(parser == "python"):
            self.m_parser = python_parser_t(self)
        elif(parser == "markdown"):
            self.m_parser = markdown_parser_t(self)
        else:
            self.m_parser = shorte_parser_t(self)
            #self.m_parser.set_cpp_parser(cpp_parser_t(self))
            # DEBUG BRAD: If you don't have the proper includes then
            #             clang may fail on types it doesn't understand. 
            self.m_parser.set_cpp_parser(clang_parser_t(self))
            self.m_parser.set_markdown_parser(markdown_parser_t(self))

        self.m_classes = {}

    def class_get(self, name):
        if(not self.m_classes.has_key(name)):
            WARNING("Constructing class [%s]" % name)
            cls = class_t()
            cls.set_name(name)
            self.m_classes[name] = cls
            return cls
        WARNING("Retrieving class")
        return self.m_classes[name]

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

    def set_theme(self, theme):
        self.m_theme = theme

    def get_theme(self, package=None):

        if("=" in self.m_theme):
            themes = self.m_theme.split(";")
            for theme in themes:
                parts = theme.split("=")
                pkg  = parts[0]
                name = parts[1]

                if(package == pkg):
                    return name

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
        self.m_doc_info.set_version(version)

    def set_package(self, package):
        self.m_package = package

    def set_template(self, template):
        self.m_template = template
        self.m_template.m_title = self.m_parser.get_title()

    def get_doc_info(self):
        return self.m_doc_info

    def get_date(self):
        return self.m_date

    def get_output_dir(self):
        return self.m_output_directory

    def set_output_dir(self, path):
        self.m_output_directory = path
        if(not os.path.exists(self.m_output_directory)):
            os.makedirs(self.m_output_directory)
    
    def has_output_file(self):
        if(self.m_output_file != None):
            return True
        return False
    def get_output_file(self):
        return self.m_output_file
    def set_output_file(self, path):
        self.m_output_file = path

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
            dir = shorte_get_config(section, key)
            dir = os.path.abspath(dir)
            return dir

        if(section == "c"):
            val = shorte_get_config(section, key)

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


        return shorte_get_config(section, key)

    def set_config(self, section, key, val):
        shorte_set_config(section, key, val)


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

        #print "Page: %s" % source_file
        self.m_parser.parse(source_file)

        #for link in self.m_wiki_links:
        #    print "LINK: [%s]" % link

    def parse_string(self, contents):
        self.m_parser.parse_string(contents)

    def add_wikiword(self, word):
        if(self.m_wiki_links.has_key(word)):
            FATAL("Wikiword %s already exists" % word)
        self.m_wiki_links[word.wikiword] = word

    def is_wiki_word(self, phrase):
        '''Returns the target link if the phrase is a wikiword
           or None if it does not exist'''
        link = None

        if(self.m_wiki_links.has_key(phrase)):

            link = self.m_wiki_links[phrase]

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

        if(not os.path.exists(PATH_INKSCAPE)):
            import shutil
            ERROR("%s not found, cannot convert" % PATH_INKSCAPE)
            path = shorte_get_startup_path() + "/templates/shared/inkscape_not_found.png"
            shutil.copyfile(path, output)
            return output

        cmd = '''%s -z -e "%s" "%s"''' % (PATH_INKSCAPE, output, input)
        #print cmd
        
        # Need a shorte delay after running inkscape because of
        # a race condition on windows
        result = os.popen(cmd).read()
        time.sleep(4)

        return output

    def convert_image(self, image):
        '''This method is called to convert an input image
           from one format to another. Currently it really only
           supports conversion via inkscape.

           @param image [I] - The image to convert

           @return The image structure updated to point
                   to the converted image
        '''

        name = image["name"]
        converter = image["converter"]
        output = image["src"]

        if(not os.path.exists(output)):
            FATAL("Image source file %s does not exist, cannot convert" % output)

        if(converter == "gnuplot"):
            FATAL("Converting inkscape image %s" % name)

        if(converter == "inkscape"):
            input = image["src"]
            output = self.inkscape_to_png(input)
            image["src"] = output
            image["ext"] = ".png"

            #print "output: %s" % output

            # If we've found the source image than remove it from
            # the list of images
            for i in self.m_images:
                if(i == input):
                    DEBUG("Removing %s from the list" % i)
                    self.m_images.remove(i)

            # Once the image has been converted remove
            # the converter flag so we don't attempt to
            # convert it multiple times.
            del image["converter"]

        self.m_images.append(output)

        return image
    
    def scale_image(self, image):
        '''This method is used to scale an image if a height or width attribute
           is specified.

           @param image [I] - The image object to scale.

           @return The modified image object with the updated source.
        '''
        width = 0
        height = 0

        width_scale_percentage = False
        height_scale_percentage = False

        if(image.has_key("width")):
            width = image["width"]
            if("%" in width):
                width_scale_percentage = True
                width = re.sub("%", "", width)
            elif("px" in width):
                width = re.sub("px", "", width)
            width = int(width)

        if(image.has_key("height")):
            height = image["height"]
            if("%" in height):
                height_scale_percentage = True
                height = re.sub("%", "", height)
            elif("px" in height):
                height = re.sub("px", "", height)
            height = int(height)

        im = Image.open(image["src"])

        scale_width  = 1.0
        scale_height = 1.0

        if(width > 0):
            if(width_scale_percentage):
                scale_width = width/100.0
            else:
                scale_width = (width / (im.size[0] * (1.0)))

            if(height == 0):
                scale_height = scale_width

        if(height > 0):
            if(height_scale_percentage):
                scale_height = height/100.0
            else:
                scale_height = (width / (im.size[1] * (1.0)))

            if(width == 0):
                scale_width = scale_height

        width = scale_width * im.size[0]
        height = scale_height * im.size[1]

        # DEBUG BRAD: Resize the image to fit
        im = im.resize((int(width),int(height)), Image.BICUBIC)
        scratchdir = shorte_get_config("shorte", "scratchdir")
        name = image["name"] + "_%dx%d" % (width,height)
        img = scratchdir + os.path.sep + name + image["ext"]
        image["name"] = name
        image["src"] = img
        #print img
        im.save(img)
            
        # If we've found the source image than remove it from
        # the list of images
        for i in self.m_images:
            if(i == image["src"]):
                DEBUG("Removing %s from the list" % i)
                self.m_images.remove(i)

        self.m_images.append(img)

        return (image,height,width)

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
    def set_define(self, name, value, override=False):
        """This method is called to set the value of
           a document define that can be used in variable
           expansion. Once a define is set any future
           attempts to set the define will be ignored unless
           the override flag is set.
        """
        #print "Setting macro: %s = %s" % (name, value)

        # If the macro is already set then don't update
        # it unless the override flag is asserted.
        if(self.m_macros.has_key(name) and override == False):
            return

        self.m_macros[name] = value

    def set_includes(self, includes):
        self.m_includes = includes
    def get_includes(self):
        return self.m_includes

    def get_function_summary(self, tag=None, filters=None):
        '''This method attempts to create a summary of all the
           available functions scanned by the parser

           @param tag     [I] - The original @functionsummary tag parsed
                                from the sources with it's modifiers
           @param filters [I] - An array of filters that is used to
                                include or exclude certain methods
                                like deprecated functions

           @return The list of functions in the function summary.
        '''

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
                    
                    obj = tag.contents

                    if(filters != None):
                        if("deprecated" in filters):
                            if(not obj.has_deprecated()):
                                continue
                        elif('!deprecated' in filters):
                            if(obj.has_deprecated()):
                                continue
                      
                    if(1): #page_title == "" or (not tag.page_title)):
                        #print "DO I GET HERE? page_title = %s" % (page_title)
                        #print tag
                        #sys.exit(-1)
                        hierarchy = obj.file
                        if(len(hierarchy) == 0):
                            hierarchy = page['source_file']

                        hierarchy = os.path.basename(hierarchy)
                        #hierarchy = hierarchy.replace(".c", "")
                        #hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")

                        #if(tag.modifiers.has_key("hierarchy")):
                        #    hierarchy = tag.modifiers["hierarchy"]

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

    def get_types_summary(self, tag=None, filters=None):

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
                
                if(tag.name in ("struct", "enum")):

                    obj = tag.contents

                    if(filters != None):
                        if("deprecated" in filters):
                            if(not obj.has_deprecated()):
                                continue
                        elif('!deprecated' in filters):
                            if(obj.has_deprecated()):
                                continue
                    
                    if(1): #page_title == "" or (not tag.page_title)):
                        hierarchy = obj.file
                        if(len(hierarchy) == 0):
                            hierarchy = page['source_file']

                        hierarchy = os.path.basename(hierarchy)
                        #hierarchy = hierarchy.replace("leeds_", "")
                        #hierarchy = hierarchy.replace(".c", "")
                        #hierarchy = hierarchy.replace(".h", "")
                        hierarchy = hierarchy.replace(".tpl", "")

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
            print ("FILE %s:\n%s" % (file, name))
        
    
    def info(self, options):
        output = []

        keys = options.info
        keys = keys.split(";")

        # Print the list of defines passed to the engine
        if("defines" in keys):
            defines = self.get_macros()
            for define in defines:
                output.append("%s = %s" % (define, defines[define]))

        if("gcc" in keys):
            if("cygwin" in platform.system().lower()):
                import subprocess
                import re
                phandle = subprocess.Popen(["/usr/bin/gcc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result = phandle.stdout.read()
                result += phandle.stderr.read()
                phandle.wait()
                rc = phandle.returncode

                matches = re.search("\(GCC\) ([0-9.]+)", result)
                gcc_version = ""
                if(matches != None):
                    gcc_version = matches.groups()[0].strip()
                else:
                    FATAL("Failed finding GCC version")

                gcc_includes = "/usr/lib/gcc/%s-pc-cygwin/%s/include" % (platform.machine(), gcc_version)
                print "GCC"
                print "  version:    %s"  % gcc_version
                print "  includes:   %s" % gcc_includes
                print "  clang args: -xc -I%s" % gcc_includes

        # Print the list of tags encountered by the parser
        if("tags" in keys):
            output.append("Tag Data")
            output.append("----------------------")
            pages = self.m_parser.get_pages()
            for page in pages:
                tags = page["tags"]
                for tag in tags:
                    output.append(indent_lines(tag.__str__(short_form=True), "    ")) 
            output.append("\n\n")

        # Print the list of tags as HTML
        if("tags2html" in keys):
            output.append('''<html>
<head>
  <style>
    table{border-collapse:collapse;margin-left:20px;}
    th{border:1px solid black;background-color:#ccc;font-weight:bold;}
    td{border:1px solid black;}
  </style>
</head>
<body>
<h1>List of Tags</h1>
<table>
  <tr><th>Tag</th><th>File</th><th>Line</th><th>Source</th></tr>
''')
            pages = self.m_parser.get_pages()
            for page in pages:
                tags = page["tags"]
                for tag in tags:
                    tdata = "<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>" % (tag.name, tag.file, tag.line, tag.source)
                    output.append(tdata)

            output.append("</table></body></html>")
            
            shorte_mkdir(self.m_output_directory)

            filename = "tags.html"
            if(self.has_output_file()):
                filename = self.get_output_file()
            path_output = self.m_output_directory + os.sep + filename
            handle = open(path_output, "wt")
            handle.write("".join(output))
            handle.close()
            
            output = ["\nTags can be found in:\n    %s\n" % path_output]


        if("c2html" in keys):
            path_input = options.files
            indexer = indexer_t()
            template = template_html_t(self, indexer)
            template.m_inline = True
            template.set_template_dir("html_inline")
            path_output = self.m_output_directory + "/" + os.path.basename(path_input) + ".html"
            template.generate_source_file(path_input, path_output)
            

        if("wikiwords" in keys):
            output.append("Summary of wiki words:")
            output.append("----------------------")
            links = self.m_wiki_links
            for link in links:
                output.append('''  %-24s
    - wikiword: %s
    - label:    %s
    - bookmark: %s
    - link:     %s
    - source:   %s''' % (link, links[link].wikiword, links[link].label, links[link].is_bookmark, links[link].link, links[link].source_file))

        elif("deprecated" in keys):
            pages = self.m_parser.get_pages()

            for page in pages:
                DEBUG(page["source_file"])
                tags = page["tags"]

                for tag in tags:
                    if(tag.name == "prototype"):
                        prototype = tag.contents
                        if(prototype.has_key("deprecated")):
                            output.append("%s is deprecated" % prototype["name"])


        return '\n'.join(output)
            
    def execute_code_block(self, tag):
        """This method is called to excute a code block or snippet
           and record the results.

           @param tag [I] - The tag to execute
        """   
        source = tag.source 

        # Save the original source before any template expansion
        original_source = source

        if(tag.has_modifier("exec")):
            exec_code = to_boolean(tag.get_modifier("exec"))
            if(not exec_code):
                return
        else:
            return

        # If the tag has a template then perform any template
        # expansion.
        if(tag.modifiers.has_key("template")):
            template = tag.modifiers["template"]

            if(not self.get_doc_info().has_template(template)):
                FATAL("Template %s was not registered when parsing %s @ line %d" % (template, tag.file, tag.line))

            template = self.get_doc_info().get_template(template)

            data = tag.source

            # If the block has an indent modifier than prefix
            # it with spaces
            if(tag.has_modifier("indent")):
                indent = int(tag.modifiers["indent"].strip())
                prefix = ''
                for i in range(0, indent):
                    prefix += ' '
                data = indent_lines(data, prefix)

            source = template.replace("$1", data)

        ignore_errors = False
        if(tag.modifiers.has_key("ignore_errors")):
            ignore_errors = to_boolean(tag.modifiers["ignore_errors"])

        show_template = True
        if(tag.modifiers.has_key("show_template")):
            show_template = to_boolean(tag.modifiers["show_template"])

        # If this code snippet is part of a template
        # determine whether or not the full source should be
        # shown or just the snippet itself
        show_full_source = False
        if(tag.modifiers.has_key("show_full_source")):
            show_full_source = to_boolean(tag.modifiers["show_full_source"])

        executor = code_executor_t()
        result = executor.execute(tag.name, source, tag.modifiers)
        tag.result = result

        if((not ignore_errors) and result.has_compile_rc() and result.get_compile_rc() != 0):
            ERROR("Failed compiling code snippet in %s @ line %d\nSource:\n%s\nErrors:\n%s" % (
                tag.file, tag.line,
                indent_lines(source, "    "),
                indent_lines(result.get_compile_result(), "    ")))

        if((not ignore_errors) and result.has_run_rc() and (result.get_run_rc() != 0)):
            ERROR("Failed executing code snippet in %s @ line %d\n%s" % (tag.file, tag.line, indent_lines(source, "    ")))

        if(result.has_image()):
            self.m_image_id += 1 
            result_image = result.get_image()
            if(os.path.exists(result_image)):
                image = '%s/example_%d.png' % (shorte_get_scratch_path(), self.m_image_id)
                shutil.move(result_image, image)
                tag.set_image(image)
                result.set_image(image)
                self.m_images.append(image)

        code = self.m_source_code_analyzer

        full_source = source
        if(not show_template):
            source = original_source

        tag.contents = code.parse_source_code(tag.name, source, tag.file, tag.line)

        # Show the full source if the user chose to display
        # either it or the template data
        if(show_full_source or show_template):
            source = full_source

        tag.source = source
        
    def generate(self, package):

        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        version = self.get_doc_info().version()

        for page in pages:

            #print "NAME: %s" % page["source_file"]
            tags = page["tags"]
            
            i = 0
            num_tags = len(tags)

            while i < num_tags:
                tag = tags[i]

                if(tag.result != None):
                    INFO("Skipping tag, already executed")
                    i += 1
                    continue
            
                if(self.tag_is_executable(tag.name)):
                    # Executing a shorte block requires special
                    # handling. Instead of actually executing anything we
                    # want to expand the results inline so that they get inserted
                    # into the document. This is mostly to support
                    # documenting shorte itself.
                    if(tag.name == "shorte"):
                        if(tag.has_modifier("exec")):
                            src = tag.source
                            # Strip any \ characters
                            src = src.replace("\\", "")
                            # Parse the tags
                            child_tags = self.m_parser._parse_header_tags("", src, 0) 
                            j = i
                            
                            # If we're executing shorte tags then create a textblock
                            # that describes the result so it is obvious in the
                            # generated document.
                            ctag = tag_t()
                            ctag.source = "The result of executing this example is shown below:"
                            ctag.contents = textblock_t(ctag.source)
                            ctag.name = "text"
                            ctag.modifiers = tag.modifiers
                            ctag.page_title = tag.page_title
                            ctag.file = tag.file
                            ctag.line = tag.line
                            child_tags.insert(0, ctag)

                            # Now insert them after the current tag
                            for t in child_tags:
                                tags.insert(j+1, t)
                                j += 1
                            i = j
                    else:
                        self.execute_code_block(tag)

                i += 1
                
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
                FATAL(to_eval)

            result = tmp_macros["result"]
            #print "RESULT: %s = %s" % ("(" + define + ")", result)
            if(int(result) == 0):
                #print "DO I GET HERE?"
                return False
            
            return True

    def generate_string(self, package):
        # First evaluate any code snippets
        pages = self.m_parser.get_pages()

        version = self.get_doc_info().version()

        for page in pages:

            #print "NAME: %s" % page["source_file"]
            tags = page["tags"]

            for tag in tags:

                # If the code block has already been
                # executed then don't run it again
                if(self.tag_is_executable(tag.name)):
                    self.execute_code_block(tag)

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
                print tmp_macros
                FATAL("ERROR parsing example2.py in %s" % os.getcwd())

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
                                INFO("PATH: %s" % path)
        
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
            if(files == None):
                return
            files = re.split("[ ,]", files)
            for file in files:
                rgx = re.compile("(\.tpl|\.txt|\.ste)")
                output = rgx.sub(".html", file)
        
                #print("output file: %s" % shorte.get_output_dir() + "/" + output);
                self.parse_page(file)
        

    def generate_packages(self, package_list, theme_list, options, zip_output=None):

        inline = False
        include_link = False
        include_link_type = 'pdf'

        #print "package_list: %s" % package_list
        #print "theme_list:   %s" % theme_list

        package_list = package_list.split("+")
        packages = []

        # Handle any modifications required by the
        # input package selection. For example html+pdf
        # needs some modifications in order to include
        # a PDF link in the HTML documentation.
        for package in package_list:
            if(package in ("html", "reveal.js")):
                packages.append(package)
                if('pdf' in package_list):
                    include_link = True
                    include_link_type = 'pdf'
                elif('txt' in package_list):
                    include_link = True
                    include_link_type = 'txt'
        
            elif(package == "html_inline"):
                inline = True
                packages.append("html_inline")
                if('pdf' in package_list):
                    include_link = True
                    include_link_type = 'pdf'
                elif('txt' in package_list):
                    include_link = True
                    include_link_type = 'txt'
        
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
                template.m_include_link = include_link
                template.m_include_link_type = include_link_type
            elif(pkg == PACKAGE_TYPE_MARKDOWN):
                template = template_markdown_t(self, indexer)
            else:
                template = template_html_t(self, indexer)
                template.m_inline = inline
                template.set_template_dir(pkg)
                
                template.m_include_link = include_link
                template.m_include_link_type = include_link_type
            
            # Set the output template and generate the
            # contents in the output directory
            self.set_template(template)
            self.generate(pkg)

        if(zip_output != None):
            zip_output = "test.zip"
            DEBUG("ZIP_OUTPUT: %s" % zip_output)
            DEBUG("OUTPUT: %s" % self.m_output_directory)
            #zipper("%s/." % self.m_output_directory, zip_output)
            zipper(self.m_output_directory, zip_output)

            
