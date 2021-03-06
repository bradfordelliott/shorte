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
"""

<sticky>
    <div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>
        $contents
    </div><br/>
</sticky>

*Result:*

<sticky>
    <div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>
        $result
    </div>
</sticky>



""")


code_template_no_result = string.Template(
"""

<sticky>
    <div style='margin-left:20px;background-color:#eee;border:1px solid #ccc;'>
        $contents
    </div>
</sticky>


""")

note_template = string.Template(
"""
    <sticky>
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
    </sticky>
""")

class template_twiki_t(template_html.template_html_t):

    def __init__(self, engine, indexer):
        
        template_html.template_html_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_theme = ""
        self.m_template_dir = shorte_get_startup_path() + "/templates/text/"
        self.m_inline = False
        self.list_indent_per_level=4

    def format_keywords(self, language, source):

        keywords = self.m_engine.get_keyword_list(language)

        output = ''
        keyword = ''
        pos_start = 0

        #print "input = %s" % source

        for i in range(0, len(source)):

            c = source[i]

            if((ord(c) >= 97 and ord(c) < 122) or (ord(c) == 95)):
                keyword += c 
            else:
                if(keyword != ''):
                    #print "  keyword1: {%s}" % keyword
                    #print "  substr:   {%s}" % source[pos_start:i]
                    if(keywords.has_key(keyword)):
                        #output += source[pos_start:i]
                        output += "<span class='keyword'>%s</span>" % keyword
                    else:
                        output += keyword

                    keyword = ''
                
                pos_start = i+1
                output += "%c" % c


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                #output += source[pos_start:i]
                output += "<span class='keyword'>%s</span>" % keyword
            else:
                output += keyword
            #print "  keyword2 = %s" % keyword

        #print "output = %s\n" % output

        return output
    
    def format_source_code(self, language, tags):

        output = ''
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        line = 1

        output += '<span class="line_num">001&nbsp;&nbsp;</span>'
        
        for tag in tags:

            type = tag.type
            source = tag.data
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)

            if(type == TAG_TYPE_CODE):

                if(source != ""):
                    source = self.format_keywords(language, source)
                    output += '<span>%s</span>' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                output += '<span class="comment">%s</span>' % source
            elif(type == TAG_TYPE_WHITESPACE):
                output += '&nbsp;'
            elif(type == TAG_TYPE_STRING):
                output += '<span class="string">%s</span>' % source
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'
                line += 1
                output += "<span class='line_num'>%03d&nbsp;&nbsp;</span>" % (line)

        #sys.exit(-1)

        return output



    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    format_note()
    #|
    #| DESCRIPTION:
    #|    This method is called to format a note tag
    #|
    #| PARAMETERS:
    #|    content (I) - The content associated with the note tag
    #|
    #| RETURNS:
    #|    The note data formatted as HTML.
    #|
    #+-----------------------------------------------------------------------------
    def format_note(self, content):

        handle = open(shorte_get_startup_path() + "/templates/shared/note.png", "rb")
        img_src = "data:image/jpeg;base64," + base64.encodestring(handle.read())
        img_src = re.sub("\n", "", img_src)

        handle.close()

        return note_template.substitute(
            {"contents" : self.format_text(content),
             "image"    : img_src})

            
    def format_checklist(self, tag):
        
        list = tag["contents"]

        source = ''

        if(tag["modifiers"].has_key("title")):
            source += "<p style='font-weight:bold;text-decoration:underline;'>%s</p>" % tag["modifiers"]["title"] 

        source += "<ul style='list-style-type:none'>"

        for elem in list:
            caption = ''
            if(elem.has_key("caption")):
                caption = " <span style='color:#999;font-style:italic;'>(%s)</span>" % elem["caption"]

            source += "<li><input type='checkbox' name='%s' %s/>%s%s</li>" % (elem["name"], elem["checked"], elem["name"], caption)

        source += "</ul>"

        if(tag["modifiers"].has_key("caption")):
            source += "<p style='font-style:italic;margin-left:40px;'>Caption: %s</p>" % tag["modifiers"]["title"] 

        return source
    
    
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
                    source += "%*s%s. %s\n" % (indent, " ", start, self.format_text(text))
                else:
                    source += "%s. %s\n" % (start, self.format_text(text))

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
                    source += "%*s%s. %s\n" % (indent, " ", start, self.format_text(text))
                else:
                    source += "%s. %s\n" % (start, self.format_text(text))
        else:
            if(elem.children):
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", self.format_text(text))
                else:
                    source += "- %s\n" % (self.format_text(text))

                num_children = len(elem.children)
                for i in range(0, num_children):
                    source += self.format_list_child(elem.children[i], indent+self.list_indent_per_level)
            else:
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", self.format_text(text))
                else:
                    source += "- %s\n" % (self.format_text(text))

        return source
    
    def format_list(self, list, ordered=False):

        source = ""

        start = 1
        for elem in list:
            source += self.format_list_child(elem, 0, ordered, start)
            start += 1

        return source
    
    
    def format_table(self, source, table):

        html = '\n'
        
        if(table.has_title()):

            html += "Title: %s\n" % (table.get_title())

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


        for row in table.get_rows():

            is_header = row["is_header"]
            is_subheader = row["is_subheader"]
            is_reserved = row["is_reserved"]

            html += '|'

            if(row["is_caption"]):
                html += "      Caption: %s\n" % (row["cols"][0])
            else: 
                col_num = 0
                for col in row["cols"]:

                    txt = self.format_text(col["text"])
                    
                    if(is_header):
                        html += ("*%s* | ") % (txt)
                    else:
                        html += (" %s | ") % (txt)

                    col_num += 1

            html += "\n"

        #if("caption" in table):
        #    html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])


        html += '\n'
        
        return html

    
    def format_struct(self, source, struct):
        
        html = '''

<sticky>
<table class='tb'>

'''
        
        html += "<tr><th colspan='%d' style='background-color:#444;font-weight:bold;color:white;border:1px solid black;'>%s</th></tr>\n" % (struct.max_cols, struct.name)
        html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (struct.max_cols, struct.description)
       
        ## If the structure has an image associated with it then
        ## display it as part of the HTML describing the structure.
        #if(struct.has_key("image")):

        #    name = struct["image"]["path"]
        #    
        #    # If inlining is turned on then we need to embed the image
        #    # into the generated output HTML file.
        #    if(self.m_inline == True):
        #        handle = open(name, "rb")
        #        name = "data:image/jpeg;base64," + base64.encodestring(handle.read())
        #        handle.close()

        #    
        #    html += "      <td colspan='%d' class='header'>%s</td>\n" % (struct["max_cols"], "Diagram")
        #    html += struct["image"]["map"]
        #    html += "<tr><th colspan='%d' style='border: 1px solid black;padding:10px;'><img src='%s' usemap='#diagram_%s'></img></th></tr>" % (struct["max_cols"], name, struct["image"]["path"])

        i = 0

        for field in struct.fields:
            
            if(i == 0):
                is_header = True
            else:
                is_header = False

            is_reserved = field.get_is_reserved()

            if(field.get_is_reserved()):
                html += "    <tr class='reserved'>\n";
            else:
                html += "    <tr>\n";

            html += "      <td>%s</td>\n" % field.get_type()
            html += "      <td>%s</td>\n" % field.get_name()
            html += "      <td>%s</td>\n" % self.format_textblock(field.get_description())
            
            html += "</tr>\n"

            i+=1
        

        html += '''
</table>
<br/>
</sticky>

'''

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
            tmp = '''---+ %s\n''' % (data.strip())

        elif(tag == "h2"):
            tmp = '''---++ %s\n''' % (data.strip())

        elif(tag == "h3"):
            tmp = '''---+++%s\n''' % (data.strip())
        
        elif(tag == "h4"):
            tmp = '''---++++%s\n''' % (data.strip())

        self.m_contents += tmp
    
    
    def append_source_code(self, tag):

        rc = ''
        rc += self.format_source_code(tag.name, tag.contents)
        result = tag.result

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
        elif(name == "pre"):
            self.m_contents += "<sticky><pre style='margin-left:30px;'>" + self.format_text(tag.contents) + "</pre></sticky>\n"
        elif(name == "note"):
            self.m_contents += self.format_note(self.format_text(tag.contents))
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name == "struct"):
            self.m_contents += self.format_struct(tag.source, tag.contents)
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        #elif(name == "checklist"):
        #    self.m_contents += self.format_checklist(tag)
        #elif(name == "image"):
        #    self.m_contents += self.format_image(tag["contents"])
        else:
            WARNING("Tag %s not supported in template_twiki" % name)

        #elif(name == "prototype"):
        #    self.m_contents += "<sticky>" + self.format_prototype(tag) + "</sticky>"
        #else:
        #    print "Undefined tag: %s [%s]" % (name, tag["source"]); sys.exit(-1)
        

    def get_contents(self):
        
        return self.m_contents
        
    def get_css(self):
        
        css = '''<link rel="stylesheet" type="text/css" media="all" href="css/%s.css" title="Default" />''' % self.m_theme

        theme = self.m_engine.get_theme()

        # Inline the CSS if necessary
        if(self.m_inline == True):
            
            handle = open("%s/%s/%s.css" % (self.m_template_dir, theme, theme), "rt")
            css = handle.read()
            handle.close()

            css = '''
<style>
%s
</style>
''' % css

        return css


    def get_index_name(self):

        return "index.html"

    def generate_index(self, title, theme, version):
        
        cnts = self.get_contents()
        
        file = open(self.m_engine.m_output_directory + "/index.twiki", "w")
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
<sticky>
<style>
span.operator {color: purple;}
span.keyword {color: blue;}
span.string {color: #9933CC;}
span.mstring {color: #9933CC;}
span.comment {color: green;}
span.line_num {color: #C0C0C0;}
table.tb {margin-top: 10px;margin-left: 20px;width:80%;border:1px solid black;border-collapse: collapse;}
td.header{background-color: #ccc;color: black;font-weight: bold;}
td.subheader{background-color: #ddd;color: black;font-weight: bold;}
td.reserved{background-color: #eee;color: #999;}
table.tb td{border: 1px solid black;padding: 5px;}
td.divider{border: 1px solid black;padding: 0px;background-color: #E0E0E0;}
</style>
</sticky>


'''

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".twiki", source_file)
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

