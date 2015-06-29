import re
import os
import string
from string import Template

from src.shorte_defines import *
from template import *

class template_markdown_t(template_t):
    def __init__(self, engine, indexer):
        template_t.__init__(self, engine, indexer)
        self.m_contents = ''
    
    def format_text(self, data):

        if(data == None):
            return
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("\\1", data)

        # Convert any inline styling blocks
        # DEBUG BRAD: Disable inline styling for now
        #expr = re.compile("@\{(.*?)\}", re.DOTALL)
        #data = expr.sub(self.parse_inline_styling, data)

        # Collapse multiple spaces
        data = re.sub('\n+', "\n", data)
        data = re.sub('<br/>', "\n", data)
        data = re.sub(" +", " ", data)
        data = re.sub("&nbsp;", " ", data)

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

                if(not ((indent/2) & 0x1)):
                    start = ord("a")
                    is_char = True
                else:
                    start = 1
                    is_num = True

                for i in range(0, num_children):
                    if(is_num):
                        source += self.format_list_child(elem.children[i], indent+2, ordered, start)
                    else:
                        source += self.format_list_child(elem.children[i], indent+2, ordered, chr(start))
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
                    source += self.format_list_child(elem.children[i], indent+2)
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
    def append_header(self, tag, file):

        data = self.format_text(tag.contents)
        tmp = ''
        (level,parent) = self.m_indexer.level(tag, data.strip(), file)
        
        if(tag.name == "h1"):
            tmp = '''# %s\n''' % data.strip()
        elif(tag.name == "h2"):
            tmp = '''## %s\n''' % data.strip()
        elif(tag.name == "h3"):
            tmp = '''### %s\n''' % data.strip()
        elif(tag.name == "h4"):
            tmp = '''#### %s\n''' % data.strip()
        elif(tag.name == "h5"):
            tmp = '''##### %s\n''' % data.strip()
        elif(tag.name in ("h","h6")):
            tmp = '''###### %s\n''' % data.strip()

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
        elif(name in "p"):
            self.m_contents += self.format_text(tag.contents) + "\n"
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        else:
            WARNING("Unsupported tag %s" % name)
    
    def get_index_name(self):
        name = self.m_engine.get_document_name()
        return "%s.markdown.txt" % name

    def generate_index(self, title, theme, version):
        cnts = '''
# Table of Contents
'''

        for topic in self.m_indexer.m_topics:
            name = topic.get_name()
            indent = topic.get_indent()
            file = os.path.basename(topic.get_file())

            if(True == self.m_inline):
                file = self.get_index_name()

            if(indent == 1):
                cnts += "- %s\n" % (name)
            elif(indent == 2):
                cnts += "  - %s\n" % (name)
            elif(indent == 3):
                cnts += "    - %s\n" % (name)
            elif(indent == 4):
                cnts += "      - %s\n" % (name)
            elif(indent == 5):
                cnts += "        - %s\n" % (name)

        if(True == self.m_inline):
            cnts += "\n\n" + self.get_contents()
        
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
            
