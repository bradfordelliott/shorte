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

from src.shorte_source_code import *

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
TOKEN_INVALID       = (0xff, "INVALID", "")

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

class comment_t:
    def __init__(self):
        self.params = {}
        self.returns = ""
        self.example = ""
        self.private = False
        self.see_also = ""
        self.deprecated = None
        self.heading = ""
        self.since = ""

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

        code = self.m_engine.m_source_code_analyzer
        self.m_keywords = code.get_keyword_list("c")

        self.m_author = "Unknown"
        self.m_file_brief = ""
        self.m_find_reference = re.compile("([@\\\]ref\s+[A-Za-z][A-Za-z0-9_]+)", re.DOTALL)
        self.m_find_in_group  = re.compile("([@\\\]\s*(ingroup|heading)(.*?)\n)", re.DOTALL)
        self.m_file_src = ""
        self.m_source_file = None
            

    def is_keyword(self, source):

        if(self.m_keywords.has_key(source)):
            return True

        return False

    def get_next_token(self, tokens, pos, token_types):

        token = tokens[pos+1]

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
        
    def set_example(self, comment, object):
        if(comment.has_key("example") and comment["example"] != ""): 
            code = self.m_engine.m_source_code_analyzer
            language = "c"
            tmp = code.parse_source_code(language, comment["example"])
            example = code_block_t()
            example.set_language(language)
            example.set_parsed(tmp)
            example.set_unparsed(comment["example"])
            struct2.example = example
    
    # Parse a C++ structure and store it
    def parse_cpp_struct(self, tokens, i):
        '''This method is called to parse the contents of a C/C++
           structure in order to extract a shorte object describing
           the structure.

           @param self   [I] - The parser class instance
           @param tokens [I] - The list of tokens from the parsed file.
           @param i      [I] - The current position in the token list.

           @return A tuple containing:
                     - The index of the next character after the struct
                     - The struct object
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

        start_of_struct = token["line"] + 1

        if(not desc.startswith("/**")):
            return None

        (comment,comment2) = self.parse_cpp_func_comment(desc)

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
        
        fields = self.parse_struct_fields2(struct_body, struct_name, start_of_struct)
        rows = self.parse_struct_fields(struct_body)
        
        max_cols = 0
        for row in rows:
            cols = len(row["cols"])
            if(cols > max_cols):
                max_cols = cols
        
        struct2 = struct_t()
        struct2.fields = fields
        struct2.set_name(struct_name)
        struct2.set_description(comment["desc"], textblock=False)
        struct2.set_description(textblock_t(comment["desc"]), textblock=True)
        struct2.comment = comment2
        struct2.private = comment2.private
        struct2.deprecated = comment2.deprecated
        struct2.max_cols = max_cols
        struct2.file = self.m_current_file
        struct2.line = start_of_struct

        if(comment.has_key("example") and comment["example"] != ""): 
            code = self.m_engine.m_source_code_analyzer
            language = "c"
            tmp = code.parse_source_code(language, comment["example"])
            example = code_block_t()
            example.set_language(language)
            example.set_parsed(tmp)
            example.set_unparsed(comment["example"])
            struct2.example = example
        

        i = pos_saved
        token = tokens[i]

        #print "STRUCT ROWS"
        for row in rows:
            name = row["cols"][1]["text"]
            desc = row["cols"][2]["text"].strip()
            #print "name: %s" % name
            #print "desc: %s" % desc
            if(0 == len(desc)):
                WARNING("Missing description of struct field %s" % name)

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
        
        return (i, struct2)


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
            col["textblock"] = textblock_t(enum["desc"])
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

    def parse_struct_fields2(self, text, struct_name, start_of_struct):

        fields = []
        states = []

        states.append(STATE_NORMAL)

        i = 0
        comment = ''
        data = ''
        field = field_t()

        while(i < len(text)):

            state = states[-1]

            if(state == STATE_NORMAL):
                if(text[i] == '/' and text[i+1] == '*' and text[i+2] == '*'):
                    states.append(STATE_COMMENT)
                    comment = ''
                    i += 3
                    continue

                else:
                    if(text[i] == ';'):
                        parts = data.strip().split(' ')
                        parts2 = []
                        for part in parts:
                            tmp = part.strip()
                            if(len(tmp) != 0):
                                parts2.append(tmp)

                        #print "FIELD: %s - [%s]" % (data.strip(), parts2[1])
                        field = field_t()
                        field.name = parts2[1]
                        tmp = trim_leading_blank_lines(comment)
                        field.set_description(textblock_t(trim_leading_blank_lines(comment)))
                        field.set_type(parts2[0])
                        fields.append(field)

                        data = ''
                    else:
                        data += text[i]

            elif(state == STATE_COMMENT):

                if(text[i] == '*' and text[i+1] == '/'):
                    i += 2
                    states.pop()
                    continue
                else: 
                    comment += text[i]

            i += 1

        if(len(data.strip())):
            parts = data.strip().split(' ')
            parts2 = []
            for part in parts:
                tmp = part.strip()
                if(len(tmp) != 0):
                    parts2.append(tmp)

            field = field_t()
            field.name = parts2[1]
            tmp = trim_leading_blank_lines(comment)
            field.set_description(textblock_t(trim_leading_blank_lines(comment)))
            field.set_type(parts2[0])
            fields.append(field)

        for field in fields:
            if(0 == len(field.get_description())):
                WARNING("Field %s.%s has no description in %s:%d" % (struct_name,field.get_name(), self.m_source_file, start_of_struct))
                
        return fields
    
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
            col["textblock"] = textblock_t(trim_leading_blank_lines(desc_original))
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

        comment2 = comment_t()

        comment["params"] = {}
        comment["returns"] = ""
        comment["example"] = ""
        comment["private"] = False
        comment["see_also"] = ""
        comment["deprecated"] = None
        comment["heading"] = ""
        
        # Anything before the @brief tag is a block of standard
        # shorte text that needs to be processed separately
        if("@brief" in text):
            INFO("Found an @brief tag") 
            parts = text.split('@brief')

            prefix = parts[0]
            shorte = shorte_parser_t(self.m_engine)
            shorte.parse_string(prefix, self.m_source_file)
            tags = shorte.m_pages[0]["tags"]
            self.page["tags"].extend(tags)

            text = parts[1]

        # Strip off any \ref sequences since shorte doesn't use them
        # Also search for any heading references used to group the
        # generated output.
        extras = True
        if(extras):
            #expr_ref = self.m_find_reference
            expr_ref = re.compile("([@\\\]ref\s+[A-Za-z][A-Za-z0-9_]+)", re.DOTALL)
            text = expr_ref.sub("", text)
            
            # Strip off any leading ingroup tag before the description
            # since shorte doesn't support that right now.
            #expr_ingroup = self.m_find_in_group
            expr_ingroup = re.compile("([@\\\]\s*(ingroup|heading)(.*)\n*)", re.DOTALL)

            #print "TEXT: [%s]" % text
            matches = expr_ingroup.search(text)
            if(matches != None):
                comment["heading"] = matches.groups()[2].strip()
                comment2.heading = matches.groups()[2].strip()
                #print "HEADING: %s" % comment["heading"]
                text = text.replace(matches.groups()[0], "")
        
        # If there is no description assume the type is private
        if(len(text) == 0):
            comment["private"] = True
            comment2.private = True

        matches = re.search("(.*?)(@[^{]|\\\)", text, re.DOTALL)

        if(matches != None):
            comment["desc"] = self.format_text(matches.groups()[0])
            comment2.desc = self.format_text(matches.groups()[0])
            comment["description"] = textblock_t(trim_leading_blank_lines(matches.groups()[0]))
            comment2.description = textblock_t(trim_leading_blank_lines(matches.groups()[0]))
        else:
            comment["desc"] = self.format_text(text)
            comment2.desc = self.format_text(text)
            comment["description"] = textblock_t(trim_leading_blank_lines(text))
            comment2.description = textblock_t(trim_leading_blank_lines(text))

        #print "COMMENT:"
        #print comment["desc"]

        matches = re.search("[@\\\]private", text, re.DOTALL)
        if(matches != None):
            comment["private"] = True
            comment2.private = True

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

            comment2.params[name] = {}
            comment2.params[name]["desc"] = desc
            comment2.params[name]["io"] = io

            #print "name = %s (%s)" % (name, desc)
            matches = expr_param.search(text, matches.end())
        
        expr_return = re.compile("[@\\\]return *([^@]*)", re.DOTALL)

        matches = expr_return.search(text)
        if(matches != None):
            desc = self.format_text(matches.groups()[0])
            comment["returns"] = desc
            comment2.returns = desc
        
        expr_example = re.compile("[@\\\]example *([^@]*)", re.DOTALL)
        matches = expr_example.search(text)
        if(matches != None):
            desc = matches.groups()[0]
            comment["example"] = desc
            comment2.example = desc
        
        expr_see_also = re.compile("[@\\\]see *([^@]*)", re.DOTALL)
        matches = expr_see_also.search(text)
        if(matches != None):
            comment["see_also"] = matches.groups()[0]
            comment2.see_also = matches.groups()[0]

        expr_deprecated = re.compile("[@\\\]deprecated *([^@]*)", re.DOTALL)
        matches = expr_deprecated.search(text)
        if(matches != None):
            
            msg = trim_leading_blank_lines(matches.groups()[0])
            msg = textblock_t(msg)
            comment["deprecated"] = msg #matches.groups()[0]
            comment2.deprecated = msg # matches.groups()[0]

        
        return (comment,comment2)

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

        start_of_enum = token["line"] + 1

        if(not desc.startswith("/**")):
            return None

        (comment,comment2) = self.parse_cpp_func_comment(desc)

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

        enum = enum_t()
        enum.name = enum_name
        enum.values = rows
        enum.comment = comment2

        enum.description = textblock_t(text)
        enum.private = comment2.private
        enum.deprecated = comment2.deprecated
        enum.line = start_of_enum
        enum.file = self.m_current_file
                 
        max_cols = 0
        for row in rows:
            cols = len(row["cols"])
            if(cols > max_cols):
                max_cols = cols
        enum.max_cols = max_cols

        return (i, enum)


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
            param = param_t()
            param.set_name(pname)
            param.set_type(ptype)
            field["name"] = pname
            field["io"] = ""
            field["type"] = ptype
            field["desc"] = ("")
            field["desc2"] = textblock_t()

            return param

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

            if(token["type"][0] == TOKEN_INVALID[0]):
                i -= 1
                continue

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

            if(token["type"][0] == TOKEN_INVALID[0]):
                i += 1 
                continue

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
        
        define = define_t()
        define.name = ''
        define.description = ''
        define.source = token["data"]

        parts = token["data"].split(" ")
        define.name = parts[1].strip()
        parts.pop(0)
        parts.pop(0)
        val = ' '.join(parts)
        
        if(val[-1] == '\n'):
            val = val[0:-1]

        define.value = textblock_t(val)
        start_of_define = token["line"] + 1
        define.line = start_of_define
        define.file = self.m_current_file

        try:
            # Search backwards till we find something that
            # isn't a comment or whitespace which indicates the
            # end of the define.
            #(i, src) = self.walk_backwards(i-1, tokens, TARGET([TOKEN_COMMENT]), SKIP([TOKEN_WHITESPACE]))
            (i, src) = self.walk_backwards(i-1, tokens, TARGET([TOKEN_COMMENT]), SKIP([]))

            (comment,comment2) = self.parse_cpp_func_comment(src)
            define.desc = comment2.desc
            define.description = comment2.description
            define.private = comment2.private
            define.heading = comment2.heading
        except:
            define.desc = ""
            define.description = textblock_t()
            define.private = True
            define.heading = ""

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
        function["heading"] = ""
        params = ''

        p2 = prototype_t()

        #print "PARSING FUNCTION"

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
        p2.set_name(src.strip())
        #print "NAME: [%s]" % function["name"]

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

        start_of_func = token["line"] + 1



        desc.reverse()
        desc = " ".join(desc)

        if(not desc.startswith("/**")):
            return None
        
        (func_comment,func_comment2) = self.parse_cpp_func_comment(desc)

        function["see_also"] = func_comment2.see_also
        p2.set_see_also(function["see_also"])

        function["deprecated"] = func_comment2.deprecated
        p2.set_deprecated(func_comment2.deprecated)
        function["private"] = func_comment2.private
        p2.set_private(func_comment2.private)

        if(func_comment2.heading != None):
            function["heading"] = func_comment2.heading

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

        if(not extract_private and True == func_comment2.private):
            raise Exception("Not outputting private functions")

        function["desc"] = func_comment2.desc
        p2.set_description(func_comment2.desc,textblock=False)
        function["desc2"] = textblock_t(func_comment2.desc)
        p2.set_description(function["desc2"], textblock=True)
        function["returns"] = func_comment2.returns
        p2.set_returns(function["returns"])
        example = func_comment2.example

        function["line"] = start_of_func
        p2.set_line(start_of_func)
        p2.set_file(self.m_current_file)

        # Build up the prototype
        prototype = ''
        for j in range(i+1, pos_definition):
            token = tokens[j]

            if(TYPE(token) != TOKEN_WHITESPACE[0] and TYPE(token) != TOKEN_COMMENT[0]):
                prototype += token["data"] + ' '

            j += 1
        prototype += ';'

        prototype = re.sub(" *([\(\)\[\]]) *", "\\1", prototype)


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
                    
        code = self.m_engine.m_source_code_analyzer
        language = "c"

        if(output_pseudocode):
            p2.set_pseudocode(pseudocode, self.m_engine.m_source_code_analyzer, "c")

        if(example != ""): 
            p2.set_example(example, self.m_engine.m_source_code_analyzer, "c")

        if(prototype != ""):
            p2.set_prototype(prototype, self.m_engine.m_source_code_analyzer, "c")

        #print "Function"
        #print "    name: %s" % function["function_name"]
        #print "    returns: %s" % function["function_returns"]
        #function["function_prototype"] = prototype
        params = self.parse_params(prototype)
        new_params = []

        for param in func_comment2.params:
            for p in params:
                if(p.get_name() == param):
                    desc = func_comment2.params[param]["desc"]
                    p.set_description(desc, textblock=False)
                    p.set_description(textblock_t(trim_leading_blank_lines(desc)), textblock=True)
                    p.set_io(func_comment2.params[param]['io'])

        # Check the list of parameter definitions and generate
        # a warning if a comment is missing.
        for param in params:
            #print "PARAM: %s" % param["name"]
            if(not func_comment2.params.has_key(param.get_name())):
                if(None == self.m_source_file):
                    self.m_source_file = self.m_current_file

                WARNING("%s missing parameter definition for %s in %s:%d" % (p2.get_name(), param.get_name(), self.m_source_file, start_of_func))
        
        p2.set_params(params)

        return (i, p2)

    # Parse the tokenized representation of a C/C++ file 
    def parse_tokens(self, page, tokens, source):
       
        num_tokens = len(tokens)
        i = 0
        last_token = None
        
        extract_private = self.m_engine.get_config("cpp_parser", "extract_private")
        if(extract_private == "1"):
            extract_private = True
        else:
            extract_private = False

        while i < num_tokens:

            token = tokens[i]
            
            #print "TOKEN: [%s] (%s) %d" % (token["data"], token["type"][1], token["line"])

            # This is an alternative way of documenting the source code. In
            # this case the users inserts headings directly into the sources
            # which gets interpreted as code.
            #if(token["type"] == TOKEN_COMMENT and 
            #    (("@h1" in token["data"] or 
            #      "@h2" in token["data"] or
            #      "@h3" in token["data"] or
            #      "@h4" in token["data"] or
            #      "@h5" in token["data"]))):
            #        text = self.format_comment(token["data"], strip_single_line_comments=False)

            #        shorte = shorte_parser_t(self.m_engine)
            #        shorte.parse_string(text, self.m_current_file)
            #        tags = shorte.m_pages[0]["tags"]
            #        i += 1

            #        # Don't want to treat this as a comment
            #        # for another type so mark it as invalid
            #        token["type"] = TOKEN_INVALID
            #        page["tags"].extend(tags)
            #        #print text
            #        continue

            if(self.match_token(token, TOKEN_KEYWORD, "struct")):
                start_i = i 
                try:
                    (i,struct) = self.parse_cpp_struct(tokens, i)
                except:
                    #import traceback
                    #tb = sys.exc_info()[2]
                    #traceback.print_tb(tb)
                    #line = tokens[i]["line"]
                    #WARNING("Encountered Exception parsing what looked like C++ struct in %s @ line %d\n%s" % (self.m_current_file, line, source[start_i:start_i+100]))
                    struct = None
                    i += 1

                header = shorte_get_config("shorte", "header_add_to_prototype")
                if(header == "None"):
                    header = None
                
                if(struct != None):

                    if(struct.private and not extract_private):
                        pass
                    else:
                        parent = None

                        if(header != None):
                            tag = tag_t()
                            tag.name = header
                            tag.contents = struct.name
                            tag.file = self.m_current_file
                            tag.line = struct.line
                            tag.source = ""
                            tag.modifiers = {}
                            page["tags"].append(tag)
                            parent = tag

                        #print "Found structure %s" % struct["title"]
                        tag = tag_t()
                        tag.name = "struct"
                        tag.contents = struct
                        tag.source = ""
                        tag.file = self.m_current_file
                        tag.line = struct.line
                        tag.modifiers = {}
                        tag.heading = parent
                        page["tags"].append(tag)

            elif(token["type"] == TOKEN_PREPROCESSOR):
                text = token["data"]
                words = text.split(" ")
                command = words[0].strip()

                #if(command == "if"):
                #    WARNING("FOUND IF [%s]" % text)
                #if(command == "ifdef"):
                #    WARNING("FOUND IFDEF [%s]" % text)
                #if(command == "endif"):
                #    WARNING("FOUND ENDIF")

                if(command == "define"):
                    try:
                        (i,define) = self.parse_cpp_define(tokens, i)
                    except:
                        define = None
                        i += 1

                    if(define != None):

                        if(define.private and not extract_private):
                            pass
                        else: 
                            parent = None

                            header = shorte_get_config("shorte", "header_add_to_define")
                            if(header != "None"):
                                tag = tag_t()
                                tag.name = header
                                tag.contents = define.name
                                tag.source = define.name
                                tag.line = define.line
                                tag.file = self.m_current_file
                                tag.modifiers = {}
                                page["tags"].append(tag)
                                parent = tag

                            tag = tag_t()
                            tag.name = "define"
                            tag.contents = define
                            tag.line = define.line
                            tag.file = self.m_current_file
                            tag.source = define.source
                            tag.modifiers = {}
                            tag.heading = parent
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
                    if(enum.private and not extract_private):
                        pass
                    else:
                        parent = None

                        header = shorte_get_config("shorte", "header_add_to_enum")

                        if(header != "None"):
                            tag = tag_t()
                            tag.name = header
                            tag.contents = enum.name
                            tag.line = enum.line
                            tag.file = self.m_current_file
                            tag.source = ""
                            tag.modifiers = {}
                            page["tags"].append(tag)
                            parent = tag

                        tag = tag_t()
                        tag.name = "enum"
                        tag.contents = enum
                        tag.source = ""
                        tag.line = enum.line
                        tag.file = self.m_current_file
                        tag.modifiers = {}
                        tag.heading = parent
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
                    FATAL("{ != [%s]" % char)
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
                    start_i = i
                    (i, prototype) = self.parse_cpp_function(tokens, i, source, is_prototype)
                except:
                    #import traceback
                    #tb = sys.exc_info()[2]
                    #traceback.print_tb(tb)
                    #WARNING("Encountered Exception parsing what looked like C++ function") # at %s" % (source[start_i:start_i+100]))
                    #print sys.exc_info()
                    prototype = None
                    i += 1
                    
                # If this wasn't a function and it wasn't an
                # extern then we need to walk
                # forward till we hit the closing brace
                if(prototype == None):
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

                    parent = None

                    header = shorte_get_config("shorte", "header_add_to_prototype")
                    
                    if(header != "None"):
                        tag = tag_t()
                        tag.name = header
                        tag.contents = prototype.get_name()
                        tag.source = ""
                        tag.file = prototype.get_file()
                        tag.line = prototype.get_line()
                        tag.modifiers = {}
                        page["tags"].append(tag)
                        parent = tag

                    tag = tag_t()
                    tag.name = "prototype"
                    tag.contents = prototype
                    tag.source = ""
                    tag.file = prototype.get_file()
                    tag.line = prototype.get_line()
                    tag.modifiers = {}
                    tag.heading = parent 
                    page["tags"].append(tag)

            i += 1

       
    # Parse the input file and turn it into
    # structures understood by shorte. 
    def parse_buffer(self, input, source_file):

        self.m_current_file = source_file

        self.page = {}
        self.page["title"] = source_file

        #self.set_title(source_file)
        #self.set_subtitle(source_file)
        self.page["tags"] = []
        self.page["source_file"] = source_file
        self.page["links"] = []


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
        source = []
        tokens = []
        line = 1

        while i < len(input):

            if(input[i] == '\\'):
                source.append(input[i])
                source.append(input[i+1])

                if(input[i+1] == '\n'):
                    line += 1

                i += 2 
                continue
           
            state = states[-1]

            if(state == STATE_LINE_COMMENT):
                source.append(input[i])
                if(input[i] == '\n'):
                    #print "APPENDING LINE COMMENT [%s]" % source
                    word = ''.join(source)
                    tokens.append(my_token(TOKEN_LINE_COMMENT, word, line, i))
                    source = []
                    states.pop()
                   
            elif(state == STATE_COMMENT):
                source.append(input[i])
                if(input[i] == '*' and input[i+1] == '/'):
                    #print "APPENDING COMMENT [%s]" % source
                    source.append(input[i+1])
                    tokens.append(my_token(TOKEN_COMMENT, ''.join(source), line, i))
                    source = []
                    states.pop()
                    i += 2

            elif(state == STATE_STRING):
                source.append(input[i])

                if(input[i] == '"'):
                    tokens.append(my_token(TOKEN_STRING, ''.join(source), line, i))
                    source = []
                    states.pop()

            elif(state == STATE_PREPROCESSOR):
                source.append(input[i])

                if(input[i] == '\n'):
                    tokens.append(my_token(TOKEN_PREPROCESSOR, ''.join(source), line, i))
                    states.pop()
                    source = []

            elif(state == STATE_NORMAL):

                if(input[i] == '#'):
                    states.append(STATE_PREPROCESSOR)

                elif(input[i] == '/' and input[i+1] == '/'):
                    source.append('//')
                    states.append(STATE_LINE_COMMENT)
                    i += 2
                    continue

                elif(input[i] == '/' and input[i+1] == '*'):
                    source.append('/*')
                    states.append(STATE_COMMENT)
                    i += 2
                    continue

                elif(input[i] == '"'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []
                    source.append(input[i])
                    states.append(STATE_STRING)

                elif(input[i] == '('):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    tokens.append(my_token(TOKEN_OPEN_BRACKET, '(', line, i))
                elif(input[i] == '['):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    tokens.append(my_token(TOKEN_OPEN_SQ_BRACKET, '[', line, i))
                elif(input[i] == ']'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    tokens.append(my_token(TOKEN_CLOSE_SQ_BRACKET, ']', line, i))
                elif(input[i] == '='):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    tokens.append(my_token(TOKEN_EQUALS, '=', line, i))

                elif(input[i] == ';'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []
                    tokens.append(my_token(TOKEN_SEMICOLON, ';', line, i))
                    source = []
                elif(input[i] == ')'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []
                    tokens.append(my_token(TOKEN_CLOSE_BRACKET, ')', line, i))
                    source = []
                elif(input[i] == '{'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []
                    tokens.append(my_token(TOKEN_OPEN_BRACE, '{', line, i))
                    source = []
                elif(input[i] == '}'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []
                    tokens.append(my_token(TOKEN_CLOSE_BRACE, '}', line, i))
                    source = []
                elif(input[i] == ' '):

                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    #tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    last_token = tokens[-1]
                    if(TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                
                elif(input[i] == '\t'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    #tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    last_token = tokens[-1]
                    if(TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line, i))
                    
                    
                elif(input[i] == '\n'):
                    if(len(source) != 0):
                        word = ''.join(source)
                        if(self.is_keyword(word)):
                           tokens.append(my_token(TOKEN_KEYWORD, word, line, i))
                        else:
                           tokens.append(my_token(TOKEN_CODE, word, line, i))
                        source = []

                    if(len(tokens) != 0):
                        last_token = tokens[-1]
                    else:
                        last_token = None
                    
                    if(last_token != None and TYPE(last_token) == TOKEN_WHITESPACE[0]):
                        last_token["data"] += input[i]
                    else:
                        tokens.append(my_token(TOKEN_WHITESPACE, input[i], line+1, i))

                else:
                    source.append(input[i])

            try:
                if(input[i] == '\n'):
                    line += 1
            except:
                WARNING("SOURCE: [%s]" % input[i-40:])
            
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

        self.parse_tokens(self.page, tokens, input)
        
        auto_summary = self.m_engine.get_config("shorte", "auto_summarize")
        if("1" == auto_summary): 
            idx = 0

            summary = string.Template('''
@h2 $name
$brief

@h3 Function Summary
This section summarizes the methods exported by this module

@functionsummary

@h3 Types Summary
This section summarizes the types exported by this module
@typesummary

@h3 Methods and Structures
The following section describes the methods and structures exported by this module in greater detail
''').substitute({"name" : source_file,
                 "brief" : self.m_file_brief})
                    
            shorte = shorte_parser_t(self.m_engine)
            shorte.parse_string(summary, self.m_current_file)
            tags = shorte.m_pages[0]["tags"]

            tags.extend(self.page["tags"])
            self.page["tags"] = tags

        self.page["file_brief"] = self.m_file_brief
        self.page["file_author"] = self.m_author

        for tag in self.page["tags"]:
            tag.source_file = self.page["source_file"]
            tag.page_title  = self.page["source_file"]


        ## Check to see if there were any includes found. If there are then
        ## pop them off one at a time and process them
        #while(len(self.m_include_queue) != 0):
        #    path = self.m_include_queue.pop(-1)
        #    self.parse(path)

        self.m_pages.append(self.page)

        return self.page

    def parse(self, source_file):

        self.m_source_file = source_file

        if(source_file.endswith(".tpl")):
            FATAL("%s does not look like a C/C++ file, please specify the correct parser" % source_file)

        input = self.load_source_file(source_file)

        return self.parse_buffer(input, source_file)
