import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from src.shorte_defines import *
from template import *

code_template = string.Template(
"""
$contents

Result:
=======
$result
""")

code_template_no_result = string.Template(
"""
$contents
""")


class template_text_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_theme = ""
        self.m_template_dir = shorte_get_startup_path() + "/templates/text/"
        self.m_inline = False

    
    def format_source_code(self, language, tags):

        output = ''
        line = 1

        output += '001: '
        
        i = 0
        for tag in tags:

            type   = tag["type"]
            source = tag["data"]
        
            if(type == TAG_TYPE_CODE):
                if(source != ""):
                    output += '%s' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                output += '%s' % source
            elif(type == TAG_TYPE_WHITESPACE):
                output += ' '
            elif(type == TAG_TYPE_STRING):
                output += source
            elif(type == TAG_TYPE_NEWLINE):
                output += '\n'
                line += 1

                # If there are any more tags then output the next line
                if(i < (len(tags)-1)):
                    output += "%03d: " % (line)

            i += 1

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
    def format_note(self, tag, label="NOTE:"):

        content = self.format_textblock(tag)
        lines = content.split('\n')
        output_lines = []
        for line in lines:
            output_lines.append("  %s" % line)

        output = '\n'.join(output_lines)

        return '''
%s
-----
%s
''' % (label,output)
            
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

        if(ordered):
            if(elem.has_key("children")):
                if(indent > 0):
                    source += "%*s%s. %s\n" % (indent, " ", start, elem["text"])
                else:
                    source += "%s. %s\n" % (start, elem["text"])

                num_children = len(elem["children"])
                
                is_num = False
                is_char = False

                if(not ((indent/4) & 0x1)):
                    start = ord("a")
                    is_char = True
                else:
                    start = 1
                    is_num = True

                for i in range(0, num_children):
                    if(is_num):
                        source += self.format_list_child(elem["children"][i], indent+4, ordered, start)
                    else:
                        source += self.format_list_child(elem["children"][i], indent+4, ordered, chr(start))
                    start += 1
            else:
                if(indent > 0):
                    source += "%*s%s. %s\n" % (indent, " ", start, elem["text"])
                else:
                    source += "%s. %s\n" % (start, elem["text"])
        else:
            if(elem.has_key("children")):
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", elem["text"])
                else:
                    source += "- %s\n" % (elem["text"])

                num_children = len(elem["children"])
                for i in range(0, num_children):
                    source += self.format_list_child(elem["children"][i], indent+4)
            else:
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", elem["text"])
                else:
                    source += "- %s\n" % (elem["text"])

        return source
    
    def format_list(self, list, ordered=False):

        source = ""

        start = 1
        for elem in list:
            source += self.format_list_child(elem, 0, ordered, start)
            start += 1

        return source
    
    
    def format_textblock(self, tag):

        paragraphs = tag["contents"]
        output = ''

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
                output += text + "\n"

        return output

    def format_questions(self, tag):

        questions = tag["contents"]

        output = "\n"
        for question in questions:

            output += "Q: "
            output += self.format_text(question["question"]) + "\n"

            if(question["answer"] != ""):
                output += "A: "
                output += self.format_text(question["answer"]) + "\n"

            output += "\n"

        return output

    
    
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
    def format_prototype(self, tag):
        
        template = string.Template("""
        <div style='margin-left:30px;border:1px solid #ccc;'>
        <div>
            <div style="margin-left: 10px;">
                <div style="color: #396592; font-weight: bold;">Function:</div>
                <p style="margin-left:10px;margin-top:5px;margin-bottom:5px;">${function_name}</p>
            </div>
        </div>
        <div>
            <div style="margin-left: 10px;">
                <div style="color: #396592; font-weight: bold;">Description:</div>
                <p style="margin-left:10px;margin-top:5px;margin-bottom:5px;">${function_desc}</p>
            </div>
        </div>
        <div style="font-size: 0.9em;">
            <div style="margin-left: 10px; margin-top: 10px;">
                ${function_prototype}
                
                <div>
                    <div style="color: #396592; font-weight: bold;">Params:</div>
                    <div style="margin-left: 0px;">
                        <table style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px; border: 0px;">
                            ${function_params}
                        </table>
                    </div>
                </div>
                
                <div>
                    <div style="color: #396592; font-weight: bold;">Returns:</div>
                    <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${function_returns}</p>
                </div>

                ${function_example}
                
            </div>
            
        </div>
        </div>
        """)
    
        template_prototype = string.Template("""
        <div>
            <div style="color: #396592; font-weight: bold;">Prototype:</div>
            <div style="font-family: courier;padding:10px;">
                ${function_prototype}
            </div>
        </div>
        """);

        template_example = string.Template('''
                <div>
                    <div style="color: #396592; font-weight: bold;">Example:</div>
                    <div style="margin-left: 10px; margin-top: 5px;">
                        The following example demonstrates the use of this method:<br><br>
                    </div>
                    <div style="margin-left: 15px; margin-right:15px; margin-bottom:10px; background-color:#f0f0f0; border:1px solid #ccc;">
                        ${function_example}
                    </div>
                </div>
            
        ''');
        
        prototype = tag["contents"]
        
        file = "blah"
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["function_prototype"] = ''
        function["function_desc"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''

        if(prototype.has_key("function_desc")):
            function["function_desc"] = prototype["function_desc"]

        if(prototype.has_key("function_prototype")):
            function["function_prototype"] = template_prototype.substitute(prototype)

        if(prototype.has_key("function_params")):
            params = prototype["function_params"]
            
            param_template = string.Template("""
                        <tr>
                            <td style="border: 0px;"><b>${param_name}</b></td>
                            <td style="font-family: courier; border: 0px;">${param_io}</td>
                            <td style="border: 0px;">-</td>
                            <td style="border: 0px;">${param_desc}</td>
                        </tr>""")

            output = ''
            for param in params:

                output += param_template.substitute(param)

            function["function_params"] = output

        if(prototype.has_key("function_returns")):
            function["function_returns"] = prototype["function_returns"]

        if(prototype.has_key("function_example")):

            example = prototype["function_example"]["parsed"]
            language = prototype["function_example"]["language"]

            example = self.format_source_code(language, example)
            function["function_example"] = example
            function["function_example"] = template_example.substitute(function)


        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)
        
        return template.substitute(function)
    
    

    
    def format_table(self, source, table):

        html = '\n'
        
        if("title" in table):

            html += "Title: %s\n" % (table["title"])

        num_cols = table["max_cols"]
        col_widths = []

        # First walk through the text and figure out the
        # maximum width of each column
        for i in range(0, num_cols):
            col_widths.append(0)

        for row in table["rows"]:

            j = 0;
            for col in row["cols"]:
                
                if(len(col["text"]) > col_widths[j]):
                    col_widths[j] = len(col["text"])
                j += 1


        for row in table["rows"]:

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
                    
                    if(is_subheader):
                        html += ("%-" + "%d" % (col_widths[col_num] + 3) + "s | ") % (txt)
                    else:
                        html += (" %-" + "%d" % (col_widths[col_num] + 2) + "s | ") % (txt)

                    col_num += 1

                if(is_header):
                    col_num = 0
                    html += "\n"
                    for col in row["cols"]:

                        html += "-"

                        for k in range(0, col_widths[col_num] + 3):
                            html += "-"

                        for p in range(0, col_num+1):
                            html += "-"

                        col_num += 1


            html += "\n"

        #if("caption" in table):
        #    html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])


        html += '\n'
        
        return html

    
    def format_struct(self, source, struct):
        
        html = "<table class='tb'>\n"
        
        if("title" in struct):
            html += "<tr><th colspan='%d' style='background-color:#444;font-weight:bold;color:white;border:1px solid black;'>%s</th></tr>\n" % (struct["max_cols"], struct["title"])
       
        # If the structure has an image associated with it then
        # display it as part of the HTML describing the structure.
        if(struct.has_key("image")):

            name = struct["image"]["path"]
            
            # If inlining is turned on then we need to embed the image
            # into the generated output HTML file.
            if(self.m_inline == True):
                handle = open(name, "rb")
                name = "data:image/jpeg;base64," + base64.encodestring(handle.read())
                handle.close()

            
            html += "      <td colspan='%d' class='header'>%s</td>\n" % (struct["max_cols"], "Diagram")
            html += struct["image"]["map"]
            html += "<tr><th colspan='%d' style='border: 1px solid black;padding:10px;'><img src='%s' usemap='#diagram_%s'></img></th></tr>" % (struct["max_cols"], name, struct["image"]["path"])

        i = 0

        for field in struct["fields"]:
            
            if(i == 0):
                is_header = True
            else:
                is_header = False

            is_reserved = field["is_reserved"]

            if(is_header):
                html += "    <tr class='header'>\n";
            else:
                html += "<tr>\n"
            
            for attr in field["attrs"]:

                attr = self.format_text(attr)

                if(is_header):
                    html += "      <td colspan='%d' class='header'>%s</td>\n" % (1, attr)
                elif(is_reserved):
                    html += "      <td colspan='%d' style='background-color:#eee; color:#999;'>%s</td>\n" % (1, attr)
                else:
                    html += "      <td colspan='%d'>%s</td>\n" % (1, attr)
            
            html += "</tr>\n"

            i+=1
        
        if("caption" in struct):
            html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (struct["max_cols"], struct["caption"])

        html += "</table><br/>"




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
            name = "data:image/jpeg;base64," + base64.encodestring(handle.read())
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

    def format_text(self, data):

        if(data == None):
            return

        # Collapse multiple spaces
        data = re.sub('\n', " ", data)
        data = re.sub(" +", " ", data)

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)
       
        words = re.split(r' ', data)

        line_length = 0
        output = ''

        for word in words:

            output += word + ' '
            line_length += (len(word) + 1)
            
            if(line_length > 80):
                line_length = 0
                output += '\n'

        return output


    def append_header(self, tag, data, file):

        data = self.format_text(data)
        header_char = '='
        tmp = ''
        
        if(tag == "h1"):
            tmp = '''\n%s %s\n''' % (self.m_indexer.level1(tag, data.strip(), file) + ". " , data.strip())
            header_char = '='

        elif(tag == "h2"):
            tmp = '''\n%s %s\n''' % (self.m_indexer.level2(tag, data.strip(), file) + ". " , data.strip())
            header_char = '-'

        elif(tag == "h3"):
            tmp = '''\n%s %s\n''' % (self.m_indexer.level3(tag, data.strip(), file) + ". " , data.strip())
            header_char = ''
        
        elif(tag == "h4"):
            tmp = '''\n%s %s\n''' % (self.m_indexer.level4(tag, data.strip(), file) + ". " , data.strip())
            header_char = ''

        print "HEADER: %s" % tmp

        length = len(tmp)
        header = ''

        for i in range(0, length - 1):
            header += header_char
        header += "\n"

        self.m_contents += tmp + header
    
    
    def append_source_code(self, tag):

        rc = ''
        rc += self.format_source_code(tag["name"], tag["contents"])
        result = tag["result"]

        if(result != None):
            self.m_contents += code_template.substitute(
                    {"contents" : rc,
                     "result"   : result});
        else:
            self.m_contents += code_template_no_result.substitute(
                    {"contents" : rc})

    
    def append(self, tag):
        
        name = tag["name"]

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_contents += self.format_text(tag["contents"]) + "\n"
        elif(name == "pre"):
            self.m_contents += self.format_text(tag["contents"]) + "\n"
        elif(name == "note"):
            self.m_contents += self.format_note(tag, "NOTE:")
        elif(name == "tbd"):
            self.m_contents += self.format_note(tag, "TBD:")
        elif(name == "table"):
            self.m_contents += self.format_table(tag["source"], tag["contents"])
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        #elif(name == "struct"):
        #    self.m_contents += self.format_struct(tag["source"], tag["contents"])
        elif(name == "ul"):
            self.m_contents += self.format_list(tag["contents"], False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag["contents"], True)
        elif(name == "questions"):
            self.m_contents += self.format_questions(tag)

        #elif(name == "checklist"):
        #    self.m_contents += self.format_checklist(tag)
        #elif(name == "image"):
        #    self.m_contents += self.format_image(tag["contents"])
        #elif(name == "prototype"):
        #    self.m_contents += self.format_prototype(tag)
        else:
            print "Undefined tag: %s [%s]" % (name, tag["source"]); sys.exit(-1)
        

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
        
        cnts = '''
Table of Contents
=================
'''

        for topic in self.m_indexer.m_topics:

            name = topic.m_vars["name"]
            indent = topic.m_vars["indent"]
            file = os.path.basename(topic.m_vars["file"])

            # If the HTML is being inlined then we need to
            # make sure that all links point back to the
            # main document.
            if(self.m_inline == True):
                file = "index.txt"
            
            #print "indent = %s" % indent

            if(indent == 1):
                cnts += "  %s\n" % (name)
            elif(indent == 2):
                cnts += "    - %s\n" % (name)
            elif(indent == 3):
                cnts += "      - %s\n" % (name)
            elif(indent == 4):
                cnts += "        %s\n" % (name)
            elif(indent == 5):
                cnts += "          %s\n" % (name)

        # If we're inlining everything we need to store the
        # entire document in the index file
        if(self.m_inline == True):
            cnts += "\n\n" + self.get_contents()

        #contents = html.substitute(
        #    {"title" : title,
        #     "contents" : cnts,
        #     "rightmenu" : "",
        #     "src" : "",
        #     "date" : datetime.date.today(),
        #     "version" : version,
        #     "css" : self.get_css()})
        
        file = open(self.m_engine.m_output_directory + "/index.txt", "w")
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
        self.m_contents = ""

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".txt", source_file)
            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                if(self.m_engine.tag_is_header(tag["name"])):
                    self.append_header(tag["name"], tag["contents"], output_file)

                elif(self.m_engine.tag_is_source_code(tag["name"])):
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

