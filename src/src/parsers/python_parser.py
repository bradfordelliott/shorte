#from shorte_parser import *

import inspect
from python_parser import *

import imp

from src.parsers.shorte_parser import *

#class python_parser_t(shorte_parser_t):
class python_parser_t(shorte_parser_t):

    def __init__(self, engine):

        self.m_engine = engine
        shorte_parser_t.__init__(self, engine)
    
    def format_comment(self, comment, strip_single_line_comments=True):

        return comment

    def parse_cpp_func_comment(self, text):
        '''This method is called to parse a comment associated with a C/C++
           function in order to extract the associated fields.

           @param self [I] - The parser class instance
           @param text [I] - The text to parse.

           @return A dictionary containing the comment attributes.
        '''

        comment = comment_t()

        # Anything before the @brief tag is a block of standard
        # shorte text that needs to be processed separately
        if("@brief" in text):
            #WARNING("Found an @brief tag") 
            parts = text.split('@brief')

            prefix = parts[0]
            shorte = shorte_parser_t(self.m_engine)
            
            # In order to support wikiwords we need to pass the source
            # file name with a .html extension. Then we need to append
            # any wiki words from the source file to the global list
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

            matches2 = re.search("\[(.*?)\] *- *(.*)", desc, re.DOTALL)
            if(matches2 != None):
                desc = matches2.groups()[1]
                io = matches2.groups()[0]

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
                
                    if(field_format == "text"):
                        val = self.format_text(val)

                    if(expr == "deprecated"):
                        msg = trim_leading_blank_lines(val)
                        msg = textblock_t(msg)
                        comment.set_deprecated(msg)
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

        #print "EXAMPLE: %s" % comment.example

        
        return comment
    
    def format_text(self, text):
        text = re.sub("#", "\#", text)
        return text

    def parse_buffer(self, input, source_file):
        '''This is a description of the parse() method
           and it describes how the method works

           @param input          [I] - The input buffer to parse
           @param source_file    [I] - The source file to parse
           @param container_file [I] - If this file was included from
                                       another source file then this will
                                       point to the container source file.

           @return N/A right now
        '''

        self.m_source_file = source_file
        
        add_header = shorte_get_config("shorte", "header_add_to_prototype")

        self.page = {}
        self.page['title'] = source_file
        self.page['tags'] = []
        self.page['source_file'] = source_file
        self.page['links'] = []
        self.page['file_brief'] = ''
        self.page['file_author'] = ''

        module = imp.load_source('inspected', source_file)
        #member_list = getmembers(python_parser_t)

        if(module.__doc__):
            shorte = shorte_parser_t(self.m_engine)
            shorte.parse_string(module.__doc__, self.m_source_file)
            tags = shorte.m_pages[0]["tags"]
            self.page["tags"].extend(tags)

        member_list = inspect.getmembers(module)
        #print member_list
        for member in member_list:

            name = member[0]
            obj  = member[1]

            if(inspect.isfunction(obj)):

                src = inspect.getsourcelines(obj)
                lineno = src[1]

                comment = self.parse_cpp_func_comment(obj.__doc__)
                prototype = prototype_t()
                prototype.set_name(name)
                prototype.file = source_file
                prototype.line = lineno
                prototype.set_description(comment.get_description())
                        
                parameters = []

                argspec = inspect.getargspec(obj)
                cparams = comment.params

                for arg in argspec.args:
                    param = param_t()
                    param.set_name(arg)

                    if(cparams.has_key(arg)):
                        param.set_description(cparams[arg].get_description())
                        param.set_io(cparams[arg].get_io())

                    parameters.append(param)

                ptype = name + "(" + ",".join(argspec.args) + ")"
                prototype.set_prototype(ptype, self.m_engine.m_source_code_analyzer, "python")
                prototype.set_params(parameters)

                if(comment.has_returns()):
                    prototype.set_returns(comment.get_returns())

                if(comment.has_since()):
                    prototype.set_since(textblock_t(comment.get_since()))
                if(comment.has_deprecated()):
                    prototype.set_deprecated(comment.get_deprecated())
                if(comment.has_see_also()):
                    prototype.set_see_also(comment.get_see_also())
                if(comment.has_example()):
                    prototype.set_example(comment.get_example(),
                                    self.m_engine.m_source_code_analyzer, "python")
                if(comment.has_requirements()):
                    prototype.set_requirements(comment.get_requirements())

                if(add_header):
                    tag = tag_t()
                    tag.name = add_header
                    tag.contents = name
                    tag.source = name
                    tag.file = source_file
                    tag.line = lineno
                    tag.modifiers = {}
                    self.page['tags'].append(tag)
                    
                    word = wikiword_t()
                    word.wikiword = name
                    word.label = name
                    word.is_bookmark = False
                    word.link = os.path.basename(source_file)
                    word.source_file = source_file
                    self.m_engine.add_wikiword(word)

                tag = tag_t()
                tag.name = 'prototype'
                tag.contents = prototype
                tag.line = lineno
                tag.file = source_file
                tag.source = 'tbd'
                tag.modifiers = {}
                self.page['tags'].append(tag)

            elif(inspect.ismethod(obj)):
                #print "Found method %s" % name
                pass

            elif(inspect.isclass(obj)):

                cls = class_t()
                cls.set_name(name)
                cls.file = source_file
                cls.line = lineno
                cls.set_description(comment.get_description())

                members = inspect.getmembers(obj)

                for member in members:
                    mname = member[0]
                    mobj  = member[1]

            
                    if(inspect.ismethod(mobj)):
                        #print "member = %s" % mname
                        p = prototype_t()
                        p.set_name(mname)
                        argspec = inspect.getargspec(mobj)
                        ptype = name + "(" + ",".join(argspec.args) + ")"
                        p.set_prototype(ptype, self.m_engine.m_source_code_analyzer, "python")
                        cls.prototype_add(p)

                if(add_header):
                    tag = tag_t()
                    tag.name = add_header
                    tag.contents = name
                    tag.source = name
                    tag.file = source_file
                    tag.line = lineno
                    tag.modifiers = {}
                    self.page['tags'].append(tag)
                    
                    word = wikiword_t()
                    word.wikiword = name
                    word.label = name
                    word.is_bookmark = False
                    word.link = os.path.basename(source_file)
                    word.source_file = source_file
                    self.m_engine.add_wikiword(word)

                tag = tag_t()
                tag.name = 'class'
                tag.contents = cls
                tag.line = lineno
                tag.file = source_file
                tag.source = 'tbd'
                tag.modifiers = {}
                self.page['tags'].append(tag)
            
                
        self.m_pages.append(self.page)
        return self.page
    
    def parse(self, source_file):
        self.parse_buffer(None, source_file)


