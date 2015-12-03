import re
import os
import string
from string import Template

from src.shorte_defines import *
from template_text import *
import template_html

class template_markdown_t(template_text_t):
    def __init__(self, engine, indexer):
        template_text_t.__init__(self, engine, indexer)

        # Instantiante the HTML template so that we can
        # format advanced objects like structures in a pass-thru
        # fashion
        self.html_template = template_html.template_html_t(engine, indexer)
        
        self.list_indent_per_level=4
        self.m_contents = ''
    
    
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

            if(tag in ("b", "bold")):
                prefix = "**"
                postfix = "**"
            elif(tag in ("i", "italic")):
                replace = replace.strip()
                prefix = "*"
                postfix = "*"
                #, "pre", "u", "i", "color", "span", "cross", "strike", "hl", "hilite", "highlight", "done", "complete", "star", "starred")):
                #pass
            elif(tag == "pre"):
                prefix = "\n\n\n```"
                postfix = "```"

            elif(tag == "strike"):
                prefix = "~~"
                postfix = "~~"

            elif(tag == "br"):
                postfix += "\n"
            elif(tag in "table"):
                table = self.m_engine.m_parser.parse_table(replace, {}, col_separators=['|','!'])
                output = self.format_table(replace, table)
                output = output.replace("\n", "<br/>")
                output = output.replace(" ", "&nbsp;")
                return output

            elif(tag == "quote"):
                textblock = textblock_t(replace)
                tag = tag_t()
                tag.contents = textblock
                return self.format_quote(tag)
                #lines = replace.split("\n")
                #prefix = "\\n"
                #replace = "> ".join(lines)
                #postfix = "\\n"

            ## Embed an inline note. This is useful when documenting
            ## source code.
            #elif(tag in ("note", "warning", "tbd", "question")):
            #    # We've already converted breaks so we need to unconvert them
            #    # to format the note properly.
            #    replace = replace.replace("<br/>", "\n")
            #    replace = replace.replace(" ", "&nbsp;")
            #    textblock = textblock_t(replace)

            #    if(tag == "note"):
            #        label = "Note"
            #    elif(tag == "warning"):
            #        label = "Warning"
            #    elif(tag == "tbd"):
            #        label = "TBD"
            #    elif(tag == "question"):
            #        label = "Question"

            #    return self.format_note(textblock, label)

        return prefix + replace + postfix
    
    def format_define(self, tag):
        html = self.html_template.format_define(tag)
        return """
        
<div>
%s
</div>

""" % (html)

    def format_enum(self, tag):
        html = self.html_template.format_enum(tag)
        return """
        
<div>
%s
</div>

""" % (html)

    def format_prototype(self, tag):
        prototype = tag.contents
        html = self.html_template.format_prototype(tag)

        return """

<div>
%s
</div>

""" % (html)

    def format_struct(self, tag):
        html = self.html_template.format_struct(tag)
        return """

<div>
%s
</div>

""" % (html)
    
    def format_text(self, data):

        if(data == None):
            return
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("\\1", data)

        # Convert any inline styling blocks
        # DEBUG BRAD: Disable inline styling for now
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)

        # Collapse multiple spaces
        #data = re.sub('\n+', "\n", data)
        data = re.sub('<br/>', "\n", data)
        data = re.sub(" +", " ", data)
        data = re.sub("&nbsp;", " ", data)

        # Escape < and >
        #data = re.sub("<", "\\<", data)
        #data = re.sub(">", "\\>", data)

        # Need to escape @ signs since they have special meaning
        # on github
        data = re.sub("@", "*@*", data)

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
    
    def format_table(self, source, table):

        html = '\n'
        
        #if(table.has_title()):
        #    html += "Title: %s\n" % (table.get_title())

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

        for row in table.get_rows():

            is_header = row["is_header"]
            is_subheader = row["is_subheader"]
            is_reserved = row["is_reserved"]
            is_title     = False
            if(row.has_key("is_title")):
                is_title = row["is_title"]

            if(is_title):
                continue

            if(row["is_caption"]):
                #html += "      Caption: %s\n" % (row["cols"][0])
                pass
            else: 
                col_num = 0

                cells = []
                for col in row["cols"]:

                    txt = self.format_text(col["text"])
                    txt = txt.replace("\n", " ")
                    
                    if(is_subheader or is_header):
                        cells.append(("%-" + "%d" % (col_widths[col_num] + 3) + "s") % (txt))
                    else:
                        cells.append((" %-" + "%d" % (col_widths[col_num] + 2) + "s") % (txt))

                html += " |".join(cells)

                col_num += 1

                if(is_header):
                    col_num = 0
                    html += "\n"

                    cells = []
                    for col in row["cols"]:
                        text = ""
                        for k in range(0, col_widths[col_num] + 3):
                            text += "-"

                        for p in range(0, col_num+1):
                            text += "-"

                        col_num += 1

                        cells.append(text)

                    html += "|".join(cells)


            html += "\n"

        #if("caption" in table):
        #    html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])
        
        html += "\n"

        return html

    def format_note(self, tag):
        content = "\n**%s:**\n\n" % tag.name.title()

        lines = tag.source.split("\n")
        for line in lines:
            content += "> " + line + "\n"

        content += "\n"

        return content

    def format_image(self, tag):
        image = tag.contents

        if(image.has_key("height") or image.has_key("width")):
            (image,height,width) = self.m_engine.scale_image(image)

        name = image["name"] + image["ext"]

        caption = name
        if(image.has_key("caption")):
            caption = image["caption"]

        src = os.path.realpath(image["src"])

        content = "\n![%s](%s)\n\n" % (caption,src)

        return content

    def format_quote(self, tag):

        output = "\n"

        tblock = self.format_textblock(tag.contents)
        
        lines = tblock.split("\n")
        for line in lines:
            output += "> %s\n" % line

        output += "\n"

        return output



    def append_header(self, tag, file):

        data = self.format_text(tag.contents)
        tmp = ''
        (level,parent) = self.m_indexer.level(tag, data.strip(), file)
        
        label = data.strip()

        if(tag.name == "h1"):
            tmp = '''# %s\n\n''' % label
        elif(tag.name == "h2"):
            tmp = '''## %s\n\n''' % label
        elif(tag.name == "h3"):
            tmp = '''### %s\n\n''' % label
        elif(tag.name == "h4"):
            tmp = '''#### %s\n\n''' % label
        elif(tag.name == "h5"):
            tmp = '''##### %s\n\n''' % label
        elif(tag.name in ("h","h6")):
            tmp = '''**%s**\n\n''' % label

        self.m_contents += tmp
    
    
    def append_source_code(self, tag):

        self.m_contents += '''

```%s
%s
```

''' % (tag.name, tag.source)

    
    def append(self, tag):
        name = tag.name

        if(name == "#"):
            return
        elif(name == "define"):
            self.m_contents += self.format_define(tag)
        elif(name == "enum"):
            self.m_contents += self.format_enum(tag)
        elif(name == "image"):
            self.m_contents += self.format_image(tag)
        elif(name in ("note", "tbd", "warning", "question")):
            self.m_contents += self.format_note(tag)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        elif(name in "p"):
            self.m_contents += self.format_text(tag.contents) + "\n\n"
        elif(name == "prototype"):
            self.m_contents += self.format_prototype(tag)
        elif(name == "quote"):
            self.m_contents += self.format_quote(tag)
        elif(name == "struct"):
            self.m_contents += self.format_struct(tag)
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        else:
            WARNING("Unsupported tag %s" % name)
    
    def get_index_name(self):
        name = self.m_engine.get_document_name()
        return "%s.md" % name

    def generate_index(self, title, theme, version):
        
        cnts = ''

        if(True == to_boolean(shorte_get_config("markdown", "include_toc"))):
            cnts += '''
# Table of Contents
'''
            for topic in self.m_indexer.m_topics:
                name = topic.get_name()
                indent = topic.get_indent()
                file = os.path.basename(topic.get_file())

                if(True == self.m_inline):
                    file = self.get_index_name()

                link = name.lower()
                link = re.sub(" +", "-", link)

                if(indent == 1):
                    cnts += "- [%s](#%s)\n" % (name,link)
                elif(indent == 2):
                    cnts += "  - [%s](#%s)\n" % (name,link)
                elif(indent == 3):
                    cnts += "    - [%s](#%s)\n" % (name,link)
                elif(indent == 4):
                    cnts += "      - [%s](#%s)\n" % (name,link)
                elif(indent == 5):
                    cnts += "        - [%s](#%s)\n" % (name,link)

            cnts += "\n\n"

        cnts += self.get_contents()
        
        # Strip any redundant blank lines that don't need to be part
        # of the output document
        cnts = self.strip_redundant_blank_lines(cnts)
        
        file = open(self.m_engine.m_output_directory + "/%s" % self.get_index_name(), "wt")
        file.write(cnts)
        file.close()

        return True


    def generate(self, theme, version, package):
        
        self.m_package = package
        self.m_inline = True

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = ''

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".markdown", source_file)
            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag, output_file)

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

        INFO("Generating markdown document")
            
