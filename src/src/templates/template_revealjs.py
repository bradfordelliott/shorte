# -*- coding: iso-8859-15 -*-
#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   template_revealjs.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a template class that is used
#|   to generate HTML documents from a Shorte template.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import os
import string
import sys
from string import Template;
import shutil
import time
import datetime
import base64

from src.shorte_defines import *
from template import *
from template_html import *
from src.shorte_source_code import *
import templates.html.html_styles as html_styles

    
class template_revealjs_t(template_html_t):

    def __init__(self, engine, indexer):
        
        template_html_t.__init__(self, engine, indexer)

        # DEBUG BRAD: These features currently don't work in
        #             the reveal.js template. They need to be
        #             eventually fixed.
        self.m_wikify = False
        self.m_allow_xrefs = False
        self.m_inline = True
    
    def _load_template(self, template_name):
        
        handle = open(shorte_get_startup_path() + "/templates/reveal.js/%s" % (template_name), "r")

        contents = handle.read()
        handle.close()

        return contents
    
    def format_list(self, list, ordered=False, indent=0):

        if(indent != 0):
            style = " style='margin-left:%dpx;' " % (40 + indent*10)
        else:
            style = " style='margin-left:40px'"

        if(not ordered):
            start_tag = "<ul%s>" % style
            end_tag = "</ul>"
        else:
            start_tag = "<ol%s>" % style
            end_tag = "</ol>"

        source = start_tag

        for elem in list:
            source += self.format_list_child(elem, start_tag, end_tag)

        source += end_tag

        return source
    
    def append_header(self, tag, data, file):

        data = self.format_text(data, False)

        if(tag == "h1"):
            if(self.m_in_section):
                self.m_contents.append("</section>")
            self.m_in_section = True

            self.m_contents.append("<section><h1>" + data.strip() + "</h1>\n")

        elif(tag == "h2"):
            self.m_contents.append("<h2>" + data.strip() + "</h2>\n")

        elif(tag == "h3"):
            self.m_contents.append("<h3>" + data.strip() + "</h3>\n")

        elif(tag == "h4"):
            self.m_contents.append("<h4>" + data.strip() + "</h4>\n")
        
        elif(tag == "h5"):
            self.m_contents.append("<h5>" + data.strip() + "</h5>\n")
        
        elif(tag == "h"):
            self.m_contents.append("<h6>" + data.strip() + "</h6>\n")
    
     
    #def append_source_code(self, tag):

    #    rc = self.format_source_code(tag.name, tag.contents)

    #    source = self.format_source_code_no_lines(tag.name, tag.contents)

    #    result = tag.result

    #    snippet_id = self.m_snippet_id
    #    self.m_snippet_id += 1

    #    if(result != None):
    #        # Convert any HTML tags in the input source
    #        lt = re.compile("<")
    #        gt = re.compile(">")
    #        nl = re.compile("\n")
    #        ws = re.compile(" ")

    #        result = lt.sub("&lt;", result)
    #        result = gt.sub("&gt;", result)
    #        result = nl.sub("<br>", result)
    #        result = ws.sub("&nbsp;", result)
    #        
    #        result = html_styles.template_code_result.substitute({"result": result})
    #    else:
    #        result = ""

    #    if(self.m_show_code_headers["code"]):
    #        snippet_id = self.m_snippet_id
    #        self.m_snippet_id += 1
    #        code_header = template_code_header.substitute(
    #                {"id" : snippet_id,
    #                 "style" : "margin-left:30px;margin-top:10px;width:100%;"})
    #        source = template_source.substitute({"id": snippet_id, "source": source})
    #    else:
    #        code_header = ""
    #        source = ""

    #    self.m_contents.append(template_code.substitute(
    #            {"contents"    : rc,
    #             "source"      : source,
    #             "code_header" : code_header,
    #             "template"    : "code",
    #             "result"      : result}))

    
    def append(self, tag):
        
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_contents.append("<p>" + self.format_text(tag.contents) + "</p>\n")
        elif(name == "text"):
            self.m_contents.append(self.format_textblock(tag))
        elif(name == "pre"):
            self.m_contents.append("<pre style='margin-left:10px;'>" + self.format_text(tag.contents) + "</pre>\n")
        elif(name == "note"):
            self.m_contents.append(self.format_note(tag, "Note", "note.png"))
        elif(name == "tbd"):
            self.m_contents.append(self.format_note(tag, "TBD", "tbd.png"))
        elif(name == "question"):
            self.m_contents.append(self.format_note(tag, "Question", "question.png"))
        elif(name == "warning"):
            self.m_contents.append(self.format_note(tag, "Warning", "warning.png"))
        elif(name == "table"):
            self.m_contents.append(self.format_table(tag.source, tag.contents))
        elif(name == "struct"):
            self.m_contents.append(self.format_struct(tag))
        elif(name == "define"):
            self.m_contents.append(self.format_define(tag))
        elif(name == "ul"):
            self.m_contents.append(self.format_list(tag.contents, False))
        elif(name == "ol"):
            self.m_contents.append(self.format_list(tag.contents, True))
        elif(name == "checklist"):
            self.m_contents.append(self.format_checklist(tag))
        elif(name == "image"):
            self.m_contents.append(self.format_image(tag.contents))
        elif(name == "imagemap"):
            self.m_contents.append(self.format_imagemap(tag))
        elif(name == "prototype"):
            self.m_contents.append(self.format_prototype(tag))
        elif(name == "testcase"):
            self.m_contents.append(self.format_testcase(tag))
        elif(name == "testcasesummary"):
            self.m_contents.append(self.format_testcase_summary(tag))
        elif(name == "enum"):
            self.m_contents.append(self.format_enum(tag))
        elif(name == "acronyms"):
            self.m_contents.append(self.format_acronyms(tag))
        elif(name == "questions"):
            self.m_contents.append(self.format_questions(tag))
        elif(name == "functionsummary"):
            self.m_contents.append(self.format_function_summary(tag))
        elif(name == "typesummary"):
            self.m_contents.append(self.format_types_summary(tag))
        elif(name == "embed"):
            self.m_contents.append(self.format_embedded_object(tag))
        elif(name == "sequence"):
            self.m_contents.append(self.format_sequence(tag))
        elif(name == "columns"):
            self.m_contents.append("<div style='float:left;'>")
            pass
        elif(name == "endcolumns"):
            self.m_contents.append("</div><div style='clear:both;'></div>")
        elif(name == "column"):
            self.m_contents.append("</div><div style='float:left;'>")
            pass
        elif(name == "input"):
            self.m_contents.append(self.format_input(tag))
        elif(name in ('class', "quote")):
            WARNING("This tag [%s] is not supported yet" % name)
        else:
            FATAL("Undefined tag: %s [%s]" % (name, tag.source))
        

        #elif(tag == "pycairo"):
        #    self.m_contents += self.format_pycairo(file, data)
        #elif(tag == "pre"):
        #    self.m_contents += "<pre style='margin-left:40px;'>%s</pre>" % data
        #else:
        #    print "Undefined tag: %s [%s]" % (tag, data); sys.exit(-1);
        #
    #def _fix_css(self, css):
    #    css = string.Template(css)

    #    css = css.substitute({"h1_color" : "#CC020C",
    #                          "h2_color" : "#CC020C",
    #                          "h3_color" : "#CC020C"}) 

    #    return css
    
    def install_support_files(self, outputdir):
        
        theme = self.m_engine.get_theme()
        
        if(os.path.exists(outputdir + "/css")):
            shutil.rmtree(outputdir + "/css")

        if(os.path.exists(outputdir + "/reveal.js")):
            shutil.rmtree(outputdir + "/reveal.js")
       
        if(os.path.exists(outputdir + "/%s.css" % theme)):
            os.remove(outputdir + "/%s.css" % theme) 
        
        ignore_patterns=('*.swp')
        #shutil.copy(shorte_get_startup_path() + "/templates/reveal.js/%s/%s.css" % (self.m_engine.get_theme(), self.m_engine.get_theme()), self.m_engine.m_output_directory)
        shutil.copytree(shorte_get_startup_path() + "/templates/reveal.js/%s/css" % theme, self.m_engine.m_output_directory + "/css") # , ignore=shutil.ignore_patterns(*ignore_patterns))
        
        handle = open(shorte_get_startup_path() + "/templates/reveal.js/%s/%s.css" % (theme,theme), "rt")
        contents = handle.read()
        handle.close()
        css = self._fix_css(contents, 'revealjs')
        #css = css.replace(".bordered", ".reveal .bordered")
        handle = open("%s/%s.css" % (outputdir, theme), "wt")
        handle.write(css)
        handle.close()

        #shutil.copy(shorte_get_startup_path() + "/templates/reveal.js/%s/%s.css" % (theme, theme), self.m_engine.m_output_directory)
        shutil.copytree(shorte_get_startup_path() + "/3rdparty/reveal.js", self.m_engine.m_output_directory + "/reveal.js") # , ignore=shutil.ignore_patterns(*ignore_patterns))

    def generate_string(self, theme, version, package):
        
        self.m_inline = True
        package = "html_inline"
        
        return self.generate(theme, version, package, True)

    def generate(self, theme, version, package, as_string=False):

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        
        # Create the content directory if it's not
        # an inline HTML doc.
        if(not self.is_inline()):
            self.m_engine._mkdir(self.get_content_dir())
        
        page_names = {}
        self.m_contents = []
        links = []
        tags = []

        title = ""
        subtitle = ""

        self.m_show_code_headers["code"] = False

        for page in pages:
            tags.extend(page["tags"])
            title = page["title"]

            if(page.has_key("subtitle")):
                subtitle = page["subtitle"]

        output_file = self.m_engine.m_output_directory + "/" + "index.html"

        html = ''
        self.m_in_section = False

        for tag in tags:

            if(self.m_engine.tag_is_header(tag.name)):
                self.append_header(tag.name, tag.contents, output_file)

            elif(self.m_engine.tag_is_source_code(tag.name)):
                self.append_source_code(tag)

            else:
                self.append(tag)

        if(self.m_in_section):
            self.m_contents.append('</section>')

        tpl = string.Template(self._load_template("%s/%s.html" % (self.m_engine.get_theme(), self.m_engine.get_theme())))
        html = tpl.substitute({"title" : title,
                        "subtitle" : subtitle,
                        "date" : self.m_engine.get_date(),
                        "version" : self.m_engine.get_doc_info().version(),
                        "author" : self.m_engine.get_doc_info().author(),
                        "contents" : self.get_contents(),
                        "pdf" : self.include_link(self.get_pdf_name(), "css/")
                        })

        output = open(output_file, "wt")
        output.write(html)
        output.close()

        self.install_support_files(self.m_engine.m_output_directory)
        
        # Copy output images - really only required if we're generating
        # an HTML document.
        if(self.is_inline() != True):
            pictures_copied = {}
            for image in self.m_engine.m_images:
            
                if(pictures_copied.has_key(image)):
                    continue

                parts = os.path.split(image)
                #print "IMAGE: [%s]" % image
                shutil.copy(image, self.m_engine.m_output_directory + "/" + parts[1])
                pictures_copied[image] = True
         
        # Now generate the document index
        #as_string = True
        #if(as_string):
        #    return self.generate_index(title=self.m_engine.get_title(), subtitle=self.m_engine.get_subtitle(), theme=self.m_engine.get_theme(), version=version, links=links, as_string=True)

        #print "Generating doc"  

