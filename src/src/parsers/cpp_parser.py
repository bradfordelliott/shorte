#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   cpp_parser.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a parser class used to
#|   parse C++ source files in order to retrieve information such as
#|   function definitions that can be used to generate Shorte
#|   documents.
#|
#|   At some point this should be replaced with a proper C/C++
#|   parser.
#|
#+----------------------------------------------------------------------------

#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import sys
import os
from shorte_parser import *
import platform
import time

from shorte_source_code import *

try:
    from libs.cairo_access import cairo
except:
    print "WARNIING: Failed to load cairo_access library"
    
from libs.records import *


TOKEN_STRING        = (1,  "STRING")
TOKEN_LINE_COMMENT  = (4,  "LINE_COMMENT")
TOKEN_COMMENT       = (5,  "COMMENT")
TOKEN_PREPROCESSOR  = (6,  "PREPROCESSOR")
TOKEN_OPEN_BRACKET  = (10, "OPEN_BRACKET", "(")
TOKEN_CLOSE_BRACKET = (11, "CLOSE_BRACKET", ")")
TOKEN_OPEN_BRACE    = (12, "OPEN_BRACE", "{")
TOKEN_CLOSE_BRACE   = (13, "CLOSE_BRACE", "}")
TOKEN_CODE          = (14, "CODE")
TOKEN_WHITESPACE    = (15, "WHITESPACE")
TOKEN_KEYWORD       = (16, "KEYWORD")
TOKEN_SEMICOLON     = (17, "SEMICOLON", ";")
TOKEN_EQUALS        = (18, "EQUALS", "=")
TOKEN_OPEN_SQ_BRACKET = (19, "OPEN_SQBRACKET", "[")
TOKEN_CLOSE_SQ_BRACKET = (20, "CLOSE_SQBRACKET", "]")
TOKEN_WHITESPACE    = (21, "SPACE", " ")

def TYPE(token):
    return token["type"][0]

def SKIP(tokens):

    skip = {}
    for token in tokens:
        skip[token] = 1

    return skip

def TARGET(tokens):

    skip = {}
    for token in tokens:
        skip[token] = 1

    return skip





def my_token(typ, data, line, pos):
    t = {}
    t["type"] = typ
    t["data"] = data
    t["line"] = line
    t["pos"]  = pos - len(data) + 1

    return t

        
class cpp_parser_t(shorte_parser_t):
    def __init__(self, engine):

        self.m_engine = engine

        shorte_parser_t.__init__(self, engine)

        c = source_code_t()
        self.m_keywords = c.get_keyword_list("c")

        self.m_author = "Unknown"
        self.m_file_brief = ""
            

    def is_keyword(self, source):

        if(self.m_keywords.has_key(source)):
            return True

        return False

    def get_next_token(self, tokens, pos, token_types):

        token = tokes[pos+1]

        return (pos+1, token)

    def get_prev_token(self, tokens, pos, token_types):

        token = tokens[pos-1]
        return (pos-1, token)

    def match_token(self, token, definition, value=None):

        if(value == None):
            value = definition[2]

        if(token["type"][0] == definition[0] and
           token["data"] == value):
            return True

        return False
    
    # Parse a C++ structure and store it
    def parse_cpp_struct(self, tokens, i):
        '''This method is called to parse the contents of a C/C++
           structure in order to extract a shorte object describing
           the structure.

           @param self   [I] - The parser class instance
           @param tokens [I] - The list of tokens from the parsed file.
           @param i      [I] - The current position in the token list.
           '''

        pos_saved = i

        k = i
        desc = []
        token = tokens[k]
        while(k >= 0):

            #print "  TK[%s]" % token["data"]

            if(token["type"][0] == TOKEN_KEYWORD[0] or
               token["type"][0] == TOKEN_CODE[0] or
               token["type"][0] == TOKEN_WHITESPACE[0]):
                donothing=1
            elif(token["type"][0] == TOKEN_LINE_COMMENT[0]):
                desc.append('\\n')
                desc.append(token["data"])
            elif(token["type"][0] == TOKEN_COMMENT[0]):
                desc.append(token["data"])
                break
            else:
                break

            k -= 1
            token = tokens[k]

        desc.reverse()
        desc = " ".join(desc)

        if(not desc.startswith("/**")):
            return None

        comment = self.parse_cpp_func_comment(desc)
        extract_private = self.m_engine.get_config("cpp_parser", "extract_private")
        if(extract_private == "1"):
            extract_private = True
        else:
            extract_private = False

        if(not extract_private and True == comment["private"]):
            raise Exception("Not outputting private structures")

        # Determine if this is a typedef'ed enum or not. That will
        # determine where we look for the struct name or type
        (k,src) = self.walk_backwards(i-1,tokens,TARGET([TOKEN_KEYWORD]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
        if(k >= 0 and (tokens[k+1]["data"] == "typedef")):
            is_typedef = True
        else:
            is_typedef = False

        struct_name = ""

        # If it's not a typedef search for the name right after the
        # struct keyword
        if(not is_typedef):
            (k,src) = self.walk_forward(i+1,tokens,TARGET([TOKEN_CODE]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
            struct_name = tokens[token][k]["data"]

        # Walk forward until I hit the opening brace
        while(not self.match_token(token, TOKEN_OPEN_BRACE)):
            i += 1
            token = tokens[i]

        # Walk to the closing brace building up the struct
        struct_body = ''
        data = ""
        while(not self.match_token(token, TOKEN_CLOSE_BRACE)):
            i += 1
            struct_body += data
            token = tokens[i]
            data = token["data"]

        rows = self.parse_struct_fields(struct_body)

        # Walk to the semicolon ending the struct
        while(not self.match_token(token, TOKEN_SEMICOLON)):

            i += 1
            token = tokens[i]

        if(is_typedef):

            # Once we've hit the semicolon walk backwards until
            # we find the struct name. We need
            # to skip any whitespace, comments, and the closing }
            (k,src) = self.walk_backwards(i-1,tokens,TARGET([TOKEN_CODE]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE, TOKEN_CLOSE_BRACE]))

            struct_name = tokens[k+1]["data"]


        max_cols = 0
        for row in rows:
            cols = len(row["cols"])
            if(cols > max_cols):
                max_cols = cols

        struct = {}
        struct["rows"] = rows
        struct["fields"] = rows
        struct["title"] = struct_name
        struct["caption"] = self.parse_textblock(comment["desc"])
        struct["max_cols"] = max_cols
        

        i = pos_saved
        token = tokens[i]

        while(not self.match_token(token, TOKEN_CLOSE_BRACE)):

            #print "    STRUCT: %s" % token["data"]
            i += 1

            if(i >= len(tokens)):
                return i - 1

            token = tokens[i]

        while(not self.match_token(token, TOKEN_SEMICOLON)):
            #print "    STRUCT: %s" % token["data"]
            i += 1
            
            if(i >= len(tokens)):
                return i - 1
            token = tokens[i]
            
        #print "    STRUCT: %s" % struct
        

        return (i, struct)


    def parse_enum_values(self, text):

        rows   = []
        states = []

        #print "ENUM_VALUES = %s" % text
        #sys.exit(-1)

        STATE_NORMAL = 0
        STATE_COMMENT = 1
        STATE_VALUE   = 2

        states.append(STATE_NORMAL)

        enum = ""
        desc = ""
        value = ""

        #print "TEXT: [%s]" % text
        enums = []

        i = 0
        while(i < len(text)):

            state = states[-1]

            if(state == STATE_NORMAL):
                if(text[i:i+4] == "/**<"):
                    #print "start of comment"
                    states.append(STATE_COMMENT)
                    desc = "/**<"
                    i += 4
                    continue
                elif(text[i:i+3] == "/**"):
                    #print "start of comment"
                    states.append(STATE_COMMENT)
                    desc = "/**"
                    i += 3
                    continue
                elif(text[i:i+2] == "/*"):
                    states.append(STATE_COMMENT)
                    desc = "/*"
                    i += 2
                    continue
                elif(text[i] == "="):
                    value = ""
                    states.append(STATE_VALUE)
                elif(text[i] == ","):
                    value = ""
                    enums.append({"key"   : enum.strip(" \n"),
                                  "value" : value.strip(" \n"),
                                  "desc"  : trim_leading_indent(self.format_comment(desc))})
                    enum  = ""
                    value = ""
                    desc  = ""
                else:
                    enum += text[i]
            elif(state == STATE_COMMENT):
                if(text[i:i+2] == "*/"):
                    desc += "*/"
                    #print "End of comment: desc = [%s]" % desc
                    states.pop()
                    i += 2
                    continue
                else:
                    desc += text[i]

            elif(state == STATE_VALUE):
                if(text[i] == ","):
                    states.pop()
                    enums.append({"key"   : enum.strip(" \n"),
                                  "value" : value.strip(" \n"),
                                  "desc"  : trim_leading_indent(self.format_comment(desc))})
                    enum  = ""
                    value = ""
                    desc  = ""
                else:
                    value += text[i]
            
            i += 1


        if(enum.strip() != ""):
            enums.append({"key"   : enum.strip(" \n"),
                          "value" : value.strip(" \n"),
                          "desc"  : self.format_comment(desc)})

        for enum in enums:

            row = {}
            row["cols"] = []
            row["is_subheader"] = False
            row["is_header"] = False
            row["is_title"] = False
            row["is_reserved"] = False
            row["is_caption"] = False
            row["is_spacer"] = False

            col = {}
            col["span"] = 1
            col["text"] = enum["key"]
            row["cols"].append(col)
            
            col = {}
            col["span"] = 1
            col["text"] = enum["value"]
            row["cols"].append(col)
            
            col = {}
            col["span"] = 1
            col["text"] = enum["desc"]
            col["textblock"] = self.parse_textblock(enum["desc"])
            row["cols"].append(col)

            rows.append(row)

        ##expr = re.compile("\/\*\*?(.*?)\*\/\s*(.*?)\s*=\s*(.*?),", re.DOTALL)
        #expr = re.compile("\/\*\*?(.*?)\*\/\s*(.*?)(\s*=\s*([A-Za-z0-9]+),|\s+})", re.DOTALL)
        ##expr = re.compile("(\/\*\*?(.*?)\*\/)?\s*(.*?)\s*=\s*([A-Za-z0-9]+)(,|\s*})", re.DOTALL)
        #matches = expr.search(text)

        #while(matches != None):
        #    row = {}
        #    row["cols"] = []
        #    row["is_subheader"] = False
        #    row["is_header"] = False
        #    row["is_reserved"] = False
        #    row["is_caption"] = False
        #    row["is_spacer"] = False

        #    desc = matches.groups()[0]
        #    print "DESC: %s" % desc
        #    if(desc != None):
        #        desc = self.format_comment(desc)
        #        desc = re.sub("[ \n]+", " ", desc)
        #    else:
        #        desc = ""

        #    #print "2 = %s" % matches.groups()[2]

        #    col = {}
        #    col["span"] = 1
        #    col["text"] = matches.groups()[1]
        #    row["cols"].append(col)
        #    
        #    col = {}
        #    col["span"] = 1
        #    col["text"] = self.format_text(matches.groups()[2])
        #    row["cols"].append(col)
        #    
        #    col = {}
        #    col["span"] = 1
        #    col["text"] = self.format_text(desc)
        #    row["cols"].append(col)

        #    rows.append(row)

        #    matches = expr.search(text, matches.end() + 1)

        #print rows
        #sys.exit(-1)
        return rows
    
    def parse_struct_fields(self, text):
        '''This method is called to parse the individual fields within a
           structure definition. It currently does this using a regular
           expression.

           @param self [I] - The parser class instance
           @param text [I] - The text to extract field definitions from

           @return An array of rows containing the fields of the structure.
           '''

        rows   = []
        states = []

        #print "TEXT: %s" % text

        expr = re.compile("\/\*\*<?(.*?)\*\/\s*([^ ]+)\s*(.*?);", re.DOTALL)
        matches = expr.search(text)

        while(matches != None):
            row = {}
            row["cols"] = []
            row["is_subheader"] = False
            row["is_header"] = False
            row["is_title"] = False
            row["is_reserved"] = False
            row["is_caption"] = False
            row["is_spacer"] = False

            desc = matches.groups()[0]
            desc = self.format_comment(desc)
            desc_original = desc
            desc = re.sub("[ \n]+", " ", desc)
            #print "DESC: %s" % desc

            fname = matches.groups()[2].strip()
           
            # Check to see if the field is a bitfield
            is_bitfield = False
            fbits = 0
            submatches = re.search("(.*?):(.*)", fname)
            if(submatches != None):
                #print "fname = %s, sub = [%s]" % (fname, submatches.groups()[1])
                fname = submatches.groups()[0].strip()
                fbits = int(submatches.groups()[1].strip())
                is_bitfield = True
            
            extract_width = False

            # Check to see if the field is an array
            is_array = False
            farry = 0
            submatches = re.search("(.*?)\[(.*?)\]", fname)
            if(submatches != None):
                fname = submatches.groups()[0].strip()
                #print "fname = %s" % fname
                if(extract_width):
                    farray = int(submatches.groups()[1].strip())
                is_array = True

            ftype = matches.groups()[1]

            fspec = ""
            if(extract_width):
                if(ftype == "cs_uint8"):
                    fspec = 1
                elif(ftype == "cs_uint16"):
                    fspec = 2
                elif(ftype == "cs_uint32"):
                    fspec = 4
                elif(ftype == "cs_uint64"):
                    fspec = 8
                else:
                    fspec = ftype
                if(is_bitfield):
                    #print "fbits = [%s]" % fbits
                    fspec = "%s" % (fbits/8)
                elif(is_array):
                    if(isinstance(fspec,int)):
                        fspec = "%dx%s" % (int(fspec)*8, farray)
                    else:
                        fspec = "%sx%s" % (fspec, farray)
            else:
                fspec = ftype

            #print "fspec = %s" % fspec

            col = {}
            col["span"] = 1
            col["text"] = fspec
            row["cols"].append(col)
            
            col = {}
            col["span"] = 1
            col["text"] = fname
            row["cols"].append(col)
            
            col = {}
            col["span"] = 1
            col["text"] = desc
            # Format the description as a textblock instead of standard text
            #print "DESC_ORIG: [%s]" % desc_original
            col["textblock"] = self.parse_textblock(trim_leading_blank_lines(desc_original))
            row["cols"].append(col)

            row["attrs"] = row["cols"]

            rows.append(row)

            matches = expr.search(text, matches.end() + 1)

        #sys.exit(-1)

        return rows

    # Strip formatting from a comment to make it
    # format agnostic
    def format_comment(self, comment, strip_single_line_comments=True):

        #print "COMMENT_BEFORE\n[%s]" % comment

        comment = re.sub("/\*\*\<", "", comment)
        comment = re.sub("/\*", "", comment)
        comment = re.sub("\*/", "", comment)
        comment = re.sub("^\s*\*", "", comment, re.MULTILINE)

        expr = re.compile("^\s*\*", re.MULTILINE)
        comment = expr.sub("", comment)
        
        if(strip_single_line_comments):
            #comment = re.sub(" +", " ", comment)
            comment = re.sub("//", "", comment)
        
        #print "COMMENT_1\n[%s]" % comment
        comment = trim_leading_blank_lines(comment)
        #print "COMMENT_2\n[%s]" % comment
        comment = trim_leading_indent(comment)
        #print "COMMENT_3\n[%s]" % comment

        return comment

    def format_text(self, text):
        #text = re.sub(" *", " ", text)
        text = re.sub("#", "\#", text)

        return text

    def parse_cpp_func_comment(self, text):
        '''This method is called to parse a comment associated with a C/C++
           function in order to extract the associated fields.

           @param self [I] - The parser class instance
           @param text [I] - The text to parse.

           @return A dictionary containing the comment attributes.
        '''

        comment = {}

        text = self.format_comment(text, strip_single_line_comments=False)
        comment["params"] = {}
        comment["returns"] = ""
        comment["example"] = ""
        comment["private"] = False
        comment["see_also"] = None
        comment["deprecated"] = None

        # Strip off any \ref sequences since shorte doesn't use them
        expr_ref = re.compile("([@\\\]ref\s+[A-Za-z][A-Za-z0-9_]+)", re.DOTALL)
        text = expr_ref.sub("", text)
        
        # Strip off any leading ingroup tag before the description
        # since shorte doesn't support that right now.
        expr_ingroup = re.compile("([@\\\]\s*ingroup(.*?)\n)", re.DOTALL)
        matches = expr_ingroup.search(text)
        if(matches != None):
            comment["ingroup"] = matches.groups()[1]
            #print "INGROUP: %s" % comment["ingroup"]
            text = text.replace(matches.groups()[0], "")
        
        # If there is no description assume the type is private
        if(len(text) == 0):
            comment["private"] = True

        matches = re.search("(.*?)(@[^{]|\\\)", text, re.DOTALL)

        if(matches != None):
            comment["desc"] = self.format_text(matches.groups()[0])
            comment["description"] = self.parse_textblock(trim_leading_blank_lines(matches.groups()[0]))
        else:
            comment["desc"] = self.format_text(text)
            comment["description"] = self.parse_textblock(trim_leading_blank_lines(text))

        #print "COMMENT:"
        #print comment["desc"]

        matches = re.search("[@\\\]private", text, re.DOTALL)
        if(matches != None):
            comment["private"] = True

        expr_param = re.compile("[@\\\]param *([^ ]*) *(([^@]|@{)*)", re.DOTALL)

        matches = expr_param.search(text)
        while(matches != None):
            name = self.format_text(matches.groups()[0])
            desc = self.format_text(matches.groups()[1])
            io = ""

            matches2 = re.search("\[(.*?)\] *- *(.*)", desc, re.DOTALL)
            if(matches2 != None):
                desc = matches2.groups()[1]
                io = matches2.groups()[0]

            comment["params"][name] = {}
            comment["params"][name]["desc"] = desc
            comment["params"][name]["io"] = io

            #print "name = %s (%s)" % (name, desc)
            matches = expr_param.search(text, matches.end())
        
        expr_return = re.compile("[@\\\]return *([^@]*)", re.DOTALL)

        matches = expr_return.search(text)
        if(matches != None):
            desc = self.format_text(matches.groups()[0])
            comment["returns"] = desc
        
        expr_example = re.compile("[@\\\]example *([^@]*)", re.DOTALL)
        matches = expr_example.search(text)
        if(matches != None):
            desc = matches.groups()[0]
            comment["example"] = desc
        
        expr_see_also = re.compile("[@\\\]see *([^@]*)", re.DOTALL)
        matches = expr_see_also.search(text)
        if(matches != None):
            comment["see_also"] = matches.groups()[0]

        expr_deprecated = re.compile("[@\\\]deprecated *([^@]*)", re.DOTALL)
        matches = expr_deprecated.search(text)
        if(matches != None):
            comment["deprecated"] = matches.groups()[0]
        
        return comment

    # Parse a C++ enumeration and store it
    def parse_cpp_enum(self, tokens, i):
        
        token = tokens[i]
        
        # See if there are any comments before the enum
        k = i
        desc = []
        token = tokens[k]
        while(k >= 0):

            #print "  TK[%s]" % token["data"]

            if(token["type"][0] == TOKEN_KEYWORD[0] or
               token["type"][0] == TOKEN_CODE[0] or
               token["type"][0] == TOKEN_WHITESPACE[0]):
                donothing=1
            elif(token["type"][0] == TOKEN_LINE_COMMENT[0]):
                desc.append('\\n')
                desc.append(token["data"])
            elif(token["type"][0] == TOKEN_COMMENT[0]):
                desc.append(token["data"])
                break
            else:
                break

            k -= 1
            token = tokens[k]

        desc.reverse()
        desc = " ".join(desc)

        if(not desc.startswith("/**")):
            return None

        comment = self.parse_cpp_func_comment(desc)

        #print "DESC: %s" % desc

        # Determine if this is a typedef'ed enum or not. That will
        # determine where we look for the enum name or type
        (k,src) = self.walk_backwards(i-1,tokens,TARGET([TOKEN_KEYWORD]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
        if(k >= 0 and (tokens[k+1]["data"] == "typedef")):
            is_typedef = True
        else:
            is_typedef = False

        enum_name = ""

        # If it's not a typedef search for the name right after the
        # enum keyword
        if(not is_typedef):
            (k,src) = self.walk_forward(i+1,tokens,TARGET([TOKEN_CODE]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
            enum_name = tokens[token][k]["data"]

        # Walk forward until I hit the opening brace
        while(not self.match_token(token, TOKEN_OPEN_BRACE)):
            i += 1
            token = tokens[i]

        # Walk to the closing brace building up the enum
        enum_body = ''
        data = ""
        while(not self.match_token(token, TOKEN_CLOSE_BRACE)):
            i += 1
            enum_body += data
            token = tokens[i]
            data = token["data"]

        rows = self.parse_enum_values(enum_body)

        # Walk to the end of the enum
        while(not self.match_token(token, TOKEN_SEMICOLON)):

            #print "    ENUM: %s" % token["data"]
            i += 1
            token = tokens[i]

        if(is_typedef):

            # Once we've hit the semicolon walk backwards until
            # we find the enum name. We need
            # to skip any whitespace, comments, and the closing }
            (k,src) = self.walk_backwards(i-1,tokens,TARGET([TOKEN_CODE]),
                    SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE, TOKEN_CLOSE_BRACE]))

            enum_name = tokens[k+1]["data"]

        text = "%s" % trim_leading_indent(comment["desc"])
        table = {}
        table["rows"] = rows
        table["title"] = enum_name

        # DEBUG BRAD: Not ready yet to treat enums as text blocks
        table["caption"] = self.parse_textblock(text)
        #table["caption"] = text

        max_cols = 0
        for row in rows:
            cols = len(row["cols"])
            if(cols > max_cols):
                max_cols = cols
        table["max_cols"] = max_cols

        return (i, table)


    # This method is called to a single parameter out of
    # the parameters passed to a C/C++ function.
    def parse_param(self, param):

        # First remove any leading and trailing whitespace
        param = param.strip()

        #print "PARAM: %s" % param

        if(len(param) == 0 or param == "void"):
            return None

        # Strip out any array operators
        param = re.sub("\[.*\]", "", param)
        # Strip out any asterisks
        param = re.sub("\*", "", param).strip()

        pieces = re.split("[ \t]+", param)
        
        if(len(pieces) > 1):

            ptype = ''
            for i in range(0, len(pieces)-1):
                ptype += pieces[i] + " "
            pname = pieces[-1]
        else:
            ptype = ''
            pname = pieces[0]

        #print "NAME: %s, TYPE: %s" % (pname, ptype)

        if(pname != "void"):
            field = {}

            # If the parameter has a pointer reference
            # then move it to the type
            pos = pname.find("*")
            if(-1 != pos):
                pname = pname[pos+1:]
                ptype += "*"

            #print "NAME: [%s]" % pname
            field["name"] = pname
            field["io"] = ""
            field["type"] = ptype
            field["desc"] = ("")
            field["desc2"] = self.parse_textblock("")

            return field

        return None

    # Parse parameters of a C/C++ function
    def parse_params(self, prototype):

        #print "    PARAMS: [%s]" % prototype
        prototype = re.sub("\n", " ", prototype)
        prototype = re.sub(" +", " ", prototype)
        matches = re.search("\((.*?)\)", prototype)

        parameters = []

        if(matches != None):
            params = re.split(",", matches.groups()[0])

            for param in params:
                #print "        PARAM: [%s]" % param

                field = self.parse_param(param)

                if(field != None):
                    parameters.append(field)

        return parameters

    def walk_backwards(self, i, tokens, target, skip):

        src = ''

        while(i >= 0):

            token = tokens[i]
            src += token["data"]

            #print("TOKEN: [%s]" % token["data"])
            if(skip.has_key(token["type"])):
                i -= 1
                #print "skipping %s" % token["data"]
                continue
            elif(target.has_key(token["type"])):
                return (i-1, src)
            else:
                # DEBUG BRAD: Need to look into whether this is real failure or not
                #print "TOKEN WITH FAILURE:"
                #print token
                raise Exception("Failed parsing ", token)
    
    def walk_forward(self, i, tokens, target, skip):

        src = ''

        while(i < len(tokens)):

            token = tokens[i]
            src += token["data"]

            #print("TOKEN: [%s]" % token["data"])
            if(skip.has_key(token["type"])):
                i += 1
                #print "skipping %s" % token["data"]
                continue
            elif(target.has_key(token["type"])):
                return (i+1, src)
            else:
                raise("Failed parsing %s" % token["type"][1])


    def parse_cpp_define(self, tokens, i):

        token = tokens[i]
        start = i
        end = False
        
        extract_private = self.m_engine.get_config("cpp_parser", "extract_private")
        if(extract_private == "1"):
            extract_private = True
        else:
            extract_private = False

        define = {}
        define["name"] = ''
        define["desc"] = ''
        define["source"] = token["data"]

        parts = token["data"].split(" ")
        define["name"] = parts[1].strip()
        parts.pop(0)
        parts.pop(0)
        val = ' '.join(parts)
        
        if(val[-1] == '\n'):
            val = val[0:-1]

        define["value"] = val

        try:
            # Search backwards till we find something that
            # isn't a comment or whitespace which indicates the
            # end of the define.
            #(i, src) = self.walk_backwards(i-1, tokens, TARGET([TOKEN_COMMENT]), SKIP([TOKEN_WHITESPACE]))
            (i, src) = self.walk_backwards(i-1, tokens, TARGET([TOKEN_COMMENT]), SKIP([]))

            comment = self.parse_cpp_func_comment(src)
            define["desc"] = comment["desc"]
            define["description"] = comment["description"]
            define["private"] = comment["private"]
        except:
            define["desc"] = ""
            define["description"] = ""
            define["private"] = True

        if(not extract_private and True == define["private"]):
            raise Exception ("not outputting private defines")


        return (start+1,define)

        


    # Parse a C++ function and turn it into a prototype definition
    def parse_cpp_function(self, tokens, i, source, is_prototype=False):
        '''This method is called to parse the contents of a C/C++
           function prototype in order to extract a shorte object
           describing the prototype.

           @param self         [I] - The parser class instance
           @param tokens       [I] - The list of tokens from the parsed file.
           @param i            [I] - The current position in the token list.
           @param source       [I] - The original source in non-tokenized format.
           @param is_prototype [I] - True if this a prototype that ends
                                     in a semicolon or False if it is actually
                                     the function definition.

           '''

        token = tokens[i]
        end = False
        brace_cnt = 0
        pos_definition = i

        function = {}
        function["name"] = ''
        function["desc"] = ""
        function["prototype"] = ""
        function["params"] = []
        function["returns"] = ""
        params = ''

        # Search backwards till we find the closing
        # bracket. If we hit anything other than a comment
        # or whitespace then it is probably not a function
        #print "Finding close bracket"
        (i, src) = self.walk_backwards(i-1, tokens, TARGET([TOKEN_CLOSE_BRACKET]), SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
        
        # Find the opening bracket
        #print "Finding open bracket"
        (i, src) = self.walk_backwards(i, tokens, TARGET([TOKEN_OPEN_BRACKET]), SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_CODE, TOKEN_KEYWORD, TOKEN_WHITESPACE, TOKEN_OPEN_SQ_BRACKET, TOKEN_CLOSE_SQ_BRACKET]))
        params += src

        # Find the function name
        (i, src) = self.walk_backwards(i, tokens, TARGET([TOKEN_CODE]), SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
        function["name"] = src.strip()
        #print "NAME: [%s]" % function["function_name"]

        # Find the function return type
        (i, src) = self.walk_backwards(i, tokens, TARGET([TOKEN_CODE, TOKEN_KEYWORD]), SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
        src = re.sub("[ \n]", "", src)
        function["returns"] = src

        # See if the word const was present before the return type
        try:
            (blah, blah2) = self.walk_backwards(i, tokens, TARGET([TOKEN_KEYWORD]), SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE]))
            function["returns"] = blah2.strip() + function["returns"]
            i = blah
        except:
            do_nothing = 1

        function["return_type"] = function["returns"]

        #print "RETURNS: [%s]" % src

        # See if there are any comments before
        # the function
        k = i
        desc = []
        token = tokens[k]
        while(k >= 0):

            #print "  TK[%s]" % token["data"]

            if(token["type"][0] == TOKEN_KEYWORD[0] or
               token["type"][0] == TOKEN_CODE[0] or
               token["type"][0] == TOKEN_WHITESPACE[0]):
                donothing=1
            elif(token["type"][0] == TOKEN_LINE_COMMENT[0]):
                desc.append('\\n')
                desc.append(token["data"])
            elif(token["type"][0] == TOKEN_COMMENT[0]):
                desc.append(token["data"])
                break
            else:
                break

            k -= 1
            token = tokens[k]

        desc.reverse()
        desc = " ".join(desc)

        if(not desc.startswith("/**")):
            return None
        
        func_comment = self.parse_cpp_func_comment(desc)

        function["see_also"] = func_comment["see_also"]

        if(func_comment["deprecated"] != None):
            function["deprecated"] = func_comment["deprecated"]

        extract_private = self.m_engine.get_config("cpp_parser", "extract_private")
        if(extract_private == "1"):
            extract_private = True
        else:
            extract_private = False

        output_pseudocode = self.m_engine.get_config("cpp_parser", "output_pseudocode")
        if(output_pseudocode == "1"):
            output_pseudocode = True
        else:
            output_pseudocode = False

        if(not extract_private and True == func_comment["private"]):
            raise Exception("Not outputting private functions")

        function["desc"] = func_comment["desc"]
        function["desc2"] = self.parse_textblock(func_comment["desc"])
        function["returns"] = func_comment["returns"]
        example = func_comment["example"]

        # Build up the prototype
        prototype = ''
        for j in range(i+1, pos_definition):
            token = tokens[j]

            if(TYPE(token) != TOKEN_WHITESPACE[0] and TYPE(token) != TOKEN_COMMENT[0]):
                prototype += token["data"] + ' '

            j += 1
        prototype += ';'

        prototype = re.sub(" *([\(\)\[\]]) *", "\\1", prototype)


        #print "PROTOTYPE: [%s]" % prototype

        i = pos_definition
        token = tokens[i]
        #print "TOKEN: [%s]" % token["data"]
        pseudocode_start = token["pos"]+1

        # Now search forward until the closing brace is found if it
        # is a definition or a semicolon if it is a prototype
        if(is_prototype):
            while(i < len(tokens) and not end):

                if(token["type"][0] == TOKEN_SEMICOLON[0]):
                    end = True
                    break

                i += 1

                if(i < len(tokens)):
                    token = tokens[i]
        
        else:
            while(i < len(tokens) and not end):

                #print "    FUNC: %s" % token["data"]
                
                if(token["type"][0] == TOKEN_OPEN_BRACE[0]):
                    brace_cnt += 1

                elif(token["type"][0] == TOKEN_CLOSE_BRACE[0]):
                    brace_cnt -= 1

                    if(brace_cnt == 0):
                        end = True
                        break

                i += 1

                if(i < len(tokens)):
                    token = tokens[i]

        pseudocode_end = token["pos"]

        pseudocode = source[pseudocode_start:pseudocode_end]
        #print "PSEUDOCODE: [%s]" % pseudocode
                    
        code = source_code_t()
        language = "c"

        if(output_pseudocode):
            tmp = code.parse_source_code(language, pseudocode)
            function["pseudocode"] = {}
            function["pseudocode"]["language"] = language
            function["pseudocode"]["parsed"] = tmp
            function["pseudocode"]["unparsed"] = pseudocode

        if(example != ""): 
            tmp = code.parse_source_code(language, example)
            function["example"] = {}
            function["example"]["language"] = language
            function["example"]["parsed"] = tmp
            function["example"]["unparsed"] = example

        if(prototype != ""):
            tmp = code.parse_source_code(language, prototype)
            function["prototype"] = {}
            function["prototype"]["language"] = language
            function["prototype"]["parsed"] = tmp
            function["prototype"]["unparsed"] = prototype


        #print "Function"
        #print "    name: %s" % function["function_name"]
        #print "    returns: %s" % function["function_returns"]
        #function["function_prototype"] = prototype
        function["params"] = self.parse_params(prototype)
            
        params = function["params"]
        new_params = []

        for param in func_comment["params"]:
            #print "PARAM: %s" % param

            for p in params:
                if(p["name"] == param):
                    desc = func_comment["params"][param]["desc"]
                    p["desc"] = desc
                    p["desc2"] =  self.parse_textblock(trim_leading_blank_lines(desc))
                    p["io"] = func_comment["params"][param]["io"]


        #if(len(new_params) > 0):
        #    function["function_params"] = new_params

        return (i, function)

    # Parse the tokenized representation of a C/C++ file 
    def parse_tokens(self, page, tokens, source):
       
        num_tokens = len(tokens)
        i = 0
        last_token = None

        while i < num_tokens:

            token = tokens[i]
            
            #print "TOKEN: [%s] (%s) %d" % (token["data"], token["type"][1], token["line"])

            if(self.match_token(token, TOKEN_KEYWORD, "struct")):
                #print "Found structure"

                try:
                    (i,struct) = self.parse_cpp_struct(tokens, i)
                except:
                    struct = None
                    i += 1
                
                if(struct != None):
                    tag = {}
                    tag["name"] = "h3"
                    tag["contents"] = struct["title"]
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

                    tag = {}
                    tag["name"] = "struct"
                    tag["contents"] = struct
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

            elif(token["type"] == TOKEN_PREPROCESSOR):
                text = token["data"]
                words = text.split(" ")
                command = words[0].strip()

                if(command == "define"):
                    try:
                        (i,define) = self.parse_cpp_define(tokens, i)
                    except:
                        define = None
                        i += 1

                    if(define != None):
                        tag = {}
                        tag["name"] = "define"
                        tag["contents"] = define
                        tag["source"] = ""
                        tag["modifiers"] = {}
                        page["tags"].append(tag)

                else:
                    i += 1

            elif(token["type"] == TOKEN_COMMENT):

                text = token["data"]
                
                #print "Found comment: %s" % text

                expr = re.compile("@file\s*([^ ]+)", re.DOTALL)
                matches = expr.search(text)
                if(matches != None):
                    #print "Found file header %s" % matches.groups()[0]

                    matches = re.search("@brief\s*([^.@]+)", text, re.DOTALL)
                    if(matches != None):
                        self.m_file_brief = self.format_comment(matches.groups()[0]).strip()
                        #print "Found brief: %s" % self.m_file_brief

                    matches = re.search("@author\s*(.*?)\*+\*/", text, re.DOTALL)
                    if(matches != None):
                        self.m_author = self.format_comment(matches.groups()[0]).strip()
                        #print "Found author: %s" % author
                    
                #print "Found multi-line comment token"
                #sys.exit(-1) 

            elif(self.match_token(token, TOKEN_KEYWORD, "enum")):
                #print "Found enum"
                try:
                    (i,enum) = self.parse_cpp_enum(tokens, i)
                except:
                    i += 1
                    enum = None

                #print enum
                
                if(enum != None):
                    tag = {}
                    tag["name"] = "h3"
                    tag["contents"] = enum["title"]
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

                    tag = {}
                    tag["name"] = "enum"
                    tag["contents"] = enum
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

            elif(self.match_token(token, TOKEN_OPEN_BRACE, "{") or self.match_token(token, TOKEN_SEMICOLON, ";")):
                #print "Found possible function"
                saved_i = i
                pos = tokens[i]["pos"]

                char = source[pos]

                is_prototype = False
                if(char == ";"):
                    is_prototype = True
                
                if(("{" != char) and (";" != char)):
                    print "{ != [%s]" % char
                    sys.exit(-1)

                try:
                    # First walkbackwards and see if this is an extern
                    (k,src) = self.walk_backwards(saved_i-1,tokens,
                                TARGET([TOKEN_KEYWORD]),
                                SKIP([TOKEN_COMMENT, TOKEN_LINE_COMMENT, TOKEN_WHITESPACE, TOKEN_STRING]))
                    keyword = tokens[k+1]["data"]

                    # If this wasn't a function and it wasn't an
                    # extern then we need to walk
                    # forward till we hit the closing brace
                    if(keyword == "extern"):
                        i += 1
                        #print "DO I GET HERE?"
                        continue
                except:
                    do_nothing=1

                try:
                    (i, function) = self.parse_cpp_function(tokens, i, source, is_prototype)
                except:
                    #import traceback
                    #tb = sys.exc_info()[2]
                    #traceback.print_tb(tb)
                    #print "Encountered Exception parsing what looked like C++ function"
                    function = None
                    i += 1
                    
                # If this wasn't a function and it wasn't an
                # extern then we need to walk
                # forward till we hit the closing brace
                if(function == None):
                    i = saved_i
                    cnt_brace = 0
                    while(1):

                        token = tokens[i]

                        # If it is a prototype then the end is a semicolon.
                        if(is_prototype):
                            if(token["type"][0] == TOKEN_SEMICOLON[0]):
                                break
                        # If it isn't a prototype then we're looking for
                        # a closing brace on the same level as the opening
                        # brace.
                        else:
                            #print "TOKEN: %s" % (token["type"][1])

                            if(token["type"][0] == TOKEN_OPEN_BRACE[0]):
                                cnt_brace += 1
                            elif(token["type"][0] == TOKEN_CLOSE_BRACE[0]):
                                cnt_brace -= 1
                                
                                if(cnt_brace == 0):
                                    break
                                
                                #print "CLOSE_BRACE: %d" % cnt_brace
                                #sys.exit(-1)
                        i += 1
                else:
                    tag = {}
                    tag["name"] = "h3"
                    tag["contents"] = function["name"]
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

                    tag = {}
                    tag["name"] = "prototype"
                    tag["contents"] = function
                    tag["source"] = ""
                    tag["modifiers"] = {}
                    page["tags"].append(tag)

            i += 1

       
    # Parse the input file and turn it into
    # structures understood by shorte. 
    def parse_buffer(self, input, source_file):

        self.m_current_file = source_file

        page = {}
        page["title"] = source_file

        #self.set_title(source_file)
        #self.set_subtitle(source_file)
        page["tags"] = []
        page["source_file"] = source_file
        page["links"] = []


        tag = {}
        tag["name"] = "h1"
        tag["contents"] = source_file
        tag["source"] = ""
        tag["modifiers"] = {}
        page["tags"].append(tag)

        tag = {}
        tag["name"] = "functionsummary"
        tag["contents"] = ""
        tag["modifiers"] = self.parse_modifiers('src="%s"' % source_file)
        page["tags"].append(tag)
        tag = {}

        STATE_NORMAL     = 0
        STATE_ESCAPE     = 1 
        STATE_COMMENT    = 2
        STATE_LINE_COMMENT    = 3
        STATE_PREPROCESSOR = 4
        STATE_STRING       = 5

        # First strip any single line quotes as they aren't
        # used by shorte. Probably could do this in a better fashion
        input = re.sub("\/\*[ \t].*?\*\/", "", input, re.DOTALL)

        states = []
        states.append(STATE_NORMAL)
        
        i = 0
        source = ''
        tokens = []
        line = 1

        while i < len(input):

            if(input[i] == '\\'):
                source += input[i]
                source += input[i+1]

                if(input[i+1] == '\n'):
                    line += 1

                i += 2 
                continue
           
            state = states[-1]

            if(state == STATE_LINE_COMMENT):
                source += input[i]
                if(input[i] == '\n'):
                    #print "APPENDING LINE COMMENT [%s]" % source
                    tokens.append(my_token(TOKEN_LINE_COMMENT, source, line, i))
                    source = ''
                    states.pop()
                   
            elif(state == STATE_COMMENT):
                source += input[i]
                if(input[i] == '*' and input[i+1] == '/'):
                    #print "APPENDING COMMENT [%s]" % source
                    source += input[i+1]
                    tokens.append(my_token(TOKEN_COMMENT, source, line, i))
                    source = ''
                    states.pop()
                    i += 2

            elif(state == STATE_STRING):
                source += input[i]

                if(input[i] == '"'):
                    tokens.append(my_token(TOKEN_STRING, source, line, i))
                    source = ''
                    states.pop()

            elif(state == STATE_PREPROCESSOR):
                source += input[i]

                if(input[i] == '\n'):
                    tokens.append(my_token(TOKEN_PREPROCESSOR, source, line, i))
                    states.pop()
                    source = ''

            elif(state == STATE_NORMAL):

                if(input[i] == '#'):
                    states.append(STATE_PREPROCESSOR)

                elif(input[i] == '/' and input[i+1] == '/'):
                    source += '//'
                    states.append(STATE_LINE_COMMENT)
                    i += 2
                    continue

                elif(input[i] == '/' and input[i+1] == '*'):
                    source += '/*'
                    states.append(STATE_COMMENT)
                    i += 2
                    continue

                elif(input[i] == '"'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''
                    source += input[i]
                    states.append(STATE_STRING)

                elif(input[i] == '('):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    tokens.append(my_token(TOKEN_OPEN_BRACKET, '(', line, i))
                elif(input[i] == '['):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    tokens.append(my_token(TOKEN_OPEN_SQ_BRACKET, '[', line, i))
                elif(input[i] == ']'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    tokens.append(my_token(TOKEN_CLOSE_SQ_BRACKET, ']', line, i))
                elif(input[i] == '='):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    tokens.append(my_token(TOKEN_EQUALS, '=', line, i))

                elif(input[i] == ';'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''
                    tokens.append(my_token(TOKEN_SEMICOLON, ';', line, i))
                    source = ''
                elif(input[i] == ')'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''
                    tokens.append(my_token(TOKEN_CLOSE_BRACKET, ')', line, i))
                    source = ''
                elif(input[i] == '{'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''
                    tokens.append(my_token(TOKEN_OPEN_BRACE, '{', line, i))
                    source = ''
                elif(input[i] == '}'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''
                    tokens.append(my_token(TOKEN_CLOSE_BRACE, '}', line, i))
                    source = ''
                elif(input[i] == ' '):

                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    #tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    last_token = tokens[-1]
                    if(TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                
                elif(input[i] == '\t'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    #tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    last_token = tokens[-1]
                    if(TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    
                    
                elif(input[i] == '\n'):
                    if(source != ''):
                        if(self.is_keyword(source)):
                           tokens.append(my_token(TOKEN_KEYWORD, source, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, source, line, i))
                        source = ''

                    if(len(tokens) != 0):
                        last_token = tokens[-1]
                    else:
                        last_token = None
                    
                    if(last_token != None and TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line+1, i))

                else:
                    source += input[i]

            try:
                if(input[i] == '\n'):
                    line += 1
            except:
                print "SOURCE: [%s]" % input[i-40:]
            
            i = i+1

        tokens_in = tokens
        tokens = []
        for i in range(0, len(tokens_in)):

            # Only include comments if they start with /**
            if(TYPE(tokens_in[i]) == TOKEN_COMMENT[0]):
                if(tokens_in[i]["data"].startswith("/**")):

                    # If it starts with /** then expand any /li
                    # tokens
                    data = tokens_in[i]["data"]
                    data = data.replace("\\li", "-")
                    tokens_in[i]["data"] = data

                    tokens.append(tokens_in[i])
                else:
                    pass
            else:
                tokens.append(tokens_in[i])

        self.parse_tokens(page, tokens, input)
                
        page["file_brief"] = self.m_file_brief
        page["file_author"] = self.m_author

        for tag in page["tags"]:
            tag["source_file"] = page["source_file"]
            tag["page_title"]  = page["source_file"]


        ## Check to see if there were any includes found. If there are then
        ## pop them off one at a time and process them
        #while(len(self.m_include_queue) != 0):
        #    path = self.m_include_queue.pop(-1)
        #    self.parse(path)

        self.m_pages.append(page)

        return page

    def parse(self, source_file):

        input = self.load_source_file(source_file)

        return self.parse_buffer(input, source_file)
