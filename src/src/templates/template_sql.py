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

template_code = string.Template(
"""
$code_header
<div class='$template'>
$contents
</div>
$source
$result
""")

sql_template_code_header = string.Template(
"""
<div class='code_header' style='width:80%;$style;'>
<span style='text-decoration:none;color:#ccc;' onmouseover="this.style.color='#0000ff';" onmouseout="this.style.color='#ccc';" onclick="e=document.getElementById('snippet_$id');myoperations.display_code(e.innerHTML);">Add to Script</span>
</div>
""")

class template_sql_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_wikify = False

        self.m_prototype_uid = 0
    
    def format_comment(self, data, prefix, start=0):

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)

        # Replace any bold
        data = re.sub(r'\*(.*?)\*', r'\1', data)


        # Collapse any newlines and multiple whitespace
        data = re.sub(r'\n', ' ', data)
        data = re.sub(r' +', ' ', data)
        
        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "\n%s    " % prefix, data)
       
        words = re.split(r' ', data)

        line_length = start
        output = ''

        for word in words:

            output += word + ' '
            line_length += (len(word) + 1)
            
            if(line_length > (80 - len(prefix))):
                line_length = 0
                output += '\n' + prefix

        return output
    
    def _format_desc(self, desc):
    
        desc = self.format_comment(desc, "//|     ")
        return desc
    
    def format_list_child(self, elem, start_tag, end_tag):
        source = ''
        if(elem.children != None):
            if(elem.type in ("checkbox", "action")):
                if(elem.checked):
                    prefix = '<input type="checkbox" checked onclick="return false;"></input>'
                else:
                    prefix = '<input type="checkbox" onclick="return false;"></input>'

                source += "<li>%s %s" % (prefix, self.format_text(elem.get_text()))
            else:
                source += "<li>%s" % self.format_text(elem.get_text())
            
            num_children = len(elem.children)
            source += start_tag
            #print "num_children = %d" % num_children
            for i in range(0, num_children):
                source += self.format_list_child(elem.children[i], start_tag, end_tag)
            source += "%s</li>" % (end_tag)
        else:
            if(elem.type in ("checkbox", "status")):
                if(elem.checked):
                    prefix = "<input type='checkbox' checked onclick='return false;'></input>"
                else:
                    prefix = "<input type='checkbox' onclick='return false;'></input>"
                source += "<li>%s " % prefix + self.format_text(elem.get_text()) + "</li>"
            else:
                source += "<li>" + self.format_text(elem.get_text()) + "</li>"

        return source
    
    def format_list(self, list, ordered=False, indent=0):

        if(indent != 0):
            style = " style='margin-left:%d;' " % indent*10
        else:
            style = ""

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
    
    def format_textblock(self, tag, standalone=True):
        '''This method is called to format a block of text
within an HTML document.

@param tag        [I] = The tag to parse, usually a dictionary object
@param standalone [I] = Is the block of text standalone or is it embedded
                        within another element like a table?
'''

        if(isinstance(tag, tag_t)):
            paragraphs = tag.contents
        else:
            paragraphs = tag

        html = ''

        if(is_array(paragraphs)):
            for p in paragraphs:
                indent  = p["indent"]
                text    = p["text"]
                is_code = p["code"]
                is_list = p["list"]

                #print "Indent: [%d], text: [%s]" % (indent, text)

                if(is_code):
                    if(standalone):
                        style = "margin-left:%dpx;background-color:#eee;" % (20)
                    else:
                        style = "margin-left:%dpx;background-color:#eee;border:1px solid #ccc;" % (0)
                else:
                    if(standalone):
                        style = "margin-left:%dpx;" % (20 + (indent * 6))
                    else:
                        style = "margin-left:%dpx;" % ((indent * 6))

                if(is_code):
                    html += "<div class='code' style='%s'><div class='snippet' style='white-space:pre'>" % style + self.format_text(text) + "</div></div>\n"
                elif(is_list):
                    html += self.format_list(p["text"], False, indent)
                else:
                    if(standalone):
                        html += "<div style='margin-left:20px;margin-bottom:10px;font-size:1.0em;%s'>" % style + self.format_text(text, expand_equals_block=True) + "</div>\n"
                    else:
                        html += "<div style='margin-left:0px;padding:0px;margin-bottom:3px;font-size:1.0em;%s'>" % style + self.format_text(text, expand_equals_block=True) + "</div>\n"
        else:
            if(standalone):
                html += "<div style='margin-left:20px;margin-bottom:10px;font-size:1.0em;'>" + self.format_text(paragraphs, expand_equals_block=True) + "</div>\n"
            else:
                html += "<div style='margin-left:0px;padding:0px;margin-bottom:3px;font-size:1.0em;'>" + self.format_text(paragraphs, expand_equals_block=True) + "</div>\n"
            
        html = re.sub("'", "&apos;", html)

        return html

    def format_keywords(self, language, source, exclude_wikiwords=[]):

        keywords = self.m_engine.get_keyword_list(language)

        output = ''
        keyword = ''
        pos_start = 0

        source = re.sub('\n', '', source)

        for i in range(0, len(source)):

            c = source[i]

            if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) < 122) or (ord(c) == 95)):
                keyword += c 
            else:
                if(keyword != ''):

                    #print "  keyword1: {%s}" % keyword
                    #print "  substr:   {%s}" % source[pos_start:i]
                    if(keywords.has_key(keyword)):
                        #output += source[pos_start:i]
                        output += "<span class='keyword'><b>%s</b></span>" % keyword
                    else:
                        output += self.wikify(keyword, exclude_wikiwords)

                    keyword = ''
                
                pos_start = i+1
                output += "%c" % c


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                #output += source[pos_start:i]
                output += "<span class='keyword'><b>%s</b></span>" % keyword
            else:
                output += self.wikify(keyword, exclude_wikiwords)
            #print "  keyword2 = %s" % keyword

        #print "output = %s\n" % output

        return output

    def sqlize(self, text):
        text.replace('\n', '<br/>')
        apos = re.compile("'")
        text = apos.sub('&apos;', text)
        return text

    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_nums=True):

        output = ''
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        show_div = True

        line = 1
        
        if(show_div):

            if(show_line_nums):
                output += "<div class='snippet' style='white-space:pre'>"
            else:
                output += "<div class='snippet' style='white-space:pre-wrap'>"

        if(show_line_nums):
            output += '<span class="ln">001  </span>'
        
        for tag in tags:

            type = tag["type"]
            source = tag["data"]
            
            if(type in (TAG_TYPE_COMMENT, TAG_TYPE_MCOMMENT)):
                source = source.replace("->", "#")

            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)
            source = re.sub("\n", "", source)
            #source = source.strip()

            if(type == TAG_TYPE_CODE):
                if(source != ""):
                    source = self.format_keywords(language, source, exclude_wikiwords)
                    #output += '<span>%s</span>' % source
                    output += '%s' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                source = self._format_links(source)
                if(self.allow_wikify_comments()):
                    source = self.wikify(source, exclude_wikiwords)
                output += '<span class="cmt">%s</span>' % source

            elif(type == TAG_TYPE_WHITESPACE):
                #output += '&nbsp;'
                output += ' '
            elif(type == TAG_TYPE_STRING):
                output += '<span class="str">%s</span>' % self.wikify(source, exclude_wikiwords)
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'
                line += 1
                #output += "<span class='line_num'>%03d&nbsp;&nbsp;</span>" % (line)

                if(show_line_nums):
                    output += "<span class='ln'>%03d  </span>" % (line)
            else:
                print "Skipping tag %s" % source
                self.exit(-1)

        if(show_div):
            output += "</div>"


        return output
    
    
    
    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)

        return self.format_image(image)
    
    def _expand_links(self, matches):

        (source, label) = self._process_link(matches)

        #print "_expand_links: source=%s,label=%s" % (source,label)
        return "<a href='%s'>%s</a>" % (source, label)
    
    def _format_links(self, data):
           
        # Expand any links
        expr = re.compile("\[\[(.*?)\]\]", re.DOTALL)
        data = expr.sub(self._expand_links, data)

        return data
    
    def wikify(self, data, exclude = []):

        if(not self.m_wikify):
            return data

        words = []
        word = ''

        for i in data:

            if(i == ',' or i == ';' or i == '\n' or i == ' ' or i == '(' or i == ')' or i == '*'):

                words.append(word)
                words.append(i)

                word = ''

            else:
                word += i

        if(len(word) > 0):
            words.append(word)

        output = ''
        for word in words:

            if(word == ',' or word == ';' or word == '\n' or word == ' ' or word == '(' or word == ')' or word == '*'):
                output += word 
            else:

                link = None

                exclude_word = False
                for tmp in exclude:
                    if(tmp == word):
                        exclude_word = True
                        break

                if(not exclude_word):
                    link = self.m_engine.is_wiki_word(word)

                if(link != None):
                    tmp = "<a href='%s#%s'>%s</a>" % (self.get_output_path(link), word, word)
                    #print "WIKIWORD: %s" % tmp
                    output += tmp
                else:
                    #print "HERE I AM: %s" % word
                    output += word

        return output
    
    def format_text(self, data, allow_wikify=True, exclude_wikify=[], expand_equals_block=False):
        if(data == None):
            return

        if(len(data) != 0):
            data = re.sub("'", "&apos;", data)
            return data

        # Convert an < and > characters
        #data = re.sub("->", "#", data)
        #data = re.sub("<", "&lt;", data)
        #data = re.sub(">", "&gt;", data)
        data = trim_blank_lines(data)

        #print "DATA: [%s]" % data

        # Strip trailing lines

        data = re.sub("\n\s*\n", "<br/><br/>", data)

        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "<br/>", data)

        if(expand_equals_block):
            data = re.sub("==+", "<div style='style=float:left; width:20%;border-top:1px solid #ccc;height:1px;'></div>", data)
        
        # Hilite any text between **** ****
        hiliter = re.compile("\*\*\*\*(.*?)\*\*\*\*", re.DOTALL)
        data = hiliter.sub("<font class='hilite'>\\1</font>", data)

        # Underline any text between __ __
        hiliter = re.compile("__(.*?)__", re.DOTALL)
        data = hiliter.sub("<u>\\1</u>", data)

        # DEBUG BRAD: Oldy Syntax
        #     Underline anything in <<<>>> brackets
        #     hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        #     data = hiliter.sub("<u>\\1</u>", data)
        
        # First make any links or references
        data = self._format_links(data)

        # Then insert any images. Make sure to add
        # them to the list of images that need to be
        # copied over.
        data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
        data = re.sub("<<(.*?)>>", self.format_inline_image, data)

        # DEBUG BRAD: Old syntax
        #    # Now convert any ** to italics
        #    italics = re.compile("\*\*(.*?)\*\*", re.DOTALL)
        #    data = italics.sub("<i>\\1</i>", data)
        #    
        #    # Now convert any *phrase* to bold
        #    bold = re.compile("\*(.*?)\*", re.DOTALL)
        #    data = bold.sub("<b>\\1</b>", data)

        # New syntax
        italics = re.compile("\/\/(.*?)\/\/", re.DOTALL)
        data = italics.sub("<i>\\1</i>", data)
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*\*(.*?)\*\*", re.DOTALL)
        data = bold.sub("<b>\\1</b>", data)

        ## Convert any inline styling blocks
        #expr = re.compile("@\{(.*?)\}", re.DOTALL)
        #data = expr.sub(self.parse_inline_styling, data)
        
        if(allow_wikify):
            data = self.wikify(data)
        
        # Escape for SQL
        if(len(data) != 0):
            data = re.sub("'", "&apos;", data)

        return data
    
    
    def format_prototype(self, tag):

        self.m_prototype_uid += 1
        template = string.Template("INSERT INTO Types (id, type, name, description, help) VALUES ('%d', 'method', '${name}', '${desc}', '${help}');\n" % self.m_prototype_uid);
        
        html = template_html.template_html_t(self.m_engine, self.m_indexer)
        html.set_template_code_header(sql_template_code_header)
        html.m_wikiword_path_prefix = False
        help = html.format_prototype(tag)
        
        prototype = tag.contents

        function = {}
        function["name"] = prototype["name"]
        function["desc"] = ''
        function["help"] = self.sqlize(help)
        
        if(prototype.has_key("desc")):
            function["desc"] = self.format_text(prototype["desc"])
        
        sql = template.substitute(function)

        if(prototype.has_key("params")):
            params = prototype["params"]
            
            for param in params:
                
                if(not param.has_key('type')):
                    param["type"] = ''

                if(not param.has_key('desc')):
                    param["desc"] = ''
                
                param_desc = ''
                for val in param["desc"]:
                    if(len(val) == 2):
                        param_desc += '<b>%s</b> = %s<br/>' % (val[0], self.format_text(val[1]))
                        #param_desc += 'tbd' self.format_text(val[1])
                    else:
                        param_desc += self.format_text(val)

                #print "DESC: ", param["param_desc"]

                param["desc"] = param_desc

                sql += string.Template("INSERT INTO Params (belongs_to, name, type, description) VALUES ('%d', '${name}', '${type}', '${desc}');\n" % self.m_prototype_uid).substitute(param);

                #for val in param["param_desc"]:
                #    if(len(val) == 2):
                #        html_tmp += '<b>%s</b> = %s<br/>' % (val[0], self.format_text(val[1]))
                #    else:
                #        html_tmp += self.format_text(val)

                #param["param_desc"] = html_tmp

                #if(param.has_key("param_type")):
                #    param["type"] = '''<td style="vertical-align:text-top;border: 0px;">%s</td>''' % param["param_type"]
                #else:
                #    param["type"] = ''

                #output += param_template.substitute(param)
        
        return sql

    def format_struct(self, tag):
        self.m_prototype_uid += 1
        template = string.Template("INSERT INTO Types (id, type, name, description, help) VALUES ('%d', 'struct', '${name}', '${desc}', '${help}');\n" % self.m_prototype_uid);

        html = template_html.template_html_t(self.m_engine, self.m_indexer)
        html.m_wikiword_path_prefix = False
        help = html.format_struct(tag.source, tag.contents)
        
        obj = tag.contents

        struct = {}
        struct["name"] = obj["title"]
        struct["desc"] = ''
        struct["help"] = self.sqlize(help)
        
        if(obj.has_key("caption")):
            struct["desc"] = self.format_textblock(obj["caption"])
        
        sql = template.substitute(struct)

        # Add the structure fields
        if(obj.has_key('fields')):
            for field in obj['fields']:

                if(field["attrs"][1].has_key("textblock")):
                    name = field["attrs"][1]["textblock"][0]['text'].strip()
                else:
                    name = field["attrs"][1]["text"].strip()
                
                if(field["attrs"][2].has_key("textblock")):
                    desc = self.format_textblock(field["attrs"][2]["textblock"])
                else:
                    desc = field["attrs"][2]["text"].strip()
                
                sql += string.Template("INSERT INTO Params (belongs_to, name, type, description) VALUES ('${belongs_to}', '${name}', '', '${desc}');\n").substitute(
                        {"belongs_to" : self.m_prototype_uid,
                         "name" : name,
                         "desc" : desc})

        return sql
        
    def format_enum(self, tag):
        self.m_prototype_uid += 1
        template = string.Template("INSERT INTO Types (id, type, name, description, help) VALUES ('%d', 'enum', '${name}', '${desc}', '${help}');\n" % self.m_prototype_uid);

        html = template_html.template_html_t(self.m_engine, self.m_indexer)
        html.m_wikiword_path_prefix = False
        help = html.format_enum(tag)

        #print "HELP [%s]" % help
        
        obj = tag.contents

        enum = {}
        enum["name"] = obj["title"]
        enum["desc"] = ''
        enum["help"] = self.sqlize(help)
        
        if(obj.has_key("caption")):
            enum["desc"] = self.format_textblock(obj["caption"])
        
        sql = template.substitute(enum)
        
        # Add the enum values
        i = 0
        for row in obj["rows"]:
            if i == 0:
                i += 1
                continue
            
            cols = row["cols"]

            enum = cols[0]["text"]

            #print "i = %d, VAL = %s" % (i, cols[1]["text"])
            #val  = int(cols[1]["text"], 16)
            desc = self.format_text(cols[2]["text"])
        
            sql += string.Template("INSERT INTO Params (belongs_to, name, type, description) VALUES ('${belongs_to}', '${name}', '', '${desc}');\n").substitute(
                    {"belongs_to" : self.m_prototype_uid,
                     "name" : enum,
                     "desc" : desc})

        return sql


    def append(self, tag):
        
        name = tag.name
        sql = ''

        if(name == "prototype"):
            sql += self.format_prototype(tag)
        elif(name == "struct"):
            sql += self.format_struct(tag)
        elif(name == "enum"):
            sql += self.format_enum(tag)

        return sql

    def generate(self, theme, version, package):

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()

        page_names = {}
        self.m_contents = ""
        links = []
        sql = '''
BEGIN TRANSACTION;
CREATE TABLE Types
(
    id INTEGER AUTO_INCREMENT,
    type TEXT,
    name TEXT,
    description TEXT,
    help TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE Params
(
    id INTEGER AUTO_INCREMENT,
    belongs_to INTEGER,
    type TEXT,
    name TEXT,
    description TEXT,
    PRIMARY KEY(id)
);

'''

        for page in pages:

            tags = page["tags"]
            title = page["title"]
            source_file = page["source_file"]

            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    skip = 1
                elif(self.m_engine.tag_is_source_code(tag.name)):
                    skip = 1
                else:
                    sql += self.append(tag)
	
	sql += '''END TRANSACTION;'''
         
        file = open(self.m_engine.m_output_directory + "/apis.sql", "w")
        file.write(sql)
        file.close()
        
        print "Generating doc"  

        

