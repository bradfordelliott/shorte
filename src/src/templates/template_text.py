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

        output += ' 001: '
        
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
                    output += " %03d: " % (line)

            i += 1

        return output


    def format_note(self, tag, label="NOTE"):
        '''This method is called to format a note tag.
           
           @param tag   [I] - The tag note object.
           @param label [I] - The label to associate with the note (could
                              also be something like a warning or a TBD)

           @return The formatted note object
        '''

        content = self.format_textblock(tag)
        lines = content.split('\n')
        output_lines = []
        for line in lines:
            output_lines.append("  %s" % line)

        output = '\n'.join(output_lines)

        label_underline = '-'
        for i in range(0, len(label)):
            label_underline += '-'

        return '''%s:
%s
%s
''' % (label,label_underline,output)

    def format_define(self, tag):
        define = tag.contents

        return '''Define: %s
Value:
    %s
Description:
%s
''' % (define.name, define.value, self.format_textblock(define.description, prefix='    '))

    def format_enum(self, tag):
        enum = tag.contents

        return '''Enum: %s
Values:
    %s
Description:
%s
''' % (enum.name, "TBD", self.format_textblock(enum.description, prefix='    '))

    def format_checklist(self, tag):
        
        list = tag.contents

        source = ''

        if(tag.modifiers.has_key("title")):
            source += "<p style='font-weight:bold;text-decoration:underline;'>%s</p>" % tag.modifiers["title"] 

        source += "<ul style='list-style-type:none'>"

        for elem in list:
            caption = ''
            if(elem.has_key("caption")):
                caption = " <span style='color:#999;font-style:italic;'>(%s)</span>" % elem["caption"]

            source += "<li><input type='checkbox' name='%s' %s/>%s%s</li>" % (elem["name"], elem["checked"], elem["name"], caption)

        source += "</ul>"

        if(tag.modifiers.has_key("caption")):
            source += "<p style='font-style:italic;margin-left:40px;'>Caption: %s</p>" % tag.modifiers["title"] 

        return source

    def parse_inline_styling(self, matches):
        data = matches.groups()[0].strip()
        #print "DATA: [%s]" % data
        #print "data: %s" % data
        parts = data.split(",")
        if(len(parts) == 1):
            tag = parts[0]
            replace = tag
        elif(len(parts) > 1):
            tag = parts[0]
            replace = ''.join(parts[1:])

        replace = trim_leading_blank_lines(replace)
        #print "TAG: %s, REPLACE: %s" % (tag,replace)
        
        if(-1 != tag.find("+")):
            tags = tag.split("+")
        else:
            tags = [tag]

        prefix = ''
        postfix = ''

        for tag in tags:
            # Check if it's an inline styling block such as color
            #   @{color:00ff00,my text here}
            if(-1 != tag.find(":")):
                parts = tag.split(":")
                tag = parts[0].strip()
                parts.pop(0)
                qualifier = ":".join(parts)

            if(tag in ("b", "bold", "pre", "u", "i", "color", "span", "cross", "strike", "hl", "hilite", "highlight", "done", "complete", "star", "starred")):
                pass
            elif(tag == "br"):
                postfix += "\n"
            elif(tag in "table"):
                table = self.m_engine.m_parser.parse_table(replace, {}, col_separators=['|','!'])
                output = self.format_table(replace, table)
                output = output.replace("\n", "<br/>")
                output = output.replace(" ", "&nbsp;")
                return output

            # Embed an inline note. This is useful when documenting
            # source code.
            elif(tag in ("note", "warning", "tbd", "question")):
                # We've already converted breaks so we need to unconvert them
                # to format the note properly.
                replace = replace.replace("<br/>", "\n")
                replace = replace.replace(" ", "&nbsp;")
                textblock = self.m_engine.m_parser.parse_textblock(replace)

                if(tag == "note"):
                    label = "Note"
                elif(tag == "warning"):
                    label = "Warning"
                elif(tag == "tbd"):
                    label = "TBD"
                elif(tag == "question"):
                    label = "Question"

                return self.format_note(textblock, label)

        return prefix + replace + postfix

        #data = matches.groups()[0].strip()
        #parts = data.split(",")
        #if(len(parts) == 1):
        #    tag = parts[0]
        #    replace = tag
        #elif(len(parts) > 1):
        #    tag = parts[0]
        #    replace = ''.join(parts[1:])
        #
        #return replace
    
    def format_list_child(self, elem, indent, ordered=False, start=0):
        source = ''

        if(ordered):
            if(elem.children != None):
                if(indent > 0):
                    source += "%*s%s. %s\n" % (indent, " ", start, self.format_text(elem.text))
                else:
                    source += "%s. %s\n" % (start, self.format_text(elem.text))

                num_children = len(elem.children)
                
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
                        source += self.format_list_child(elem.children[i], indent+4, ordered, start)
                    else:
                        source += self.format_list_child(elem.children[i], indent+4, ordered, chr(start))
                    start += 1
            else:
                if(indent > 0):
                    source += "%*s%s. %s\n" % (indent, " ", start, self.format_text(elem.text))
                else:
                    source += "%s. %s\n" % (start, self.format_text(elem.text))
        else:
            if(elem.children):
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", self.format_text(elem.text))
                else:
                    source += "- %s\n" % (self.format_text(elem.text))

                num_children = len(elem.children)
                for i in range(0, num_children):
                    source += self.format_list_child(elem.children[i], indent+4)
            else:
                if(indent > 0):
                    source += "%*s- %s\n" % (indent, " ", self.format_text(elem.text))
                else:
                    source += "- %s\n" % (self.format_text(elem.text))

        return source
    
    def format_list(self, list, ordered=False):

        source = "\n"

        start = 1
        for elem in list:
            source += self.format_list_child(elem, 0, ordered, start)
            start += 1

        return source
    
    
    def format_textblock(self, tag, prefix='', prefix_first_line=True, pad_textblock=False):

        if(isinstance(tag, tag_t)):
            paragraphs = tag.contents
        else:
            paragraphs = tag
        
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

        return output

    def format_questions(self, tag):

        questions = tag.contents

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
        
        if(table.has_title()):

            html += "Title: %s\n" % (table.get_title())

        num_cols = table.get_max_cols()
        col_widths = []

        # First walk through the text and figure out the
        # maximum width of each column
        for i in range(0, num_cols):
            col_widths.append(0)

        max_width = 0
        for row in table.get_rows():

            j = 0;
            for col in row["cols"]:
                
                if(len(col["text"]) > col_widths[j]):
                    col_widths[j] = len(col["text"])
                    max_width += col_widths[j]
                j += 1

        # Add a table header
        html += "+"
        for i in range(0, max_width+1):
            html += "-"
        html += "+\n"


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
                    txt = txt.replace("\n", " ")
                    
                    if(is_subheader):
                        html += ("%-" + "%d" % (col_widths[col_num] + 3) + "s | ") % (txt)
                    else:
                        html += (" %-" + "%d" % (col_widths[col_num] + 2) + "s | ") % (txt)

                    col_num += 1

                if(is_header):
                    col_num = 0
                    html += "\n"
                    for col in row["cols"]:

                        html += "+"

                        for k in range(0, col_widths[col_num] + 3):
                            html += "-"

                        for p in range(0, col_num+1):
                            html += "-"

                        col_num += 1

                    html += "+"


            html += "\n"

        #if("caption" in table):
        #    html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])
        
        # Add a table footer
        html += "+"
        for i in range(0, max_width+1):
            html += "-"
        html += "+\n"

        return html

    
    def format_struct(self, tag):

        struct = tag.contents

        i = 0
        fields = ''
        for field in struct.get_fields():
            
            fields += "| %2d | %20s | %s" % (field.width, field.name, self.format_textblock(field.desc, prefix="|    |                      | ", prefix_first_line=False))
            
            i+=1

        output = string.Template('''
+-----------------------------------------------------------------------------
| Structure: $name
|
${desc}|
+-----------------------------------------------------------------------------
| Fields:
+-----------------------------------------------------------------------------
${fields}+-----------------------------------------------------------------------------
''').substitute({"name" : struct.get_name(),
                 "desc" : self.format_textblock(struct.get_description(), "|  "),
                 "fields" : fields})

        return output

        
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
     
    def convert_image(self, image):
        from PIL import Image
        import random
        from bisect import bisect
         
        # greyscale.. the following strings represent
        # 7 tonal ranges, from lighter to darker.
        # for a given pixel tonal level, choose a character
        # at random from that range.
         
        greyscale = [
                    " ",
                    " ",
                    ".,-",
                    "_ivc=!/|\\~",
                    "gjez2]/(YL)t[+T7Vf",
                    "mdK4ZGbNDXY5P*Q",
                    "W8KMA",
                    "#%$"
                    ]
        #greyscale = [
        #            " ",
        #            " ",
        #            ".",
        #            "=",
        #            "+",
        #            "*",
        #            "8",
        #            "#"
        #            ]
         
        # using the bisect class to put luminosity values
        # in various ranges.
        # these are the luminosity cut-off points for each
        # of the 7 tonal levels. At the moment, these are 7 bands
        # of even width, but they could be changed to boost
        # contrast or change gamma, for example.
         
        zonebounds=[36,72,108,144,180,216,252]
         
        # open image and resize
        # experiment with aspect ratios according to font
         
        im=Image.open(image)
        im=im.resize((160, 75),Image.BILINEAR)
        im=im.convert("L") # convert to mono
         
        # now, work our way over the pixels
        # build up str
         
        str=""
        for y in range(0,im.size[1]):
            for x in range(0,im.size[0]):
                lum=255-im.getpixel((x,y))
                row=bisect(zonebounds,lum)
                possibles=greyscale[row]
                str=str+possibles[random.randint(0,len(possibles)-1)]
            str=str+"\n"
         
        return str


    def format_image(self, tag):

        image = tag.contents

        name = image["name"] + image["ext"]
        
        return "\nImage:\n  see " + name
    
    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)

        return self.format_image(image)

    def format_text(self, data):

        if(data == None):
            return
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("\\1", data)

        # Convert any inline styling blocks
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)

        # Collapse multiple spaces
        data = re.sub('\n+', "\n", data)
        data = re.sub('<br/>', "\n", data)
        data = re.sub(" +", " ", data)
        data = re.sub("&nbsp;", " ", data)

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)

        output = data
       
        #words = re.split(r' ', data)

        #line_length = 0
        #output = ''

        #for word in words:

        #    output += word + ' '
        #    line_length += (len(word) + 1)
        #    
        #    if(line_length > 80):
        #        line_length = 0
        #        output += '\n'

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
            header_char = '-'
        
        elif(tag == "h4"):
            tmp = '''\n%s %s\n''' % (self.m_indexer.level4(tag, data.strip(), file) + ". " , data.strip())
            header_char = '-'

        length = len(tmp)
        header = ''

        for i in range(0, length - 1):
            header += header_char
        header += "\n"

        self.m_contents += tmp + header
    
    
    def append_source_code(self, tag):

        rc = ''
        rc += self.format_source_code(tag.name, tag.contents)
        result = tag.result

        if(result != None):
            self.m_contents += code_template.substitute(
                    {"contents" : rc,
                     "result"   : result});
        else:
            self.m_contents += code_template_no_result.substitute(
                    {"contents" : rc})

    
    def append(self, tag):
        
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_contents += self.format_text(tag.contents) + "\n"
        elif(name == "pre"):
            self.m_contents += self.format_text(tag.contents) + "\n"
        elif(name == "note"):
            self.m_contents += self.format_note(tag, "NOTE")
        elif(name == "warning"):
            self.m_contents += self.format_note(tag, "WARNING")
        elif(name == "tbd"):
            self.m_contents += self.format_note(tag, "TBD")
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        elif(name == "struct"):
            self.m_contents += self.format_struct(tag)
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        elif(name == "questions"):
            self.m_contents += self.format_questions(tag)
        elif(name == "image"):
            self.m_contents += self.format_image(tag)
        elif(name == "define"):
            self.m_contents += self.format_define(tag)
        elif(name == "enum"):
            self.m_contents += self.format_enum(tag)

        #elif(name == "checklist"):
        #    self.m_contents += self.format_checklist(tag)
        #elif(name == "image"):
        #    self.m_contents += self.format_image(tag["contents"])
        #elif(name == "prototype"):
        #    self.m_contents += self.format_prototype(tag)
        elif(name in ("functionsummary", "typesummary")):
            WARNING("Unsupported tag %s" % name)
        elif(name in ("struct", "prototype")):
            WARNING("Unsupported tag %s" % name)
        else:
            FATAL("Undefined tag: %s [%s]" % (name, tag.source))
        

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

        #return "index.txt"
        name = self.m_engine.get_document_name()
        return "%s.txt" % name

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
                file = self.get_index_name()
            
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
        
        file = open(self.m_engine.m_output_directory + "/%s" % self.get_index_name(), "wt")
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

        INFO("Generating text document")

