import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from src.shorte_includes import *
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
        
        self.list_indent_per_level=1
    
    def format_list_child(self, elem, indent, ordered=False, start=0):
        source = ''

        prefix = ""
        if(elem.type in ("checkbox", "action")):
            prefix = "[ ] "
            if(elem.checked):
                prefix = "[x] "

        text = prefix + elem.text
        if(ordered):
            if(elem.children != None):

                if(indent > 0):
                    source += "%s %s\n" % ('#'*(indent+1), self.format_text(text))
                else:
                    source += "# %s\n" % (self.format_text(text))

                num_children = len(elem.children)
                
                is_num = False
                is_char = False

                if(not ((indent/self.list_indent_per_level) & 0x1)):
                    start = ord("a")
                    is_char = True
                else:
                    start = 1
                    is_num = True

                for i in range(0, num_children):
                    if(is_num):
                        source += self.format_list_child(elem.children[i], indent+self.list_indent_per_level, ordered, start)
                    else:
                        source += self.format_list_child(elem.children[i], indent+self.list_indent_per_level, ordered, chr(start))
                    start += 1
            else:
                if(indent > 0):
                    source += "%s %s\n" % ("#"*(indent+1), self.format_text(text))
                else:
                    source += "# %s\n" % (self.format_text(text))
        else:
            if(elem.children):
                if(indent > 0):
                    source += "%s %s\n" % ('*'*(indent+1), self.format_text(text))
                else:
                    source += "* %s\n" % (self.format_text(text))

                num_children = len(elem.children)
                for i in range(0, num_children):
                    source += self.format_list_child(elem.children[i], indent+self.list_indent_per_level)
            else:
                if(indent > 0):
                    source += "%s %s\n" % ('*'*(indent+1), self.format_text(text))
                else:
                    source += "* %s\n" % (self.format_text(text))

        return source
    
    def format_list(self, list, ordered=False):

        source = "\n"

        start = 1
        for elem in list:
            source += self.format_list_child(elem, 0, ordered, start)
            start += 1

        source += "\n"

        return source

    def format_textblock(self, tag, prefix='', prefix_first_line=True, pad_textblock=False):
        '''This method is called to format an @text block.
           
           @param tag               [I] - The textblock tag being formatted
           @param prefix            [I] - A prefix to prepend to each line.
           @param prefix_first_line [I] - Indent the first line.
           @param pad_textblock     [I] - Pad the textblock with spaces before and after.

           @return The formatted text.
        '''

        if(isinstance(tag, tag_t)):
            textblock = tag.contents
        else:
            textblock = tag

        if(isinstance(textblock, textblock_t)):
            paragraphs = textblock.paragraphs
        else:
            paragraphs = textblock

        output = '\n'

        for p in paragraphs:
            text = p["text"]
            is_code = p["code"]
            is_list = p["list"]

            if(is_code):
                lines = text.split("\n")
                for line in lines:
                    output += "    %s\n" % line
            elif(is_list):
                output += self.format_list(text)
            else:
                output += self.format_text(text)
            output += "\n"

        while(output.startswith("\n")):
            output = output[1:]

        while(output.endswith("\n")):
            output = output[0:-1]

        lines = output.split('\n')
        output = ''
        for i in range(0, len(lines)):
            if(i == 0):
                if(prefix_first_line):
                    output += prefix + lines[i] + '\n'
                else:
                    output += lines[i] + '\n'
            else:
                output += prefix + lines[i] + '\n'

        if(pad_textblock):
            return "\n" + output + "\n"

        output += "\n"

        return output
    
    def format_source_code(self, language, tags, source=""):

        return '''
<syntaxhighlight lang=%s>
%s
</syntaxhighlight>
''' % (language, source)

    def format_table(self, source, table):

        html = '\n'
        
        #if("title" in table):
        #    html += "Title: %s\n" % (table["title"])

        num_cols = table.get_max_cols()
        col_widths = []

        for i in range(0, num_cols):
            col_widths.append(0)

        for row in table.get_rows():

            j = 0;
            for col in row["cols"]:
                
                if(len(col["text"]) > col_widths[j]):
                    col_widths[j] = len(col["text"])
                j += 1

        html += "{| class=\"wikitable\"\n"

        for row in table.get_rows():

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
                    txt = re.sub("\n *", "\n", txt)
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

    def format_object(self, tag, title):
        
        obj = tag.contents

        text = "{| class='wikitable'\n"
        
        text += "!colspan=3 style='text-align:left'|%s: %s\n" % (title, obj.get_name())
        text += "|-\n"
        text += "|colspan=3 style='text-align:left'|%s\n" % self.format_textblock(obj.get_description()).strip()
        text += "|-\n"

        if(obj.has_fields()):
            text += "!colspan=3 style='text-align:left'|Fields:\n"
            text += "|-\n"
            text += "!Width/Type\n"
            text += "!Name\n"
            text += "!Description\n"
            text += "|-\n"

            for field in obj.get_fields():
                if(field.get_is_spacer()):
                    text += "!colspan=3\n"
                else:
                    desc = self.format_textblock(field.get_description()).strip()
                    ftype = self.format_text(field.get_type())

                    text += "|%s\n" % ftype
                    text += "|%s\n" % field.get_name()
                    text += "|%s\n" % desc
                    text += "|-\n"

        elif(obj.has_params()):
            text += "!colspan=3 style='text-align:left'|Parameters:\n"
            text += "|-\n"
            text += "!Type\n"
            text += "!Name\n"
            text += "!Description\n"
            text += "|-\n"

            params = obj.get_params()
            for param in params:
                text += "|%s\n" % param.get_type()
                text += "|%s\n" % param.get_name()
                text += "|%s\n" % self.format_textblock(param.get_description())
                text += "|-\n"

        elif(obj.has_values()):
            text += "!colspan=3 style='text-align:left'|Values:\n"
            text += "|-\n"
            text += "!Name\n"
            text += "!Value\n"
            text += "!Description\n"
            text += "|-\n"

            values = obj.values2
            for val in values:

                text += "|%s\n" % val.get_name()
                text += "|%s\n" % val.get_value()
                text += "|%s\n" % self.format_textblock(val.get_description())
                text += "|-\n"
        
        if(obj.has_returns()):
            text += "!colspan=3 style='text-align:left'|Returns:\n"
            text += "|-\n"
            text += "|colspan=3|%s\n" % self.format_text(obj.get_returns())
            text += "|-\n"

        if(obj.has_see_also()):
            text += "!colspan=3 style='text-align:left'|See:\n"
            text += "|-\n"
            text += "|colspan=3|%s\n" % self.format_text(obj.get_see_also())
            text += "|-\n"
            
        text += "|}\n"

        return text
    
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
            self.m_contents += "<nowiki>" + self.format_note(self.format_text(tag.contents)) + "</nowiki>"
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name == "struct"):
            self.m_contents += self.format_object(tag, "Structure")
        elif(name == "prototype"):
            self.m_contents += self.format_object(tag, "Prototype")
        elif(name == "enum"):
            self.m_contents += self.format_object(tag, "Enumeration")
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        else:
            WARNING("Tag %s not supported in template_mediawiki" % name)

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

