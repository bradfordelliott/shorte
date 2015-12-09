# -*- coding: iso-8859-15 -*-
"""This is the base class for all output templates"""

import os
import re
import string
from src.shorte_defines import *

HEADING_DEFAULT = 0
HEADING1 = 1
HEADING2 = 2
HEADING3 = 3
HEADING4 = 4
HEADING5 = 5
HEADING6 = 6

class template_t(object):
    """The base class template. All other output templates
       are derived from this class"""
   
    def __init__(self, engine, indexer):
        """Constructor for the template object.

           @param engine  [I] - The shorte engine instance
           @param indexer [I] - The indexer used to track page numbers
        """
        
        #print "Constructing template"
        
        self.m_contents = ""
        self.m_engine = engine
        self.m_indexer = indexer
        
        self.m_wikify = int(self.m_engine.get_config("wikify", "allow"))
        self.m_wikify_comments = int(self.m_engine.get_config("wikify", "allow_in_comments"))
        
        self.m_end_characters = list(string.punctuation)
        self.m_end_characters.append(' ')
        self.m_end_characters.append('\t')
        self.m_end_characters.append('\r')
        self.m_end_characters.append('\n')
        # Can't use _ as a separator for wikiwords because we want to hyperlink
        # C Code. Also, don't use @ as a separator since we need it for documenting
        # shorte tags.
        self.m_end_characters.remove('_')
        self.m_end_characters.remove('@')

        self.m_end_characters_dict = {}
        for i in self.m_end_characters:
            self.m_end_characters_dict[i] = True

    def allow_wikify_comments(self):
        return self.m_wikify_comments
    
    def format_links(self, data):
        """This method is called from format_text() to format shorte or
           markdown links

           @param data [I] - The text to parse to replace links.

           @return The formatted string with links replaced.
        """

        output = ""
        start = 0
        end = len(data)

        STATE_NORMAL = 0
        STATE_HYPERLINK = 1
        STATE_SHORTE_LINK = 2
        STATE_MARKDOWN_LINK = 3
        STATE_MARKDOWN_IMAGE = 4
        STATE_OPEN_BRACKET = 5

        states = []
        states.append(STATE_NORMAL)

        i = start
        output = ""

        replacement = "" 

        while(i < end):
            state = states[-1]

            segment = data[i:i+8]

            #print "STATE: %d" % state
            #print "segment: [%s]" % segment

            if(state == STATE_NORMAL):
                if(data[i:i+2] == "[["):
                    replacement = ""
                    states.append(STATE_SHORTE_LINK)
                    i += 2
                elif(data[i] == "["):
                    replacement = "["
                    states.append(STATE_OPEN_BRACKET)
                    i += 1
                elif(data[i:i+2] == "!["):
                    replacement = "!["
                    states.append(STATE_OPEN_BRACKET)
                    i += 2
                elif(segment.startswith("http://")):
                    states.append(STATE_HYPERLINK)
                    replacement = data[i:i+7]
                    i += 7
                elif(segment.startswith("https://")):
                    states.append(STATE_HYPERLINK)
                    replacement = data[i:i+8]
                    i += 8
                elif(segment.startswith("mailto://")):
                    states.append(STATE_HYPERLINK)
                    replacement = data[i:i+9]
                    i += 9
                elif(segment.startswith("ftp://")):
                    states.append(STATE_HYPERLINK)
                    replacement = data[i:i+6]
                    i += 6
                else:
                    output += data[i]
                    i += 1

            elif(state == STATE_HYPERLINK):

                if(data[i].isalpha() or data[i].isdigit() or data[i] in ("-", "%", ".", "_", "/", "?", "=", "+")):
                    replacement += data[i]
                else:
                    if(replacement.endswith(".")):
                        replacement = replacement[0:-1]
                        output += self.format_link(replacement, replacement) + "."
                    else:
                        output += self.format_link(replacement, replacement)
                    replacement = ""

                    states.pop()
                    output += data[i]

                i += 1

            elif(state == STATE_SHORTE_LINK):
                if(data[i:i+2] == "]]"):
                    if("," in replacement):
                        parts = replacement.split(",")
                        output += self.format_link(parts[0], parts[1])
                    else:
                        output += self.format_link(replacement, replacement)
                    replacement = ""
                    i += 2
                    states.pop()
                else:
                    replacement += data[i]
                    i += 1

            elif(state == STATE_OPEN_BRACKET):
                if(data[i] == "]"):
                    states.pop()
                    if(data[i:i+2] == "]("):
                        i += 1
                        url = ""
                        if(replacement.startswith("![")):
                            states.append(STATE_MARKDOWN_IMAGE)
                            label = replacement[2:]
                        else:
                            states.append(STATE_MARKDOWN_LINK)
                            label = replacement[1:]
                        replacement = ""
                    else:
                        replacement += data[i]
                        output += replacement
                        replacement = ""
                else:
                    replacement += data[i]

                i += 1

            elif(state == STATE_MARKDOWN_LINK):
                if(data[i] == ")"):
                    output += self.format_link(url, label)
                    states.pop()
                else:
                    url += data[i]

                i += 1
            
            elif(state == STATE_MARKDOWN_IMAGE):
                if(data[i] == ")"):
                    tag = {}
                    tag["src"] = url
                    tag["caption"] = label
                    image = self.m_engine.m_parser.parse_image(tag)
                    output += self.format_image(image)
                    states.pop()
                else:
                    url += data[i]

                i += 1

        if(replacement != ""):
            if(replacement.endswith(".")):
                replacement = replacement[0:-1]
                output += self.format_link(replacement, replacement) + "."
            else:
                output += self.format_link(replacement, replacement)

        return output
    
    def format_python(self, input_source, modifiers):
        self.m_contents += ""

    def format_perl(self, input_source, modifiers):
        self.m_contents += ""
    
    def format_shell(self, input_source, modifiers):
        self.m_contents += ""

    def format_pycairo(self, file, input_source):
        self.m_contents += ""
    
    def format_d(self, input_source, modifiers):
        self.m_contents += ""

    def format_c(self, input_source, modifiers):
        self.m_contents += ""
    
    def format_code(self, source):
        self.m_contents += ""

    def format_note(self, content):
        self.m_contents += ""

    def format_unordered_list(self, source):
        self.m_contents += ""
    
    def format_ordered_list(self, source, start):
        self.m_contents += ""

    def format_table(self, source):    
        self.m_contents += ""
    
    def format_prototype(self, source, file):
        self.m_contents += ""

    def append_header(self, tag, data, file):
        self.m_contents += ""

    def append_source_code(self, tag, data, modifiers):
        self.m_contents += ""

    def append(self, tag_field, data, modifiers):
        self.m_contents += ""

    def get_contents(self):
        return self.m_contents
    
    def install_support_files(self, outputdir):
        return False
        
    def _process_link(self, matches):

        data = matches.groups()[0]

        matches = re.search("(.*),(.*)", data)

        if(matches != None):

            source = matches.groups()[0].strip()
            label  = matches.groups()[1].strip()
            
            # If the source begins with an @ sign then it is a local
            # link within the same document so we need to convert the
            # @ sign to # for HTML
            if(source.startswith("@")):
                external = False
            else:
                external = True

            source = re.sub("^@", "#", source)
            label = re.sub("(.*?@)", "", label)

            source = re.sub("^\"(.*)\"", "\\1", source) 
            label  = re.sub("^\"(.*)\"", "\\1", label) 

            #print "source = %s, label = %s" % (source, label)
        else:
            source = data.strip()
            label = source

            # If the source begins with an @ sign then it is a local
            # link within the same document so we need to convert the
            # @ sign to # for HTML
            source = re.sub("^@", "#", source)

            label = re.sub("(.*?@)", "", label)
            external = False

            #print "source = %s, label = %s" % (source, label)
        
        expr = re.compile("(\$[A-Za-z0-9_]+)", re.DOTALL)
        source = xmlize(expr.sub(self.m_engine._expand_url, source))
        label  = expr.sub(self.m_engine._expand_url, label)

        return (source, label, external)

    def _table_row(self):
        row = {}
        row["is_subheader"] = False
        row["is_header"] = False
        row["is_reserved"] = False
        row["is_caption"] = False
        row["is_spacer"] = False
        row["is_crossed"] = False

        return row
    
    def strip_redundant_blank_lines(self, cnts):
        """This is a generic method that can be used to strip
           redundant blank lines from a generated document.

           @param cnts [I] - The buffer to search for redundant
                             blank lines.

           @return The return array with redundant blank lines removed.
        """

        # Strip any redundant blank lines that don't need to be part
        # of the output document
        lines = cnts.split("\n")
        blank_line_count = 0
        output = []
        for line in lines:
            if(len(line.strip()) == 0):
                blank_line_count += 1
                if(blank_line_count >= 2):
                    continue
            else:
                blank_line_count = 0

            output.append(line)

        return "\n".join(output)


    def wikify(self, data, exclude = [], debug=False):

        if(not self.m_wikify):
            return data

        excluded = {}
        check_excluded = False
        for e in exclude:
            excluded[e] = True
            check_excluded = True

        words = []
        word = ''

        #print "Wikify"
        
        # Figure out the list of punctuation characters that are used to
        # split up wikiwords.
        # DEBUG BRAD: Switched to a dictionary for speedup
        #end_characters = self.m_end_characters
        end_characters = self.m_end_characters_dict

        for i in data:

            # DEBUG BRAD: Switched to a dictionary for speedup
            #if(i in end_characters):
            if(end_characters.has_key(i)):

                words.append(word)
                words.append(i)

                word = ''

            else:
                word += i

        if(len(word) > 0):
            words.append(word)

        output = ''

        for word in words:
            
            if(debug):
                print "    Checking [%s]" % word

            # DEBUG BRAD: Switched to a dictionary for performance
            #if(word in end_characters):
            if(end_characters.has_key(word)):
                output += word 
            else:

                link = None

                exclude_word = False

                # DEBUG BRAD: Switched to a dictionary for performace
                #for tmp in exclude:
                #    if(tmp == word):
                #        exclude_word = True
                #        break
                if(check_excluded):
                    if(excluded.has_key(word)):
                        exclude_word = True
            
                is_bookmark = False

                if(not exclude_word):
                    link = self.m_engine.is_wiki_word(word)
                    if(link != None):
                        is_bookmark = link.is_bookmark
                        
                        #link_word = word
                        #word = link.label
                        #link = link.link

                    # If we didn't find a match for the word then it might
                    # contain a period which we didn't use as a separator for wiki words.
                    # In that case need to try the first part and see if there
                    # is a wikiword match for it.
                    else:
                        pos = word.rfind(".")

                        if(pos != -1):
                            link = self.m_engine.is_wiki_word(word[0:pos])
                            #if(link != None):
                            #    link = link.link
                            #    link_word = word[0:pos]
                            #    word = link.label

                if(link != None):
                    output += self.format_wikiword(link, word)
                else:
                    output += word

        return output

    def xmlize(self, data):

        # Convert an < and > characters
        data = re.sub("&", "&amp;", data)
        data = re.sub("'", "&apos;", data)
        data = re.sub("<", "&lt;", data)
        data = re.sub(">", "&gt;", data)

        #data = re.sub("", "&apos;", data)
        #data = re.sub("®", "&#174;", data)

        return data




