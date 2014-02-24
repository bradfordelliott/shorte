#!/bin/bash/env python
import re
import sys
sys.path.append("..")
from shorte_defines import trim_leading_indent, trim_leading_blank_lines

class cpp_parser_t():

    def format_comment1(self, comment, strip_single_line_comments=True):

        #print "COMMENT_BEFORE\n[%s]" % comment
        chars = list(comment)
        output = ''
        i = 0
        length = len(chars)
        while i < length:
            if(chars[i] == '\r'):
                i += 1
                continue

            if(chars[i] == '\n'):
                output += chars[i]
                i += 1

                # Search forward and see if the next
                # line starts with an asterisk that needs to
                # be stripped
                j = i
                while(j < length and (chars[j] == ' ')):
                    j += 1

                if(j < length and chars[j] == '*'):
                    if(j + 1 < length and chars[j+1] != '/'):
                        i = j + 1
                        continue

            elif(chars[i] == '/'):
                if(chars[i+1] == '*'):
                    i += 1
                    while(chars[i] == '*'):
                        i += 1
                else:
                    output += chars[i]
                    i += 1

            elif(chars[i] == '*'):
                if(chars[i+1] == '/'):
                    i += 2

                else:
                    output += chars[i]
                    i += 1

            else:
                output += chars[i]
                i += 1

        comment = output

        #comment = re.sub("/\*\*\<", "", comment)
        #comment = re.sub("/\*", "", comment)
        #comment = re.sub("\*/", "", comment)
        #comment = re.sub("^\s*\*", "", comment, re.MULTILINE)

        #expr = re.compile("^\s*\*", re.MULTILINE)
        #comment = expr.sub("", comment)
        #
        #if(strip_single_line_comments):
        #    #comment = re.sub(" +", " ", comment)
        #    comment = re.sub("//", "", comment)
        
        #print "COMMENT_1\n[%s]" % comment
        comment = trim_leading_blank_lines(comment)
        #print "COMMENT_2\n[%s]" % comment
        comment = trim_leading_indent(comment)
        #print "COMMENT_3\n[%s]" % comment

        return comment
    def format_comment2(self, comment, strip_single_line_comments=True):

        #print "COMMENT_BEFORE\n[%s]" % comment
        chars = list(comment)
        output = []
        i = 0
        length = len(chars)
        while i < length:
            if(chars[i] == '\r'):
                i += 1
                continue

            if(chars[i] == '\n'):
                output.append(chars[i])
                i += 1

                # Search forward and see if the next
                # line starts with an asterisk that needs to
                # be stripped
                j = i
                while(j < length and (chars[j] == ' ')):
                    j += 1

                if(j < length and chars[j] == '*'):
                    if(j + 1 < length and chars[j+1] != '/'):
                        i = j + 1
                        continue

            elif(chars[i] == '/'):
                if(chars[i+1] == '*'):
                    i += 1
                    while(chars[i] == '*'):
                        i += 1
                else:
                    output.append(chars[i])
                    i += 1

            elif(chars[i] == '*'):
                if(chars[i+1] == '/'):
                    i += 2

                else:
                    output.append(chars[i])
                    i += 1

            else:
                output.append(chars[i])
                i += 1

        comment = ''.join(output)

        #comment = re.sub("/\*\*\<", "", comment)
        #comment = re.sub("/\*", "", comment)
        #comment = re.sub("\*/", "", comment)
        #comment = re.sub("^\s*\*", "", comment, re.MULTILINE)

        #expr = re.compile("^\s*\*", re.MULTILINE)
        #comment = expr.sub("", comment)
        #
        #if(strip_single_line_comments):
        #    #comment = re.sub(" +", " ", comment)
        #    comment = re.sub("//", "", comment)
        
        #print "COMMENT_1\n[%s]" % comment
        comment = trim_leading_blank_lines(comment)
        #print "COMMENT_2\n[%s]" % comment
        comment = trim_leading_indent(comment)
        #print "COMMENT_3\n[%s]" % comment

        return comment

    def format_comment3(self, comment, strip_single_line_comments=True):

        lines = comment.split('\n')
        from cStringIO import StringIO
        output = StringIO()

        for line in lines:
            
            chars = list(line)
            for char in chars:
                output.write(char)
                pass

        return '' #output

    def format_comment4(self, comment, strip_single_line_comments=True):

        lines = comment.split('\n')
        output = ''

        for line in lines:
            
            chars = list(line)
            for char in chars:
                output += char
                pass

        return output
    
    def format_comment5(self, comment, strip_single_line_comments=True):

        lines = comment.split('\n')
        output = []

        for line in lines:
            
            chars = list(line)
            for char in chars:
                output.append(char)
                pass

        return ''.join(output)


    def format_comment(self, comment, strip_single_line_comments=True):

        #print "COMMENT_BEFORE\n[%s]" % comment

        comment = re.sub("/\*\*\<", "", comment)
        comment = re.sub("/\*", "", comment)
        comment = re.sub("\*/", "", comment)
        comment = re.sub("^\s*\*", "", comment, re.MULTILINE)

        #expr = re.compile("^\s*\*", re.MULTILINE)
        #comment = expr.sub("", comment)
        
        if(strip_single_line_comments):
            #comment = re.sub(" +", " ", comment)
            comment = re.sub("//", "", comment)
        
        #print "COMMENT_1\n[%s]" % comment
        comment = trim_leading_blank_lines(comment)
        #print "COMMENT_2\n[%s]" % comment
        comment = trim_leading_indent(comment)
        #print "COMMENT_3\n[%s]" % comment

        return comment

parser = cpp_parser_t()

#print "[%s]" % parser.format_comment('''
#/** 
# * This is a test of the function parser
# * to ensure that comments are stripped properly
# */
#''')

for i in range(0, 100000):

    parser.format_comment('''
/** 
 * This is a test of the function parser
 * to ensure that comments are stripped properly
 * This is a test of the function parser
 * to ensure that comments are stripped properly
 * This is a test of the function parser
 * This is a test of the function parser
 * This is a test of the function parser
 * to ensure that comments are stripped properly
 * to ensure that comments are stripped properly
 * to ensure that comments are stripped properly
 */
''')

    #print "[%s]" % parser.format_comment2('''
    #/** This is a test of the function parser
    # * to ensure that comments are stripped properly
    # */
    #''')
    #
    #print "[%s]" % parser.format_comment2('''
    #/** This is a test of the function parser
    # * to ensure that comments are stripped properly
    # *  
    # *  @param one [I] - This is the first
    # *                   parameter.
    # *  @param two [I] - This is the second parameter.
    # */
    #''')

