# -*- coding: iso-8859-15 -*-
import re
import os
import string
from string import Template;

from src.shorte_defines import *
from template import *

EOL = "\r\n"

HEADING_DEFAULT = 0
HEADING1 = 1
HEADING2 = 2
HEADING3 = 3
HEADING4 = 4


class template_word_t(template_t):

    def __init__(self, engine, indexer):

        template_t.__init__(self, engine, indexer)
   
        self.m_sections = []
        section = {}
        headings = []
        section["Headings"] = headings
        self.m_sections.append(section)

        # DEBUG BRAD: Add a fake heading in case the
        # document doesn't start with a header tag.
        heading = {}
        heading["Title"] = ""
        heading["Type"] = HEADING_DEFAULT 
        heading["Content"] = ""
        self.m_headptr = heading["Content"]
        self.m_header_id = 0
        self.m_sections[0]["Headings"].append(heading)

        self.m_image_id = 3

        self.m_wikify = True

    def get_index_name(self):
        return "%s.doc" % self.m_engine.get_document_name()
    
    def append_page(self, pages, title, source_file):

        return ""

    def append_header(self, tag, data, file):

        data = self.format_text(data)

        if(tag == "h1"):
            
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING1
            heading["Content"] = ""
            self.m_headptr = heading["Content"]
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)

        elif(tag == "h2"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING2
            heading["Content"] = ""
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
        
        elif(tag == "h3"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING3
            heading["Content"] = ""
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
        
        elif(tag == "h4"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING4
            heading["Content"] = ""
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
    
    def append_source_code(self, tag):

        output = ''

        output += self.format_source_code(tag.name, tag.contents)
        result = tag.result

        if(result != None):
            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            ws = re.compile(" ")
            nl = re.compile("\\\\n")

            result = lt.sub("&lt;", result)
            result = gt.sub("&gt;", result)
            result = nl.sub("__NEWLINE__", result)
        
            output += self.format_bold("Result:")
            output += self.format_pre(result)
        
        self.m_sections[0]["Headings"][self.m_header_id]["Content"] += output
 
    def _expand_links(self, matches):

        (source, label, external) = self._process_link(matches)

        return '''</w:t></w:r><w:hlink w:dest=\"%s\">
            <w:r>
              <w:rPr>
                <w:rStyle w:val="Hyperlink"/>
              </w:rPr>
              <w:t>%s</w:t>
            </w:r>
          </w:hlink><w:r><w:t>''' % (source, label)

    def _format_links(self, data):
        
        # Expand any links
        expr = re.compile("\[\[(.*?)\]\]", re.DOTALL)
        data = expr.sub(self._expand_links, data)

        return data

    def format_image(self, image, within_text=True):
        
        # Check to see if the image requires conversion such as
        # is the case with inkscape SVG files
        if(image.has_key("converter")):
            image = self.m_engine.convert_image(image)

        data = encode_image(image["src"])
        style = ""

        # DEBUG BRAD: Should use the PIL module to figure out the
        #             dimentions of the image and insert them into
        #             the document. Otherwise the images get inserted
        #             as small images
        if(image.has_key("width")):
            style += "width:%s;" % image["width"]
        else:
            style += "width:600px;"

        if(image.has_key("height")):
            style += "height:%s;" % image["height"]
        else:
            style += "height:463px;"

        if(style != ""):
            style = "style=\"%s\"" % style

        #print "STYLE = [%s]" % style

        if(within_text):
            data = """
</w:t></w:r></w:p><w:p>
    <w:r>
        <w:pict>
            <w:binData w:name="wordml://%d.png" xml:space="preserve">%s</w:binData>
            <v:shape id="%s" %s>
                <v:imagedata src="wordml://%d.png"/>
            </v:shape>
        </w:pict>
    </w:r>
</w:p><w:p><w:r><w:t>
""" % (self.m_image_id, data, self.m_image_id, style, self.m_image_id)
        else:
            data = """
<w:p>
    <w:r>
        <w:pict>
            <w:binData w:name="wordml://%d.png" xml:space="preserve">%s</w:binData>
            <v:shape id="%s" %s>
                <v:imagedata src="wordml://%d.png"/>
            </v:shape>
        </w:pict>
    </w:r>
</w:p>
""" % (self.m_image_id, data, self.m_image_id, style, self.m_image_id)
        self.m_image_id += 1

        return data


    def format_inline_image(self, matches):
        
        image = self.m_engine.m_parser.parse_inline_image(matches)

        return self.format_image(image)


    def format_text(self, data):

        if(data == None):
            return

        data = self.xmlize(data)
        
        # Collapse multiple spaces
        data = re.sub('\n', " ", data)
        data = re.sub(" +", " ", data)

        # Escape any backslashes
        data = data.replace("\\", "\\\\")

        # Trim leading and trailing and multiple whitespace
        data = data.strip()
            
        # First make any links
        data = self._format_links(data)
       
        # Now convert any [[[phrase]]] to highlighted text
        highlight = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        data = highlight.sub("</w:t></w:r><w:r><w:rPr><w:b/><w:highlight w:val=\"yellow\"/></w:rPr><w:t>\\1</w:t></w:r><w:r><w:t>", data)
        
        # Underline anything in <<<>>> brackets
        hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        data = hiliter.sub("\\1", data)
                   
        # Now convert any ** to italics
        italics = re.compile("\*\*(.*?)\*\*")
        data = italics.sub("</w:t></w:r><w:r><w:rPr><w:i/></w:rPr><w:t>\\1</w:t></w:r><w:r><w:t>", data)
          
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*")
        data = bold.sub("</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>\\1</w:t></w:r><w:r><w:t>", data)

        data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
        data = re.sub("<<(.*?)>>", self.format_inline_image, data)

        #print "DATA: [%s]" % data

        return "<w:r><w:t>%s</w:t></w:r>" % data

    
    def format_struct(self, source, struct):    

        xml = '''
<w:tbl>
  <w:tblPr>
    <w:tblW w:w="0" w:type="auto"/>
    <w:tblInd w:w="558" w:type="dxa"/>
    <w:tblBorders>
      <w:top w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:left w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:bottom w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:right w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:insideH w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:insideV w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
    </w:tblBorders>
    <w:tblLook w:val="04A0"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="4735"/>
    <w:gridCol w:w="4726"/>
  </w:tblGrid>
'''

        xml += '''
            <w:tr>
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="4778" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:rPr>
                          <w:b/>
                      </w:rPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    <w:r><w:t>Type</w:t></w:r>
                  </w:p>
                </w:tc>
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="4778" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:rPr>
                          <w:b/>
                      </w:rPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    <w:r><w:t>Name</w:t></w:r>
                  </w:p>
                </w:tc>
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="4778" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:rPr>
                          <w:b/>
                      </w:rPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    <w:r><w:t>Description</w:t></w:r>
                  </w:p>
                </w:tc>
            </w:tr>
'''

        for field in struct.fields:

            xml += "    <w:tr>\n";
            
            col_width = 4788

            parts = [field.get_type(), field.get_name(), self.format_textblock(field.get_description())]
            
            is_reserved = field.get_is_reserved()
                    
            for part in parts:
                xml += '''
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="%d" w:type="dxa"/>
                    <!--<w:shd w:val="clear" w:color="auto" w:fill="D0D0D0"/>-->
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    %s
                  </w:p>
                </w:tc>
''' % (col_width, part)

            xml += "</w:tr>\n"
                        
        xml += "</w:tbl>"

        return xml
    
            
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    format_table()
    #|
    #| DESCRIPTION:
    #|    This method is called to format the contents of a table and generate
    #|    the XML output necessary for inserting into the word document.
    #| 
    #| PARAMETERS:
    #|    source (I) - The input table source to parse. 
    #| 
    #| RETURNS:
    #|    None.
    #|
    #+-----------------------------------------------------------------------------
    def format_table(self, source, table, format_text=True):    
        
        xml = '''
<w:tbl>
  <w:tblPr>
    <w:tblW w:w="0" w:type="auto"/>
    <w:tblInd w:w="558" w:type="dxa"/>
    <w:tblBorders>
      <w:top w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:left w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:bottom w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:right w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:insideH w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
      <w:insideV w:val="single" w:sz="4" wx:bdrwidth="10" w:space="0" w:color="000000"/>
    </w:tblBorders>
    <w:tblLook w:val="04A0"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="4735"/>
    <w:gridCol w:w="4726"/>
  </w:tblGrid>
'''

        for row in table.get_rows():

            xml += "    <w:tr>\n";
            
            col_width = 4788

            is_header = False
            is_subheader = False
            is_caption = False

            if(row["is_header"]):
                is_header = True

            for col in row["cols"]:
            
                if(is_header):
                    xml += '''
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="%d" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:rPr>
                          <w:b/>
                      </w:rPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    %s
                  </w:p>
                </w:tc>
''' % (col_width, self.format_text(col["text"]))

                elif(is_subheader):
                    xml += '''
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="%d" w:type="dxa"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    %s
                  </w:p>
                </w:tc>
''' % (col_width, self.format_text(col["text"]))
                        
                elif(is_caption):
                    xml += '''
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="%d" w:type="dxa"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    %s
                  </w:p>
                </w:tc>
''' % (col_width, self.format_text(col["text"]))
                else:
                    xml += '''
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="%d" w:type="dxa"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr>
                      <w:ind w:left="0"/>
                    </w:pPr>
                    %s
                  </w:p>
                </w:tc>
''' % (col_width, self.format_text(col["text"]))

            xml += "</w:tr>\n"
                        
        xml += "</w:tbl>"

        return xml

    
    def format_note(self, source):
        
        source = self.format_text(source)

        xml = '''
<w:p>
   <w:r>
   <w:rPr>
     <w:b/>
   </w:rPr>
   <w:t>Note:</w:t>
   </w:r>
</w:p>
<w:p>
   <w:pPr>
     <w:pStyle w:val="Note"/>
   </w:pPr>
   %s
</w:p>
''' % source

        return xml

        
    
    

    def format_bold(self, input):

        xml = '''<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>%s</w:t></w:r></w:p>''' % input

        return xml
        
    def format_pre(self, input):
        
        xml = ''

        lines = input.split("\n")
       
        for line in lines:

            xml += '''<w:p><w:pPr><w:pStyle w:val="Code"/></w:pPr><w:r><w:t>%s</w:t></w:r></w:p>''' % line

        return xml

    def format_textblock(self, tag, wrap=True):

        if(isinstance(tag, tag_t)):
            paragraphs = tag.contents
        else:
            paragraphs = tag

        xml = ''
        
        for p in paragraphs:
            indent = p["indent"]
            text = p["text"]
            is_code = p["code"]
            is_list = p["list"]

            if(is_code):
                xml += self.format_pre(text)
                blah = ""
            elif(is_list):
                xml += self.format_list(p["text"], False)
                blah = ""
            else:
                if(wrap):
                    xml += "<w:p>%s</w:p>" % self.format_text(text)
                else:
                    xml += "%s" % self.format_text(text)

        
        return xml

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
                        output += '</w:t></w:r><w:r><w:rPr><w:color w:val="0000ff"/></w:rPr><w:t>%s</w:t></w:r><w:r><w:t>' % keyword
                    else:
                        output += keyword

                    keyword = ''
                
                pos_start = i+1
                output += "%c" % c


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                output += '</w:t></w:r><w:r><w:rPr><w:color w:val="0000ff"/></w:rPr><w:t>%s</w:t></w:r><w:r><w:t>' % keyword
            else:
                output += keyword

        return output


    def format_list_child(self, elem, level):

        source = ''
        if(elem.children != None):
            source += '''
<w:p>
   <w:pPr>
     <w:pStyle w:val="BodyText"/>
     <w:listPr>
       <w:ilvl w:val="%d"/>
       <w:ilfo w:val="9"/>
       <wx:t wx:val="·"/>
       <wx:font wx:val="Symbol"/>
     </w:listPr>
   </w:pPr>
   <w:r>
    <w:t>%s</w:t>
   </w:r>
</w:p>''' % (level, elem.get_text())
            
            num_children = len(elem.children)
            for i in range(0, num_children):
                source += self.format_list_child(elem.children[i], level+1) 
            
        else:
            source += '''
<w:p>
   <w:pPr>
     <w:pStyle w:val="BodyText"/>
     <w:listPr>
       <w:ilvl w:val="%d"/>
       <w:ilfo w:val="9"/>
       <wx:t wx:val="·"/>
       <wx:font wx:val="Symbol"/>
     </w:listPr>
   </w:pPr>
   <w:r>
    <w:t>%s</w:t>
   </w:r>
</w:p>
'''% (level, self.format_text(elem.get_text()))

        return source


    def format_list(self, list, ordered=False):

        source = ""

        for elem in list:
            source += self.format_list_child(elem, 0)

        return source


    def format_checklist(self, tag):

        source = ""

        list = tag["contents"]

        for elem in list:

            source += '''
<w:p>
   <w:pPr>
     <w:pStyle w:val="BodyText"/>
     <w:listPr>
       <w:ilvl w:val="0"/>
       <w:ilfo w:val="9"/>
       <wx:t wx:val="·"/>
       <wx:font wx:val="Symbol"/>
     </w:listPr>
   </w:pPr>
   <w:r>
    <w:t>%s</w:t>
   </w:r>
</w:p>
'''% elem["name"]

        return source
    
    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_numbers=True, show_frame=True):

        output = ''

        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        line = 1

        output = ''
        
        if(show_frame):
            output = '''
<w:p>
<w:pPr>
    <w:pStyle w:val="Code"/>
</w:pPr>'''

        if(show_line_numbers):
            output += '<w:r><w:rPr><w:color w:val="C0C0C0"/></w:rPr><w:t>%04d </w:t></w:r>' % line
        
        for tag in tags:

            type = tag["type"]
            source = tag["data"]
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)
        
            # DEBUG BRAD: Can't get a direct replacement
            # with \\\\n to work because the INSERT_CONTENTS_HERE
            # replacement hangs in generate_index() so we'll do
            # an indirect replacement of \n with __NEWLINE__
            # and then replace that again later
            source = nl.sub("__NEWLINE__", source)

            if(type == TAG_TYPE_CODE):
                source = self.format_keywords(language, source)
                output += '<w:r><w:t>%s</w:t></w:r>' % source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                output += '<w:r><w:rPr><w:color w:val="00B050"/></w:rPr><w:t>%s</w:t></w:r>' % source
            elif(type == TAG_TYPE_WHITESPACE):
                output += '<w:r><w:t> </w:t></w:r>'
            elif(type == TAG_TYPE_STRING):
                output += '<w:r><w:rPr><w:color w:val="B0B050"/></w:rPr><w:t>%s</w:t></w:r>' % source
            elif(type == TAG_TYPE_NEWLINE):
                output += '</w:p><w:p><w:pPr><w:pStyle w:val="Code"/></w:pPr>\n'
                line += 1
        
                if(show_line_numbers):
                    output += '<w:r><w:rPr><w:color w:val="C0C0C0"/></w:rPr><w:t>%04d </w:t></w:r>' % line

        if(show_frame):
            output += "</w:p>"

        return output
    
    
    def format_prototype(self, tag):
        
        xml = '''
<w:p>
<w:pPr>
    <w:pStyle w:val="Code"/>
</w:pPr>'''

        prototype = tag.contents
        
        file = "blah"
        function = {}
        function["function_name"] = self.format_text(prototype.get_name())
        function["function_example"] = ''
        function["function_pseudocode"] = ''
        function["function_prototype"] = ''
        function["function_desc"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''
        function["function_see_also"] = ''

        function["function_desc"] = self.format_textblock(prototype.get_description())

        if(prototype.has_prototype()):
            function["function_prototype"] = prototype.get_prototype()

        if(prototype.has_params()):
            params = prototype.get_params()

            table = {}
            table["max_cols"] = 4 
            table["rows"] = []

            param_template = string.Template("""
                        <text:p text:style-name="prototype_indent">
                            <text:span text:style-name="prototype_param_name">${name}</text:span>
                            <text:span>${io}</text:span>
                            <text:span>-</text:span>
                            <text:span>${desc}</text:span>
                        </text:p>
                        """)

            output = ''
            for p in params:
            
                param = {}
                param["name"] = p.get_name()
                if(p.has_io()):
                    param['io']   = p.get_io()
                else:
                    param['io'] = ''
                param["desc"] = p.get_description()

                output += param_template.substitute(param)

            function["function_params"] = output
            #function["function_params"] = self.format_table("", table)
            
            #print "output = %s" % output

        if(prototype.has_returns()):
        
            xml = '''
<text:p text:style-name="prototype">
    <text:span text:style-name="prototype_bold">Returns:</text:span>
</text:p>
<text:p text:style-name="prototype_indent">
    %s
</text:p>
''' % prototype.get_returns()

            function["function_returns"] = xml

        if(prototype.has_see_also()):
            xml = '''
<text:p text:style-name="prototype">
    <text:span text:style-name="prototype_bold">See Also:</text:span>
</text:p>
<text:p text:style-name="prototype_indent">
    %s
</text:p>
''' % self.format_text(prototype.get_see_also())

            function["function_see_also"] = xml

        if(prototype.has_example()):

            language = prototype.get_example().get_language()
            example  = prototype.get_example().get_parsed()

            example = self.format_source_code(language, example)
        
            xml = '''
<text:p text:style-name="prototype">
    <text:span text:style-name="prototype_bold">Example:</text:span>
</text:p>
<text:p text:style-name="prototype_indent">
    The following example demonstrates the use of this method:\n
</text:p>
%s
''' % example

            function["function_example"] = xml
        
        
        if(prototype.has_pseudocode()):

            language = prototype.get_pseudocode().get_language()
            example  = prototype.get_pseudocode().get_parsed()
            example = self.format_source_code(language, example)
        
            xml = '''
<text:p text:style-name="prototype">
    <text:span text:style-name="prototype_bold">Pseudocode:</text:span>
</text:p>
<text:p text:style-name="prototype_indent">
    The following pseudocode describes the implementation of this method:\n
</text:p>
%s
''' % example

            function["function_pseudocode"] = xml


        topic = topic_t({"name"   : prototype.get_name(),
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)

        draw_box = 0 # int(self.m_engine.get_config("odt", "prototype_draw_box"))
        
        template = string.Template("""
$box_start
        <w:p><w:r><w:t></w:t></w:r></w:p>

        <w:p><w:r><w:rPr><w:color w:val="B0B050"/><w:b/></w:rPr><w:t>Function:</w:t></w:r></w:p>
        <w:p>
           <w:pPr><w:pStyle w:val="BodyTextIndent"/></w:pPr>
           <w:r>${function_name}</w:r>
        </w:p>
        
        <w:p><w:r><w:rPr><w:color w:val="B0B050"/><w:b/></w:rPr><w:t>Description:</w:t></w:r></w:p>
        <w:p>
           <w:pPr><w:pStyle w:val="BodyTextIndent"/></w:pPr>
           <w:r>${function_desc}</w:r>
        </w:p>
        
        <w:p><w:r><w:rPr><w:color w:val="B0B050"/><w:b/></w:rPr><w:t>Prototype:</w:t></w:r></w:p>
        <w:p>
           <w:r><w:t>TBD</w:t></w:r>
        </w:p>
        
        <w:p><w:r><w:rPr><w:color w:val="B0B050"/><w:b/></w:rPr><w:t>Params:</w:t></w:r></w:p>
        <w:p>
           <w:r><w:t>TBD</w:t></w:r>
        </w:p>

$box_end
""")

        function["box_start"] = ''
        function["box_end"] = ''

        xml = template.substitute(function)

        return xml

    def format_wikiword(self, link, link_word, label, is_bookmark):
        '''This method is called to format a wikiword. It is called by
           the wikify method in the template base class'''
        
        
        return '''</w:t></w:r><w:hlink w:dest=\"%s\">
            <w:r>
              <w:rPr>
                <w:rStyle w:val="Hyperlink"/>
              </w:rPr>
              <w:t>%s</w:t>
            </w:r>
          </w:hlink><w:r><w:t>
''' % (link, label)

    
    def htmlize_prototype(self, input_prototype):

        # Make copy of list before modifying it so
        # we don't permanently change it
        prototype = []
        for t in input_prototype:
            prototype.append(t)

        # First tag is the return type so we'll strip it off
        return_type = prototype[0]
        prototype.pop(0)
        prototype.pop(0)

        rt = return_type["data"]
        
        if(return_type["data"] == "const"):
            rt += " " + prototype[0]["data"]
            prototype.pop(0)
            prototype.pop(0)

        prototype = self.format_source_code("c", prototype, [], False, False)
        return (self.wikify(rt), prototype)
    
    def format_function_summary(self, tag):

        tags = self.m_engine.get_function_summary(tag)

        table = {}
        #table["title"] = "Function Summary"
        table["caption"] = "Function Summary"
        table["max_cols"] = 2
        table["column-styles"] = ["shorte_type_summary_col1", "shorte_type_summary_col2"]
        table["rows"] = []

        hierarchy = ''
        
        for tag in tags:

            function = tag["contents"]

            style = "" # self.m_styles["table"]["cell"]["fhier"]

            if(tag["hierarchy"] != hierarchy):
                hierarchy = tag["hierarchy"]
                row = self._table_row()

                cols = []
                cols.append({"span":2, 'text': hierarchy, "style": style})
                row["cols"] = cols
                table["rows"].append(row)

            row = self._table_row()

            cols = []
            name = function["function_name"]
            tmp = function["function_prototype"].get_parsed()
            (returns, prototype) = self.htmlize_prototype(tmp)
            #print prototype
            
            style = "" # self.m_styles["table"]["cell"]["fname"]
            text_style = "" # self.m_styles["para"]["fdesc"]
            cols.append({"span":1, 'text':returns,   "style": style, "text-style": text_style})
            cols.append({"span":1, 'text':prototype, "style": style})
            row["cols"] = cols
            table["rows"].append(row)

            row = self._table_row()
            cols = []

            style = "" # self.m_styles["table"]["cell"]["fdesc"]
            cols.append({"span":1, 'text':'', "style": style})

            text_style = "" # self.m_styles["para"]["fdesc"]
            function_desc = ''
            if(function.has_key("function_desc")):
                function_desc = function["function_desc"]
            cols.append({"span":1, 'text':function_desc, "style": style, "text-style": text_style})

            row["cols"] = cols

            table["rows"].append(row)

        return self.format_table("", table, False)
   
    
    def format_type_summary(self, tag):

        tags = self.m_engine.get_types_summary(tag)

        table = {}
        #table["title"] = "Type Summary"
        table["caption"] = "Type Summary"
        table["max_cols"] = 2
        table["column-styles"] = ["shorte_type_summary_col1", "shorte_type_summary_col2"]
        table["rows"] = []

        hierarchy = ''
        
        for tag in tags:

            struct = tag.contents

            if(tag.hierarchy != hierarchy):
                hierarchy = tag.hierarchy
                row = self._table_row()
                cols = []
                style = "" # self.m_styles["table"]["cell"]["fhier"]
                cols.append({"span":2, 'text': hierarchy, "style": style})
                row["cols"] = cols
                table["rows"].append(row)

            row = self._table_row()

            cols = []

            name = ''
            if(struct.has_key("title")):
                name = struct["title"]
            text = self.wikify(name)

            style = "" # self.m_styles["table"]["cell"]["fname"]
            text_style = "" # self.m_styles["para"]["fdesc"]
            text_style_code = "" # self.m_styles["para"]["code2"]

            cols.append({"span":1, 'text':tag["name"], "style": style, "text-style": text_style})
            cols.append({"span":1, 'text':text, "style" : style, "text-style": text_style_code})
            row["cols"] = cols
            table["rows"].append(row)


            row = self._table_row()
            cols = []

            style = "" # self.m_styles["table"]["cell"]["fdesc"]
            cols.append({"span":1, 'text':'', "style": style})

            desc = ''
            if(struct.has_key("caption")):
                desc = struct["caption"]
            text_style = "" # self.m_styles["para"]["fdesc"]
            cols.append({"span":1, 'text':desc, "style": style, "text-style": text_style})

            row["cols"] = cols

            table["rows"].append(row)

        return self.format_table("", table, False)

    
    def format_sequence(self, tag):

        image = tag.contents
        output = self.format_image(image, False)
        output += self.format_table("", tag.contents["html"])

        return output

    def append(self, tag):
        
        name = tag.name

        if(name == "#"):
            return
        if(name in "p"):
            data = self.format_text(tag.contents)
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += "<w:p>%s</w:p>" % data
        elif(name == "text"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_textblock(tag)
        elif(name == "pre"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_pre(tag.contents)
        elif(name == "note"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(tag.contents)
        elif(name == "table"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_table(tag.source, tag.contents)
        elif(name == "ul"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag.contents, True)
        elif(name == "checklist"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_checklist(tag)
        elif(name == "image"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += "<w:p><w:r><w:t>%s</w:t></w:r></w:p>" % self.format_image(tag.contents)
        elif(name == "struct"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_struct(tag.source, tag.contents)
        elif(name == "prototype"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_prototype(tag)
        elif(name == "question"):
            print "WARNING: Skipping questions for now"
        elif(name == "enum"):
            print "WARNING: Skipping enums for now"
        elif(name == "sequence"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_sequence(tag)
        elif(name == "acronyms"):
            print "WARNING: Skipping acronyms for now"
        # These tags not supported in word documents
        elif(name in ("input", "columns", "column", "endcolumns", "imagemap")):
            pass
        elif(name == "questions"):
            print "WARNING: Skipping questions for now"
        elif(name == "tbd"):
            print "WARNING: Skipping tbd for now"
        elif(name == "functionsummary"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_function_summary(tag)
        elif(name == "typesummary"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_type_summary(tag)
        elif(name == "testcasesummary"):
            print "WARNING: Skipping testcasesummary for now"
        elif(name == "testcase"):
            print "WARNING: Skipping testcase for now"
        elif(name == "embed"):
            print "WARNING: Skipping embed for now"
        else:
            FATAL("Undefined tag: %s [%s]" % (name, tag.source))
 

    def _doc_pages_to_xml(self):

        # Add the document body
        xml = ""
    
        for section in self.m_sections:
        
            margin_top = "735pt"
            
            xml += "<wx:sub-section>" + EOL

            for heading in section["Headings"]:

                header_type = ""
                if(heading["Type"] == HEADING1):
                    header_type = "Heading1"
                elif(heading["Type"] == HEADING2):
                    header_type = "Heading2"
                elif(heading["Type"] == HEADING3):
                    header_type = "Heading3"
                elif(heading["Type"] == HEADING_DEFAULT):
                    header_type = "Normal"
                else:
                    header_type = "Heading4"

                xml += '''
<w:p>
    <w:pPr>
        <w:pStyle w:val=\"%s\"/>"
    </w:pPr>
    <w:r>
       <w:t>%s</w:t>
    </w:r>
</w:p>
''' % (header_type, heading["Title"])

                
                if(heading.has_key("Content")):
                    xml += heading["Content"]
        
            
            
            xml += "</wx:sub-section>" + EOL
                
    
        return xml
        

    def _load_template(self):
        
        handle = open("%s/templates/word/%s.xml" % (shorte_get_startup_path(), self.m_engine.get_theme()), "r")
        contents = handle.read()
        handle.close()
        return contents
    
    def generate_index(self, title, theme, version):

        xml = self._load_template()
        pages = self._doc_pages_to_xml()

        xml = re.sub("DOCUMENT_TITLE",    self.xmlize(self.m_engine.get_title()), xml)
        xml = re.sub("DOCUMENT_SUBTITLE", self.xmlize(self.m_engine.get_subtitle()), xml)
        xml = re.sub("DOCUMENT_VERSION",  self.xmlize(self.m_engine.get_doc_info().version()), xml)

        xml = re.sub("<wx:sub-section.*?[[INSERT_CONTENTS_HERE]].*?<\/wx:sub-section>", pages, xml)
        xml = re.sub("__NEWLINE__", '\\\\n', xml)

        file = open(self.m_engine.m_output_directory + "/" + self.get_index_name(), "w")
        file.write(xml)
        file.close()

        return xml
    
    def generate(self, theme, version, package):
        
        pages = self.m_engine.m_parser.get_pages()

        for page in pages:
            
            tags = page["tags"]

            for tag in tags:
            
                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag.name, tag.contents, "blah")
                
                elif(self.m_engine.tag_is_source_code(tag.name)):
                    self.append_source_code(tag)

                else:
                    self.append(tag)

        # Now generate the document index
        self.generate_index(self.m_engine.get_title(), theme, version)

        print "Generating doc"  
   
