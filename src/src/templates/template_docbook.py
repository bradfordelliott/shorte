# -*- coding: iso-8859-15 -*-
"""
This module contains the definition of a template class that is used
to generate docbook documents.
"""

import re
import os
import string
import subprocess
from string import Template

from src.shorte_defines import *
from template_markdown import *

class template_docbook_t(template_t):
    """This class generates docbook output files"""

    def __init__(self, engine, indexer):
        """The constructor for the docbook template
           
           @param engine [I] - The instance of the shorte engine.
           @param indexer [I] - An indexer object.

           @return None
        """
        template_t.__init__(self, engine, indexer)

        self.list_indent_per_level=4
        self.m_contents = ''

        # The list of generated cross references to avoid duplication
        self.m_cross_references = {}
    
    def append(self, tag):
        """This method is used to append a tag to the output
           document

           @param tag [I] - The tag to append to the output document
           
           @return None
        """
        name = tag.name

        if(name == "#"):
            return
        elif(name in "p"):
            self.m_contents += self.format_text(tag.contents) + "\n\n"
        elif(name == "text"):
            self.m_contents += self.format_textblock(tag)
        elif(name == "ul"):
            self.m_contents += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_contents += self.format_list(tag.contents, True)
        elif(name == "pre"):
            self.m_contents += self.format_pre(tag)
        elif(name == "table"):
            self.m_contents += self.format_table(tag.source, tag.contents)
        elif(name in ("note", "tbd", "warning", "question")):
            self.m_contents += self.format_note(tag)
        elif(name == "quote"):
            self.m_contents += self.format_quote(tag)
        elif(name == "image"):
            self.m_contents += self.format_image(tag)
        elif(name == "define"):
            self.m_contents += self.format_define(tag)
        elif(name == "enum"):
            self.m_contents += self.format_enum(tag)
        elif(name == "struct"):
            self.m_contents += self.format_struct(tag)
        elif(name == "prototype"):
            self.m_contents += self.format_prototype(tag)
        elif(name == "vl"):
            self.m_contents += self.format_variable_list(tag)
        else:
            WARNING("Unsupported tag %s" % name)
    
    def get_index_name(self):
        name = self.m_engine.get_document_name()
        return "%s" % name
    
    def parse_inline_styling(self, matches):
        data = matches.groups()[0].strip()
        #print "parse_inline_styling"
        #print "  DATA: [%s]" % data
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
                replace = replace.strip()
                prefix = self.xml('<emphasis role="strong">')
                postfix = self.xml("</emphasis>")
            elif(tag in ("i", "italic", "italics")):
                replace = replace.strip()
                prefix = self.xml('<emphasis>')
                postfix = self.xml("</emphasis>")
                #, "pre", "u", "i", "color", "span", "cross", "strike", "hl", "hilite", "highlight", "done", "complete", "star", "starred")):
                #pass
            elif(tag in ("img", "image")):
                prefix = ''
                replace = self.format_inline_image_str(replace)
                postfix = ''
            elif(tag == "pre"):
                return self.format_pre(replace)
            elif(tag == "strike"):
                prefix = "~~"
                postfix = "~~"

            elif(tag == "br"):
                postfix += "\n"
            elif(tag in "table"):
                table = self.m_engine.m_parser.parse_table(replace, {}, col_separators=['|','!'])
                output = self.format_table(replace, table)
                #output = output.replace("\n", "<br/>")
                #output = output.replace(" ", "&nbsp;")
                return output

            # Can't support nested quotes properly yet. This really requires
            # a re-write of the textblock object.
            elif(tag == "quote"):
                prefix = self.xml("</para>")
                replace = self.format_quote(replace.strip())
                postfix = self.xml("<para>")

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

        define = tag.contents

        if(define.is_deprecated()):
            define_name = self.xmlize(define.get_name()) + self.xml("<emphasis>  (THIS DEFINE IS DEPRECATED)</emphasis>")
        else:
            define_name = self.xmlize(define.get_name())

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<!--<?dbfo keep-together="always"?>-->
<tgroup cols='1'>
    <tbody>
        <row>
            <?dbfo bgcolor="#d0d0d0"?>
            <entry><emphasis role='code_object_title'>Define:</emphasis> ${name}</entry>
        </row>
        <row>
            <?dbfo bgcolor="#f0f0f0"?>
            <entry><emphasis role='code_object_section_title'>Value:</emphasis></entry></row>
        <row>
            <entry>${value}</entry></row>
        ${common}
    </tbody>
</tgroup>
</informaltable>
""").substitute({"name"   : define_name,
                 "value"  : self.format_textblock(define.get_value()),
                 "common" : self.format_object_common_sections(define)}))

        return xml

    def format_enum(self, tag):
        """This method is called to format an enumeration into docbook
           format

           @param tag [I] - The shorte tag containing the enumeration.

           @return The enumeration formatted for docbook output.
        """
        enum = tag.contents
        
        if(enum.is_deprecated()):
            enum_name = self.xmlize(enum.get_name()) + self.xml("<emphasis>  (THIS ENUM IS DEPRECATED)</emphasis>")
        else:
            enum_name = self.xmlize(enum.get_name())

        values = self.xml("""
    <row>
        <?dbfo bgcolor="#e0e0e0"?>
        <entry><emphasis role='code_object_section_title'>Values:</emphasis></entry>
    </row>
</tbody>
</tgroup>
<tgroup cols='2'>
   <colspec colnum="1" colname="col1" colwidth="1*"/>
   <colspec colnum="2" colname="col2" colwidth="2*"/>
   <tbody>
        <row>
            <?dbfo bgcolor="#f0f0f0"?>
            <entry><emphasis role='strong'>Name</emphasis></entry>
            <entry><emphasis role='strong'>Description</emphasis></entry>
        </row>
""")

        show_enum_vals = False

        rindex = 0
        for row in enum.values:
            values += "<row>"
            if(rindex & 1):
                values += '<?dbfo bgcolor="#f7f7f7"?>'
            rindex += 1

            col_index = 0

            for col in row["cols"]:
                # Don't attempt to wikify or format the enum name. Instead
                # create a link or cross reference to it
                if(col_index == 0):
                    link = col["text"]
                    if(link in self.m_cross_references):
                        WARNING("Duplicate cross reference detected on enumerated value %s" % col["text"])
                        values += self.xml("<entry><para>") + self.xmlize(self.format_for_zero_breaks(col["text"])) + \
                                  self.xml("</para></entry>")
                    else:
                        self.m_cross_references[link] = True
                        values += self.xml("<entry><para id='%s' xreflabel='%s'>" % (self.xmlize(col["text"]), self.xmlize(col["text"]))) + \
                                  self.xmlize(self.format_for_zero_breaks(col["text"])) + \
                                  self.xml("</para></entry>")
                
                else:
                    if((not show_enum_vals) and col_index == 1):
                        col_index += 1
                        continue

                    values += self.xml("<entry>") + self.format_textblock(col["textblock"]) + self.xml("</entry>")

                col_index += 1
            values += "</row>"

        values += self.xml("</tbody></tgroup><tgroup cols='1'><tbody>")

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<!--<?dbfo keep-together="always"?>-->
<tgroup cols='1'>
    <tbody>
        <row>
            <?dbfo bgcolor="#d0d0d0"?>
            <entry><emphasis role='code_object_title'>Enum:</emphasis> ${name}</entry>
        </row>
        ${values}
        ${common}
    </tbody>
</tgroup>
</informaltable>
""").substitute({"name"   : enum_name,
                 "values" : values,
                 "common" : self.format_object_common_sections(enum)}))

        return xml

    def format_for_zero_breaks(self, txt):
        """This is a first pass at dealing with table wrapping.
           Not sure if there is a better way of dealing with this.

           @param txt [I] - The text to insert zero width break
                            characters into so that tables wrap
                            cleanly.
           
           @return The text with wrap characters inserted.
        """
        chars = list(txt)

        output = []
        count = 0
        for c in chars:
            if(c in (' ', '\t', '\r', '-', '.', ',', ';')):
                count = 0
            if(c == '_'):
                output.append(c)
                output.append('@8203;')
                count = 0 
                continue
            elif(count > 10):
                output.append('@8203;')
                count = 0
            output.append(c)
            count += 1

        return ''.join(output)

    def format_image(self, tag):

        if(isinstance(tag, tag_t)):
            image = tag.contents
        else:
            image = tag

        # Due to a bug in Apache fop some PNGs seem to crash.
        # Always converting them to the Image library seems
        # to fix the issue.
        #image.has_key("height") or image.has_key("width")):
        if(True):
            (image,height,width) = self.m_engine.scale_image(image)

        name = image["name"] + image["ext"]

        caption = name
        if(image.has_key("caption")):
            caption = image["caption"]

        src = os.path.realpath(image["src"])

        img_format = image["ext"]
        img_format = img_format.replace(".", "")
        img_format = img_format.upper()
        
        max_width = 650
        max_height = 650

        if(height > max_height):
            new_height = max_height
            new_width = (max_height/(1.0*height)) * width
            
            height = new_height
            width = new_width
        
        if(width > max_width):
            new_width = max_width
            new_height = (max_width/(1.0*width)) * height
            height = new_height
            width = new_width
        
        dpi = 96.0
        width = "%fin" % (width/dpi)
        height = "%fin" % (height/dpi)

        #contents = re.sub("<imagedata", '<imagedata scalefit="1" width="100%"', contents)

        xml = self.xml(string.Template("""
<mediaobject>
<imageobject>
    <imagedata fileref="${path}" format="${format}" width="${width}" height="${height}"/>
</imageobject>
${caption}
</mediaobject>
""").substitute({"path" : src, "format" : img_format, "caption" : "", "width" : width, "height" : height}))

        # DEBUG: Temporary debug for the K2 user guide
        #xml = ''
        return xml

    def format_inline_image_str(self, data):
        image = self.m_engine.m_parser.parse_inline_image_str(data)
        return self.format_image(image)

    def format_link(self, url, label):
        """This is a callback method used by the format_links() method in template.py
           used to format hyperlinks

           @param url   [I] - The target URL
           @param label [I] - The label associated with the URL
        """
        return self.xml("<ulink url='%s'>%s</ulink>" % (self.xmlize(url), self.xmlize(label)))
    
    def format_prototype(self, tag):
        """This method is called to convert a prototype declaration
           into a docbook construct.

           @param tag [I] - The shorte tag to convert.

           @return The docbook XML containing the prototype declaration
        """
        prototype = tag.contents
        
        if(prototype.is_deprecated()):
            func_name = self.xmlize(prototype.get_name()) + self.xml("<emphasis>  (THIS FUNCTION IS DEPRECATED)</emphasis>")
        else:
            func_name = self.xmlize(prototype.get_name())

        xml_prototype = ''
        if(prototype.has_prototype()):
            exclude_wikiwords = []
            exclude_wikiwords.append(prototype.get_name())

            language = prototype.get_prototype().get_language()
            example  = prototype.get_prototype().get_parsed()
            
            tmp = self.format_source_code(language, example, exclude_wikiwords, False)
            xml_prototype = self.xml('''

<row>
<entry>
<programlisting linenumbering='numbered' language='%s'>''' % language) + tmp + \
            self.xml('''
</programlisting>
</entry>
</row>

''')

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<tgroup cols='1'>
    <tbody>
        <row>
            <?dbfo bgcolor="#d0d0d0"?>
            <entry><emphasis role='code_object_title'>Function:</emphasis> ${name}</entry>
        </row>
        ${common}
    </tbody>
</tgroup>
</informaltable>
""").substitute({"name"   : func_name,
                 "common" : self.format_object_common_sections(prototype)}))

        return xml

    def format_struct(self, tag):
        struct = tag.contents
        
        if(struct.is_deprecated()):
            struct_name = self.xmlize(struct.get_name()) + self.xml("<emphasis>  (THIS STRUCTURE IS DEPRECATED)</emphasis>")
        else:
            struct_name = self.xmlize(struct.get_name())

        fields = self.xml("""
    <row>
        <?dbfo bgcolor="#e0e0e0"?>
        <entry><emphasis role='code_object_section_title'>Fields:</emphasis></entry>
    </row>
</tbody>
</tgroup>
<tgroup cols='3'>
   <colspec colnum="1" colname="col1" colwidth="1.5*"/>
   <colspec colnum="2" colname="col2" colwidth="1*"/>
   <colspec colnum="3" colname="col3" colwidth="4*"/>
   <tbody>
        <row>
            <?dbfo bgcolor="#f0f0f0"?>
            <entry><emphasis role='strong'>Width</emphasis></entry>
            <entry><emphasis role='strong'>Name</emphasis></entry>
            <entry><emphasis role='strong'>Description</emphasis></entry>
        </row>
""")
        
        findex = 0
        for field in struct.get_fields():
            
            fields += "<row>"
            if(findex & 1):
                fields += '<?dbfo bgcolor="#f7f7f7"?>'
            findex += 1
            fdesc = self.format_textblock(field.get_description())
            fname = self.format_text(field.get_name())
            ftype = self.format_text(field.get_type())

            fields += self.xml("<entry>") + ftype + self.xml("</entry>")
            fields += self.xml("<entry>") + fname + self.xml("</entry>")
            fields += self.xml("<entry>") + fdesc + self.xml("</entry>")

            fields += "</row>"

        fields += self.xml("</tbody></tgroup><tgroup cols='1'><tbody>")

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<!--<?dbfo keep-together="always"?>-->
<tgroup cols='1'>
    <tbody>
        <row>
            <?dbfo bgcolor="#d0d0d0"?>
            <entry><emphasis role='code_object_title'>Structure:</emphasis> ${name}</entry>
        </row>
        ${fields}
        ${common}
    </tbody>
</tgroup>
</informaltable>
""").substitute({"name"   : struct_name,
                 "fields" : fields,
                 "common" : self.format_object_common_sections(struct)}))

        return xml

    
    def format_text(self, data, allow_wikify=True, exclue_wikify=[]):

        if(data == None):
            return
                    
        data = re.sub('<br/>', "\n", data)
        
        #data = self.format_for_zero_breaks(data)

        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("\\1", data)
        
        # First make any links or references
        data = self.format_links(data)

        # Convert any inline styling blocks
        # DEBUG BRAD: Disable inline styling for now
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)
        
        if(allow_wikify):
            data = self.wikify(data)
        
        # Escape any XML characters
        data = self.xmlize(data)

        # Collapse multiple spaces
        #data = re.sub('\n+', "\n", data)
        #data = re.sub(" +", " ", data)
        #data = re.sub("&nbsp;", " ", data)

        # Escape < and >
        #data = re.sub("<", "\\<", data)
        #data = re.sub(">", "\\>", data)

        # Need to escape @ signs since they have special meaning
        # on github
        #data = re.sub("@", "*@*", data)

        # Replace any links
        data = re.sub(r'\[\[(->)?(.*?)\]\]', r'\2', data)

        output = data

        return output

    def xml(self, data):
        data = data.replace("<", "@lt;")
        data = data.replace(">", "@gt;")
        data = data.replace('"', "@quot;")
        data = data.replace("'", "@apos;")
        data = data.replace("&", "@amp;")

        return data
    
    def format_quote(self, tag):
        if(isinstance(tag, tag_t)):
            text = self.format_textblock(tag.contents)
        else:
            text = self.format_text(tag)

        xml = self.xml("<blockquote><para>") + text + self.xml("</para><para></para></blockquote>")

        return xml

    
    
    def format_keywords(self, language, source, exclude_wikiwords=[]):

        keywords = self.m_engine.get_keyword_list(language)

        output = ''
        keyword = ''
        pos_start = 0

        #print "input = %s" % source

        for i in range(0, len(source)):

            c = source[i]

            #if((ord(c) >= 97 and ord(c) < 122) or (ord(c) == 95)):
            #    keyword += c 
            if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.')):
                keyword += c 
            else:
                if(keyword != ''):
                    #print "  keyword1: {%s}" % keyword
                    #print "  substr:   {%s}" % source[pos_start:i]
                    if(keywords.has_key(keyword)):
                        #output += source[pos_start:i]
                        output += '<emphasis role="code_keyword">%s</emphasis>' % keyword
                    else:
                        output += self.wikify(keyword, exclude_wikiwords)
                        #output += keyword

                    keyword = ''
                
                pos_start = i+1
                output += "%c" % c


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                #output += source[pos_start:i]
                output += '<emphasis role="code_keyword">%s</emphasis>' % keyword
            else:
                #output += keyword
                output += self.wikify(keyword, exclude_wikiwords)
            #print "  keyword2 = %s" % keyword

        #print "output = %s\n" % output

        return output
    
    def format_list(self, list, ordered=False):
        xml = self.xml("\n<div>\n")
        
        if(ordered):
            xml += self.xml("<orderedlist>\n")
        else:
            xml += self.xml("<itemizedlist>\n")

        for elem in list:
            xml += self.format_list_child(elem, ordered, prefix="    ")

        if(ordered):
            xml += self.xml("</orderedlist>\n")
        else:
            xml += self.xml("</itemizedlist>\n")
            
        xml += self.xml("</div>\n\n")

        return xml
    
    def format_list_child(self, elem, ordered=False, start=0, prefix=""):
        xml = prefix + self.xml("<listitem>\n")

        #prefix = ""
        #if(elem.type in ("checkbox", "action")):
        #    prefix = "[ ] "
        #    if(elem.checked):
        #        prefix = "[x] "

        text = prefix + elem.text
        if(ordered):
            if(elem.children != None):

                xml += prefix + self.xml("<para>") + self.format_text(text) + self.xml("</para>")
                num_children = len(elem.children)
                
                xml += prefix + self.xml("<orderedlist>\n")
                for i in range(0, num_children):
                    xml += self.format_list_child(elem.children[i], ordered, prefix = prefix + "    ")
                xml += prefix + self.xml("</orderedlist>\n")
            else:
                xml += prefix + self.xml("<para>") + self.format_text(text) + self.xml("</para>\n")
        else:
            if(elem.children):
                xml += prefix + self.xml("<para>") + self.format_text(text) + self.xml("</para>\n")

                xml += prefix + self.xml("<itemizedlist>\n")
                num_children = len(elem.children)
                for i in range(0, num_children):
                    xml += self.format_list_child(elem.children[i], prefix = prefix+"    ")
                xml += prefix + self.xml("</itemizedlist>\n")
            else:
                xml += prefix + self.xml("<para>") + self.format_text(text) + self.xml("</para>\n")

        xml += prefix + self.xml("</listitem>\n")
        return xml

    def format_object_common_sections(self, obj):
        '''This method formats common sections of a
           code object (like enum, struct, prototype, etc)
           and sets them into the input dictionary

           @param obj   [I] - The code object being formatted
        '''
        
        xml = ""
        xml += self.format_object_section(obj, 'description')
        xml += self.format_object_section(obj, 'prototype')
        xml += self.format_object_section(obj, 'params')
        xml += self.format_object_section(obj, 'example')
        xml += self.format_object_section(obj, 'deprecated')
        xml += self.format_object_section(obj, 'since')
        xml += self.format_object_section(obj, 'see')
        xml += self.format_object_section(obj, 'requires')
        xml += self.format_object_section(obj, 'returns')

        return xml

    def format_object_section(self, obj, section):

        if(section == 'deprecated'):
            if(not obj.is_deprecated()):
                return ''

            title = 'Deprecated:'
            paragraph = self.format_textblock(obj.get_deprecated())
        
        elif(section == "description"):
            if(not obj.has_description()):
                return ''

            title = "Description:"
            paragraph = self.format_textblock(obj.get_description())
        
        elif(section == 'example'):
            if(not obj.has_example()):
                return ''
            
            exclude_wikiwords = [obj.get_name()]
            language = obj.get_example().get_language()
            example  = obj.get_example().get_parsed()
            source = self.format_source_code(language, example, exclude_wikiwords, False)

            title = "Example:"
            paragraph = self.xml("<para>The following example demonstrates the use of this method:</para><programlisting linenumbering='numbered' language='%s'>" % language) + source + self.xml("</programlisting>")

        elif(section == "params"):
            if(not obj.has_params()):
                return ''
            
            params = obj.get_params()
            paragraph = self.xml("""<para><informaltable frame="topbot" colsep="0">
<tgroup cols="4">
   <colspec colnum="1" colname="col1" colwidth="2*"/>
   <colspec colnum="2" colname="col2" colwidth="1*"/>
   <colspec colnum="3" colname="col3" colwidth="0.5*"/>
   <colspec colnum="4" colname="col4" colwidth="4*"/>
<tbody>
  <row>
    <?dbfo bgcolor='#e0e0e0'?>
    <entry><emphasis role='strong'>Name</emphasis></entry>
    <entry><emphasis role='strong'>Type</emphasis></entry>
    <entry><emphasis role='strong'>I/O</emphasis></entry>
    <entry><emphasis role='strong'>Description</emphasis></entry>
  </row>
""")
            pindex = 0
            for param in params:
                pname = self.xmlize(param.get_name())
                ptype = ''
                if(param.has_type()):
                    ptype = self.xmlize(param.get_type())
                
                pio = ''
                if(param.has_io()):
                    pio = self.xmlize(param.get_io())

                paragraph += self.xml("  <row>\n")
                if(pindex & 1):
                    paragraph += self.xml("    <?dbfo bgcolor='#f7f7f7'?>\n")

                paragraph += self.xml("    <entry>") + pname + self.xml("</entry>\n")
                paragraph += self.xml("    <entry>") + ptype + self.xml("</entry>\n")
                paragraph += self.xml("    <entry>") + pio + self.xml("</entry>\n")
                paragraph += self.xml("    <entry>") + self.format_textblock(param.get_description()) + self.xml("</entry>\n")
                
                paragraph += self.xml("  </row>\n")

                pindex += 1

            paragraph += self.xml("</tbody>\n</tgroup>\n</informaltable></para>\n")

            title = "Params:"

        elif(section == "prototype"):
            if(not obj.has_prototype()):
                return ''
            
            exclude_wikiwords = [obj.get_name()]
            language = obj.get_prototype().get_language()
            example  = obj.get_prototype().get_parsed()
            source = self.format_source_code(language, example, exclude_wikiwords, False)

            title = "Prototype:"
            paragraph = self.xml("<programlisting linenumbering='numbered' language='%s'>" % language) + source + self.xml("</programlisting>")
        
        elif(section == 'requires'):
            if(not obj.has_requirements()):
                return ''

            title = 'Requirements:'
            paragraph = self.format_textblock(obj.get_requirements())

        elif(section == 'returns'):
            if(not obj.has_returns()):
                return ''
            
            title = "Returns:"
            paragraph = self.format_text(obj.get_returns())

        elif(section == 'see'):
            if(not obj.has_see_also()):
                return ''
            
            title = "See Also:"
            paragraph = self.format_text(obj.get_see_also())

        elif(section == "since"):
            if(not obj.has_since()):
                return ''

            title = "Introduced In:"
            paragraph = self.format_textblock(obj.get_since())


        else:
            FATAL("Unsupported section: %s" % construct)


        template_section = string.Template("""
<row>
<?dbfo bgcolor="#e0e0e0"?>
<entry><emphasis role='code_object_section_title'>${title}</emphasis></entry>
</row>
<row><entry>${paragraph}</entry></row>
        """)
        
        return template_section.substitute({"title" : title, "paragraph" : paragraph})
    
    
    def format_note(self, tag):

        xml_tag = "note"

        title = tag.name.title()
        if(tag.name == "tbd"):
            title = "TBD"
        elif(tag.name == "warning"):
            xml_tag = "warning"
        
        xml = string.Template(self.xml("""
<div>
<para></para>
<${tag}>
<title>${title}</title>
<para>
${content}
</para>
</${tag}>
<para></para>
</div>
""")).substitute({"tag"     : xml_tag,
                 "title"   : tag.name.title(),
                 "content" : self.format_textblock(tag.contents)})

        return xml
    
    def format_revision_history(self):
        
        history = self.m_engine.get_doc_info().revision_history()
        xml = ""
        if(history != None):

            # Error out if the revision history is not formatted correctly for docbook
            expected_columns = int(shorte_get_config("docbook", "revision_history_cols"))

            if(history.max_cols != expected_columns):
                FATAL("""The revision history for docbook templates must be formatted as follows:

    @doc.revisions
    - Version | Date           | Author | Description
    - 1.0     | 04 March, 2011 | BE     | Blah blah blah, this is something here describing the revision
    - 1.4.0   | 05 March, 2011 | BE     | Something else

You can disable this error by passing -s \"docbook.revision_history_cols=3;\" at the shorte command line.
This will skip the author column which is missing in some legacy documents.
""")

            rows = history.rows
            xml += "<revhistory>"
            rindex = 0
            for row in rows:
                cols = row["cols"]

                if(history.max_cols == 3):
                    rev_number = self.format_text(cols[0]["text"])
                    rev_date   = self.format_text(cols[1]["text"])
                    rev_author = ""
                    rev_desc   = self.format_textblock(cols[2]["textblock"])
                elif(history.max_cols == 4):
                    rev_number = self.format_text(cols[0]["text"])
                    rev_date   = self.format_text(cols[1]["text"])
                    rev_author = self.format_text(cols[2]["text"])
                    rev_desc   = self.format_textblock(cols[3]["textblock"])

                if(rindex == 0):
                    xml += "<revision>"
                    xml += "<?dbfo bgcolor='#e0e0e0'?>"
                    xml += '<revnumber><emphasis role="strong">%s</emphasis></revnumber>' % rev_number
                    xml += '<date><emphasis role="strong">%s</emphasis></date>' % rev_date
                    if(history.max_cols == 4):
                        xml += '<authorinitials><emphasis role="strong">%s</emphasis></authorinitials>' % rev_author
                    xml += '<revremark><emphasis role="strong">%s</emphasis></revremark>' % rev_desc
                    xml += "</revision>"
                elif(rindex > 0):
                    xml += "<revision>"
                    xml += '<revnumber>%s</revnumber>' % rev_number
                    xml += "<date>%s</date>" % rev_date
                    if(history.max_cols == 4):
                        xml += "<authorinitials>%s</authorinitials>" % rev_author
                    xml += "<revremark>%s</revremark>" % rev_desc
                    xml += "</revision>"
                rindex += 1

                #for col in cols:
                #    xml += "<revnumber>"

            xml += "</revhistory>"

            
        return xml
    
    
    def format_table(self, source, table):

        xml = self.xml("<informaltable>\n")
        
        num_cols = table.get_max_cols()
        col_widths = []

        col_num_check = 0
        for row in table.get_rows():
            
            if(len(row["cols"]) > col_num_check):
                col_num_check = len(row["cols"])

        if(num_cols != col_num_check):
            FATAL("Number of columns doesn't line up!")

        xml += self.xml("  <tgroup cols=\"%d\">\n" % num_cols)
        
        if(table.has_widths()):
            widths = table.get_widths()

            if(len(widths) != num_cols):
                FATAL("Column widths doesn't line up")
            cindex = 0
            
            smallest_width = 100
            for width in widths:
                if(width < smallest_width):
                    smallest_width = width

            for width in widths:
                
                # For some reason the columns widths need to be specified backwards
                # Not sure if this is a bug in my table generation or a bug in the version
                # of docbook I'm using.
                #width = width/(1.0*smallest_width)
                width = smallest_width/(1.0*width)

                xml += self.xml('  <colspec colnum="%d" colname="col%d" colwidth="%.1f*"/>\n' % (cindex, cindex, width))
                cindex += 1
        else:
            for cindex in xrange(0, num_cols):
                xml += self.xml('  <colspec colnum="%d" colname="col%d"/>\n' % (cindex, cindex))

        xml += self.xml("  <tbody>\n")

        # If the table has a title then output it now
        if(table.has_title()):
            colspec = " namest='col%d' nameend='col%d' " % (0, table.get_max_cols()-1)
            xml += self.xml("<row><?dbfo bgcolor='#909090'?><entry %s><emphasis role='strong'>" % colspec) + self.xmlize(table.get_title()) + self.xml("</emphasis></entry></row>\n")
        
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
                
                xml += self.xml("      <row>\n")

                if(is_header):
                    xml += self.xml('<?dbfo bgcolor="#b0b0b0"?>')
                elif(is_subheader):
                    xml += self.xml('<?dbfo bgcolor="#d0d0d0"?>')

                col_index = 0
                for col in row["cols"]:

                    #txt = self.format_for_zero_breaks(col["text"])
                    txt = self.format_textblock(col["textblock"])
                    span = col["span"]

                    if(span > 1):
                        if((col_index + span - 1) > (num_cols-1)):
                            FATAL("Failed parsing this table")
                        span_spec = " namest='col%d' nameend='col%d'" % (col_index, col_index+span-1)
                    else:
                        span_spec = ''

                    if(is_header or is_subheader):
                        xml += self.xml("        <entry%s><emphasis role='strong'>" % span_spec) + txt + self.xml("</emphasis></entry>\n")
                    else:
                        xml += self.xml("        <entry%s>" % span_spec) + txt + self.xml("</entry>\n")
                    
                    col_index += 1

                xml += self.xml("      </row>\n")

        # If the table has a title then output it now
        if(table.has_caption()):
            colspec = " namest='col%d' nameend='col%d' " % (0, table.get_max_cols()-1)
            xml += self.xml("<row><?dbfo bgcolor='#909090'?><entry %s><emphasis role='strong'>Caption:</emphasis>" % colspec) + self.format_textblock(table.get_caption()) + self.xml("</entry></row>\n")

        xml += self.xml("    </tbody>\n")
        xml += self.xml("  </tgroup>\n")
        xml += self.xml("</informaltable>\n")

        return xml
    
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

        output = self.xml("\n\n<div>\n")

        for p in paragraphs:
            output += self.xml("<para>")
            text = p["text"]
            is_code = p["code"]
            is_list = p["list"]

            if(is_code):
                output += self.format_pre(text)
            elif(is_list):
                output += self.format_list(text)
            else:
                output += self.format_text(text)

            output += self.xml("</para>\n")

        output += self.xml("</div>\n\n")

        return output
    
    def format_wikiword(self, wikiword, link_word):
        '''This method is called to format a wikiword. It is called by
           the wikify method in the template base class'''

        # If the document is being inlined then need to get
        # rid of the link prefix and just use a local link
        if(1): #self.is_inline()):
            output = "<xref linkend='%s'>%s</xref>" % (wikiword.wikiword, wikiword.label)
        else:
            if(0): #self.m_wikiword_path_prefix):
                output = "<ulink url='%s#%s'>%s</ulink>" % (self.get_output_path(wikiword.link), wikiword.wikiword, wikiword.label)
            else:
                output = "<ulink href='%s'>%s</ulink>" % (wikiword.wikiword, wikiword.label)

        return self.xml(output)

    def format_pre(self, tag):
        xml = self.xml("""\n\n<div>
<programlisting linenumbering='numbered'>""")
        if(isinstance(tag, tag_t)):
            xml += self.format_text(tag.contents)
        else:
            xml += self.format_text(tag)

        xml += self.xml("</programlisting></div>\n\n")

        return xml

    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_numbers=True, show_frame=True):

        line = 1

        output = ''

        for tag in tags:

            type = tag.type
            source = self.xmlize(tag.data)
            #source = re.sub("( +)", self.__replace_whitespace, source)

            if(type == TAG_TYPE_CODE):
                source = self.format_keywords(language, source, exclude_wikiwords)
                output += self.xml('<emphasis role="code_default">') + source + self.xml("</emphasis>")
            elif(type in (TAG_TYPE_COMMENT, TAG_TYPE_MCOMMENT, TAG_TYPE_XMLCOMMENT)):
                output += self.xml('<emphasis role="code_comment">') + source + self.xml("</emphasis>")
            elif(type == TAG_TYPE_PREPROCESSOR):
                output += self.xml('<emphasis role="code_preprocessor">') + source + self.xml("</emphasis>")
            elif(type == TAG_TYPE_WHITESPACE):
                #output += '<literallayout> </literallayout>'
                output += ' '
            elif(type == TAG_TYPE_STRING):
                output += self.xml('<emphasis role="code_string">') + source + self.xml("</emphasis>")
            elif(type == TAG_TYPE_NEWLINE):
                line += 1
                #output += '<literallayout>\n</literallayout>'
                output += '\n'
                
                #if(show_line_numbers):
                #    output += '<text:span text:style-name="%s">%03d </text:span>' % (self.m_styles["span"]["code_line_numbers"], line)
            
        return output
        
    def format_variable_list(self, tag):
        vlist = tag.contents

        xml = self.xml("<variablelist>\n")
        xml += self.xml("<?dbfo list-presentation=\"blocks\" term-presentation=\"bold\"?>\n")
        for item in vlist.get_items():
            name = item.get_name()
            value = item.get_value()

            xml += self.xml("<varlistentry><term><emphasis role='strong'>") + self.xmlize(name) + self.xml("</emphasis></term>")
            xml += self.xml("<listitem>") + self.format_textblock(value) + self.xml("</listitem>")
            xml += self.xml("</varlistentry>")

        xml += self.xml("</variablelist>")

        return xml

    def append_source_code(self, tag):
                
        xml = self.format_source_code(tag.name, tag.contents)
        self.m_contents += self.xml('''
<div>
<programlisting linenumbering='numbered' language='%s'>''' % tag.name)
        self.m_contents += xml
        self.m_contents += self.xml('''
</programlisting>
</div>

''')

    def generate_index(self, title, theme, version):

        import_str = "from templates.docbook.%s import *" % theme
        exec(import_str)
        custom_styles = custom_styles()
        
        cnts = self.get_contents()
        cnts = cnts.replace("@lt;", "<")
        cnts = cnts.replace("@gt;", ">")
        cnts = cnts.replace("@quot;", '"')
        cnts = cnts.replace("@amp;", '&')
        cnts = cnts.replace("@apos;", "'")
        cnts = cnts.replace("@8203;", "&#8203;")

        index_name = self.get_index_name()
        index_name = index_name.replace("/", "_")
        output_file = self.m_engine.m_output_directory + os.sep + index_name
        markdown_file = output_file + ".md"
        docbook_file  = output_file + ".xml"
        pdf_file      = output_file + ".pdf"
        xsl_file = shorte_get_scratch_dir() + "/docbook.xsl"

        status = ""
        if(self.m_engine.get_doc_info().has_status()):
            status = self.m_engine.get_doc_info().get_status()

        xsl = custom_styles.get_template(status)
        handle = open(xsl_file, "wb")
        handle.write(xsl)
        handle.close()

        file = open(docbook_file, "wb")
        header = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN"
                  "http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd">
<article>
  <articleinfo>
    <title></title>
  </articleinfo>
"""
        file.write(header)
        file.write(cnts)
        file.close()
  
        doc_info = self.m_engine.get_doc_info()

        revhistory = self.format_revision_history()
        revhistory = revhistory.replace("@lt;", "<")
        revhistory = revhistory.replace("@gt;", ">")
        revhistory = revhistory.replace("@quot;", '"')
        revhistory = revhistory.replace("@amp;", '&')
        revhistory = revhistory.replace("@apos;", "'")
        revhistory = revhistory.replace("@8203;", "&#8203;")

        title_page = custom_styles.format_title_page(self.m_engine, doc_info, revhistory)
        
        handle = open(docbook_file, "rt")
        contents = handle.read()
        handle.close()
        
        handle = open(docbook_file, "w")
        contents = re.sub("<article>", "<book>", contents)
        contents = re.sub("DOCTYPE article", "DOCTYPE book", contents)
        contents = re.sub("""<articleinfo>
    <title></title>
  </articleinfo>
""", title_page, contents)
        #contents = re.sub("<sect1 ", '<sect1 status="draft" ', contents)
        contents = re.sub("<programlisting>\s*", "<programlisting>", contents)
        contents = re.sub("</article>", "", contents) 
        #contents = re.sub('<chapter id="">', '<chapter id="blah">', contents) 
        #contents = re.sub('<sect1 id="">', '<sect1 id="blah2">', contents) 

        # Strip out any divs inserted to pass markup through pandoc
        contents = re.sub("<div>", "", contents) 
        contents = re.sub("</div>", "", contents) 


        contents += custom_styles.format_last_page()
        
        contents += "</book>"

        handle.write(contents)
        handle.close()

        path_fop = shorte_get_config("docbook", "path.fop", True)
        path_fop_xconf = shorte_get_config("docbook", "path.fop.xconf", True)

        cmd = [path_fop, "-c", path_fop_xconf,
                "-param", "template_path", shorte_get_startup_path() + "/templates/docbook",
                "-param", "header.image.filename", shorte_get_startup_path() + "/templates/docbook/%s/%s_banner.png" % (theme,theme),
                "-param", "draft.watermark.image", shorte_get_startup_path() + "/templates/shared/draft.png",
                "-xml", docbook_file,
                "-xsl", xsl_file, "-pdf", pdf_file]
        phandle = subprocess.Popen(cmd, stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)
        result = phandle.stdout.read()
        #result += phandle.stderr.read()
        phandle.wait()

        #print result

        return True

    def generate(self, theme, version, package):
        
        self.m_package = package
        self.m_inline = True

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = ''
            
        # Create a stack as we navigate headings so that we can
        # manage outputting the closing tag.
        headings = []

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".markdown", source_file)
            path = self.m_engine.get_output_dir() + "/" + output_file

            #print "PAGE: %s" % page["source_file"]
            
            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    
                    # Store the level of the heading. We'll zero base it
                    # since the docbook sections like sect1 are actually level
                    # 2 headings.
                    tagname = tag.name
                    if(tagname == "h"):
                        level = 5
                    else:
                        level = int(tag.name[1:]) - 1

                    # Step through the stack and close any open headers
                    while(len(headings) > 0):
                        # Get the level of the last heading
                        last = headings[-1]

                        # Close any open headings if we're going up in the heading hierarchy
                        if(level <= last["level"]):
                            headings.pop()
                            #print "%sClosing level %d (%s)" % ("    "*last["level"],last["level"],last["name"])#, headings
                            #print "%s>Headings:" % ("    "*(last["level"]+3))
                            #for heading in headings:
                            #    print "%s> - %s" % ("    "*(last["level"]+3),heading["name"])
                            if(last["level"] == 0):
                                self.m_contents += self.xml("</chapter>\n\n")
                            else:
                                self.m_contents += self.xml("</sect%d>\n\n" % last["level"])
                        else:
                            break

                    heading_label = self.format_text(tag.contents, allow_wikify=False)

                    link = tag.contents.strip()
                    if(tag.has_modifiers()):
                        modifiers = tag.get_modifiers()
                        if("wikiword" in modifiers):
                            link = modifiers["wikiword"]

                    if(link in self.m_cross_references):
                        link = ""
                    else:
                        self.m_cross_references[link] = True
                        link = " id='%s' xreflabel='%s' " % (link, heading_label)

                    headings.append({"level" : level, "name" : heading_label})

                    #print "%sOpening level %d (%s)" % ("    "*level, level, heading_label)
                    #print "%s>Headings:" % ("    "*(level+3))
                    #for heading in headings:
                    #    print "%s> - %s" % ("    "*(level+3),heading["name"])

                    if(level == 0):
                        self.m_contents += self.xml("\n<chapter %s>\n<title>" % link) + heading_label + self.xml("</title>\n\n")
                    else:
                        self.m_contents += self.xml("\n<sect%d %s>\n<title>" % (level, link)) + heading_label + self.xml("</title>\n\n")

                elif(self.m_engine.tag_is_source_code(tag.name)):
                    self.append_source_code(tag)

                else:
                    self.append(tag)

        # Close any heading blocks
        while(len(headings) > 0):
            level = headings.pop()
            #print "%sClosing level %d (%s)" % ("    "*level["level"],level["level"], level["name"])#, headings
            #print "%s>Headings:" % ("    "*(level["level"]+3))
            #for heading in headings:
            #    print "%s> - %s" % ("    "*(level["level"]+3),heading["name"])
            if(level["level"] == 0):
                self.m_contents += self.xml("</chapter>\n\n")
            else:
                self.m_contents += self.xml("</sect%d>\n\n" % level["level"])

        # Now generate the document index
        self.generate_index(self.m_engine.get_title(), self.m_engine.get_theme(), version)

        #if(self.m_inline != True):
        #    self.install_support_files(self.m_engine.get_output_dir())
       
        ## Copy output images - really only required if we're generating
        ## an HTML document.
        #if(self.m_inline != True):
        #    for image in self.m_engine.m_parser.m_images:
        #        shutil.copy(image, self.m_engine.get_output_dir() + "/" + image)

        INFO("Generating docbook document")

