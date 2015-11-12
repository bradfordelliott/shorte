import sys

class span_t(object):
    def __init__(self):
        self.children = []
        self.source = ""
    
    def parse(self, source):

        i = 0
        end = len(source)

        STATE_NORMAL = 0
        STATE_BACKTICKS = 1
        STATE_LIST = 2
        STATE_ORDERED_LIST = 3
        STATE_QUOTE_BLOCK = 4

        states = []
        states.append(STATE_NORMAL)

        parents = [self]

        span = textspan_t()
        while(i < end):
            state = states[-1]

            if(len(parents) > 1):
                parent = parents[-1]
            else:
                parent = self

            if(state == STATE_NORMAL):
                
                # If the line starts with - or * then treat it
                # as a list. If it is ** then it is actually bold text
                if(source[i] == "-"): #  or (data[i] == "*" and (i+1 < len(data) and data[i+1] != "*"))):
                    if(i == 0 or source[i-1] == "\n"):
                        parent.children.append(span)
                        span = listblock_t()
                        span.source += "-"
                        states.append(STATE_LIST)
                        i += 1
                    else:
                        span += data[i]
                        i += 1

                # If the line starts with a number followed by . and then a space then it
                # must be the start of an ordered list
                elif((i == 0 or source[i-1] == "\n") and (i < len(source)-1) and ((source[i].isdigit()) and source[i+1:i+3] == ". ")):
                    parent.children.append(span)
                    span = listblock_t()
                    span.source += source[i]
                    states.append(STATE_ORDERED_LIST)
                    i += 1

                elif((i == 0 or source[i-1] == "\n") and (source[i] == ">")):
                    parent.children.append(span)
                    span = quoteblock_t()
                    span.source += source[i]
                    states.append(STATE_QUOTE_BLOCK)
                    i += 1

                elif(source[i:i+3] == "```"):
                    parent.children.append(span)
                    span = textspan_t()
                    states.append(STATE_BACKTICKS)
                    i += 3
                    
                    # Search forward till we find the end of line. Everything
                    # up till then is the language specifier
                    language = ""
                    while(i < end and source[i] != "\n"):
                        language += source[i]
                        i += 1
                    span = codeblock_t(language)

                else:
                    span.source += source[i]
                    i += 1

            elif(state == STATE_BACKTICKS):
                if(source[i:i+3] == "```"):
                    parent.children.append(span)
                    states.pop()
                    if(len(parents) > 1):
                        span = parents.pop()
                    else:
                        span = textspan_t()

                    i += 3
                else:
                    span.source += source[i]
                    i += 1

            elif(state == STATE_LIST):
                if(source[i] == "\n" and (i > len(source)-2 or source[i+1] == "\n")):
                    span.source += source[i]
                    i += 2
                    parent.children.append(span)
                    states.pop()
                    if(len(parents) > 1):
                        span = parents.pop()
                    else:
                        span = textspan_t()
                else:
                    span.source += source[i]
                    i += 1
            
            elif(state == STATE_ORDERED_LIST):
                if(source[i] == "\n" and (i > len(source)-2 or source[i+1] == "\n")):
                    span.source += source[i]
                    i += 2
                    parent.children.append(span)
                    states.pop()

                    if(len(parents) > 1):
                        span = parents.pop()
                    else:
                        span = textspan_t()
                else:
                    span.source += source[i]
                    i += 1

            elif(state == STATE_QUOTE_BLOCK):
                if(source[i-1] == "\n" and source[i] != ">"):
                    span.source += source[i]
                    i += 1
                    parent.children.append(span)
                    states.pop()

                    if(len(parents) > 1):
                        span = parents.pop()
                    else:
                        span = textspan_t()
                else:
                    span.source += source[i]
                    i += 1


            else:
                print("Invalid state encountered!");
                sys.exit(-1)

        if(len(span.source) != 0):
            parent.children.append(span)
    def __str__(self, prefix=""):
        output =  "%s%s\n" % (prefix, type(self).__name__)
        output += "%s---------\n" % prefix
        lines = self.source.split("\n")
        for line in lines:
            output += "%s%s\n" % (prefix + "   >", line)

        for child in self.children:
            output += child.__str__(prefix + "   >")

        return output

class quoteblock_t(span_t):
    def __init__(self):
        span_t.__init__(self)

class codeblock_t(span_t):
    def __init__(self, language):
        span_t.__init__(self)
        self.language = language

class listblock_t(span_t):
    def __init__(self):
        span_t.__init__(self)

class textspan_t(span_t):
    def __init__(self):
        span_t.__init__(self)

class textblock_t(span_t):

    def __init__(self, source):
        span_t.__init__(self)

        self.source = source
        self.children = []
        self.parse(source)

    def __str__(self, prefix=""):
        output =  "%sTextblock\n" % prefix
        output += "%s---------\n" % prefix

        for elem in self.children:
            if(type(elem) is str):
                lines = elem.split("\n")
                for line in lines:
                    output += "%s%s\n" % (prefix + "   >", line)
            else:
                output += elem.__str__(prefix + "   >")

        return output

if __name__ == "__main__":

    text = """
1. Part 1
    2. Part 1A
       
       This is a second line in the list item
       
           This is a block of text within a list
           and another paragraph
       
       This is the remainder of the list item
       
       ```c
       a code block in back ticks
       This is another paragraph in
       the code block
       ```
3. Part 2
4. XXX
5. YYY
6. A
7. B
8. C
9. D
10. E
11. F
12. G

This is another paragraph here with a list in it:

- one
    
    > This is a quote within a list item.
    > that spans multiple lines
    >
    > ```c
    > with a nested code block
    > ```
    
    and this is a new paragraph in that same
    list item with a nested code block
    
        A nested code block
        that spans multiple lines.
- two
- three
    - four
        - five

Followed by an indented code block

    Indented block

> This is a quote
> This is also part of that quote

This is a final paragraph
"""
    tb = textblock_t(text)
    print tb

