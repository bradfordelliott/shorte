import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from src.shorte_defines import *
from template import *
import template_html


code_template = string.Template(
"""<div><div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>$contents</div><br/></div>

*Result:*

<div><div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>$result</div></div>

""")


code_template_no_result = string.Template(
"""<div><div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>$contents</div></div>
""")

note_template = string.Template(
"""
    <div>
    <div style='margin-left: 30px; color: red; border-left: 1px solid #C0C0C0;width:100%;'>
    <table>
        <tr>
            <td><img style="height:50px;" src="$image"></td>
            <td>
                <div style='font-weight:bold;color:black;text-decoration:underline;'>Note:</div>
                <div style="margin-left:10px;">$contents</div>
            </td>
        </tr>
    </table>
    </div>
    </div>
""")

class template_mediawiki_t(template_html.template_html_t):

    def __init__(self, engine, indexer):
        
        template_html.template_html_t.__init__(self, engine, indexer)

    
    def format_source_code(self, language, tags, source=""):

        output = ''
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        line = 1

        source = source.replace('\\', '')
        return '<pre>%s</pre>' % source

        output += '<span style="color:#c0c0c0;">001&nbsp;&nbsp;</span>'
        
        for tag in tags:

            type = tag["type"]
            source = tag["data"]
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)

            if(type == TAG_TYPE_CODE):

                if(source != ""):
                    source = self.format_keywords(language, source)
                    output += '<span>%s</span>' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                output += '<span style="color:green;">%s</span>' % source
            elif(type == TAG_TYPE_WHITESPACE):
                output += '&nbsp;'
            elif(type == TAG_TYPE_STRING):
                output += '<span style="color:#9933CC;">%s</span>' % source
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'
                line += 1
                output += "<span style='color:#c0c0c0;'>%03d&nbsp;&nbsp;</span>" % (line)

        return output

    def format_table(self, source, table):

        html = '\n'
        
        #if("title" in table):
        #    html += "Title: %s\n" % (table["title"])

        num_cols = table["max_cols"]
        col_widths = []

        for i in range(0, num_cols):
            col_widths.append(0)

        for row in table["rows"]:

            j = 0;
            for col in row["cols"]:
                
                if(len(col["text"]) > col_widths[j]):
                    col_widths[j] = len(col["text"])
                j += 1

        html += "{|\n"

        for row in table["rows"]:

            is_header = row["is_header"]
            is_subheader = row["is_subheader"]
            is_reserved = row["is_reserved"]

            if(row["is_caption"]):
                #html += "      Caption: %s\n" % (row["cols"][0])
                pass
            else: 
                col_num = 0
                for col in row["cols"]:

                    txt = self.format_text(col["text"])
                    colspan = col["span"]
                    
                    if(is_header):
                        html += ('''! style="background-color:#c0c0c0;" colspan='%d'|%s\n''') % (colspan,txt)

                    elif(is_subheader):
                        html += ('''! style="background-color:#a0a0a0;" colspan='%d'|%s\n''') % (colspan,txt)
                    else:
                        html += ("| %s\n") % (txt)

                    col_num += 1

            html += "\n|-\n"

        #if("caption" in table):
        #    html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])


        html += '|}\n'
        
        return html

    
    def _expand_links(self, matches):

        data = matches.groups()[0]

        matches = re.search("(.*?),(.*)", data)

        if(matches != None):

            source = matches.groups()[0].strip()
            label  = matches.groups()[1].strip()

            print "source = %s, label = %s" % (source, label)
        else:
            source = data.strip()
            label = source

            source = re.sub("->", "#", source)
            label = re.sub("->", "", label)

            print "source = %s, label = %s" % (source, label)
        
        expr = re.compile("(\$[A-Za-z0-9_]+)", re.DOTALL)
        source = xmlize(expr.sub(self.m_engine._expand_url, source))
        label  = expr.sub(self.m_engine._expand_url, label)

        return "<a href='%s'>%s</a>" % (source, label)
    
    def _format_links(self, data):
           
        # Expand any links
        expr = re.compile("\[\[(.*?)\]\]", re.DOTALL)
        data = expr.sub(self._expand_links, data)

        return data

    def parse_style(self, data):
        data = style.strip()
        matches = re.search("style=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    def parse_caption(self, data):
        data = style.strip()
        matches = re.search("caption=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    def parse_href(self, data):
        data = style.strip()
        matches = re.search("href=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    import base64


    def format_image(self, image):

        name = image["name"]

        # If inlining is turned on then we need to embed the image
        # into the generated output HTML file.
        if(self.m_inline == True):
            handle = open(name, "rb")
            data = base64.encodestring(handle.read())
            data = re.replace("\n", "", data)
            name = "data:image/jpeg;base64," + data
            handle.close()

        style = ""
        caption = ""
        href_start = ""
        href_end   = ""

        if(image.has_key("width")):
            style += "width:%s;" % image["width"]
        if(image.has_key("height")):
            style += "height:%s;" % image["height"]
        if(image.has_key("caption")):
            caption = image["caption"]

        if(image.has_key("href")):
            href_start = "<a style='text-decoration:none;' href='%s'>" % image["href"]
            href_end = "</a>"


        if(image.has_key("align") and (image["align"] == "center" or image["align"] == "right")):
            if(image["align"] == "center"):
            
                return """
%s
<center>
<table style='text-align:center;'>
    <tr><td><img src='%s' style=\"%s\"/></td></tr>
    <tr><td><b>%s</b></td></tr>
</table>
</center>
%s
""" % (href_start, name, style, caption, href_end)
            elif(image["align"] == "right"):
                return """
%s
<table style='text-align:center;float:right;'>
    <tr><td><img src='%s' style=\"%s\"/></td></tr>
    <tr><td><b>%s</b></td></tr>
</table>
%s
""" % (href_start, name, style, caption, href_end)
                

        else:
            return """
%s
<span style='display:inline;'>
<table style='display:inline;text-align:center;'>
    <tr><td><img src='%s' style=\"%s\"/></td></tr>
    <tr><td><b>%s</b></td></tr>
</table>
</span>
%s
""" % (href_start, name, style, caption, href_end)

    
    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)

        return self.format_image(image)

    
    def append_header(self, tag, data, file):

        data = self.format_text(data)
        header_char = '='
        tmp = ''
        
        if(tag == "h1"):
            tmp = '''\n=%s=\n\n''' % (data.strip())

        elif(tag == "h2"):
            tmp = '''\n==%s==\n\n''' % (data.strip())

        elif(tag == "h3"):
            tmp = '''\n===%s===\n\n''' % (data.strip())
        
        elif(tag == "h4"):
            tmp = '''\n====%s====\n\n''' % (data.strip())
        
        elif(tag == "h5"):
            tmp = '''\n=====%s=====\n\n''' % (data.strip())
        
        elif(tag == "h"):
            tmp = '''\n======%s======\n\n''' % (data.strip())

        self.m_contents += tmp
    
    
    def append_source_code(self, tag):

        rc = '\n'
        rc += self.format_source_code(tag.name, tag.contents, tag.source)
        result = tag.result

        self.m_contents += rc + "\n"
        return ''

        if(result != None):

            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            nl = re.compile("\n")
            ws = re.compile(" ")

            result = lt.sub("&lt;", result)
            result = gt.sub("&gt;", result)
            result = nl.sub("<br>", result)
            result = ws.sub("&nbsp;", result)

            self.m_contents += code_template.substitute(
                    {"contents" : rc,
                     "result"   : result,
                     "source"   : "blah"});
        else:
            self.m_contents += code_template_no_result.substitute(
                    {"contents" : rc,
                     "source"   : "blah"});

    
    def append(self, tag):
        
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_contents += self.format_text(tag.contents) + "\n"
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        elif(name == "pre"):
            self.m_contents += "<pre style='margin-left:30px;'>" + self.format_text(tag.contents) + "</pre>\n"
        elif(name == "note"):
            self.m_contents += "<sticky>" + self.format_note(self.format_text(tag.contents)) + "</sticky>"
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name == "struct"):
            self.m_contents += "<sticky>" + self.format_struct(tag.source, tag.contents) + "</sticky>"
        elif(name == "ul"):
            self.m_contents += "<sticky>" + self.format_list(tag.contents, False) + "</sticky>"
        elif(name == "ol"):
            self.m_contents += "<sticky>" + self.format_list(tag.contents, True) + "</sticky>"
        elif(name == "prototype"):
            self.m_contents += "<sticky>" + self.format_prototype(tag) + "</sticky>"
        #else:
        #    print "Undefined tag: %s [%s]" % (name, tag["source"]); sys.exit(-1)
        

    def get_contents(self):
        
        return self.m_contents
        
    def get_index_name(self):

        return "index.html"

    def generate_index(self, title, theme, version):
        
        cnts = self.get_contents()
        
        file = open(self.m_engine.m_output_directory + "/index.wiki", "w")
        file.write(cnts)
        file.close()

        return True

    def set_template_dir(self, template_dir):
        self.m_template_dir = shorte_get_startup_path() + "/templates/%s/" % template_dir
    
    
    def install_support_files(self, outputdir):
        
        #if(os.path.exists(outputdir)):
        #    shutil.rmtree(outputdir)
       
        #os.makedirs(outputdir)

        print "No support files"
    
    def generate(self, theme, version, package):

        self.m_package = package
        self.m_inline = True
        
        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = '''
'''

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".mediawiki", source_file)
            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag.name, tag.contents, output_file)

                elif(self.m_engine.tag_is_source_code(tag.name)):
                    self.append_source_code(tag)

                else:
                    self.append(tag)

        # Now generate the document index
        self.generate_index(self.m_engine.get_title(), self.m_engine.get_theme(), version)

        #if(self.m_inline != True):
        #    self.install_support_files(self.m_engine.get_output_dir())
       
        ## Copy output images - really only required if we're generating
        ## an HTML document.
        #if(self.m_inline != True):
        #    for image in self.m_engine.m_parser.m_images:
        #        shutil.copy(image, self.m_engine.get_output_dir() + "/" + image)

        print "Generating doc"  

