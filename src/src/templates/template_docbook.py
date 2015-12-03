# -*- coding: iso-8859-15 -*-
import re
import os
import string
import subprocess
from string import Template

from src.shorte_defines import *
from template_markdown import *

class template_docbook_t(template_t):
    def __init__(self, engine, indexer):
        template_t.__init__(self, engine, indexer)

        self.list_indent_per_level=4
        self.m_contents = ''
    
    def append(self, tag):
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
        else:
            WARNING("Unsupported tag %s" % name)
    
    def get_index_name(self):
        name = self.m_engine.get_document_name()
        return "%s" % name
    
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
                replace = replace.strip()
                prefix = self.xml('<emphasis role="strong">')
                postfix = self.xml("</emphasis>")
            elif(tag in ("i", "italic", "italics")):
                replace = replace.strip()
                prefix = self.xml('<emphasis>')
                postfix = self.xml("</emphasis>")
                #, "pre", "u", "i", "color", "span", "cross", "strike", "hl", "hilite", "highlight", "done", "complete", "star", "starred")):
                #pass
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
<?dbfo keep-together="always"?>
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
                if((not show_enum_vals) and col_index == 1):
                    col_index += 1
                    continue
                else:
                    col_index += 1
                values += self.xml("<entry>") + self.format_textblock(col["textblock"]) + self.xml("</entry>")
            values += "</row>"

        values += self.xml("</tbody></tgroup><tgroup cols='1'><tbody>")

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<?dbfo keep-together="always"?>
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
    
    def format_prototype(self, tag):
        prototype = tag.contents
        
        if(prototype.is_deprecated()):
            func_name = self.xmlize(prototype.get_name()) + self.xml("<emphasis>  (THIS FUNCTION IS DEPRECATED)</emphasis>")
        else:
            func_name = self.xmlize(prototype.get_name())

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
            fdesc = self.xmlify(self.format_textblock(field.get_description()))
            fname = self.xmlify(field.get_name())
            ftype = self.format_text(field.get_type())

            fields += self.xml("<entry>") + ftype + self.xml("</entry>")
            fields += self.xml("<entry>") + fname + self.xml("</entry>")
            fields += self.xml("<entry>") + fdesc + self.xml("</entry>")

            fields += "</row>"

        fields += self.xml("</tbody></tgroup><tgroup cols='1'><tbody>")

        xml = self.xml(string.Template("""
<informaltable frame="all" rowsep="0">
<?dbfo keep-together="always"?>
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

    
    def format_text(self, data):

        if(data == None):
            return
        
        data = re.sub('<br/>', "\n", data)

        # Escape any XML characters
        data = self.xmlify(data)
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("\\1", data)

        # Convert any inline styling blocks
        # DEBUG BRAD: Disable inline styling for now
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)

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

                xml += prefix + self.xml("<para>") + self.format_textblock(text) + self.xml("</para>")
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
        xml += self.format_object_section(obj, 'example')
        xml += self.format_object_section(obj, 'deprecated')
        xml += self.format_object_section(obj, 'since')
        xml += self.format_object_section(obj, 'see')
        xml += self.format_object_section(obj, 'requires')

        return xml

    def format_object_section(self, obj, section):

        if(section == "since"):
            if(not obj.has_since()):
                return ''

            title = "Introduced In:"
            paragraph = self.format_textblock(obj.get_since())

        elif(section == 'deprecated'):
            if(not obj.is_deprecated()):
                return ''

            title = 'Deprecated:'
            paragraph = self.format_textblock(obj.get_deprecated())
        
        elif(section == 'requires'):
            if(not obj.has_requirements()):
                return ''

            title = 'Requirements:'
            paragraph = self.format_textblock(obj.get_requirements())

        elif(section == "description"):
            if(not obj.has_description()):
                return ''

            title = "Description:"
            paragraph = self.format_textblock(obj.get_description())

        elif(section == 'see'):
            if(not obj.has_see_also()):
                return ''
            
            title = "See Also:"
            paragraph = self.format_text(obj.get_see_also())

        elif(section == 'example'):
            if(not obj.has_example()):
                return ''

            return ""

            template_example = string.Template('''
<div>
    <div class='cb_title'>Example:</div>
    <div style="margin-left: 10px; margin-top: 5px;margin-bottom:0px;">
    The following example demonstrates the use of this ${type}:<br>
    </div>
    ${example}
</div>
''');
            example  = obj.example.get_parsed()
            language = obj.example.get_language()

            if(self.m_show_code_headers["example"]):
                snippet_id = self.m_snippet_id
                self.m_snippet_id += 1
                code_header = self.m_template_code_header.substitute(
                    {"id" : snippet_id,
                     "style" : "margin-left:10px;margin-top:2px;"})
                source = html_styles.template_source.substitute({
                                "id":     snippet_id,
                                "source": self.format_source_code_no_lines(language, example)})
            else:
                code_header = ""
                source = ""
                        
            example = self.format_source_code(language, example)

            example_result = ""

            if(obj.has_example_result()):
                result = obj.get_example_result()
                if(result.has_compile_result()):
                    rc  = result.get_compile_rc()
                    val = result.get_compile_result()
                    example_result += self.format_code_result(val, rc, "Compile:", "cb_title", "code2")
                if(result.has_run_result()):
                    rc = result.get_run_rc()
                    val = result.get_run_result()
                    example_result += self.format_code_result(val, rc, "Result:", "cb_title", "code2")
                
            code = template_code.substitute(
                       {"contents" : example,
                        "source"   : source,
                        "code_header" : code_header,
                        "template" : "code2",
                        "result"   : example_result})

            return template_example.substitute({"example" : code, "type" : obj.type})

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
                 "content" : self.xmlify(tag.source)})

        return xml
    
    def format_revision_history(self):
        
        history = self.m_engine.get_doc_info().revision_history()
        xml = ""
        if(history != None):

            # Error out if the revision history is not formatted correctly for docbook
            if(history.max_cols != 4):
                FATAL("""The revision history for docbook templates must be formatted as follows:

    @doc.revisions
    - Version | Date           | Author | Description
    - 1.0     | 04 March, 2011 | BE     | Blah blah blah, this is something here describing the revision
    - 1.4.0   | 05 March, 2011 | BE     | Something else

""")

            rows = history.rows
            xml += "<revhistory>"
            rindex = 0
            for row in rows:
                cols = row["cols"]
                if(rindex == 0):
                    xml += "<revision>"
                    xml += '<revnumber><emphasis role="strong">%s</emphasis></revnumber>' % cols[0]["text"]
                    xml += '<date><emphasis role="strong">%s</emphasis></date>' % cols[1]["text"]
                    xml += '<authorinitials><emphasis role="strong">%s</emphasis></authorinitials>' % cols[2]["text"]
                    xml += '<revremark><emphasis role="strong">%s</emphasis></revremark>' % cols[3]["text"]
                    xml += "</revision>"
                elif(rindex > 0):
                    xml += "<revision>"
                    xml += '<revnumber>%s</revnumber>' % cols[0]["text"]
                    xml += "<date>%s</date>" % cols[1]["text"]
                    xml += "<authorinitials>%s</authorinitials>" % cols[2]["text"]
                    xml += "<revremark>%s</revremark>" % cols[3]["text"]
                    xml += "</revision>"
                rindex += 1

                #for col in cols:
                #    xml += "<revnumber>"

            xml += "</revhistory>"

            
        return xml
    
    
    def format_table(self, source, table):

        xml = self.xml("<table>\n")
        
        if(table.has_title()):
            xml += self.xml("<title>") + self.xmlize(table.get_title()) + self.xml("</title>\n")
        if(table.has_caption()):
            xml += self.xml("<caption><para><emphasis role='strong'>Caption:</emphasis></para>") + self.format_textblock(table.get_caption()) + self.xml("</caption>")

        num_cols = table.get_max_cols()
        col_widths = []

        # First walk through the text and figure out the
        # maximum width of each column
        for i in range(0, num_cols):
            col_widths.append(0)

        xml += self.xml("  <tgroup cols=\"%d\">\n" % num_cols)

        max_width = 0
        for row in table.get_rows():
            j = 0;
            for col in row["cols"]:
                
                if(len(col["text"]) > col_widths[j]):
                    col_widths[j] = len(col["text"])
                    max_width += col_widths[j]
                j += 1

        body_started = False

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

                if(is_header):
                    xml += self.xml("    <thead>\n")
                elif(not body_started):
                    xml += self.xml("    <tbody>\n")
                    body_started = True

                xml += self.xml("      <row>\n")

                cells = []
                for col in row["cols"]:

                    txt = self.format_text(col["text"])
                    txt = txt.replace("\n", " ")

                    xml += self.xml("        <entry>") + txt + self.xml("</entry>\n")
                    
                    #if(is_subheader or is_header):
                    #    cells.append(("%-" + "%d" % (col_widths[col_num] + 3) + "s") % (txt))
                    #else:
                    #    cells.append((" %-" + "%d" % (col_widths[col_num] + 2) + "s") % (txt))

                #html += " |".join(cells)

                col_num += 1

                xml += self.xml("      </row>\n")

                if(is_header):
                    xml += self.xml("    </thead>\n")
                    body_started = False

                #if(is_header):
                #    col_num = 0
                #    html += "\n"

                #    cells = []
                #    for col in row["cols"]:
                #        text = ""
                #        for k in range(0, col_widths[col_num] + 3):
                #            text += "-"

                #        for p in range(0, col_num+1):
                #            text += "-"

                #        col_num += 1

                #        cells.append(text)

                #    xml += "|".join(cells)



        
        xml += self.xml("    </tbody>\n")
        xml += self.xml("  </tgroup>\n")
        xml += self.xml("</table>\n")

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

        return wikiword.label

        ## If the document is being inlined then need to get
        ## rid of the link prefix and just use a local link
        #if(self.is_inline()):
        #    output = "<a href='#%s'>%s</a>" % (wikiword.wikiword, wikiword.label)
        #else:
        #    if(self.m_wikiword_path_prefix):
        #        output = "<a href='%s#%s'>%s</a>" % (self.get_output_path(wikiword.link), wikiword.wikiword, wikiword.label)
        #    else:
        #        output = "<a href='%s'>%s</a>" % (wikiword.wikiword, wikiword.label)

        #return output
    
    

    def format_pre(self, tag):
        xml = self.xml("""\n\n<div>
<programlisting linenumbering='numbered'>""")
        if(isinstance(tag, tag_t)):
            xml += self.format_textblock(tag.content)
        else:
            xml += self.format_text(tag)

        xml += self.xml("</programlisting></div>\n\n")

        return xml

    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_numbers=True, show_frame=True):

        line = 1

        output = ''

        for tag in tags:

            type = tag.type
            source = self.xmlify(tag.data)
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
        
        module = "inphi"
        import_str = "from templates.docbook.%s import *" % module
        exec(import_str)
        custom_styles = custom_styles()
        
        cnts = self.get_contents()
        cnts = cnts.replace("@lt;", "<")
        cnts = cnts.replace("@gt;", ">")

        index_name = self.get_index_name()
        index_name = index_name.replace("/", "_")
        output_file = self.m_engine.m_output_directory + os.sep + index_name
        markdown_file = output_file + ".md"
        docbook_file  = output_file + ".xml"
        pdf_file      = output_file + ".pdf"
        xsl_file = "templates/docbook/inphi/inphi_modified.xsl"
        xsl_template_file = "templates/docbook/inphi/inphi.xsl"

        # Open the XSL file
        handle = open(shorte_get_startup_path() + os.sep + xsl_template_file)
        xsl = handle.read()
        handle.close()

        xsl = xsl.replace("<!--SHORTE_DOCBOOK_STYLES-->", custom_styles.get_template())
        handle = open(shorte_get_startup_path() + os.sep + xsl_file, "wb")
        handle.write(xsl)
        handle.close()

        if(1):
            file = open(markdown_file, "wb")
            file.write(cnts)
            file.close()

            # Now use pandoc to convert to docbook
            cmd = ["/usr/local/bin/pandoc", "-s", "--chapters", "-f", "markdown_strict+pipe_tables", "-t", "docbook", markdown_file, "-o", docbook_file + ".markdown"]

            phandle = subprocess.Popen(cmd, stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)
            result = phandle.stdout.read()
            #result += phandle.stderr.read()
            phandle.wait()

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

        title_page = custom_styles.format_title_page(self.m_engine, doc_info, self.format_revision_history())
        
        handle = open(docbook_file, "rt")
        contents = handle.read()
        handle.close()
        
        handle = open(docbook_file, "w")
        contents = re.sub("<article>", "<book>", contents)
        contents = re.sub("DOCTYPE article", "DOCTYPE book", contents)
        contents = re.sub("<imagedata", '<imagedata scalefit="1" width="100%"', contents)
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

        
        cmd = ["/Users/belliott/fop/fop-2.0/fop", "-c", "/Users/belliott/fop/fop-2.0/conf/fop.xconf",
                "-param", "template_path", shorte_get_startup_path() + "/templates/docbook",
                "-param", "header.image.filename", "/Users/belliott/Dropbox/shorte/src/templates/docbook/inphi/inphi_banner.png",
                "-param", "draft.watermark.image", "/Users/belliott/Dropbox/shorte/src/templates/shared/draft.png",
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

            print "PAGE: %s" % page["source_file"]
            
            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    
                    # Store the level of the heading. We'll zero base it
                    # since the docbook sections like sect1 are actually level
                    # 2 headings.
                    tagname = tag.name
                    if(tagname == "h"):
                        FATAL("DO I GET HERE?")
                        level = 6
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

                    heading_label = self.format_text(tag.contents)
                    headings.append({"level" : level, "name" : heading_label})

                    #print "%sOpening level %d (%s)" % ("    "*level, level, heading_label)
                    #print "%s>Headings:" % ("    "*(level+3))
                    #for heading in headings:
                    #    print "%s> - %s" % ("    "*(level+3),heading["name"])
                    if(level == 0):
                        self.m_contents += self.xml("\n<chapter>\n<title>") + heading_label + self.xml("</title>\n\n")
                    else:
                        self.m_contents += self.xml("\n<sect%d>\n<title>" % level) + heading_label + self.xml("</title>\n\n")

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
    
    
    def xmlify(self, source):
        source = source.replace("&", "&amp;")
        source = source.replace("<", "&lt;")
        source = source.replace(">", "&gt;")
        source = source.replace("'", "&apos;")
        source = source.replace('"', "&quot;")
        return source
