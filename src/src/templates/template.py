# -*- coding: iso-8859-15 -*-
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

class template_t:
   
    def __init__(self, engine, indexer):
        
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

    def allow_wikify_comments(self):
        return self.m_wikify_comments
    
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
    
    
    def wikify(self, data, exclude = [], debug=False):

        if(not self.m_wikify):
            return data

        words = []
        word = ''

        #print "Wikify"
        
        # Figure out the list of punctuation characters that are used to
        # split up wikiwords.
        end_characters = self.m_end_characters

        for i in data:

            if(i in end_characters):

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

            if(word in end_characters):
                output += word 
            else:

                link = None

                exclude_word = False
                for tmp in exclude:
                    if(tmp == word):
                        exclude_word = True
                        break

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
        data = re.sub("", "&apos;", data)
        data = re.sub("<", "&lt;", data)
        data = re.sub(">", "&gt;", data)

        data = re.sub("®", "&#174;", data)

        return data




