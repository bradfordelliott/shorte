"""The clang parser is a replacement for cpp_parser. It is used to
   parse C/C++ files and convert them into tagged objects suitable for
   use within shorte.
"""
import sys
import inspect
import re
import traceback


from src.shorte_defines import *
from src.shorte_source_code import *
from src.parsers.shorte_parser import *

import platform
osname = platform.system().lower()
# On Cygwin use the built-in clang libraries
if("cygwin" in osname):
    import clang.cindex
# Otherwise use the one provided in the 3rdparty directory
else:
    #print "OSNAME: %s" % osname
    if(osname == "darwin"):
        osname = "osx"
    elif("cygwin" in osname):
        osname = "cygwin"
    clang_path = os.path.normpath(shorte_get_startup_path() + '/3rdparty/clang/%s' % osname)

    sys.path.insert(0, clang_path)
    #WARNING("CLANG FILE:")
    #print clang.__file__
    #WARNING("CLANG_PATH: %s" % clang_path)
    import clang.cindex
    clang.cindex.Config.set_library_path(clang_path)

def get_rtokens(tu, extent):
    '''Helper method to return all tokens in an extent. This method could be
       moved to cindex.py if it is useful to other users. It is similar to the
       static TokenGroup.get_tokens() method but it reverses the generator in
       order to walk backwards.
    '''
    tokens_memory = clang.cindex.POINTER(clang.cindex.Token)()
    tokens_count = clang.cindex.c_uint()

    clang.cindex.conf.lib.clang_tokenize(tu, extent, clang.cindex.byref(tokens_memory),
            clang.cindex.byref(tokens_count))

    count = int(tokens_count.value)

    # If we get no tokens, no memory was allocated. Be sure not to return
    # anything and potentially call a destructor on nothing.
    if count < 1:
        return

    tokens_array = clang.cindex.cast(tokens_memory, clang.cindex.POINTER(clang.cindex.Token * count)).contents
    token_group = clang.cindex.TokenGroup(tu, tokens_memory, tokens_count)

    for i in xrange(count-1, 0, -1):
        token = clang.cindex.Token()
        token.int_data = tokens_array[i].int_data
        token.ptr_data = tokens_array[i].ptr_data
        token._tu = tu
        token._group = token_group

        yield token


    
class clang_parser_t(shorte_parser_t):
    """This is the implementation of the clang parser
       for C/C++ source files"""

    def __init__(self, engine):
        """The constructor for the clang parser.

           @param engine [I] - Reference to the shorte engine defined in shorte.py
        """

        self.m_engine = engine

        # Initialize the base parser class
        shorte_parser_t.__init__(self, engine)

        self.m_author = "Unknown"
        self.m_file_brief = ""
        self.m_file_src = ""
        self.m_source_file = None

        # Newer versions of clang seem to fail if you create
        # cindex but don't actually call parse(). To avoid
        # this issue we'll only create the cindex object
        # if we're actually parsing something.
        self.cindex = None
        self.tu = None

        self.processed = []

        self.m_types = {}

    def __del__(self):
        print "delete clang_parser_t"
        del self.tu
        #del self.cindex

    def object_register(self, name, object):
        self.m_types[name] = True

    def object_is_registered(self, name):
        if(self.m_types.has_key(name)):
            return True
        return False

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

        # Anything before the @brief tag is a block of standard
        # shorte text that needs to be processed separately
        if("@brief" in text):
            #WARNING("Found an @brief tag") 
            parts = text.split('@brief')

            prefix = parts[0]
            shorte = shorte_parser_t(self.m_engine)
            
            shorte.parse_string(prefix, self.m_source_file)
            tags = shorte.m_pages[0]["tags"]
            #links = shorte.get_wiki_links()
            #self.add_wiki_links(links)
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
            expr_ingroup = re.compile("([@\\\]\s*(ingroup|heading)(.*?)\n*)", re.DOTALL)

            #print "TEXT: [%s]" % text
            matches = expr_ingroup.search(text)
            if(matches != None):
                comment.heading = matches.groups()[2].strip()
                #print "HEADING: [%s]" % comment.heading
                text = text.replace(matches.groups()[0], "")
        
        # If there is no description assume the type is private
        if(len(text) == 0):
            comment.private = True

        matches = re.search("(.*?)(@[^{]|\\\)", text, re.DOTALL)

        if(matches != None):
            comment.desc = self.format_text(matches.groups()[0])
            comment.description = textblock_t(trim_leading_blank_lines(matches.groups()[0]))
        else:
            comment.desc = self.format_text(text)
            comment.description = textblock_t(trim_leading_blank_lines(text))

        matches = re.search("[@\\\]private", text, re.DOTALL)
        if(matches != None):
            comment.private = True

        expr_param = re.compile("[@\\\]param *([^ ]*) *(([^@]|@{)*)", re.DOTALL)

        matches = expr_param.search(text)
        while(matches != None):
            name = self.format_text(matches.groups()[0])
            desc = self.format_text(matches.groups()[1])
            io = ""

            # Parameters declarations typically look like
            #     @param my_param [I] - This is a description
            # or
            #     @param my_param (I) - This is a description
            matches2 = re.search("(\[|\()(.*?)(\]|\)) *- *(.*)", desc, re.DOTALL)
            if(matches2 != None):
                desc = matches2.groups()[3]
                io = matches2.groups()[1]

            p = param_t()
            p.set_description(desc, textblock=False)
            p.set_description(textblock_t(desc), textblock=True)
            p.set_io(io)
            
            comment.params[name] = p

            #print "name = %s (%s)" % (name, desc)
            matches = expr_param.search(text, matches.end())

        exprs = {
            "return" : 
                {"expr"  : "[@\\\]return *([^@]*)",
                 "format" : "text"},
            "pseudocode" :
                {"expr"  : "[@\\\]pseudocode *([^@]*)",
                 "format" : ""},
            "example" :
                {"expr" : "[@\\\]example *([^@]*)",
                 "format" : ""},
            "see" :
                {"expr" : "[@\\\]see *([^@]*)",
                 "format" : ""},
            "deprecated" :
                {"expr" : "[@\\\]deprecated *([^@]*)",
                 "format" : ""},
            "since" :
                {"expr" : "[@\\\]since *([^@]*)",
                 "format" : ""},
            "requirements" : 
                {"expr"   : "[@\\\]requires *([^@]*)",
                 "format" : ""},
        }

        try:
            for expr in exprs:
                regex = exprs[expr]["expr"]
                field_format = exprs[expr]["format"]

                regex = re.compile(regex, re.DOTALL)

                matches = regex.search(text)
                val = ''
                if(matches != None):
                    val = matches.groups()[0]

                    # Check to see if the section has any modifiers
                    if(val.strip().startswith(":")):
                        pos = val.find("\n")
                        modifiers = val[0:pos-1]
                        comment.modifiers[expr] = {}
                        comment.modifiers[expr] = self.parse_modifiers(modifiers)
                        val = val[pos+1:]
                
                    if(field_format == "text"):
                        val = self.format_text(val)

                    if(expr == "deprecated"):
                        msg = trim_leading_blank_lines(val)
                        msg = textblock_t(msg)
                        comment.deprecated = msg
                    else:
                        if(field_format == "text"):
                            val = self.format_text(val)

                        if(expr == "return"):
                            comment.returns = val
                        elif(expr == "example"):
                            comment.example = val
                        elif(expr == "pseudocode"):
                            comment.pseudocode = val
                        elif(expr == "see"):
                            comment.see_also = val
                        elif(expr == "since"):
                            comment.since = val
                        elif(expr in ("requires", "requirements")):
                            comment.set_requirements(val)

        except:
            print sys.exc_info()
            sys.exit(-1)

        return comment
        #print "EXAMPLE: %s" % comment.example

    def query_comment_before(self, start, end):

        extent = self.tu.get_extent(self.m_source_file, (start, end))

        # DEBUG BRAD: This appears to be off by 1 token. It is getting a token
        #             that it shouldn't. Not sure why that is.
        tokens = clang.cindex.TokenGroup.get_tokens(self.tu, extent)
        
        #print "CODE: [%s]" % self.m_file_src[start_location-50:start_location]
        #for token in tokens:
        #    print "  token:%s" % token.spelling
            
        comment = None
        for t in reversed(list(tokens)):
            #print "  token: %s" % t.spelling
            # Ignore it if is # or define
            if(t.spelling in ('#', 'define')):
                continue
            # DEBUG BRAD: Not sure why I need to do this
            if(t.kind == clang.cindex.TokenKind.KEYWORD):
                continue
            if t.kind == clang.cindex.TokenKind.COMMENT:
                comment = t.spelling
                break
            else:
                #WARNING("Skipping [%s] [%s] @ line %d" % (t.kind, t.spelling, t.location.line))
                pass
            break

        if(comment != None):
            if(not comment.startswith("/**")):
                INFO("Skipping parsing comment %s at %s:%d" % (comment, self.m_source_file, cursor.location.line))
                comment = None
            else:
                comment = self.parse_cpp_func_comment(comment)

        return comment

        

    def query_comment(self, cursor):
        comment = None

        #FATAL("Was this successful?")
        if(cursor.raw_comment != None):
            comment = self.parse_cpp_func_comment(cursor.raw_comment)
            if(not cursor.raw_comment.startswith("/**")):
                FATAL("Failed parsing comment %s" % cursor.raw_comment)
                comment = None
        else:
            start_location = cursor.extent.start.offset
            end_location = cursor.extent.end.offset + 1
            # DEBUG BRAD: Pass start_location-2 in order to get the #define
            #             before the actual definition.
            extent = self.tu.get_extent(self.m_source_file, (0, start_location-2))
        
            # Get the tokens related to the #define in reverse order
            try:
                items = get_rtokens(self.tu, extent)
            except:
                tokens = clang.cindex.TokenGroup.get_tokens(self.tu, extent)
                # DEBUG BRAD: This is painfully slow!!!
                items = reversed(list(tokens))

            # macro comment maybe in tokens. Not in cursor.raw_comment
            comment = None

            for t in items:
                # Ignore it if is # or define
                if(t.spelling in ('#', 'define')):
                    continue
                elif t.kind == clang.cindex.TokenKind.COMMENT:
                    comment = t.spelling
                    break
                else:
                    #WARNING("Skipping [%s] [%s]" % (t.kind, t.spelling))
                    pass
                break

            if(comment != None):
                if(not comment.startswith("/**")):
                    INFO("Skipping parsing comment %s at %s:%d" % (comment, self.m_source_file, cursor.location.line))
                    comment = None
                else:
                    comment = self.parse_cpp_func_comment(comment)

        return comment
        
    def load_source_file(self, source_file): 
        
        handle = open(source_file, "rt")
        self.m_file_src = handle.read()
        handle.close()

        #WARNING("Loading %s" % source_file)

        # At least under cygwin there is no difference with or without
        # this defined
        options = clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD | clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES

        # Add the list of include files
        includes = self.m_engine.get_includes()
        args = []
        
        # Fetch the command line arguments to pass to clang
        clang_args = shorte_get_config("clang", "args", expand_os=True)
        if(len(clang_args) > 0):
            args = clang_args.split(' ')
        else:
            # DEBUG BRAD: For some reason this currently doesn't work if I
            #             set it to -xc++. It barfs when it encounters this construct:
            #                 #ifdef __cplusplus
            #                 extern "C" {
            args.append('-xc++')
            #args.append('-xc')
            #args.append('-nostdlib')
            #args.append('-nostdinc')
            ##args.append('--help')
            #args.append('-nostdinc++')
            #args.append('-nobuiltininc')
            #args.append('-mrelax-all')

            # If we're on Linux we might need this to get things
            # to work
            #args.append('-I/home/belliott/projects/shorte/src/3rdparty/clang/include')
            #args.append('-I/usr/include')

        for include in includes:
            args.append("-I%s" % include)
        
        #args.append('-w')
        #args.append('-Xanalyzer')
        #args.append('-analyzer-disable-all-checks')

        # Add the list of preprocessor defines.
        defines = self.m_engine.get_macros()
        for define in defines:
            args.append("-D%s=%s" % (define, defines[define]))

        #WARNING("ARGS")
        #print ' '.join(args)


        STATUS("Parsing %s with clang: args=%s" % (source_file, " ".join(args)))

        
        #args = ['-DCS_LITTLE_ENDIAN', '-Imodules', '-Iplatform']

        if(self.cindex == None):
            self.cindex = clang.cindex.Index.create()

        tu = self.cindex.parse(source_file, args=args, options=options)
        self.tu = tu

        for diag in tu.diagnostics:
            if(diag.severity >= 3):
                msg =  "CLANG Parser Error:\n"
                msg += "  severity: %d\n" % diag.severity
                filename = diag.location.file
                if(filename == None):
                    filename = source_file
                msg += "  location: %s @ %d\n" % (filename, diag.location.line)
                msg += "  message:  %s\n" % diag.spelling
                #print diag.severity
                #print diag.location
                #print diag.spelling
                parser_errors = shorte_get_config("clang", "parser_errors")
                if("warn" == parser_errors):
                    WARNING(msg)
                elif("error" == parser_errors):
                    ERROR(msg)
                elif("fatal" == parser_errors):
                    FATAL(msg)
                else:
                    FATAL("Invalid setting of clang.parser_errors in config file: [%s]" % parser_errors)
            elif(diag.severity == 2):
                message  = "CLANG Parser Warning\n"
                message += "  severity: %d\n" % diag.severity
                filename = diag.location.file
                if(filename == None):
                    filename = source_file
                message += "  location: %s @ %d\n" % (filename, diag.location.line)
                message += "  message:  %s\n" % diag.spelling
                message += "  source_file: %s" % source_file
                WARNING(message)
        #tu = self.cindex.parse(source_file, args=args)
        
        #tu = index.parse(source_file)

        return tu
        
    def parse_buffer_impl(self, page, path, top, tu):

        functions = {}
        enums = {}

        #print "PARSING %s" % page

        typedefs = {}
        typedefs2 = {}
        for cursor in top.get_children():
            if(cursor.kind == clang.cindex.CursorKind.TYPEDEF_DECL):
                #print dir(cursor)
                #print "DISPLAYNAME: %s" % cursor.displayname
                #print "TYPEDEF:     %s" % cursor.underlying_typedef_type.spelling
                #print "SPELLING:    %s" % cursor.spelling
                typedef = cursor.type.spelling
                typename = cursor.underlying_typedef_type.spelling

                if(typename.startswith('struct')):
                    typename = typename[6:]
                elif(typename.startswith('enum')):
                    typename = typename[4:]
                #typename = typename.replace('struct','')
                #typename = typename.replace('enum','')
                typename = typename.strip()
                #print " TYPEDEF %s = %s" % (typename, typedef)
                typedefs[typename] = typedef

                if(not typedefs2.has_key(typename)):
                    typedefs2[typename] = []
                typedefs2[typename].append(typedef)

        add_header = shorte_get_config("shorte", "header_add_to_prototype")

        for cursor in top.get_children():
            try:
                if(cursor.location.file == None):
                    continue
                elif('/usr/include' in str(cursor.location.file)):
                    continue
                elif('/usr/lib' in str(cursor.location.file)):
                    continue
                    
                #print '    visiting %s [%s] at %s:%d' % (cursor.kind, cursor.spelling, cursor.location.file, cursor.location.line)
               
                #raise Exception("Doing nothing for now")
                # Skip anything like global constants that don't belong to
                # this module. It seems like cursor.location.file might be a
                # unicode string so need to cast to the same type to avoid
                # a mismatch
                if(str(cursor.location.file) != str(path)):
                    #print "      Doesn't belong to %s" % path
                    raise Exception("Doesn't belong to this file")
                    #pass
                
                #print '    visiting %s [%s] at %s:%d' % (cursor.kind, cursor.spelling, cursor.location.file, cursor.location.line)

                #tag = tag_t()
                #tag.name = "h"
                #tag.contents = "%s @%s:%d => %s" % (cursor.kind, cursor.location.file, cursor.location.line, cursor.spelling)
                #tag.source = tag.contents
                #tag.file = cursor.location.file
                #tag.line = cursor.location.line
                #tag.modifiers = {}
                #page["tags"].append(tag)

                access_spec = None

                # access_specifier is not available in older versions of clang (3.4 or older)
                # so we'll wrapper it in an catch block to prevent it from bombing out.
                try:
                    if(cursor.kind == clang.cindex.CursorKind.CXX_ACCESS_SPEC_DECL):
                        access_spec = cursor.access_specifier
                        #"access: %d" % access_spec
                except:
                    WARNING("This version of clang is too old, can't get access specifiers")
            
                if cursor.kind in (clang.cindex.CursorKind.ENUM_DECL,
                                   clang.cindex.CursorKind.FUNCTION_DECL,
                                   clang.cindex.CursorKind.STRUCT_DECL,
                                   clang.cindex.CursorKind.MACRO_DEFINITION,
                                   clang.cindex.CursorKind.CLASS_DECL,
                                   clang.cindex.CursorKind.CXX_METHOD,
                                   clang.cindex.CursorKind.CONSTRUCTOR):

                    comment = self.query_comment(cursor)

                    # If the object has no comment then assume it is private
                    if(comment == None or comment.is_private()):
                        raise Exception("Assumed private function")

                    file = path
                    line = cursor.location.line

                    object_name = cursor.spelling
                    if(object_name == None or len(object_name) == 0):
                        object_name = cursor.displayname
                    if(object_name == None or len(object_name) == 0):
                        object_name = cursor.type.spelling

                    # If the object has a typedef then default to that instead. Eventually
                    # we'll support aliases but that doesn't work right now.
                    #if(typedefs.has_key(object_name)):
                    #    WARNING("Renaming %s to %s" % (object_name, typedefs[object_name]))
                    #    object_name = typedefs[object_name]
                            
                    #if(cursor.kind == clang.cindex.CursorKind.MACRO_DEFINITION):
                    #    object_name = cursor.displayname
                    #elif(cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL):
                    #    object_name = cursor.spelling
                    #elif(cursor.kind == clang.cindex.CursorKind.ENUM_DECL):
                    #    object_name = cursor.type.spelling
                    #elif(cursor.kind == clang.cindex.CursorKind.STRUCT_DECL):
                    #    object_name = cursor.spelling
                    #elif(cursor.kind == clang.cindex.CursorKind.CLASS_DECL):
                    #    object_name = cursor.type.spelling

                    #print "VISITING"
                    #print "  dn     =%s" % cursor.displayname
                    #print "  sp     =%s" % cursor.spelling
                    #print "  type.sp=%s" % cursor.type.spelling

                    if(self.object_is_registered(object_name)):
                        #print "ALREADY REGISTERED"
                        #print "  dn     =%s" % cursor.displayname
                        #print "  sp     =%s" % cursor.spelling
                        #print "  type.sp=%s" % cursor.type.spelling
                        raise Exception("object %s already parsed" % object_name)

                    if(add_header != "None" and not (cursor.kind in (clang.cindex.CursorKind.STRUCT_DECL, clang.cindex.CursorKind.ENUM_DECL))):
                        tag = tag_t()
                        tag.name = add_header
                        tag.contents = object_name
                        tag.source = ""
                        tag.file = path 
                        tag.line = cursor.location.line
                        tag.modifiers = {}
                        page["tags"].append(tag)
                
                        word = wikiword_t()
                        word.wikiword = object_name
                        word.label = object_name
                        word.is_bookmark = False
                        word.link = os.path.basename(tag.file)
                        self.m_engine.add_wikiword(word)

                    if(cursor.kind == clang.cindex.CursorKind.MACRO_DEFINITION):
                        define = define_t()
                        object_data = define
                        define.name = object_name
                        define.desc = comment.desc
                        define.description = comment.description
                        define.private = comment.private
                        define.heading = comment.heading
                        define.line = cursor.location.line
                        define.file = path
                    
                        start_offset = cursor.extent.start.offset
                        end_offset   = cursor.extent.end.offset + 1
                        tmp = self.m_file_src[start_offset:end_offset]
                        tmp = tmp.replace(define.name, '')
                        define.value = textblock_t(tmp.strip())
                        
                        if(comment.has_since()):
                            define.set_since(textblock_t(comment.since))
                        if(comment.has_requirements()):
                            define.set_requirements(textblock_t(comment.get_requirements()))

                        tag = tag_t()
                        tag.name = "define"
                        tag.contents = define
                        tag.line = define.line
                        tag.file = define.file
                        tag.source = define.source
                        tag.modifiers = {}
                        tag.heading = define.heading
                        page["tags"].append(tag)
                        

                        #print '@define: file=%s line=%d' % (file, line)
                        #print '--name: %s' % cursor.displayname
                        #print '--description:'
                        #print indent_lines(comment.desc, '    ')
                        #print '--value:'

                        #name = cursor.displayname


                        #print '    %s' % content

                        # raw_comment doesn't work with defines
                        # because they are stripped by the preprocessor
                        # print cursor.raw_comment

                    elif(cursor.kind in (clang.cindex.CursorKind.FUNCTION_DECL,
                                         clang.cindex.CursorKind.CXX_METHOD,
                                         clang.cindex.CursorKind.CONSTRUCTOR)):

                        prototype = prototype_t()
                        object_data = prototype
                        prototype.set_name(object_name)
                        prototype.set_returns(comment.returns)
                        prototype.set_description(comment.desc, textblock=False)
                        prototype.set_description(comment.description, textblock=True)


                        if(comment.has_pseudocode()):
                            prototype.set_pseudocode(
                                comment.get_pseudocode(),
                                self.m_engine.m_source_code_analyzer, "c")

                        prototype.set_see_also(comment.see_also)
                            
                        if(comment.has_since()):
                            prototype.set_since(textblock_t(comment.since))
                        if(comment.has_requirements()):
                            prototype.set_requirements(textblock_t(comment.get_requirements()))

                        prototype.set_private(comment.private)
                        prototype.set_deprecated(comment.deprecated)

                        prototype.set_line(cursor.location.line)
                        prototype.set_file(self.m_source_file)


                        #print '@prototype: language="c" file=%s line=%d' % (file, line)
                        #print '--function: %s' % cursor.spelling
                        #print "--prototype:"

                        ptype = ''
                        args = cursor.get_arguments()
                        
                        arg_list = []
                        parameters = []
                        for arg in args:
                            arg_type = arg.type.spelling
                            if(arg_type.startswith("_Bool")):
                                arg_type = arg_type.replace("_Bool", "bool")
                            arg_name = arg.spelling
                            arg_list.append("%s %s" % (arg_type, arg_name))

                            #print "ARG.START = %d" % arg.extent.start.offset
                            #print "CODE: [%s]" % self.m_file_src[cursor.extent.start.offset:arg.extent.start.offset]
                            
                            acmt = self.query_comment_before(cursor.extent.start.offset, arg.extent.start.offset)
                            
                            param = param_t()

                            if(acmt != None):
                                desc = acmt.desc.strip()
                                matches = re.search('^(\[(.*?)\]\s*-\s*)', desc)
                                if(matches != None):
                                    io = matches.groups()[1]
                                    match = matches.groups()[0]
                                    desc = desc.replace(match, '')
                                    param.set_io(io)

                            param.set_name(arg_name)
                            param.set_type(arg_type)

                            if(acmt != None):
                                param.set_description(desc, textblock=False)
                                param.set_description(textblock_t(desc), textblock=True)

                            parameters.append(param)

                        prototype.set_params(parameters)

                        result_type = cursor.result_type.spelling
                        if(result_type.startswith("_Bool")):
                            result_type = result_type.replace("_Bool", "bool")

                        ptype = "    %s %s(" % (result_type, cursor.spelling) + ', '.join(arg_list) + ");"
                        prototype.set_prototype(ptype,
                                self.m_engine.m_source_code_analyzer, "c")

                        for param in comment.params:
                            data = comment.params[param]
                            name = param
                            io   = data.get_io()
                            #print data

                            for i in range(0, len(parameters)):
                                p = parameters[i]
                                if(p.name == name):
                                    p.set_description(data.get_description(False), textblock=False)
                                    p.set_description(data.get_description(True),  textblock=True)
                                    p.set_io(io)

                        prototype.validate_params()
                        
                        if(cursor.kind in (clang.cindex.CursorKind.CXX_METHOD, clang.cindex.CursorKind.CONSTRUCTOR)):
                            # Get the name of the class that this belongs to
                            cname = cursor.lexical_parent.displayname
                            cls = self.m_engine.class_get(cname)
                            prototype.set_class(cls)
                            
                            # access_specifier is only available in newer versions of clang (> 3.4)
                            # so we'll trap the error here.
                            try:
                                access = cursor.access_specifier
                                prototype.set_access_spec(access)
                            except:
                                WARNING("This version of clang is too old, can't get access specifiers")

                            cls.prototype_add(prototype)

                        tag = tag_t()
                        tag.name = "prototype"
                        tag.contents = prototype
                        tag.line = prototype.line
                        tag.file = prototype.file
                        tag.source = prototype.source
                        tag.modifiers = {}
                        # DEBUG BRAD: THis doesn't work
                        #tag.heading = prototype.heading
                        page["tags"].append(tag)
                        
                        #self.object_register(prototype.get_name(), prototype)
                        
                        #self.object_register(f

                    elif(cursor.kind == clang.cindex.CursorKind.ENUM_DECL):
                        
                        #print "@enum: file=%s line=%d" % (file, line)
                        #print "--name: ", cursor.type.spelling

                        #print "--description:"
                        #print indent_lines(comment.desc, '    ')
                        
                        children = cursor.get_children()
                        rows = []
                        # DEBUG BRAD: Need to re-write this code to be
                        #             more like structure fields
                        for child in children:
                            if(child.raw_comment != None):
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
                                col["text"] = child.spelling
                                row["cols"].append(col)
                                
                                col = {}
                                col["span"] = 1
                                col["text"] = "%d" % child.enum_value
                                row["cols"].append(col)
                                
                                cmnt = self.parse_cpp_func_comment(child.raw_comment)

                                col = {}
                                col["span"] = 1
                                col["text"] = cmnt.desc
                                col["textblock"] = cmnt.description
                                row["cols"].append(col)

                                rows.append(row)

                                #print '- %s | %s |\n%s' % (child.spelling, child.enum_value, indent_lines(comment.desc, '    '))
                            #else:
                            #    WARNING("Enum parameter %s missing description" % child.spelling)
                    
                        # If the type has multiple typedefs/aliases
                        # then construct the list of types here.
                        types = []
                        types.append(object_name)

                        if(typedefs2.has_key(object_name)):
                            for t in typedefs2[object_name]:
                                types.append(t)

                        for t in types:
                            if(self.object_is_registered(t)):
                                #print "ALREADY REGISTERED: %s" % t
                                #print "  dn     =%s" % cursor.displayname
                                #print "  sp     =%s" % cursor.spelling
                                #print "  type.sp=%s" % cursor.type.spelling
                                continue

                            if(add_header != "None"):
                                tag = tag_t()
                                tag.name = add_header
                                tag.contents = t
                                tag.source = ""
                                tag.file = path 
                                tag.line = cursor.location.line
                                tag.modifiers = {}
                                page["tags"].append(tag)
                        
                                word = wikiword_t()
                                word.wikiword = t
                                word.label = t
                                word.is_bookmark = False
                                word.link = os.path.basename(tag.file)
                                self.m_engine.add_wikiword(word)

                            # If the type has multiple typedefs then
                            # record the other aliases in the see_also
                            # field.
                            see_also = []
                            for t2 in types:
                                if(t != t2):
                                    see_also.append(t2)

                            enum = enum_t()
                            object_data = enum
                            enum.set_name(t)
                            enum.values = rows
                            enum.comment = comment
                            enum.set_description(comment.desc, textblock=False)
                            enum.set_description(comment.description, textblock=True)
                            enum.private = comment.private
                            enum.deprecated = comment.deprecated
                            enum.line = cursor.location.line
                            enum.file = self.m_source_file
                            enum.max_cols = 3
                            enum.set_see_also(', '.join(see_also))
                            
                            if(comment.has_since()):
                                enum.set_since(textblock_t(comment.since))
                            if(comment.has_requirements()):
                                enum.set_requirements(textblock_t(comment.get_requirements()))

                            tag = tag_t()
                            tag.name = "enum"
                            tag.contents = enum
                            tag.source = ""
                            tag.line = enum.line
                            tag.file = enum.file
                            tag.modifiers = {}
                            tag.heading = comment.heading
                            page["tags"].append(tag)
                            
                            if(comment.has_example()):
                                object_data.set_example(
                                    comment.get_example(),
                                    self.m_engine.m_source_code_analyzer, "c")

                            object_data.set_comment(comment)
                                
                            self.object_register(object_name, object_data)
                        
                        # Mark this block of code as processed so that
                        # we don't process it again
                        start_offset = cursor.extent.start.offset
                        end_offset   = cursor.extent.end.offset + 1
                        self.processed.append([start_offset, end_offset])

                        continue


                    elif(cursor.kind == clang.cindex.CursorKind.STRUCT_DECL):

                        #print "--description:"
                        #print indent_lines(comment.desc, '    ')

                        fields = []

                        children = cursor.get_children()
                        #print '-- fields:'
                        #print '- Type | Name | Description'

                        for child in children:
                            #print "child:", child
                            bits = child.type.spelling
                            if(bits.startswith("_Bool")):
                                #FATAL("DO I GET HERE?")
                                bits = bits.replace("_Bool", "bool")
                            
                            name = child.spelling
                        
                            #print "Parsing field %s, bits: %s" % (name,bits)
                            if(name == None):
                                continue

                            if(child.raw_comment != None):
                                fcomment = self.parse_cpp_func_comment(child.raw_comment)
                                #print '''- %s | %s |\n%s
#''' % (bits, name, indent_lines(comment.desc, '    '))

                            field = field_t()
                            field.set_name(name)
                            field.set_description(fcomment.description)
                            field.set_type(bits)
                            fields.append(field)
                       
                        # If the type has multiple typedefs/aliases
                        # then construct the list of types here.
                        types = []
                        types.append(object_name)
                        if(typedefs2.has_key(object_name)):
                            for t in typedefs2[object_name]:
                                types.append(t)

                        for t in types:
                            if(self.object_is_registered(t)):
                                #print "ALREADY REGISTERED"
                                #print "  dn     =%s" % cursor.displayname
                                #print "  sp     =%s" % cursor.spelling
                                #print "  type.sp=%s" % cursor.type.spelling
                                continue

                            if(add_header != "None"):
                                tag = tag_t()
                                tag.name = add_header
                                tag.contents = t
                                tag.source = ""
                                tag.file = path 
                                tag.line = cursor.location.line
                                tag.modifiers = {}
                                page["tags"].append(tag)
                                
                                word = wikiword_t()
                                word.wikiword = t
                                word.label = t
                                word.is_bookmark = False
                                word.link = os.path.basename(tag.file)
                                self.m_engine.add_wikiword(word)

                            # If the type has multiple typedefs then
                            # record the other aliases in the see_also
                            # field.
                            see_also = []
                            for t2 in types:
                                if(t != t2):
                                    see_also.append(t2)

                            struct = struct_t()
                            object_data = struct
                            struct.set_name(t)
                            struct.set_description(comment.desc, textblock=False)
                            struct.set_description(comment.description)
                            struct.private = comment.private
                            struct.heading = comment.heading
                            struct.line = cursor.location.line
                            struct.file = path
                            struct.max_cols = 3 #len(struct.fields)
                            struct.fields.extend(fields)
                            struct.set_see_also(', '.join(see_also))
                        
                            if(comment.has_since()):
                                struct.set_since(textblock_t(comment.since))
                            if(comment.has_requirements()):
                                struct.set_requirements(textblock_t(comment.get_requirements()))
                            #if(comment.has_deprecated()):
                            #    struct.set_deprecated(True, comment.deprecated_msg)
                            struct.deprecated = comment.deprecated

                            tag = tag_t()
                            tag.name = "struct"
                            tag.contents = struct
                            tag.line = struct.line
                            tag.file = struct.file
                            tag.source = struct.source
                            tag.modifiers = {}
                            tag.heading = struct.heading
                            page["tags"].append(tag)

                            if(comment.has_example()):
                                object_data.set_example(
                                    comment.get_example(),
                                    self.m_engine.m_source_code_analyzer, "c")

                            object_data.set_comment(comment)
                                
                            self.object_register(object_name, object_data)
                        
                        # Mark this block of code as processed so that
                        # we don't process it again
                        start_offset = cursor.extent.start.offset
                        end_offset   = cursor.extent.end.offset + 1
                        self.processed.append([start_offset, end_offset])

                        continue
                    

                    elif(cursor.kind == clang.cindex.CursorKind.CLASS_DECL):

                        cls = self.m_engine.class_get(object_name)
                        cls.set_name(object_name)
                        cls.set_description(comment.desc, textblock=False)
                        cls.set_description(comment.description)
                        cls.line = cursor.location.line
                        cls.file = path
                        if(comment.has_since()):
                            cls.set_since(textblock_t(comment.since))

                        #print "@class: file=%s line=%d" % (file, line)
                        #print "--name: " , cursor.type.spelling
                        #print "--description:"
                        #print indent_lines(comment.desc, '    ')

                        tag = tag_t()
                        tag.name = "class"
                        tag.contents = cls
                        tag.line = cls.line
                        tag.file = cls.file
                        tag.modifiers = {}
                        page["tags"].append(tag)

                        pass
    
                    #print ''
                    if(comment.has_example()):
                        object_data.set_example(
                            comment.get_example(),
                            self.m_engine.m_source_code_analyzer, "c")

                    object_data.set_comment(comment)
                        
                    self.object_register(object_name, object_data)
                    
                    # Mark this block of code as processed so that
                    # we don't process it again
                    start_offset = cursor.extent.start.offset
                    end_offset   = cursor.extent.end.offset + 1
                    self.processed.append([start_offset, end_offset])

            except Exception as e:
                if(cursor.spelling != None):
                    object_name = cursor.spelling
                else:
                    object_name = cursor.displayname

                if(len(object_name) == 0):
                    object_name = cursor.type.spelling

                #WARNING("SKIPPING %s" % object_name)
                #traceback.print_exc()

                #sys.exc_info()
                #WARNING(str(e))
                pass
            


    def parse_file_brief(self, text):
        shorte = shorte_parser_t(self.m_engine)
        text = self.format_comment(text, strip_single_line_comments=False)
        parts = text.split('@brief')
        text = parts[1]
        #print text
        shorte.parse_string(text, self.m_source_file)
        tags = shorte.m_pages[0]["tags"]
        self.page["tags"].extend(tags)

    def parse_buffer(self, input, source_file):
         
        self.m_source_file = source_file

        INFO("Parsing %s" % source_file)

        if(source_file.endswith(".tpl")):
            FATAL("%s does not look like a C/C++ file, please specify the correct parser" % source_file)

        tu = self.load_source_file(source_file)
        self.m_source_file = source_file

        self.page = {}
        self.page["title"] = source_file
        self.page["tags"] = []
        self.page["source_file"] = source_file
        self.page["links"] = []
        self.page["file_brief"] = self.m_file_brief
        self.page["file_author"] = self.m_author
        

        # Step through all the tags searching for the file brief
        for x in tu.cursor.get_tokens():
            if(x.kind == clang.cindex.TokenKind.COMMENT):
                text = x.spelling
                if("@file" in text):
                    self.parse_file_brief(text)
        

        self.parse_buffer_impl(self.page, source_file, tu.cursor, tu)

        #tu.__del__()
        
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
''').substitute({"name" : self.m_source_file,
                 "brief" : self.m_file_brief})
                    
            shorte = shorte_parser_t(self.m_engine)
            shorte.parse_string(summary, self.m_current_file)
            tags = shorte.m_pages[0]["tags"]

            tags.extend(self.page["tags"])
            self.page["tags"] = tags

        self.m_pages.append(self.page)

        return self.page


    def parse(self, source_file):

        self.parse_buffer(None, source_file)

