from src.shorte_defines import *
from src.textblock import list_item_t, textblock_t

class parser_t:

    def __init__(self):

        # The list of tags that qualify as source code elements
        self.m_source_code_tags = {
            "python"     : True,
            "perl"       : True,
            "shell"      : True,
            "c"          : True,
            "cpp"        : True,
            "sql"        : True,
            "code"       : True,
            "batch"      : True,
            "vera"       : True,
            "bash"       : True,
            "java"       : True,
            "verilog"    : True,
            "tcl"        : True,
            "shorte"     : True,
            "xml"        : True,
            "swift"      : True,
            "go"         : True,
            "javascript" : True,
            }
    
    def tag_is_header(self, tag_name):
        if(tag_name in ("h1", "h2", "h3", "h4", "h5", "h")):
            return True

        return False

    def tag_is_executable(self, tag_name):

        if(tag_name in ("python", "perl", "d", "c", "cpp", "vera", "bash", "java", "verilog", "tcl", "batch", "swift", "go", "javascript", "shorte")):
            return True

        return False
    
    def tag_is_source_code(self, tag_name):

        if(self.m_source_code_tags.has_key(tag_name)):
            return True

        return False
    
    def get_attribute_as_bool(self, attributes, key):
    
        if(attributes.has_key(key)):
            val = attributes[key]
    
            if(val in ("True", "true", "1")):
                return True
            elif(val in ("False", "false", "0")):
                return False
            else:
                FATAL("Can't parse attribute")
    
        return False
    
    def get_attribute_as_string(self, attributes, key):
        if(attributes.has_key(key)):
            return attributes[key]
        return ""

    def get_attribute_as_int(self, attributes, key):
        if(attributes.has_key(key)):
            val = int(attributes[key], 10)
            return val
        return 0
    
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

        items = []
        item = []
        item_indent = 0
        #print "PARSING LIST: [%s]" % source

        STATE_NORMAL = 0
        STATE_INLINE_FORMATTING = 1

        state = STATE_NORMAL

        for i in range(0, len(source)):

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
            litem.set_text(''.join(item))
            litem.indent = item_indent
            items.append(litem)

        (i, list) = self.parse_list_child(0, items)

        #for elem in list:
        #    print elem

        return list

    def get_indent_of_line(self, data, start_of_line):

        i = start_of_line
        indent = []
        len_data = len(data)

        while(i < len_data and data[i] == ' '):
            indent.append('0')
            i += 1
        
        return ''.join(indent)


    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    parse_modifiers()
    #|
    #| DESCRIPTION:
    #| 
    #| PARAMETERS:
    #|    modifiers    (I) - Modifiers impacting the source
    #| 
    #| RETURNS:
    #|    Dictionary containing any code modifiers. Currently consists of   
    #|      source  - The name of the source machine
    #|      machine - The target machine to execute on
    #|
    #+-----------------------------------------------------------------------------
    def parse_modifiers(self, modifiers):

        return shorte_parse_modifiers(modifiers)

