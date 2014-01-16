import re
import os
import string
import sys
from string import Template;
import shutil
import datetime

from src.shorte_defines import *
from template import *


class template_labview_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = ""
        self.m_wikify = False
    
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

    
    def format_source_code(self, language, tags, exclude_wikiwords=[]):

        output = ''
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        line = 1

        output += '<span class="line_num">001&nbsp;&nbsp;</span>'
        
        for tag in tags:

            type = tag["type"]
            source = tag["data"]
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)

            if(type == TAG_TYPE_CODE):
                if(source != ""):
                    source = self.format_keywords(language, source, exclude_wikiwords)
                    output += '<span>%s</span>' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                output += '<span class="comment">%s</span>' % source
            elif(type == TAG_TYPE_WHITESPACE):
                output += '&nbsp;'
            elif(type == TAG_TYPE_STRING):
                output += '<span class="string">%s</span>' % self.wikify(source, exclude_wikiwords)
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'
                line += 1
                output += "<span class='line_num'>%03d&nbsp;&nbsp;</span>" % (line)

        return output
    
    
    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)

        return self.format_image(image)
    
    def _expand_links(self, matches):

        (source, label) = self._process_link(matches)

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
                    output += "<a href='%s#%s'>%s</a>" % (self.get_output_path(link), word, word)
                else:
                    output += word

        return output
    
    def format_text(self, data, allow_wikify=True, exclude_wikify=[]):
        
        # Convert an < and > characters
        #data = re.sub("->", "#", data)
        #data = re.sub("<", "&lt;", data)
        #data = re.sub(">", "&gt;", data)

        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "<br>", data)

        # Hilite any text between [< >] brackets
        hiliter = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        data = hiliter.sub("<font class='hilite'>\\1</font>", data)
       
        # Underline anything in <<<>>> brackets
        hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        data = hiliter.sub("<u>\\1</u>", data)
        
        # First make any links
        data = self._format_links(data)

        # Then insert any images. Make sure to add
        # them to the list of images that need to be
        # copied over.
        data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
        data = re.sub("<<(.*?)>>", self.format_inline_image, data)

        # Now convert any ** to italics
        italics = re.compile("\*\*(.*?)\*\*", re.DOTALL)
        data = italics.sub("<i>\\1</i>", data)
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("<b>\\1</b>", data)

        return data
    
    
    def format_prototype(self, tag):

        
        template = string.Template("""
<html>
<head>
<style>
    span.operator {color: purple;}
    span.keyword {color: blue;}
    span.string {color: #9933CC;}
    span.mstring {color: #9933CC;}
    span.comment {color: green;}
    span.line_num {color: #C0C0C0;}
    
    div.container {font-size:0.8em;margin-left:10px;margin-top:10px;margin-bottom:20px;}
    div.block {margin-left:10px;}
    div.section {color:#396592;font-weight:bold;}
    p {margin-left:10px;margin-top:5px;margin-bottom:5px}
    div.code {margin-left:15px;margin-right:15px;margin-bottom:10px;background-color:#f0f0f0;border:1px solid #ccc;font-family:Courier New;font-size:0.9em;}
    td {font-size:0.8em;}

</style>
<title>${function_name}</title>
</head>
<body>
<div class=container>
<div>
    <div class="block">
        <div class="section">Function:</div>
        <p>${function_name}</p>
    </div>
</div>
<div>
    <div class="block">
        <div class="section">Description:</div>
        <p>${function_desc}</p>
    </div>
</div>
<div>
    <div class="block">
        ${function_prototype}
        ${function_params}
        ${function_returns}
        ${function_example}
        ${function_see_also}
    </div>
</div>
</div>
</body>
</html>
        """)
    
        template_prototype = string.Template("""
        <div>
            <div class="section">Prototype:</div>
            <div class="code">
                ${function_prototype}
            </div>
        </div>
        """);

        template_example = string.Template('''
                <div>
                    <div class="section">Example:</div>
                    <div style="margin-left: 10px; margin-top: 5px;">
                        The following example demonstrates the use of this method:<br><br>
                    </div>
                    <div class="code">
                        ${function_example}
                    </div>
                </div>
            
        ''');
        
        
        template_pseudocode = string.Template('''
                <div>
                    <div class="section">Pseudocode:</div>
                    <div style="margin-left: 10px; margin-top: 5px;">
                        The following pseudocode describes the implementation of this method:<br><br>
                    </div>
                    <div class="code">
                        ${function_pseudocode}
                    </div>
                </div>
            
        ''')
                
        template_returns = string.Template('''
            <div>
                <div class="section">Returns:</div>
                <p>${function_returns}</p>
            </div>
        ''')
        
        template_see_also = string.Template('''
            <div>
                <div class="section">See Also:</div>
                <p>${see_also}</p>
            </div>
        ''')
        
        template_called_by = string.Template('''
            <div>
                <div class="section">Called By:</div>
                <p>${called_by}</p>
            </div>
        ''')
        
        template_calls = string.Template('''
            <div>
                <div class="section">Calls:</div>
                <p>${calls}</p>
            </div>
        ''')
        
        template_params = string.Template('''
        <div>
                    <div class="section">Params:</div>
                    <div style="margin-left: 0px;">
                        <table style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px; border: 0px solid black;">
                            ${function_params}
                        </table>
                    </div>
                </div>
                ''')
        
        prototype = tag["contents"]

        file = "blah"
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["function_prototype"] = ''
        function["function_desc"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''
        function["function_pseudocode"] = ''
        function["function_see_also"] = ''
        function["function_calls"] = ''
        function["function_called_by"] = ''

        if(prototype.has_key("function_desc")):
            function["function_desc"] = self.format_text(prototype["function_desc"])
        
        exclude_wikiwords = []
        exclude_wikiwords.append(function["function_name"])

        if(prototype.has_key("function_prototype")):
            language = prototype["function_prototype"]["language"]
            example = prototype["function_prototype"]["parsed"]

            function["function_prototype"] = self.format_source_code(language, example, exclude_wikiwords)
            function["function_prototype"] = template_prototype.substitute(function)

        if(prototype.has_key("function_params")):
            params = prototype["function_params"]
            
            param_template = string.Template("""
                        <tr style=''>
                            ${type}
                            <td style="vertical-align:text-top;border: 0px;"><b>${param_name}</b></td>
                            <td style="vertical-align:text-top;font-family: Courier New; border: 0px;">(${param_io})</td>
                            <td style="vertical-align:text-top;border: 0px;">-</td>
                            <td style="vertical-align:text-top;border: 0px;">${param_desc}</td>
                        </tr>""")

            output = ''
            for param in params:

                html_tmp = ''
                for val in param["param_desc"]:
                    if(len(val) == 2):
                        html_tmp += '<b>%s</b> = %s<br/>' % (val[0], self.format_text(val[1]))
                    else:
                        html_tmp += self.format_text(val)

                param["param_desc"] = html_tmp

                if(param.has_key("param_type")):
                    param["type"] = '''<td style="vertical-align:text-top;border: 0px;">%s</td>''' % param["param_type"]
                else:
                    param["type"] = ''

                output += param_template.substitute(param)
            
            params = {}
            params["function_params"] = output
            function["function_params"] = template_params.substitute(params)

        if(prototype.has_key("function_returns")):
            function["function_returns"] = template_returns.substitute(prototype)

        if(prototype.has_key("function_example")):

            example = prototype["function_example"]["parsed"]
            language = prototype["function_example"]["language"]

            example = self.format_source_code(language, example, exclude_wikiwords)
            function["function_example"] = example
            function["function_example"] = template_example.substitute(function)
        
        # DEBUG BRAD: This is currently failing so temporarily removed it from
        #             the LabView template.
        #if(prototype.has_key("function_see_also")):
        #    params = {}
        #    params["see_also"] = self.format_text(prototype["function_see_also"])
        #    function["function_see_also"] = template_see_also.substitute(params)
        
        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)
        
        return template.substitute(function)

    def get_parent_hierarchy(self, hierarchy):

        levels = hierarchy.split(":")

        parts = []

        for i in range(0, len(levels)-1):
            parts.append(levels[i])


        return ":".join(parts)
            
    def create_python_snippet(self, function):

        fproto = function["function_prototype"]["parsed"]
        prototype = []
        for t in fproto:
            #print "TAG:", t
            prototype.append(t)

        name = function["function_name"]

        snippet = ""

        # First tag is the return type so we'll strip it off
        return_type = prototype[0]["data"]
        prototype.pop(0)
        prototype.pop(0)

        # Search for the first open bracket
        param_type = ""
        param_name = ""
        STATE_NORMAL = 0
        STATE_PTYPE  = 1
        STATE_PNAME  = 2

        states = []
        states.append(STATE_NORMAL)
        params = []

        while(len(prototype) > 0):
            t = prototype.pop(0)
            state = states[-1]

            if(state == STATE_NORMAL):
                if(t["data"] == "(" or t["data"] == ","):
                    states.append(STATE_PTYPE)
                    param_type = ""
                    param_name = ""

                    # Pop any whitespace
                    while(prototype[0]["data"] == " "):
                        t = prototype.pop(0)

                elif(t["data"] == ")"):
                    break

            elif(state == STATE_PTYPE):
                if(t["data"] == " "):
                    states.append(STATE_PNAME)
                    param_name = ""
                else:
                    param_type += t["data"]

            elif(state == STATE_PNAME):
                #print "In Param name: t=%s" % t["data"]
                if(t["data"] == "," or t["data"] == ")"):
                    #print "t[data] = %s" % t["data"]
                    #print "Do I get here? type = %s, name = %s" % (param_type, param_name)
                    params.append((param_type, param_name))
                    param_type = ""
                    param_name = ""
                    
                    # Pop any trailing whitespace
                    while(prototype[0]["data"] == " "):
                        t = prototype.pop(0)
                    
                    states.pop()

                else:
                    param_name += t["data"]
            
        if(return_type == "cs_status"):
            snippet += "status = "
        elif(return_type == "void"):
            do_nothing = 1
        else:
            snippet += "%s = " % return_type
        
        snippet += name
        snippet += "("

        for param in params:
            typ  = param[0]
            name = param[1]
            snippet += "%s, " % (name)

        if(len(params) > 0):
            # Get rid of the trailing ,
            snippet = snippet[0:len(snippet)-2]
        
        snippet += ")"

        #print snippet
        #sys.exit(-1)

        return snippet


    def get_hierarchy(self):

        tags = self.m_engine.get_function_summary()

        hierarchy = ''
       
        output = ''
        is_first = True

        hierarchies_output = {}

        for tag in tags:

            function = tag["contents"]

            if(not (tag.has_key("hierarchy"))):
                tag["hierarchy"] = tag["source"]

            if(tag["hierarchy"] != hierarchy):
                hierarchy = tag["hierarchy"]

                if(not is_first):
                    output += "- ENDHIERARCHY\n\n\n"

                # If this is a subhierarchy then see if we've output
                # the parent or not
                parent = self.get_parent_hierarchy(hierarchy)

                if(not hierarchies_output.has_key(parent)):
                    if(parent != ""):
                        output += "- HIERARCHY: {%s}\n\n" % parent
                        output += "- ENDHIERARCHY\n\n"
                    hierarchies_output[parent] = 1

                #print("CURRENT = %s, PARENT = %s\n" % (hierarchy,parent))

                is_first = False
                output += "- HIERARCHY: {%s}\n\n" % hierarchy

                hierarchies_output[hierarchy] = 1

            desc = ""
            if(function.has_key("function_desc")):
                desc = function["function_desc"]

            snippet = self.create_python_snippet(function)

            output += "  - FUNCTION: {%s}\n" % function["function_name"]
            output += "      PROTOTYPE: {%s}\n" % function["function_prototype"]["unparsed"]
            output += "      HELP:      {%s.html}\n" % function["function_name"]
            #output += "      DESC:      {%s}\n" % desc
            output += "      SNIPPET:   {%s}\n" % snippet
            output += "      CATEGORY:  {%s}\n" % hierarchy
            output += "      PARENT:    {%s}\n" % parent
            output += "  - ENDFUNCTION\n"
            output += '\n'
                    
        output += "-  ENDHIERARCHY\n\n\n"

        return output
    
    
    def append(self, tag):
        
        name = tag["name"]

        if(name == "prototype"):

            prototype = tag["contents"]
            path = prototype["function_name"]
            path = self.m_engine.get_output_dir() + "/" + path + ".html"
            handle = open(path, "wt")
            handle.write(self.format_prototype(tag))
            handle.close()

    def generate(self, theme, version, package):

        output = self.get_hierarchy()
        handle = open("hierarchy.h", "wt")
        handle.write(output)
        handle.close()


        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()

        page_names = {}
        self.m_contents = ""
        links = []

        for page in pages:

            tags = page["tags"]
            title = page["title"]
            source_file = page["source_file"]

            for tag in tags:

                if(self.m_engine.tag_is_header(tag["name"])):
                    skip = 1
                elif(self.m_engine.tag_is_source_code(tag["name"])):
                    skip = 1
                else:
                    self.append(tag)
            
        print "Generating doc"  

        

