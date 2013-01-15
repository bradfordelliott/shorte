
class parser_t:

    def __init__(self):

        do_nothing=1
    
    
    def strip_indent(self, input, indent):

        if(indent == 0):
            return input

        #print "INPUT=[%s], indent=%d" % (input, indent)

        for i in range(0, indent+1):
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
            indent = item[1]
            text   = item[0].strip()
            children = None

            #print "%*sitem=%s, indent=%d" % (x*3, " ", text, indent)

            # Check to see if the next element has a greater
            # indent, if it is then it's a child
            if(i+1 < len(items)):
                next_item = items[i+1]
                next_indent = next_item[1]
                next_text = next_item[0].strip()
                
                # If the next node in the list has a smaller
                # indent then we've hit the end of this branch
                if(next_indent < indent):
                    #print "%*sstopping at %s, curr_text = %s" % (x*3, " ", next_text, text)
                    #print "%*sAdding node %s" % (x*3, " ", text)
                    node = {}
                    node["text"] = text
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
            node = {}
            node["text"] = text
            if(children != None):
                if(len(children) > 0):
                    node["children"] = children
                    children = []

            nodes.append(node)

            # Check the next item in the list and make sure it's not
            # then end of this level
            if(i < len(items)):
                next_item = items[i]
                next_indent = next_item[1]
                if(next_indent < indent):
                    #print "Next item %s is up one level" % next_item[0].strip()
                    i -= 1
                    break

        return (i+1,nodes)

    def parse_list(self, source, modifiers):

        items = []
        item = ""
        item_indent = 0

        for i in range(0, len(source)):

            if(source[i] == '-'):

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
                    item += source[i]
                    continue

                # Output the last item if it exists
                if(item != ""):
                    items.append([item, item_indent])
                item = ""

                # Figure out the indent level of this item
                item_indent = 0
                j = i
                while(j >= 0):
                    if(source[j] == '\n'):
                        break
                    j -= 1
                    item_indent += 1
                

            else:
                item += source[i]

        if(item != ""):
            items.append([item, item_indent])

        (i, list) = self.parse_list_child(0, items)

        #for elem in list:
        #    print elem

        return list

    def parse_textblock(self, data):

        STATE_NORMAL = 0
        STATE_LIST = 1
        STATE_CODE = 2
        states = []
        states.append(STATE_NORMAL)

        segments = []
        segment = {}
        segment["type"] = "text"
        segment["text"] = ""
        i = 0

        #print "DATA: [%s]" % data

        while(i < len(data)):

            state = states[-1]

            if(state == STATE_NORMAL):
                if(data[i] == "-"):
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

                # Start of a new segment
                elif(data[i] == "\n" and (i < len(data)-1) and data[i+1] == "\n"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "text"
                    segment["text"] = ""
                    i += 2 
                elif(data[i] == "{" and data[i+1] == "{"):
                    segments.append(segment)
                    segment = {}
                    segment["type"] = "code"
                    segment["text"] = ""
                    i += 2
                    states.append(STATE_CODE)
                else:
                    segment["text"] += data[i]
                    i += 1
            elif(state == STATE_CODE):
                
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
            elif(state == STATE_LIST):
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

        if(segment["text"] != ""):
            segments.append(segment)

        #for segment in segments:
        #    print "SEGMENT: \n%s" % segment

        paragraphs = []

        for segment in segments:
            indent = 0
            text = segment["text"]
            type = segment["type"]

            #print "Segment [%s]" % segment

            for i in range(0, len(text)):
                if(text[i] == ' '):
                    indent += 1
                else:
                    break

            is_code = False
            is_list = False
            
            # Handle any code blocks detected within the
            # textblock. Code blocks are represented by {{ }}
            if(type == "code"):
                #print "TEXT = [%s]" % text
                text = self.parse_block(text)
                is_code = True
            elif(type == "list"):

                #print "LIST: [%s]" % text

                elements = self.parse_list(text, "")

                text = elements
                is_list = True

            paragraphs.append({
                "indent":indent,
                "text":text,
                "code":is_code,
                "list":is_list})
        
        return paragraphs
    
    
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


        STATE_TAG = 0
        STATE_VALUE = 2
        STATE_STRING = 1

        tag = ""
        value = ""
        string = ""

        #print "MODIFIERS: [%s]" % modifiers

        tags = {}
        states = []
        states.append(STATE_TAG)

        i = 0
        while i < len(modifiers):

            state = states[-1]

            #print "STATE: %d, char: %c" % (state, modifiers[i])

            if(modifiers[i] == '\\'):
                i += 1
                continue

            if(state == STATE_TAG):

                if(modifiers[i] == "="):
                    value = ""
                    states.append(STATE_VALUE)
                else:
                    tag += modifiers[i]
                    #print "building tag: %s" % tag

            elif(state == STATE_STRING):
                
                if(modifiers[i] == '"' and modifiers[i-1] != '\\'):
                    states.pop()
                else:
                    string += modifiers[i]

            elif(state == STATE_VALUE):
               
                value += string
                string = ""
                
                if(modifiers[i] == '"'):
                    states.append(STATE_STRING)

                elif(modifiers[i] == " "):

                    tags[tag.strip()] = value.strip()

                    #print "Adding tag: %s" % tag
                    tag = ""
                    value = ""
                    states.pop()

                else:
                    value += modifiers[i]

            i += 1

        if(value != "" or string != ""):
            value += string
            #print "tag = %s, value = %s" % (tag, value)
            tags[tag.strip()] = value.strip()
        elif(tag != ""):
            tags[tag.strip()] = ""


        #for tag in tags:
        #    print "TAG: [%s] = [%s]" % (tag, tags[tag])

        return tags
