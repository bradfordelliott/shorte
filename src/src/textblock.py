"""
This module contains the definition of the textblock
object. This is the basis of most blocks of text
within a shorte document.
"""

import sys
sys.path.append(".")
from src.shorte_defines import *

class list_item_t:
    """This class contains the definition of an item
       within a list"""

    def __init__(self):

        self.text = None
        self.indent = 0
        self.children = None
        self.type = "list"
        self.checked = False
        self.starred = False
        self.priority = 0

        # Additional options for checklist items
        self.comments = None
        self.date     = None
        self.who      = None

    def set_text(self, text):

        #print "LIST ITEM TEXT: %s" % text

        # See if it starts with an action [] but make sure
        # it isn't a hyperlink
        if(not text.startswith("[[") and text.startswith("[")):
            self.type = "checkbox"
            self.checked = False

            pos = 1
            modifier = ''
            for i in range(0,len(text)):
                if(text[i] == ']'):
                    pos = i+1
                    break
                else:
                    modifier += text[i]
            
            text = text[pos:]
            start_tag = ""
            end_tag = ""

            for i in range(0, len(modifier)):
                
                if(modifier[i] == 'x'):
                    self.checked = True
                    start_tag += "@{cross,"
                    end_tag += "}"

                elif(modifier[i] == 'a'):
                    self.type = "action"
                    start_tag = "*ACTION:*" + start_tag

                elif(modifier[i] in ('0', '1', '2', '3', '4', '5')):
                    self.priority = int(modifier[i])

                elif(modifier[i] == '*'):
                    self.starred = True

            text = text.strip()
            if(text.startswith(":")):
                text = text[1:].strip()
                modifiers = shorte_parse_modifiers(text)
                text = modifiers["text"]

                if(modifiers.has_key("comments")):
                    self.comments = modifiers["comments"]
                if(modifiers.has_key("date")):
                    self.date = modifiers["date"]
                if(modifiers.has_key("who")):
                    self.who = modifiers["who"]
                    

            text = start_tag + text + end_tag
            text = text.strip()

            #print "ITEM:"
            #print "  TEXT: %s" % text
            #print "  PRIORITY: %d" % self.priority

        self.text = text

    def get_text(self):

        return self.text.strip()

    def __str__(self, indent=0):

        output = "%s%s\n" % (" "*indent, self.text)
        if(self.children != None):
            for child in self.children:
                output += child.__str__(indent+4)
            
        return output


class textblock_t(object):
    '''This class is intended to represent an blocks of
       text within a shorte document.
       
       The eventual goal is that all text objects will be
       wrappered by this object to make the parsing
       and formatting consistent.
    '''

    TYPE_TEXT         = 0
    TYPE_LIST         = 1
    TYPE_ORDERED_LIST = 2
    TYPE_CODE         = 3
    TYPE_QUOTE        = 4
    TYPE_TABLE        = 5

    def __init__(self, data=""):
        self.source = data
        self.paragraphs = []
        self.list_indent_per_level = 4

        self.parse(data)

    def translate_type(self, inp):
        if(inp == textblock_t.TYPE_TEXT):
            return "text"
        elif(inp == textblock_t.TYPE_LIST):
            return "list (unordered)"
        elif(inp == textblock_t.TYPE_ORDERED_LIST):
            return "list (ordered)"
        elif(inp == textblock_t.TYPE_CODE):
            return "code"
        elif(inp == textblock_t.TYPE_QUOTE):
            return "quote"
        elif(inp == textblock_t.TYPE_TABLE):
            return "table"

        return "unknown"

    def get_source(self):
        return self.source
    
    def format_text(self, text):
        return text

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

    def to_text(self):
        '''This method is called to format a textblock
        '''
        paragraphs = self.paragraphs
        prefix_first_line = False
        pad_textblock = False
        prefix = ""

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
            output += "\n"

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

        output += "\n"

        return output


    def get_indent_of_line(self, data, start_of_line):

        i = start_of_line
        indent = []
        len_data = len(data)

        while(i < len_data and data[i] == ' '):
            indent.append('0')
            i += 1
        
        return ''.join(indent)
    
    def strip_indent(self, input, indent):
        
        #print "\n\nINPUT=[%s], indent=%d" % (input, indent)

        if(indent == 0):
            return input

        len_input = len(input)

        for i in range(0, indent+1):
            if(i >= (len_input-1)):
                break

            if(input[i] != ' '):
                break

        return input[i:]

    def parse_block(self, text):

        lines = text.split("\n")
        
        # Remove any leading blank lines
        for line in lines:
            if(len(line) == 0):
                lines.remove(line)
            else:
                break

        # Figure out the indent of the first line
        indent = 0
        for i in range(0, len(lines[0])):
            if(lines[0][i] == ' '):
                indent += 1
            else:
                break

        #print "Indent = %d" % indent
        
        lines_out = []
        for line in lines:
            if(len(line) == 0):
                continue
            lines_out.append(self.strip_indent(line, indent))
            #lines_out.append(line)

        if(len(lines_out) == 0):
            return ""

        #print "DO I get here? len=%d" % len(lines_out)
        #print lines_out
        return "\n".join(lines_out)
    
    
    def parse_list_child(self, i, items, x=1):
        
        #print "%*sparsing text=%s, i=%d" % (x*3, " ", items[i][0].strip(), i)
        nodes = []

        while(i < len(items)):
            item   = items[i]
            indent = item.indent
            text   = item.get_text()
            children = None

            #print "%*sitem=%s, indent=%d" % (x*3, " ", text, indent)

            # Check to see if the next element has a greater
            # indent, if it is then it's a child
            if(i+1 < len(items)):
                next_item = items[i+1]
                next_indent = next_item.indent
                next_text = next_item.get_text()
                
                # If the next node in the list has a smaller
                # indent then we've hit the end of this branch
                if(next_indent < indent):
                    #print "%*sstopping at %s, curr_text = %s" % (x*3, " ", next_text, text)
                    #print "%*sAdding node %s" % (x*3, " ", text)
                    node = list_item_t()
                    node.checked = item.checked
                    node.type = item.type
                    node.children = item.children
                    node.starred = item.starred
                    node.priority = item.priority
                    node.set_text(text)
                    nodes.append(node)
                    return (i+1, nodes)
                # If the next node is indented more than it's
                # a child of this node.
                elif(next_indent > indent):
                    #print "%*sWalking children of %s" % (x*3, " ", text)
                    (i, children) = self.parse_list_child(i+1, items, x+1)

                # Otherwise we're at the same level so continue
                # adding elements.
                else:
                    #print "%*sContinue at text=%s,next_text=%s" % (x*3, " ", text, next_text)
                    i += 1
            else:
                i += 1
              
            #print "%*sAdding node %s" % (x*3, " ", text)
            node = list_item_t()
            node.checked = item.checked
            node.type = item.type
            node.starred = item.starred
            node.priority = item.priority
            node.set_text(text)
            node.children = item.children
            if(children != None):
                if(len(children) > 0):
                    node.children = children
                    children = []

            nodes.append(node)

            # Check the next item in the list and make sure it's not
            # then end of this level
            if(i < len(items)):
                next_item = items[i]
                next_indent = next_item.indent
                if(next_indent < indent):
                    #print "Next item %s is up one level" % next_item[0].strip()
                    i -= 1
                    break

        return (i+1,nodes)

    def parse_list(self, source, modifiers):
        '''This is an internal method that is used to
           parse a list within a textblock object

           @param source    [I] - The source string to parse
           @param modifiers [I] - The list of any modifiers attached to the list.

           @return The list object
        '''

        items = []
        item = []
        item_indent = 0
        #print "PARSING LIST: [%s]" % source

        STATE_NORMAL = 0
        STATE_INLINE_FORMATTING = 1

        state = STATE_NORMAL

        end = len(source)

        for i in xrange(0, end):

            if(state == STATE_INLINE_FORMATTING):
                if(source[i] == '}'):
                    state = STATE_NORMAL

                item.append(source[i])
            
            elif(state == STATE_NORMAL):
                if(source[i] == '@' and source[i+1] == '{'):
                    item.append(source[i])
                    state = STATE_INLINE_FORMATTING
                    continue
                
                elif(source[i] in ('-')):

                    # Look backwards till the first newline
                    # to ensure this is a list item and not
                    # a dash between two words:
                    j = i-1
                    is_list_item = True
                    while(j > 0):
                        if(source[j] == "\n"):
                            break
                        elif(source[j] != " "):
                            is_list_item = False
                        j -= 1

                    if(not is_list_item):
                        item.append(source[i])
                        continue

                    # Output the last item if it exists
                    if(len(item) != 0):
                        litem = list_item_t()
                        litem.set_text(''.join(item))
                        litem.indent = item_indent
                        items.append(litem)
                    item = []

                    # Figure out the indent level of this item
                    item_indent = 0
                    j = i
                    while(j >= 0):
                        if(source[j] == '\n'):
                            break
                        j -= 1
                        item_indent += 1
                    

                else:
                    item.append(source[i])

        if(len(item) != 0):
            litem = list_item_t()
            litem.text = ''.join(item)
            litem.indent = item_indent
            items.append(litem)

        (i, list) = self.parse_list_child(0, items)

        #for elem in list:
        #    print elem

        return list

    def parse(self, data):
        '''This method is used to parse an input data string
           and convert it into a textblock object'''
        #print "PARSING TEXTBLOCK: [%s]" % data

        data = trim_leading_indent(data)

        STATE_NORMAL = 0
        STATE_LIST = 1
        STATE_CODE = 2
        STATE_INLINE = 3
        STATE_ESCAPE = 4
        STATE_QUOTE = 5
        STATE_ORDERED_LIST = 6
        STATE_CODE_BACKTICKS = 7
        states = []
        states.append(STATE_NORMAL)

        segments = []
        segment = {}
        segment["type"] = "text"
        segment["text"] = ""
        i = 0

        #print "DATA: [%s]" % data
        end = len(data)-1
        while(i < len(data)):

            state = states[-1]

            if(state == STATE_ESCAPE):
                segment["text"] += data[i]
                states.pop()
                i += 1
                continue
                
            if(data[i] == '\\'):
                i += 1
                states.append(STATE_ESCAPE)
                continue

            if(state == STATE_NORMAL):

                # If the line starts with - or * then treat it
                # as a list. If it is ** then it is actually bold text
                if(data[i] == "-"): #  or (data[i] == "*" and (i+1 < len(data) and data[i+1] != "*"))):
                    if(i == 0 or data[i-1] == "\n"):
                        #print "Starting a list, last seg=%s" % segment
                        i += 1 
                        segments.append(segment)
                        segment = {}
                        segment["type"] = "list"
                        segment["text"] = "-"
                        states.append(STATE_LIST)
                    else:
                        segment["text"] += data[i]
                        i += 1

                # If the line starts with a number followed by . then it
                # must be the start of an ordered list
                elif((i == 0 or (data[i-1] == "\n") or (i == 0)) and (i < len(data)-1) and ((data[i].isdigit()) and data[i+1:i+3] == ". ")):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "orderedlist"
                    segment["text"] = data[i]
                    i += 1
                    states.append(STATE_ORDERED_LIST)

                # Start of a new segment
                elif(data[i] == "\n" and (i < len(data)-1) and data[i+1] == "\n"):
                    #print "SEGMENT [%s]" % segment["text"]
                    #print "Start of new segment"
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = "" 
                    i += 1 

                # DEBUG BRAD: This is not implemented
                #  If a line is indented then we should treat all consecutive lines
                #  that have the same indent level as an indented block.
                #elif(data[i] == "\n" and (i < len(data)-1) and data[i+1] in (" ")):
                elif((data[i] == "\n") and (i < end) and (data[i+1] == " ")):
                    segments.append(segment)

                    # Look forward and see if there are anything but spaces. If not
                    # then we'll ignore it.
                    j = i+1
                    all_whitespace = True
                    while(j <= end and data[j] != "\n"):
                        if(data[j] != " "):
                            all_whitespace = False
                        j += 1


                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""

                    if(all_whitespace):
                        i = j
                        continue

                    #tmp = data[i:]
                    #tmp = tmp.replace(" ", ".")
                    
                    j = i+1

                    block = ""

                    same_indent = True
                    while(same_indent):
                        prefix = ""

                        while((j <= len(data)-1) and data[j] == ' '):
                            prefix += "0"
                            block += " "
                            j += 1
                        
                        if(j >= (len(data)-1)):
                            break

                        # Add the rest of the text to the end of the line
                        while((j <= len(data)-1) and data[j] != '\n'):
                            block += data[j]
                            j += 1

                        #print "data[%d] = [%s]" % (j, data[j])
                        block += "\n"

                        # Now that I've hit the newline get the indent
                        # level of the next line. If it is the same then
                        # continue adding this line to the current paragraph
                        #
                        # If it is different then stop processing
                        j += 1
                        #print "REMAINDER: [%s]" % data[j:]
                        indent = self.get_indent_of_line(data, j)

                        #if(indent != prefix):
                        if(len(indent) < 4):
                            same_indent = False
                            #print "indent [%s] != prefix [%s]" % (indent,prefix)
                            break

                    segment["text"] = block

                    #print "   TEXT: [%s]" % segment["text"]
                    #i = j+1
                    i = j
                    
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""

                    #i += 2

                elif(data[i:i+3] == "```"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "code"
                    segment["text"] = ""
                    i += 3
                    states.append(STATE_CODE_BACKTICKS)
                    
                    # Search forward till we find the end of line. Everything
                    # up till then is the language specifier
                    language = ""
                    while(i < end and data[i] != "\n"):
                        language += data[i]
                        i += 1
                    segment["language"] = language

                elif(data[i] == "{" and data[i+1] == "{"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "code"
                    segment["text"] = ""
                    i += 2
                    states.append(STATE_CODE)

                elif(data[i] == '@' and data[i+1] == "{"):
                    #segments.append(segment)
                    #segment = {}
                    #segment["type"] = "text"
                    segment["text"] += "@"
                    i += 1
                    states.append(STATE_INLINE)
                
                # Check for inline quotes
                elif((i == 0 and data[i] == ">") or (data[i-1] == "\n" and data[i] == ">")):
                    i += 1
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "quote"
                    segment["text"] = ""
                    states.append(STATE_QUOTE)
                
                else:
                    #print "In Else block"
                    segment["text"] += data[i]
                    i += 1

            elif(state == STATE_INLINE):
                if(data[i] == "}"):
                    segment["text"] += "}"
                    i += 1
                    #segments.append(segment)
                    #segment = {}
                    #segment["type"] = "text"
                    #segment["text"] = ""
                    states.pop()
                else:
                    segment["text"] += data[i]
                    i += 1

            elif(state == STATE_CODE):
                #print "PARSING CODE"
                
                if(data[i] == "}" and data[i+1] == "}"):
                    segment["text"] += ""
                    i += 2
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    states.pop()
                else:
                    segment["text"] += data[i]
                    i += 1


            elif(state == STATE_CODE_BACKTICKS):
                if(data[i:i+3] == "```"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    
                    i += 3


                    states.pop()
                else:
                    segment["text"] += data[i]
                    i += 1


            elif(state == STATE_LIST):
                #print "PARSING LIST"
                if(data[i] == "\n" and (i > len(data)-2 or data[i+1] == "\n")):
                    segment["text"] += data[i]
                    i += 2 
                    segments.append(segment)
                    states.pop()
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                else:
                    segment["text"] += data[i]
                    i += 1
                #print "  [%s]" % segment["text"]

            elif(state == STATE_ORDERED_LIST):
                if(data[i] == "\n" and (i > len(data)-2 or data[i+1] == "\n")):
                    segment["text"] += data[i]
                    i += 2 
                    segments.append(segment)
                    states.pop()
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                else:
                    segment["text"] += data[i]
                    i += 1


            elif(state == STATE_QUOTE):
                if(data[i] == "\n" and data[i+1] != ">"):
                    segment["text"] += data[i]
                    i += 1
                    segments.append(segment)
                    states.pop()
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                else:
                    if(data[i] == "\n" and data[i+1] == ">"):
                        segment["text"] += data[i]
                        i += 2
                    else:
                        segment["text"] += data[i]
                        i += 1


        if(segment["text"] != ""):
            segments.append(segment)

        #s = 0
        #for segment in segments:
        #    print "SEGMENT[%d]: [%s]" % (s,segment)
        #    s+=1
        paragraphs = []

        for segment in segments:
            indent = 0
            text = segment["text"]
            type = segment["type"]

            #print "Segment"
            #print text

            for i in range(0, len(text)):
                if(text[i] == ' '):
                    indent += 1
                else:
                    break

            is_code = False
            is_list = False
            is_table = False
            is_quote = False
            
            # Handle any code blocks detected within the
            # textblock. Code blocks are represented by {{ }}
            if(type == "code"):
                #print "TEXT = [%s]" % text
                text = self.parse_block(text)
                is_code = True
                type = textblock_t.TYPE_CODE
            
            elif(type == "quote"):

                #text = self.parse_block(trim_leading_indent(text))
                text = self.parse_block(text)
                is_quote = True
                type = textblock_t.TYPE_QUOTE

            elif(type == "list"):

                #print "LIST: [%s]" % text
                
                elements = self.parse_list(text, "")

                text = elements
                is_list = True

                type = textblock_t.TYPE_LIST

            elif(type == "orderedlist"):
                #print "LIST: [%s]" % text

                # For ordered lists we need to strip off any 1. prefix
                # to make it easier for shorte to parse.
                lines = text.split("\n")
                output = []
                for line in lines:
                    line = re.sub(r"^(\s*)[0-9]+\.", r"\1-", line)
                    output.append(line)

                elements = self.parse_list("\n".join(output), "")

                text = elements
                is_list = True

                type = textblock_t.TYPE_ORDERED_LIST


            elif(type == "table"):
                elements = self.parse_table(text, "")

                text = elements
                is_table = True

                type = textblock_t.TYPE_TABLE

            else:
                type = textblock_t.TYPE_TEXT
                text = trim_blank_lines(text)

            language = "c"
            if(segment.has_key("language")):
                language = segment["language"]

            paragraphs.append({
                "indent":indent,
                "type":type,
                "text":text,
                "code":is_code,
                "language":language,
                "list":is_list,
                "quote":is_quote,
                "table":is_table})
        
        self.paragraphs = paragraphs
        return paragraphs

    def __str__(self):
        '''This method is called to output a textblock as a human
           readable string for debug purposes'''
        output =  "Textblock\n"
        output += "=========\n"
        output += "  num paragraphs: %d\n" % len(self.paragraphs)
        for paragraph in self.paragraphs:
            ptype = paragraph["type"]
            output += "  paragraph:\n"
            output += "    type: %s\n" % self.translate_type(ptype)

            if(ptype in (textblock_t.TYPE_TEXT, textblock_t.TYPE_CODE, textblock_t.TYPE_QUOTE)):
                lines = paragraph["text"].split("\n")
                for line in lines:
                    output += "    [%s]\n" % line
            elif(ptype == textblock_t.TYPE_ORDERED_LIST):
                output += "    data:\n"
                items = paragraph["text"]
                for item in items:
                    output += item.__str__(6)

        return output


if __name__ == "__main__":

    text = """
1. Part 1
    2. Part 1A
3. Part 2

This is a block of text

    # This line is indented
    this is a line
    this is also a line
        this is indented further
        so is this

This is some more text

And a new paragraph and a table:
@{table,
- One   | Two
- Three | Four
}

"""
    tb = textblock_t(text)
    print tb
