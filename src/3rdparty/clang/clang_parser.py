import sys
import clang.cindex
import inspect
import re

sys.path.append("../..")
from src.shorte_defines import *
from src.shorte_source_code import *
from src.parsers.shorte_parser import *

class comment_t:
    def __init__(self):
        self.params = {}
        self.returns = None
        self.example = None
        self.private = False
        self.see_also = None
        self.deprecated = False
        self.deprecated_msg = None
        self.heading = None

    def is_private(self):
        return self.private

    def has_example(self):
        if(self.example != None):
            return True
        return False

    def get_example(self):
        return self.example

    def has_returns(self):
        if(self.returns != None):
            return True
        return False
    def get_returns(self):
        return self.returns

    def has_pseudocode(self):
        return False

    def has_see_also(self):
        if(self.see_also != None):
            return True
        return False
    def get_see_also(self):
        return self.see_also

    def has_heading(self):
        if(self.heading != None):
            return True
        return False
    def get_heading(self):
        return self.heading
    
    
class clang_parser_t(shorte_parser_t):
    def __init__(self):
        self.file_content = None
        pass

    def format_text(self, text):
        #text = re.sub(" *", " ", text)
        text = re.sub("#", "\#", text)

        return text
    
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

    def parse_cpp_func_comment(self, text):
        '''This method is called to parse a comment associated with a C/C++
           function in order to extract the associated fields.

           @param self [I] - The parser class instance
           @param text [I] - The text to parse.

           @return A dictionary containing the comment attributes.
        '''

        text = self.format_comment(text, strip_single_line_comments=False)

        comment = comment_t()

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
                comment.heading = matches.groups()[2].strip()
                #print "HEADING: %s" % comment["heading"]
                text = text.replace(matches.groups()[0], "")
        
        # If there is no description assume the type is private
        if(len(text) == 0):
            comment.private = True

        matches = re.search("(.*?)(@[^{]|\\\)", text, re.DOTALL)

        if(matches != None):
            comment.desc = self.format_text(matches.groups()[0])
            comment.description = self.parse_textblock(trim_leading_blank_lines(matches.groups()[0]))
        else:
            comment.desc = self.format_text(text)
            comment.description = self.parse_textblock(trim_leading_blank_lines(text))

        #print "COMMENT:"
        #print comment["desc"]

        matches = re.search("[@\\\]private", text, re.DOTALL)
        if(matches != None):
            comment.private = True

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

            comment.params[name] = {}
            comment.params[name]["desc"] = desc
            comment.params[name]["io"] = io

            #print "name = %s (%s)" % (name, desc)
            matches = expr_param.search(text, matches.end())
        
        expr_return = re.compile("[@\\\]return *([^@]*)", re.DOTALL)

        matches = expr_return.search(text)
        if(matches != None):
            desc = self.format_text(matches.groups()[0])
            comment.returns = desc
        
        expr_example = re.compile("[@\\\]example *([^@]*)", re.DOTALL)
        matches = expr_example.search(text)
        if(matches != None):
            desc = matches.groups()[0]
            comment.example = desc
        
        expr_see_also = re.compile("[@\\\]see *([^@]*)", re.DOTALL)
        matches = expr_see_also.search(text)
        if(matches != None):
            comment.see_also = matches.groups()[0]

        expr_deprecated = re.compile("[@\\\]deprecated *([^@]*)", re.DOTALL)
        matches = expr_deprecated.search(text)
        if(matches != None):
            
            msg = trim_leading_blank_lines(matches.groups()[0])
            msg = self.parse_textblock(msg)
            comment.deprecated = True
            comment.deprecated_msg = msg # matches.groups()[0]

        return comment

    def query_comment(self, cursor):
        comment = None

        if(cursor.raw_comment != None):
            comment = self.parse_cpp_func_comment(cursor.raw_comment)
        else:
            start_location = cursor.extent.start.offset
            end_location = cursor.extent.end.offset + 1
            # DEBUG BRAD: Not sure why this is start_location-2 instead of -1
            extent = tu.get_extent(path, (0, start_location-2))
            tokens = clang.cindex.TokenGroup.get_tokens(tu, extent)

            #print "CODE: [%s]" % self.file_content[start_location:end_location]

            # macro comment maybe in tokens. Not in cursor.raw_comment
            comment = None
            for t in reversed(list(tokens)):
                # Ignore it if is # or define
                if(t.spelling in ('#', 'define')):
                    continue
                if t.kind == clang.cindex.TokenKind.COMMENT:
                    comment = t.spelling
                    break
                else:
                    WARNING("Skipping [%s] [%s]" % (t.kind, t.spelling))
                break

            if(comment != None):
                comment = self.parse_cpp_func_comment(comment)

        return comment
        

    def parse(self, path, cursor, tu):
    
        functions = {}
        enums = {}
            
        if(self.file_content == None):
            handle = open(path, "rt")
            self.file_content = handle.read()
            handle.close()
            
        # Skip anything like global constants that don't belong to
        # this module. It seems like cursor.location.file might be a
        # unicode string so need to cast to the same type to avoid
        # a mismatch
        if(str(cursor.location.file) != str(path)):
            for c in cursor.get_children():
                self.parse(path, c, tu)
            return

        print "@h %s @%s => %s" % (cursor.kind, cursor.location.file, cursor.spelling)

        #print 'visiting ', cursor.kind
        if cursor.kind in (clang.cindex.CursorKind.ENUM_DECL,
                           clang.cindex.CursorKind.FUNCTION_DECL,
                           clang.cindex.CursorKind.STRUCT_DECL,
                           clang.cindex.CursorKind.MACRO_DEFINITION,
                           clang.cindex.CursorKind.CLASS_DECL):

    
            #comment = self.query_comment(cursor)

            comment = None

            if(cursor.raw_comment != None):
                comment = self.parse_cpp_func_comment(cursor.raw_comment)

            # Preprocessor doesn't have .raw_comment
            elif(cursor.kind == clang.cindex.CursorKind.MACRO_DEFINITION):

                start_location = cursor.extent.start.offset
                end_location = cursor.extent.end.offset + 1
                # DEBUG BRAD: Not sure why this is start_location-2 instead of -1
                extent = tu.get_extent(path, (0, start_location-2))
                tokens = clang.cindex.TokenGroup.get_tokens(tu, extent)

                #print "CODE: [%s]" % self.file_content[start_location:end_location]

                # macro comment maybe in tokens. Not in cursor.raw_comment
                comment = None
                for t in reversed(list(tokens)):
                    # Ignore it if is # or define
                    if(t.spelling in ('#', 'define')):
                        continue
                    if t.kind == clang.cindex.TokenKind.COMMENT:
                        comment = t.spelling
                        break
                    else:
                        WARNING("Skipping [%s] [%s]" % (t.kind, t.spelling))
                    break

                if(comment != None):
                    comment = self.parse_cpp_func_comment(comment)


            # If the object has no comment then assume it is private
            if(comment == None or comment.is_private()):
                for c in cursor.get_children():
                    self.parse(path, c, tu)
                return
               
            file = cursor.location.file
            line = cursor.location.line

            if(cursor.kind == clang.cindex.CursorKind.MACRO_DEFINITION):
                print '@define: file=%s line=%d' % (file, line)
                print '--name: %s' % cursor.displayname
                print '--description:'
                print indent_lines(comment.desc, '    ')
                print '--value:'

                name = cursor.displayname

                start_offset = cursor.extent.start.offset
                end_offset   = cursor.extent.end.offset + 1
                content = self.file_content[start_offset:end_offset]

                content = content.replace(name, '')
                print '    %s' % content

                # raw_comment doesn't work with defines
                # because they are stripped by the preprocessor
                # print cursor.raw_comment

            elif(cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL):
                print '@prototype: language="c" file=%s line=%d' % (file, line)
                print '--function: %s' % cursor.spelling
                print "--prototype:"

                args = cursor.get_arguments()
                
                arg_list = []
                for arg in args:
                    arg_type = arg.type.spelling
                    arg_name = arg.spelling
                    arg_list.append("%s %s" % (arg_type, arg_name))

                print ("    %s %s(" % (cursor.result_type.spelling, cursor.spelling)) + ','.join(arg_list) + ");"

                #children = cursor.get_children()
                #for child in children:
                #    print "    CHILD: %s" % child.raw_comment
                
                if(comment != None):
                    print "--description:"
                    print indent_lines(comment.desc, '    ')
                    if(comment.has_returns()):
                        print "--returns:"
                        print "    %s" % comment.get_returns()
                    print "--params:"
                    for param in comment.params:
                        data = comment.params[param]
                        name = param
                        io   = data['io']
                        desc = data['desc']
                        print '''  -- %s | %s | %s\n''' % (name, io, desc)

                    if(comment.has_example()):
                        print "--example:"
                        print "%s" % comment.get_example()

                    if(comment.has_pseudocode()):
                        print "--pseudocode:"
                        print "%s" % comment.get_pseudocode()

                    if(comment.has_see_also()):
                        print "--see also:"
                        print "    %s" % comment.get_see_also()

            elif(cursor.kind == clang.cindex.CursorKind.ENUM_DECL):
                print "@enum: file=%s line=%d" % (file, line)
                print "--name: ", cursor.type.spelling

                print "--description:"
                print indent_lines(comment.desc, '    ')
                
                children = cursor.get_children()
                print '''-- values:
- Enum Name | Enum Value | Enum Description
'''
                for child in children:
                    if(child.raw_comment != None):
                        comment = self.parse_cpp_func_comment(child.raw_comment)

                        print '- %s | %s |\n%s' % (child.spelling, child.enum_value, indent_lines(comment.desc, '    '))
                    #else:
                    #    WARNING("Enum parameter %s missing description" % child.spelling)

            elif(cursor.kind == clang.cindex.CursorKind.STRUCT_DECL):
                print "@struct: file=%s line=%d" % (file, line)
                print "--name: ", cursor.type.spelling
                
                print "--description:"
                print indent_lines(comment.desc, '    ')

                children = cursor.get_children()
                print '-- fields:'
                print '- Type | Name | Description'

                for child in children:
                    bits = child.type.spelling
                    name = child.spelling  
                    if(child.raw_comment != None):
                        comment = self.parse_cpp_func_comment(child.raw_comment)
                        print '''- %s | %s |\n%s
''' % (bits, name, indent_lines(comment.desc, '    '))

            elif(cursor.kind == clang.cindex.CursorKind.CLASS_DECL):
                print "@class: file=%s line=%d" % (file, line)
                print "--name: " , cursor.type.spelling
                print "--description:"
                print indent_lines(comment.desc, '    ')
    
            print ''
            
        # Recurse for children of this node
        for c in cursor.get_children():

            self.parse(path, c, tu)

parser = clang_parser_t()

index = clang.cindex.Index.create()
#tu = index.parse(sys.argv[1], args=['-x', 'c', '-DCS_HAS_DEBUG_LOOPBACKS'])
options = clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
tu = index.parse(sys.argv[1], options=options)
#tokens = tu.cursor.get_tokens()
#print tokens

print "@body"
print "@h1 %s" % tu.spelling

parser.parse(sys.argv[1], tu.cursor, tu)

