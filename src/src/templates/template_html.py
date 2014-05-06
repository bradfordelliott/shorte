# -*- coding: iso-8859-15 -*-
#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   html_template.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a template class that is used
#|   to generate HTML documents from a Shorte template.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import os
import string
import sys
from string import Template;
import shutil
import time
import datetime
import base64

from src.shorte_defines import *
from template import *
from src.shorte_source_code import *

template_html_tooltips = '''
    <style>
        #dhtmltooltip
        {
         position: absolute;
         width: 450px;
         border: 3px solid #807B60; 
         padding: 5px;
         background-color: #E8DFAC;
         visibility: hidden;
         z-index: 200;
         border-radius: 7px;
         -moz-border-radius: 7px;
        }
    </style>
'''

template_code_header = string.Template(
"""
<div class='code_header' style='width:80%;$style;'>
<span style='text-decoration:none;color:#ccc;' onmouseover="this.style.color='#0000ff';" onmouseout="this.style.color='#ccc';" onclick="e=document.getElementById('snippet_$id');display_code(e.innerHTML);">View Source</span> |
<span style='text-decoration:none;color:#ccc;' onmouseover="this.style.color='#0000ff';" onmouseout="this.style.color='#ccc';" onclick="print_code(document.getElementById('snippet_$id').innerHTML);">Print</span>
</div>
""")

template_source = string.Template(
"""
<div class='source' id="snippet_$id">
$source
</div>
""")

template_code_result = string.Template(
"""
    <br/>
    <div class='code_result'>Result:</div>
    <div class='code'>
        $result
    </div>
""")

template_code = string.Template(
"""
$code_header
<div class='$template'>
$contents
</div>
$source
$result
""")

note_template = string.Template(
"""
<div style='margin-left: 20px; margin-top:10px; margin-bottom:10px; margin-right:30px;border:1px solid #ccc;background:#f8f7cf;border-radius:6px;-moz-border-radius:6px;-webkit-border-radius:6px;'>
  <table>
    <tr valign="top">
        <td>
            <div style='font-weight:bold;color:black;text-decoration:underline;'><img style='height:35px;margin-left:-10px;margin-top:-10px;' src="$image"></img>$title:</div>
            <div style="margin-left:10px;margin-top:5px;">$contents</div>
        </td>
    </tr>
  </table>
</div>
""")

question_template = string.Template(
"""
    <div style='margin-left: 30px; color: red; border-left: 1px solid #C0C0C0;width:100%;'>
    <table>
        <tr>
            <td><img style="height:50px;" src="$image"></td>
            <td>
                <div style='font-weight:bold;color:black;text-decoration:underline;'>Question:</div>
                <div style="margin-left:10px;">$contents</div>
            </td>
        </tr>
    </table>
    </div>
""")


cairo_template = string.Template(
"""<div style='margin-left: 25px; color: #396592;'>Example:</div>
   <div style='font-family: courier new; font-size: 1.0em; margin-left: 30px; background-color: #F0F0F0; border: 1px solid #C0C0C0;'>
   $contents
   </div><br>
   <div style='margin-left: 25px; color: #396592;'>Result:</div>
   <div style='font-family: courier new; font-size: 1.0em; margin-left: 30px;'>
   $result
   </div>
""")

template_javascript = '''
<div id="dhtmltooltip"></div> 

<script type="text/javascript"> 
 
      var offsetxpoint=-60 //Customize x offset of tooltip
      var offsetypoint=20 //Customize y offset of tooltip
      var ie=document.all
      var ns6=document.getElementById && !document.all
      var enabletip=false
      
      if (ie||ns6)
         var tipobj=document.all? document.all["dhtmltooltip"] : document.getElementById? document.getElementById("dhtmltooltip") : ""
 
      function ietruebody()
      {
         return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
      }
 
      function ddrivetip(thetext, thecolor, thewidth)
      {
         if (ns6||ie)
         {
            if (typeof thewidth!="undefined")
            {
               tipobj.style.width=thewidth+"px"
            }
            
            if (typeof thecolor!="undefined" && thecolor!="") tipobj.style.backgroundColor=thecolor
            {
               tipobj.innerHTML=thetext
            }
            
            enabletip=true
            return false
         }
      }
 
      function positiontip(e)
      {
         if (enabletip)
         {
            var curX=(ns6)?e.pageX : event.x+ietruebody().scrollLeft;
            var curY=(ns6)?e.pageY : event.y+ietruebody().scrollTop;
            //Find out how close the mouse is to the corner of the window
            var rightedge=ie&&!window.opera? ietruebody().clientWidth-event.clientX-offsetxpoint : window.innerWidth-e.clientX-offsetxpoint-20
            var bottomedge=ie&&!window.opera? ietruebody().clientHeight-event.clientY-offsetypoint : window.innerHeight-e.clientY-offsetypoint-20
 
            var leftedge=(offsetxpoint<0)? offsetxpoint*(-1) : -1000
 
            //if the horizontal distance isn't enough to accomodate the width of the context menu
            if (rightedge<tipobj.offsetWidth)
            {
               //move the horizontal position of the menu to the left by it's width
               tipobj.style.left=ie? ietruebody().scrollLeft+event.clientX-tipobj.offsetWidth+"px" : window.pageXOffset+e.clientX-tipobj.offsetWidth+"px"
            }
            else if (curX<leftedge)
            {
               tipobj.style.left="5px"
            }
            else
            {
               //position the horizontal position of the menu where the mouse is positioned
               tipobj.style.left=curX+offsetxpoint+"px"
            }
            
            //same concept with the vertical position
            if (bottomedge<tipobj.offsetHeight)
            {
               tipobj.style.top=ie? ietruebody().scrollTop+event.clientY-tipobj.offsetHeight-offsetypoint+"px" : window.pageYOffset+e.clientY-tipobj.offsetHeight-offsetypoint+"px"
            }
            else
            {
               tipobj.style.top=curY+offsetypoint+"px"
            }
            
            tipobj.style.visibility="visible"
         }
      }  
 
      function hideddrivetip()
      {
         if (ns6||ie)
         {
            enabletip=false
            tipobj.style.visibility="hidden"
            tipobj.style.left="-1000px"
            tipobj.style.backgroundColor=''
            tipobj.style.width=''
         }
      }

function print_code(snippet)
{
   w=window.open('','myconsole',
    'width=600,height=450,left=10,top=10'
     +',menubar=1'
     +',toolbar=0'
     +',status=1'
     +',scrollbars=1'
     +',resizable=1')
   w.document.writeln(
    '<html><head><title>Source Code Example. For printing, choose File | Print</title></head>'
   +'<body bgcolor=white onLoad="self.focus()" style="font-family:Courier New;font-size:0.9em;">'
   +'<font color=red><b><i>For printing, <a href=# onclick="window.print();return false;">click here</a> or choose File | Print</i></b></font><br/><br/>'
   + snippet
   )

   w.document.writeln('</body></html>')
   w.document.close()
}

function display_code(snippet)
{
    w=window.open('','myconsole',
     'width=600,height=450,left=10,top=10'
      +',menubar=1'
      +',toolbar=0'
      +',status=1'
      +',scrollbars=1'
      +',resizable=1')
    w.document.writeln(
            '<html><head><title>Source Code Example. For printing, choose File | Print</title><style>span.ln{visibility:hidden;}</style></head>'
    +'<body bgcolor=white onLoad="self.focus()" style="font-family:Courier;font-size:0.9em;">'
    + snippet
    )

    w.document.writeln('</body></html>')
    w.document.close()
}
      
 
   document.onmousemove=positiontip
 
   </script> 
  
<!--
   This seems to screw up printing of images
   <script type="text/javascript">$(function() {
       $.fn.maphilight.defaults = {
       	fill: true,
       	fillColor: '87CEFA',
       	fillOpacity: 0.4,
       	stroke: false,
       	strokeColor: '000000',
       	strokeOpacity: 0.1,
       	strokeWidth: 3,
       	fade: true,
       	alwaysOn: true,
       	neverOn: false,
       	groupBy: false,
       	wrapClass: true,
       	shadow: false,
       	shadowX: 0,
       	shadowY: 0,
       	shadowRadius: 6,
       	shadowColor: '000000',
       	shadowOpacity: 0.8,
       	shadowPosition: 'outside',
       	shadowFrom: false
       };
       $('.map').maphilight();

       
   });</script>
-->

'''
    
def javascriptize(text):

    text = re.sub(" +", " ", text)
    text = text.replace("\n", "<br/>")
    text = text.replace("'", "\\'")
    text = text.replace('"', "\\'")

    return text

class template_html_t(template_t):

    def __init__(self, engine, indexer):
        
        template_t.__init__(self, engine, indexer)

        self.m_contents = []
        self.m_engine = engine
        self.m_indexer = indexer
        self.m_theme = ""
        self.m_template_dir = shorte_get_startup_path() + "/templates/"
        self.m_inline = False
        self.m_include_link = False
        self.m_include_link_type = 'pdf'
        self.m_wikiword_path_prefix = True
        
        self.m_show_code_headers = {}
        self.m_show_code_headers["pseudocode"] = False
        self.m_show_code_headers["code"] = False
        self.m_show_code_headers["example"] = False

        display_headers = self.m_engine.get_config("html", "show_code_header")
        if(display_headers != None):
            segments = display_headers.split(",")
            for segment in segments:
                #print "segment: %s" % segment
                self.m_show_code_headers[segment] = True

        self.m_snippet_id = 1

        self.m_template_code_header = template_code_header

    def is_inline(self):
        return self.m_inline

    def set_template_code_header(self, template):
        self.m_template_code_header = template

    def get_pdf_name(self):
        name = self.m_engine.get_document_name()
        name = name.replace("©", "")
        name = name.replace("®", "")

        return name

    def include_link(self, pdf_path, icon_location=""):

        pdf = ''

        doc_type = self.m_include_link_type

        icon = '%s.png' % doc_type

        if(self.m_include_link):
            img_src = ''
            if(self.is_inline() == True):
                handle = open(shorte_get_startup_path() + "/templates/shared/50x50/%s" % icon, "rb")
                img_src = "data:image/jpeg;base64," + base64.encodestring(handle.read())
                handle.close()
            else:
                if(len(icon_location) == 0):
                    img_src = "css/%s" % icon
                else:
                    img_src = "%s/%s" % (icon_location,icon)

            pdf = '''<span style='float:right;'><a href="%s.%s"><img style='height:50px;padding-top:5px;' src="%s"/></a></span>''' % (pdf_path, doc_type, img_src)

        return pdf

    def get_content_subdir(self):
        return "content"

    def get_content_dir(self):

        return self.m_engine.get_output_dir() + "/content/"

    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    format_python()
    #|
    #| DESCRIPTION:
    #|    This method is called to format a snippet of python within a section
    #|    of a source document. For the moment this is just a basic python
    #|    formatter until I can implement something more sophisticated.
    #| 
    #| PARAMETERS:
    #|    source (I) - The block of python source that is being formatted.
    #| 
    #| RETURNS:
    #|    The block of python source code formatted as HTML.
    #|
    #+-----------------------------------------------------------------------------
    def format_pycairo(self, file, input_source):
        output = ""
        start = 0
        
        # Run the python interpreter to get an answer
        tmp = open("tmpexample.py", "w")
        tmp.write(input_source)
        tmp.close()
        python_result = os.popen("%s tmpexample.py 2>&1" % python).read();
        
        # Convert any HTML tags in the input source
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\n")
        ws = re.compile(" ")
        
        input_source = lt.sub("&lt;", input_source)
        input_source = gt.sub("&gt;", input_source)
        
        python_result = lt.sub("&lt;", python_result)
        python_result = gt.sub("&gt;", python_result)
        python_result = nl.sub("<br>", python_result)
        python_result = ws.sub("&nbsp;", python_result)
        
        # Trim the first leading blank line
        for i in range(len(input_source)):
            if(input_source[i] == '\n'):
                start = i+1
                break;
            elif(input_source[i] != ' '):
                break;
        
        # Trim any trailing blank lines
        i = len(input_source) - 1
        while(i >= 0):
            if(input_source[i] == ' ' or
               input_source[i] == '\n' or
               input_source[i] == '\r'):
                i -= 1
            else:
                break
            
        
        STATE_NORMAL   = 1
        STATE_COMMENT  = 2
        STATE_STRING   = 3
        STATE_MSTRING  = 4
        
        state = STATE_NORMAL
        
        end = i + 1
        i = start
        
        
        line = 1
        
        output += "<span class='ln'>0001&nbsp;&nbsp;</span>"
        
        while i < end:
            
            if(state == STATE_NORMAL):
                if(input_source[i] == '#'):
                    output += "<span class='comment'>#"
                    state = STATE_COMMENT
                elif(input_source[i] == '\n'):
                    output += "<br>"
                    line += 1
                    output += "<span class='ln'>%04d&nbsp;&nbsp;</span>" % (line)
                elif(input_source[i] == ' '):
                    output += "&nbsp;"
                elif(input_source[i] == '(' or
                     input_source[i] == ')' or
                     input_source[i] == '=' or
                     input_source[i] == ',' or
                     input_source[i] == ':'):
                    output += "<span class='operator'>%s</span>" % (input_source[i])
                elif(input_source[i] == '"'):
                    if(input_source[i+1] == '"' and input_source[i+2] == '"'):
                        output += "<span class='mstring'>\"\"\""
                        i += 2
                        state = STATE_MSTRING
                    else:
                        output += "<span class='string'>\""
                        state = STATE_STRING
                else:
                    output += input_source[i]
            
            elif(state == STATE_COMMENT):
                if(input_source[i] == '\n'):
                    output += "</span><br>"
                    line += 1
                    output += "<span class='ln'>%04d&nbsp;&nbsp;</span>" % (line)
                    state = STATE_NORMAL
                elif(input_source[i] == ' '):
                    output += "&nbsp;"
                else:
                    output += input_source[i]
            
            elif(state == STATE_STRING):
                if(input_source[i] == '"'):
                    output += "\"</span>"
                    state = STATE_NORMAL
                elif(input_source[i] == '\n'):
                    output += "<br>"
                    line += 1
                    output += "<span class='ln'>%04d&nbsp;&nbsp;</span>" % (line)
                elif(input_source[i] == ' '):
                    output += "&nbsp;"
                else:
                    output += input_source[i]
            
            elif(state == STATE_MSTRING):
                if(input_source[i] == '"' and input_source[i+1] == '"' and input_source[i+2] == '"'):
                    output += "\"\"\"</span>"
                    state = STATE_NORMAL
                    i+=2
                elif(input_source[i] == '\n'):
                    output += "<br>"
                    line += 1
                    output += "<span class='ln'>%04d&nbsp;&nbsp;</span>" % (line)
                elif(input_source[i] == ' '):
                    output += "&nbsp;"
                else:
                    output += input_source[i]
            
            i += 1
        
        if(state == STATE_COMMENT):
            output += "</span>"
        
        id = self.m_indexer.image()
        
        if(os.path.exists("cairo.png")):
            image_name = "example_%d.png" % id
            shutil.move("cairo.png", image_name)
            python_result += "<img src='%s'/>" % image_name
            g_images.append(image_name)
        else:
            print("Error parsing %s, python example failed to produce output\n\n%s" % (file, input_source))
            #sys.exit(0)
        
        return cairo_template.substitute({"contents" : output,
                                          "result"   : python_result});
    
    
    def format_keywords(self, language, source, exclude_wikiwords=[]):

        keywords = self.m_engine.get_keyword_list(language)

        output = []
        keyword = ''
        pos_start = 0

        #source = re.sub('\n', '', source)

        for i in range(0, len(source)):

            c = source[i]

            # Debug brad - added ord(c) == 46 to get the leeds.write combo
            #if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.' and i < (len(source) - 1) and source[i+1] == ' ')):
            #if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.' and (i < len(source) - 1) and source[i+1] not in (' ', '\n', '\t'))):
            if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.')):
                keyword += c 
            # DEBUG BRAD: This isn't perfect since it doesn't account for the fact
            #             that shorte tags should only be at the beginning of a line
            #             and not in the middle of a line.
            elif(language == "shorte" and c == '@'):
                keyword += c
            else:
                if(keyword != ''):

                    #print "  keyword1: {%s}" % keyword
                    #print "  substr:   {%s}" % source[pos_start:i]
                    if(keywords.has_key(keyword)):
                        #output += source[pos_start:i]
                        output.append("<span class='kw'>")
                        output.append(keyword)
                        output.append("</span>")
                    else:
                        output.append(self.wikify(keyword, exclude_wikiwords))

                    keyword = ''
                
                pos_start = i+1
                output.append("%c" % c)


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                #output += source[pos_start:i]
                output.append("<span class='kw'>")
                output.append(keyword)
                output.append("</span>")
            else:
                output.append(self.wikify(keyword, exclude_wikiwords))
            #print "  keyword2 = %s" % keyword

        #print "output = %s\n" % output

        return ''.join(output)


    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_numbers=True):

        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        allow_line_numbers = int(self.m_engine.get_config("html", "allow_line_numbers"))
        
        line_number_div = ''
        output = ''

        line = 1

        # Inline line numbers
        if(allow_line_numbers == 1):
            output += '<span class="ln">001  </span>'
        # Line numbers in floating div
        elif(allow_line_numbers == 2):
            line_number_div += '001  \n'
        
        for tag in tags:

            type = tag["type"]
            source = tag["data"]
            
            if(type in (TAG_TYPE_COMMENT, TAG_TYPE_MCOMMENT)):
                source = source.replace("->", "#")

            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)
            source = re.sub("\n", "", source)
            #print "SOURCE: %s" % source
        
            # Convert any inline styling blocks
            expr = re.compile("@\{(.*?)\}", re.DOTALL)
            source = expr.sub(self.parse_inline_styling, source)

            #source = source.strip()

            if(type == TAG_TYPE_CODE):
                if(source != ""):
                    source = self.format_keywords(language, source, exclude_wikiwords)
                    #output += '<span>%s</span>' % source
                    output += '%s' % source
            elif(type in (TAG_TYPE_COMMENT, TAG_TYPE_MCOMMENT, TAG_TYPE_XMLCOMMENT)):
                source = self._format_links(source)
                if(self.allow_wikify_comments()):
                    source = self.wikify(source, exclude_wikiwords)
                output += '<span class="cmt">%s</span>' % source

            elif(type == TAG_TYPE_WHITESPACE):
                #output += '&nbsp;'
                output += ' '
            elif(type == TAG_TYPE_STRING):
                output += '<span class="str">%s</span>' % self.wikify(source, exclude_wikiwords)
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'
                line += 1
                #output += "<span class='ln'>%03d&nbsp;&nbsp;</span>" % (line)

                if(allow_line_numbers == 1):
                    output += "<span class='ln'>%03d  </span>" % (line)
                elif(allow_line_numbers == 2):
                    line_number_div += '%03d  \n' % line
            else:
                print "Skipping tag %s" % source
                self.exit(-1)
        
        
        html = ''
        if(allow_line_numbers == 2 and show_line_numbers):
            html = "<div class='snippet' style='white-space:pre-wrap'>"
            html += "<div style='width:4%;float:left;white-space:pre;color:#ccc;'>" + line_number_div + "</div>"
            html += "<div style='width:95%;float:left;white-space:pre-wrap'>" + output + "</div>"
            html += "<div style='clear:both;'></div>"
            html += "</div>"
        else:
            html = "<div class='snippet' style='white-space:pre-wrap'>" + output + "</div>"
        
        return html
    
    
    def format_source_code_no_lines(self, language, tags):

        output = "<div class='snippet'>"
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")

        for tag in tags:

            type = tag["type"]
            source = tag["data"]
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)

            if(type == TAG_TYPE_CODE):
                if(source != ""):
                    #output += '<span>%s</span>' % source
                    output += source
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                #output += '<span class="cmt">%s</span>' % source
                output += source
            elif(type == TAG_TYPE_WHITESPACE):
                output += '&nbsp;'
            elif(type == TAG_TYPE_STRING):
                #output += '<span class="str">%s</span>' % source
                output += source
            elif(type == TAG_TYPE_NEWLINE):
                output += '<br/>'

        output += "</div>"

        return output

    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    format_note()
    #|
    #| DESCRIPTION:
    #|    This method is called to format a note tag
    #|
    #| PARAMETERS:
    #|    content (I) - The content associated with the note tag
    #|
    #| RETURNS:
    #|    The note data formatted as HTML.
    #|
    #+-----------------------------------------------------------------------------
    def format_note(self, tag, label="Note", img_src="note.png"):

        content = self.format_textblock(tag)
        
        img_src = self.insert_image(img_src)

        return note_template.substitute(
            {"contents" : content,
             "image"    : img_src,
             "title"    : label})
    
    def format_checklist(self, tag):
        
        list = tag.contents

        source = ''

        if(tag.modifiers.has_key("title")):
            source += "<p style='font-weight:bold;text-decoration:underline;'>%s</p>" % tag.modifiers["title"] 

        source += "<ul style='list-style-type:none'>"

        for elem in list:
            caption = ''
            if(elem.has_key("caption")):
                caption = " <span style='color:#999;font-style:italic;'>(%s)</span>" % elem["caption"]

            source += "<li><input type='checkbox' name='%s' %s/>%s%s</li>" % (elem["name"], elem["checked"], elem["name"], caption)

        source += "</ul>"

        if(tag.modifiers.has_key("caption")):
            source += "<p style='font-style:italic;margin-left:40px;'>Caption: %s</p>" % tag.modifiers["title"] 

        return source
    
    
    def format_list_child(self, elem, start_tag, end_tag):
        
        source = ''

        if(elem.children != None):
            prefix = ''
            
            # DEBUG BRAD: Need to do this in such a way that it doesn't
            #             re-link the image each time in the inlined version
            if(elem.starred):
                prefix = "<div class='star'></div>"

            elif(elem.priority > 0):
                prefix = "<div class='pri_0%d'></div>" % elem.priority


            if(elem.type in ("checkbox", "action")):
                if(elem.checked):
                    prefix += '<input type="checkbox" checked onclick="return false;"></input>'
                else:
                    prefix += '<input type="checkbox" onclick="return false;"></input>'
            
            source += "<li>%s %s" % (prefix, self.format_text(elem.get_text()))

            num_children = len(elem.children)
            source += start_tag
            #print "num_children = %d" % num_children
            for i in range(0, num_children):
                source += self.format_list_child(elem.children[i], start_tag, end_tag)
            source += "%s</li>" % (end_tag)
        else:
            prefix = ''
            # DEBUG BRAD: Need to do this in such a way that it doesn't
            #             re-link the image each time in the inlined version
            if(elem.starred):
                prefix = "<div class='star'></div>"
            
            elif(elem.priority > 0):
                prefix = "<div class='pri_0%d'></div>" % elem.priority

            if(elem.type in ("checkbox", "action")):
                if(elem.checked):
                    prefix += "<input type='checkbox' checked onclick='return false;'></input>"
                else:
                    prefix += "<input type='checkbox' onclick='return false;'></input>"

            source += "<li>%s " % prefix + self.format_text(elem.get_text()) + "</li>"

        return source
    
    def format_list(self, list, ordered=False, indent=0):

        if(indent != 0):
            style = " style='margin-left:%d;' " % indent*10
        else:
            style = ""

        if(not ordered):
            start_tag = "<ul%s>" % style
            end_tag = "</ul>"
        else:
            start_tag = "<ol%s>" % style
            end_tag = "</ol>"

        source = start_tag

        for elem in list:
            source += self.format_list_child(elem, start_tag, end_tag)

        source += end_tag

        return source

    def htmlize_prototype(self, input_prototype):

        # Make copy of list before modifying it so
        # we don't permanently change it
        prototype = []
        for t in input_prototype:
            prototype.append(t)

        # First tag is the return type so we'll strip it off
        return_type = prototype[0]
        prototype.pop(0)
        prototype.pop(0)

        rt = return_type["data"]
        
        if(return_type["data"] == "const"):
            rt += "&nbsp;" + prototype[0]["data"]
            prototype.pop(0)
            prototype.pop(0)

        prototype = self.format_source_code("c", prototype, [], False)
        return (self.wikify(rt), prototype)
   

    def format_function_summary(self, tag):

        if(tag.modifiers):
            if(tag.modifiers.has_key("src")):
                src_file = tag.modifiers["src"]
                tag.page_title = src_file

        tags = self.m_engine.get_function_summary(tag)

        html = '<table style="border-collapse:collapse;border:0px;margin-left:30px;background-color:#fafafa;">'

        hierarchy = ''
    
        for tag in tags:

            function = tag.contents

            desc = ''
            if(function.has_key("desc2")):
                desc = self.format_textblock(function["desc2"])
            elif(function.has_key("desc")):
                desc = function["desc"]
            
            if(tag.hierarchy != hierarchy):
                hierarchy = tag.hierarchy
                html += '''
<tr valign=top>
    <td colspan=2 style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#eee;padding:2px;font-weight:bold;">%s</td>
</tr>''' % (hierarchy)

            if(function.has_key("prototype")):
                prototype = function["prototype"]["parsed"]
                (returns, prototype) = self.htmlize_prototype(prototype)
            else:
                returns = ''
                prototype = ''

            html += string.Template('''
<tr valign=top>
    <td style="border-top:1px solid #ccc;border-bottom:1px solid #eee;font-family: Courier New;font-size:0.8em;padding:2px;">$return </td>
    <td style='border-top:1px solid #ccc;border-bottom:1px solid #eee;font-family: Courier New;font-size:0.8em;padding:2px;'>$prototype</td>
</tr>
<tr valign=top>
    <td style="border-bottom:1px solid #ccc;padding:2px;">&nbsp;</td>
    <td style='border-top:0px;border-bottom:1px solid #ccc;color:#888;padding:2px;'>$desc</td>
</tr>
''').substitute({"returns": returns, "prototype" : prototype, "desc" : desc, "return" : returns})
        
        html += '</table><br/>'

        return html


    def format_types_summary(self, tag):

        tags = self.m_engine.get_types_summary(tag)

        html = '<table style="border-collapse:collapse;border:0px;margin-left:30px;background-color:#fafafa;">'
    
        for tag in tags:

            struct = tag.contents

            desc = ''
            name = ''

            if(tag.name == "enum"):
                desc = self.format_textblock(struct.description)
                name = struct.name
            else:
                desc = self.format_textblock(struct.description)
                name = struct.name

            html += string.Template('''
<tr valign=top>
    <td style="border-top:1px solid #ccc;border-bottom:1px solid #eee;font-family: Courier New;font-size:0.8em;padding:2px;">$type </td>
    <td style='border-top:1px solid #ccc;border-bottom:1px solid #eee;font-family: Courier New;font-size:0.8em;padding:2px;'>$name</td>
</tr>
<tr valign=top>
    <td style="border-bottom:1px solid #ccc;padding:2px;">&nbsp;</td>
    <td style='border-top:0px;border-bottom:1px solid #ccc;color:#888;padding:2px;'>$desc</td>
</tr>
''').substitute({"type": tag.name, "name" : self.format_text(name), "desc" : desc})
        
        html += '</table><br/>'


        return html

    def format_testcase_summary(self, tag):

        tags = self.m_engine.get_testcase_summary(tag)
            
        show_results = False
        if(self.m_engine.get_config("html", "testcase_summary_show_results") == "1"):
            show_results = True

        html = '''<table class="bordered">
<tr class='header'>
<td style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#ddd;padding:2px;font-weight:bold;">Name</td>
<td style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#ddd;padding:2px;font-weight:bold;">Status</td>
<td style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#ddd;padding:2px;font-weight:bold;">Duration</td>
'''

        if(show_results == True):
            html += '<td style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#ddd;padding:2px;font-weight:bold;">Results</td>'

        html += '</tr>'


        category = ''
    
        for tag in tags:

            testcase = tag.contents
            
            if(tag.category != category):
                category = tag.category
                html += '''
<tr valign=top>
    <td colspan=4 style="border-top:1px solid #ccc;border-bottom:1px solid #ccc;background-color:#eee;padding:2px;font-weight:bold;">Category: %s</td>
</tr>''' % (category)

            status = testcase["status"].upper()
            if(status == "PASSED"):
                status = "<span style='color:green;'>PASSED</span>"
            elif(status == "SKIPPED"):
                status = "<span style='color:yellow;'>SKIPPED</span>"
            else:
                status = "<span style='color:red;'>FAILED</span>"

            html += string.Template('''
<tr valign=top>
    <td style="border-top:1px solid #ccc;border-bottom:1px solid #eee;font-size:0.9em;padding:2px;"><a href="#$name">$name</a> </td>
    <td style='border-top:1px solid #ccc;border-bottom:1px solid #eee;border-left:1px solid:#ccc;border-right:1px solid:#ccc;font-size:0.9em;padding:2px;'>$status</td>
    <td style='border-top:1px solid #ccc;border-bottom:1px solid #eee;font-size:0.9em;padding:2px;'>$duration</td>
''').substitute({"name": testcase["name"], "status" : status, "desc" : self.format_textblock(testcase["desc"]), "duration" : testcase["duration"]})
    
            if(show_results == True):
                html += '''<td style='border-top:1px solid #ccc;border-bottom:1px solid #eee;font-size:0.9em;padding:2px;'><a href="#Status: %s">Status: %s</a></td>''' % (testcase["name"], testcase["name"])
            html += '</tr>';
        
        html += '</table><br/>'

        return html
    
    def format_prototype(self, tag):
        '''This method is called to format a prototype within an HTML
           document.

           @param self [I] - The instance of the formatter class
           @param tag  [I] - The tag containing the prototype

           @return The prototype formatted as HTML
        '''

        template = string.Template("""
        <div class="bordered" style="margin-top:10px;${background}">
        <div style='background-color:#ccc;padding:10px;'>${private}<b>Function:</b> ${name}</div>
        <div>
            <div style="margin-left: 10px;">
                <div style="color: #396592; font-weight: bold;">Description:</div>
                <div style="margin-left:0px;margin-top:5px;margin-bottom:5px;">${desc}</div>
            </div>
        </div>
        <div class='prototype' style="font-size: 0.9em;">
            <div style="margin-left: 10px; margin-top: 10px;">
                ${prototype}
                
                ${params}
                ${returns}
                

                ${example}
                ${called_by}
                ${calls}
                ${pseudocode}
                ${see_also}
                ${deprecated}
                
            </div>
            
        </div>
        </div>
        """)
    
        template_prototype = string.Template("""
        <div>
            <div style="color: #396592; font-weight: bold;">Prototype:</div>
            <div style="margin-left: 15px; margin-right:15px; font-family:courier new;">
                ${prototype}
            </div>
        </div>
        """);

        template_example = string.Template('''
                <div>
                    <div style="color: #396592; font-weight: bold;">Example:</div>
                    <div style="margin-left: 10px; margin-top: 5px;margin-bottom:0px;">
                        The following example demonstrates the use of this method:<br>
                    </div>
                    ${example}
                </div>
            
        ''');
        
        
        template_pseudocode = string.Template('''
                <div>
                    <div style="color: #396592; font-weight: bold;">Pseudocode:</div>
                    <div style="margin-left: 10px; margin-top: 5px;">
                        The following pseudocode describes the implementation of this method:<br>
                    </div>
                    ${pseudocode}
                </div>
            
        ''')
                
        template_returns = string.Template('''
            <div>
                <div style="color: #396592; font-weight: bold;">Returns:</div>
                <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${returns}</p>
            </div>
        ''')
        
        template_see_also = string.Template('''
            <div>
                <div style="color: #396592; font-weight: bold;">See Also:</div>
                <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${see_also}</p>
            </div>
        ''')
        
        template_deprecated = string.Template('''
            <div>
                <div style="color: #396592; font-weight: bold;">Deprecated:</div>
                <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${deprecated}</p>
            </div>
        ''')
        
        template_called_by = string.Template('''
            <div>
                <div style="color: #396592; font-weight: bold;">Called By:</div>
                <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${called_by}</p>
            </div>
        ''')
        
        template_calls = string.Template('''
            <div>
                <div style="color: #396592; font-weight: bold;">Calls:</div>
                <p style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px;">${calls}</p>
            </div>
        ''')
        
        template_params = string.Template('''
        <div>
                    <div style="color: #396592; font-weight: bold;">Params:</div>
                    <div style="margin-left: 0px;">
                        <table style="margin-left: 10px; margin-top: 5px; margin-bottom: 5px; border: 0px solid black;">
                            ${params}
                        </table>
                    </div>
                </div>
                ''')
        
        prototype = tag.contents
        
        file = "blah"
        function = {}
        function["name"] = prototype["name"]
        function["example"] = ''
        function["prototype"] = ''
        function["desc"] = ''
        function["params"] = ''
        function["returns"] = ''
        function["pseudocode"] = ''
        function["see_also"] = ''
        function["deprecated"] = ''
        function["calls"] = ''
        function["called_by"] = ''

        if(prototype.has_key("desc")):
            function["desc"] = self.format_text(prototype["desc"], expand_equals_block=True)
        if(prototype.has_key("desc2")):
            #print "Do I get here?"
            tag = tag_t()
            tag.contents = prototype["desc2"]
            #print "CONTENTS [%s]" % tag["contents"]
            function["desc"] = self.format_textblock(tag)
        
        exclude_wikiwords = []
        exclude_wikiwords.append(function["name"])

        if(prototype.has_key("prototype")):
            language = prototype["prototype"]["language"]
            example = prototype["prototype"]["parsed"]
            
            if(self.m_show_code_headers.has_key("prototype") and self.m_show_code_headers["prototype"]):
                snippet_id = self.m_snippet_id
                self.m_snippet_id += 1
                code_header = self.m_template_code_header.substitute(
                        {"id" : snippet_id,
                         "style" : "margin-left:10px;margin-top:2px;background-color:transparent;"})
                source = template_source.substitute({
                    "id":     snippet_id,
                    "source": self.format_source_code_no_lines(language, example)})

            else:
                code_header = ""
                source = ""

            example = self.format_source_code(language, example, exclude_wikiwords, False)

            code = template_code.substitute(
                    {"contents"    : example,
                     "source"      : source,
                     "code_header" : code_header,
                     "template"    : "code2",
                     "result"      : ""})

            function["prototype"] = code
            function["prototype"] = template_prototype.substitute(function)

        if(prototype.has_key("params") and (len(prototype["params"]) > 0)):
            params = prototype["params"]
            
            param_template = string.Template("""
                        <tr style='border-bottom:1px solid #ccc;'>
                            ${type}
                            <td style="vertical-align:text-top;border: 0px;"><b>${name}</b></td>
                            <td style="vertical-align:text-top;font-family: courier new; border: 0px;">(${io})</td>
                            <td style="vertical-align:text-top;border: 0px;">-</td>
                            <td style="vertical-align:text-top;border: 0px;">${desc}</td>
                        </tr>""")

            output = ''
            for param in params:

                html_tmp = ''
                for val in param["desc"]:
                    if(len(val) == 2):
                        html_tmp += '<b>%s</b> = %s<br/>' % (val[0], self.format_text(val[1]))
                    else:
                        html_tmp += self.format_text(val)

                param["desc"] = html_tmp

                if(param.has_key("desc2")):
                    tag = tag_t()
                    tag.contents = param["desc2"]
                    param["desc"] = self.format_textblock(tag)
                else:
                    print "WTF?"
                    sys.exit(-1)

                if(param.has_key("type")):
                    param["type"] = '''<td style="vertical-align:text-top;border: 0px;">%s</td>''' % param["type"]
                else:
                    param["type"] = ''

                output += param_template.substitute(param)
            
            params = {}
            params["params"] = output
            function["params"] = template_params.substitute(params)

        if(prototype.has_key("returns")):
            function["returns"] = template_returns.substitute(prototype)

        if(prototype.has_key("example")):

            example = prototype["example"]["parsed"]
            language = prototype["example"]["language"]
            
            if(self.m_show_code_headers["example"]):
                snippet_id = self.m_snippet_id
                self.m_snippet_id += 1
                code_header = self.m_template_code_header.substitute(
                        {"id" : snippet_id,
                         "style" : "margin-left:10px;margin-top:2px;background-color:transparent;"})
                source = template_source.substitute({
                    "id":     snippet_id,
                    "source": self.format_source_code_no_lines(language, example)})
            else:
                code_header = ""
                source = ""
            
            example = self.format_source_code(language, example)

            code = template_code.substitute(
                       {"contents" : example,
                        "source"   : source,
                        "code_header" : code_header,
                        "template" : "code2",
                        "result"   : ""})

            function["example"] = code
            function["example"] = template_example.substitute(function)
        
        
        if(prototype.has_key("pseudocode")):

            pseudocode = prototype["pseudocode"]["parsed"]
            language = prototype["pseudocode"]["language"]
            
            if(self.m_show_code_headers["pseudocode"]):
                snippet_id = self.m_snippet_id
                self.m_snippet_id += 1
                code_header = self.m_template_code_header.substitute(
                        {"id" : snippet_id,
                         "style" : "margin-left:10px;margin-top:2px;"})
                source = template_source.substitute({"id": snippet_id, "source": self.format_source_code_no_lines(language, pseudocode)})
            else:
                code_header = ""
                source = ""
            
            pseudocode = self.format_source_code(language, pseudocode)

            code = template_code.substitute(
                       {"contents" : pseudocode,
                        "source"   : source,
                        "code_header" : code_header,
                        "template" : "code2",
                        "result"   : ""})
           
            function["pseudocode"] = code
            function["pseudocode"] = template_pseudocode.substitute(function)

        if(prototype.has_key("see_also")):
            params = {}
            params["see_also"] = self.format_text(prototype["see_also"])
            function["see_also"] = template_see_also.substitute(params)
        
        is_deprecated = False
        if(prototype.has_key("deprecated") and prototype["deprecated"] != False):
            #print "prototype.deprecated = %s" % prototype["deprecated"]
            #print "         .msg        = %s" % prototype["deprecated_msg"]
            params = {}
            params["deprecated"] = self.format_text(prototype["deprecated_msg"])
            function["deprecated"] = template_deprecated.substitute(params)
            is_deprecated = True

        is_private = False
        function["private"] = ""
        if(prototype.has_key("private") and prototype["private"] == True):
            function["private"] = self.insert_image("lock.png", height=20,width=20,wrap=True)

        if(prototype.has_key("called_by")):
            params = {}
            params["called_by"] = self.format_text(prototype["called_by"])
            function["called_by"] = template_called_by.substitute(params)
        
        if(prototype.has_key("calls")):
            params = {}
            params["calls"] = self.format_text(prototype["calls"])
            function["calls"] = template_calls.substitute(params)

        function["background"] = '';
        
        if(is_deprecated):
            function["name"] += " (THIS METHOD IS DEPRECATED)"
            function["background"] = "background: url('css/images/deprecated.png') center;";
            
        topic = topic_t({"name"   : prototype["name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)

        
        return template.substitute(function)
    
    
    def format_testcase(self, tag):
        
        template = string.Template("""
        <div class="bordered" style="margin-top:10px;">
        <div class="question"><b>Test Case: </b> ${name}</div>
        <div>
            <div style="margin-left: 10px;margin-bottom:10px;">
                <div style="color: #396592; font-weight: bold;">Status:&nbsp;&nbsp;&nbsp; ${status}</div>
            </div>
            ${duration}
            <div style="margin-left: 10px;">
                <div style="color: #396592; font-weight: bold;">Description:</div>
                <p style="margin-left:10px;margin-top:5px;margin-bottom:5px;">${desc}</p>
            </div>
        </div>
        </div>
        """)

        testcase = tag.contents

        duration = ""
        if(testcase["duration"] != ""):
            duration = '''
    <div style="margin-left: 10px;margin-bottom:10px;">
        <div style="color: #396592; font-weight: bold;">Duration:&nbsp;&nbsp;&nbsp; <span style='color:black;'>%s</span></div>
    </div>
''' % testcase["duration"]
        vars = {}
        vars["desc"] = self.format_textblock(testcase["desc"])
        vars["name"] = testcase["name"]
        vars["duration"] = duration

        if(testcase["status"].lower() == "passed"):
            vars["status"] = "<span style='color:green;'>PASSED</span>"
        elif(testcase["status"].lower() == "skipped"):
            vars["status"] = "<span style='color:orange;'>SKIPPED</span>"
        else:
            vars["status"] = "<span style='color:red;'>FAILED</span>"

        return template.substitute(vars)

    
    def format_table(self, source, table):
        
        #html = "<div class='tb'><table class='tb'>\n"

        if(table.has_key("width")):
            width = 'width="100%"'
        else:
            width = ''

        html = "<table class='bordered' %s>" % width

        if("title" in table):
            html += "<tr><th colspan='%d'>%s</th></tr>\n" % (table["max_cols"], table["title"])

        i = 0

        max_cols = table["max_cols"]
        widths = []
        if(table.has_key("widths")):
            widths = table["widths"]

        for row in table["rows"]:
            
            is_subheader = row["is_subheader"]
            is_header    = row["is_header"]
            is_reserved  = row["is_reserved"]
            is_crossed   = row["is_crossed"]
            is_title     = False
            if(row.has_key("is_title")):
                is_title = row["is_title"]

            if(is_title):
                html += "<tr><th colspan='%d'>%s</th></tr>\n" % (table["max_cols"], row["cols"][0]["text"])
                i+= 1
                continue
            elif(is_header):
                html += "<tr class='header'>\n";
            elif(row["is_caption"]):
                html += "<tr class='caption'>\n";
            else:
                html += "<tr>\n"

            if(row["is_caption"]):
                html += "<td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td>\n" % (table["max_cols"], self.format_text(row["cols"][0]["text"]))
            elif(row["is_spacer"]):
                html += "<td colspan='%d' class='caption' style='border:0px;text-align:center;'>&nbsp;</td>\n"
            else: 
                cindex = 0
                for col in row["cols"]:

                    # If this is the first row that has all columns
                    if(max_cols == len(row["cols"]) and len(widths) != 0):
                        width='width="%d%%"' % widths[cindex]
                    else:
                        width = ''

                    cindex += 1

                    if(col.has_key("textblock")):
                        tag = tag_t() 
                        tag.contents = col["textblock"]
                        text = self.format_textblock(tag, False)
                    else:
                        text = self.format_text(col["text"])

                    colspan = col["span"]

                    if(colspan > 1):
                        colspan = "colspan='%d'" % colspan
                    else:
                        colspan = ''

                    if(is_header == True):
                        html += "<td %s %s class='header'>%s</td>\n" % (colspan, width, text)
                    elif(is_subheader == True):
                        html += "<td %s %s class='subheader'>%s</td>\n" % (colspan, width, text)
                    elif(is_reserved == True):
                        html += "<td %s %s class='reserved'>%s</td>\n" % (colspan, width, text)
                    elif(is_crossed == True):
                        html += "<td %s %s class='reserved'><strike>%s</strike></td>\n" % (colspan, width, text)
                    else:
                        html += "<td %s %s>%s</td>\n" % (colspan, width, text)
            
            html += "</tr>\n"

            i+=1


        if("caption" in table):
            html += "<tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:left;'><b>Caption:</b> %s</td></tr>\n" % (table["max_cols"], self.format_textblock(table["caption"], False))
        
        html += "</table>"

        #html += "</div>"
        
        return html
    
    def format_sequence(self, tag):

        image = tag.contents
        html = self.format_image(image)
        html += '''
<style>
table.inline
{
    border-collapse:collapse;
    margin-left:30px;
}
table.inline tr.header td.tableheader
{
    border: 1px solid black;
    color: #f0f0f0;
    background-color:#202020;
}
table.inline td
{
    border:1px solid black;
}
table.inline tr.alternaterow
{
    background-color:#f0f0f0;
}
</style>
'''
        html += self.format_table("", tag.contents["html"])

        return html

    def format_input(self, tag):

        input = tag.contents
        label = input["label"]

        if(input["type"] == "submit"):
            html = '''
<input type="submit" name="%s" value="%s"></input>
''' % (input["name"], input["label"])

        elif(input["type"] == "textarea"):
            html = '''
<textarea name="%s">
</textarea>
''' % input["name"]

        else:
            html = '''
<p><span>%s:</span> <input type="%s" name="%s" value="%s"/></p>
''' % (label, input["type"], input["name"], input["label"])

        return html


    def format_textblock(self, tag, standalone=True):
        '''This method is called to format a block of text
within an HTML document.

@param tag        [I] = The tag to parse, usually a dictionary object
@param standalone [I] = Is the block of text standalone or is it embedded
                        within another element like a table?
'''

        if(isinstance(tag, tag_t)):
            paragraphs = tag.contents
        else:
            paragraphs = tag

        html = ''

        if(is_array(paragraphs)):
            for p in paragraphs:
                indent  = p["indent"]
                text    = p["text"]
                is_code = p["code"]
                is_list = p["list"]

                #print "Indent: [%d], text: [%s]" % (indent, text)

                if(is_code):
                    if(standalone):
                        style = "style = 'margin-left:%dpx;background-color:#eee;'" % (20)
                    else:
                        style = "style = 'margin-left:%dpx;background-color:#eee;border:1px solid #ccc;'" % (0)
                else:
                    if(indent > 0):
                        if(standalone):
                            style = "style='margin-left:%dpx;'" % (20 + (indent * 6))
                        else:
                            style = "style='margin-left:%dpx;'" % ((indent * 6))
                    else:
                        style = ''

                if(is_code):
                    html += "<div class='code' %s><div class='snippet' style='white-space:pre'>" % style + self.format_text(text) + "</div></div>\n"
                elif(is_list):
                    html += self.format_list(p["text"], False, indent)
                else:
                    if(standalone):
                        html += "<div class='tblkps' %s>" % style + self.format_text(text, expand_equals_block=True) + "</div>\n"
                    else:
                        html += "<div class='tblkp' %s>" % style + self.format_text(text, expand_equals_block=True) + "</div>\n"
        else:
            if(standalone):
                html += "<div class='tblkps'>" + self.format_text(paragraphs, expand_equals_block=True) + "</div>\n"
            else:
                html += "<div class='tblkp'>" + self.format_text(paragraphs, expand_equals_block=True) + "</div>\n"

        return html

    def format_questions_old(self, tag):

        html = '<table style="width:70%;margin-left:30px;background-color:#ddd;">'

        questions = tag.contents


        for question in questions:

            html += '''
    <tr style='background-color:#c0c0c0;'><td style='font-weight:bold;'>Question:</td></tr>
    <tr><td style='padding-left:20px;'>%s</td></tr>
    <tr style='background-color:#c0c0c0;'><td style='font-weight:bold;'>Answer:</td></tr>
    <tr><td style='padding-left:20px;'>%s</td></tr>
    <tr><td style='border:0px';>&nbsp;</td></tr>
''' % (self.format_text(question["question"]), self.format_text(question["answer"]))

        html += '</table>'

        return html

    def format_questions(self, tag):

        html = ''

        questions = tag.contents

        for question in questions:

            html += '''
    <div class="bordered">
        <div class="question"><b>Q:</b> %s</div>
        <div class="answer"><b>A:</b> %s</div>
    </div>
    <br/>

''' % (self.format_text(question["question"]), self.format_text(question["answer"]))

        return html

    
    def format_acronyms(self, tag):

        source = tag.source
        table = tag.contents

        html = "<table class='bordered'>\n"

        if("title" in table):

            html += "<tr><th colspan='%d'>%s</th></tr>\n" % (table["max_cols"], table["title"])

        i = 0

        for row in table["rows"]:
            
            is_subheader = row["is_subheader"]
            is_header    = row["is_header"]
            is_reserved  = row["is_reserved"]

            if(is_header):
                html += "    <tr class='header'>\n";
            elif(row["is_caption"]):
                html += "    <tr class='caption'>\n";
            else:
                html += "<tr>\n"

            if(row["is_caption"]):
                html += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td>\n" % (table["max_cols"], self.format_text(row["cols"][0]["text"]))
            elif(row["is_spacer"]):
                html += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'>&nbsp;</td>\n"
            else: 

                col_index = 0

                for col in row["cols"]:

                    # Don't attempt to wikify or format the acronym name. Instead
                    # create a link to it
                    if(col_index == 0):
                        if(is_header or is_subheader):
                            text = col["text"]
                        else:
                            text = '<a name="%s"></a>%s' % (col["text"], col["text"])
                    else:
                        text = self.format_text(col["text"])

                    colspan = col["span"]

                    if(is_header == True):
                        html += "      <td colspan='%d' class='header'>%s</td>\n" % (colspan, text)
                    elif(is_subheader == True):
                        html += "      <td colspan='%d' class='subheader'>%s</td>\n" % (colspan, text)
                    elif(is_reserved == True):
                        html += "      <td colspan='%d' class='reserved'>%s</td>\n" % (colspan, text)
                    else:
                        html += "      <td colspan='%d'>%s</td>\n" % (colspan, text)

                    col_index += 1
            
            html += "</tr>\n"

            i+=1

        if("caption" in table):
            html += "      <tr class='caption'><td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td></tr>\n" % (table["max_cols"], table["caption"])

        html += "</table><br/>"
        
        return html
    
    
    def insert_image(self, img_src, height=50, width=50, wrap=False, float="", title=""):

        if(self.is_inline() == True):
            handle = open(shorte_get_startup_path() + "/templates/shared/%dx%d/%s" % (height,width,img_src), "rb")
            img_src = "data:image/jpeg;base64," + base64.encodestring(handle.read())
            img_src = re.sub("\n", "", img_src)

            handle.close()
        else:
            img_src = "css/" + img_src

        if(wrap):
            if(float == "right"):
                return "<img src='%s' title='%s' style='float:right;'></img>" % (img_src,title)
            return "<img src='%s' title='%s'></img>" % (img_src,title)

        return img_src

    def format_enum(self, tag):
        '''This method is called to format an enum for display within an
           HTML document.

           @param self [I] - The template class instance
           @param tag  [I] - The tag defining the enum to convert to HTML.
            
           @return The HTML snippet defining the enum
           '''

        enum = tag.contents

        # The name of the enumeration
        name = enum.name
        
        style = ''
        if(enum.deprecated):
            style = "style=\"background: url('css/images/deprecated.png') center;\"";

        img = ''
        
        if(enum.deprecated):
            img += self.insert_image("icon_error.png", height=20, width=20, wrap=True, float="right", title="This enum is deprecated")

        if(enum.private == True):
            img += self.insert_image("lock.png", height=20, width=20, wrap=True, float="right", title="This enum is private")
        
        
        if(self.m_engine.get_config("shorte", "show_enum_values") == "1"):
            show_enum_vals = True
            max_cols = enum.max_cols
        else:
            show_enum_vals = False
            max_cols = enum.max_cols - 1

        values = '<table class="bordered" style="margin-left:5px">'
        
        values += "<tr><th colspan='%d'>Enum Values</th></tr>\n" % (enum.max_cols)

        i = 0

        if(show_enum_vals):
            values += '''
<tr class='header'>
  <td>Name</td>
  <td>Value</td>
  <td>Description</td>
</tr>'''
        else:
            values += '''
<tr class='header'>
  <td>Name</td>
  <td>Description</td>
</tr>'''
        

        for row in enum.values:
            is_subheader = row["is_subheader"]
            is_header    = row["is_header"]
            is_reserved  = row["is_reserved"]
            
            # If this is the first row and it is a header
            # then skip it as it is likely just the table
            # header.
            #if(i == 0 and is_header):
            #    i+=1
            #    continue

            if(is_header):
                values += "    <tr class='header'>\n";
            elif(row["is_caption"]):
                values += "    <tr class='caption'>\n";
            else:
                values += "<tr valign=top>\n"

            if(row["is_caption"]):
                values += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td>\n" % (max_cols, self.format_text(row["cols"][0]["text"]))
            elif(row["is_spacer"]):
                values += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'>&nbsp;</td>\n"
            else: 

                col_index = 0

                for col in row["cols"]:

                    # Don't attempt to wikify or format the acronym name. Instead
                    # create a link to it
                    if(col_index == 0):
                        if(is_header or is_subheader):
                            text = col["text"]
                        else:
                            text = '<a name="%s"></a>%s' % (col["text"], col["text"])
                    else:
                        if(col.has_key("textblock")):
                            text = self.format_textblock(col["textblock"])
                            #print "ENUM_TB [%s]" % text
                        else:
                            text = self.format_text(col["text"], False)
                            #print "ENUM_T [%s]" % text

                    colspan = col["span"]

                    if((not show_enum_vals) and col_index == 1):
                        col_index += 1
                        continue
                    
                    if(is_header == True):
                        values += "      <td colspan='%d' class='header'>%s</td>\n" % (colspan, text)
                    elif(is_subheader == True):
                        values += "      <td colspan='%d' class='subheader'>%s</td>\n" % (colspan, text)
                    elif(is_reserved == True):
                        values += "      <td colspan='%d' class='reserved'>%s</td>\n" % (colspan, text)
                    else:
                        values += "      <td colspan='%d'>%s</td>\n" % (colspan, text)

                    col_index += 1
            
            values += "</tr>\n"

            i+=1

        values += "</table>"

        html = string.Template('''
<div class='bordered' $style>
<div style='background-color:#ccc;padding:10px;'><b>Enum:</b> ${name}$img</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Description:</div>
        <div style="margin-left:0px;margin-top:5px;margin-bottom:5px;">${desc}</div>
    </div>
</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Values:</div>
        <div style="margin:0px;">${values}</div>
    </div>
</div>
</div><br/>''').substitute({
    "style"  : style,
    "img"    : img,
    "name"   :  name,
    "values" : values,
    "desc"   : self.format_textblock(enum.description)})

        return html


    def format_define(self, tag):

        define = tag.contents

        html = string.Template('''
<div class='bordered'>
<div style='background-color:#ccc;padding:10px;'><b>Define:</b> ${name}</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Value:</div>
        <div style="margin-left:0px;margin-top:5px;margin-bottom:5px;">${value}</div>
    </div>
</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Description:</div>
        <div style="margin-left:0px;margin-top:5px;margin-bottom:5px;">${desc}</div>
    </div>
</div>
</div><br/>''').substitute({
    "name" : define.name,
    "value" : self.format_textblock(define.value),
    "desc" : self.format_textblock(define.description)})

        return html

    def format_object_example(self, obj):

        if(obj.example == None):
            return ''
        
        template_example = string.Template('''
                <div style="margin-left:10px;">
                    <div style="color: #396592; font-weight: bold;">Example:</div>
                    <div style="margin-left: 10px; margin-top: 5px;margin-bottom:0px;">
                        The following example demonstrates the use of this ${type}:<br>
                    </div>
                    ${example}
                </div>
            
        ''');
            
        example  = obj.example["parsed"]
        language = obj.example["language"]
        
        if(self.m_show_code_headers["example"]):
            snippet_id = self.m_snippet_id
            self.m_snippet_id += 1
            code_header = self.m_template_code_header.substitute(
                    {"id" : snippet_id,
                     "style" : "margin-left:10px;margin-top:2px;"})
            source = template_source.substitute({
                "id":     snippet_id,
                "source": self.format_source_code_no_lines(language, example)})
        else:
            code_header = ""
            source = ""
        
        example = self.format_source_code(language, example)

        code = template_code.substitute(
                   {"contents" : example,
                    "source"   : source,
                    "code_header" : code_header,
                    "template" : "code2",
                    "result"   : ""})

        return template_example.substitute({"example" : code, "type" : obj.type})
        
    
    # Called for format a structure for HTML output 
    def format_struct(self, source, struct):
        '''This method is called to format the contents of an @struct tag
           as an HTML entity.

           @param self [I] - The instance of the formatter class
           @param source [I] - The original source of the structure
           @param struct [I] - The object defining the structure.

           @return The HTML output of the structure
        '''
        
        
        html = ""
        
        html += "<table class='bordered'>\n"
        
        if(struct.private == True):
            img = "<img src='css/lock.png'></img>"
        else:
            img = ''
        html += "<tr><th colspan='%d'>%sStructure Fields</th></tr>\n" % (struct.max_cols, img)
       

        # If the structure has an image associated with it then
        # display it as part of the HTML describing the structure.
        if(struct.image != None):

            map_name = struct.name
            name = struct.image["path"]
            
            # If inlining is turned on then we need to embed the image
            # into the generated output HTML file.
            if(self.is_inline() == True):
                handle = open(name, "rb")
                name = "data:image/jpeg;base64," + base64.encodestring(handle.read())
                handle.close()
            else:
                name = os.path.basename(name)

            
            html += "      <td colspan='%d' class='header'>%s</td>\n" % (struct.max_cols, "Diagram")
            html += struct.image["map"]
            html += "<tr><td colspan='%d' style='background-color:white;padding:10px;'><img src='%s' usemap='#diagram_%s' style='border:0px;text-decoration:none'></img></th></td>" % (struct.max_cols, name, struct.name)
        
        html += '''
<tr class='header'>
  <td>Type</td>
  <td>Name</td>
  <td>Description</td>
  </tr>'''

        i = 0

        for field in struct.fields:
            
            is_header = False

            is_reserved = field["is_reserved"]

            if(is_header):
                html += "    <tr class='header'>\n";
            else:
                html += "<tr>\n"

            
            if(field["is_caption"]):
                html += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'><b>Caption: %s</b></td>\n" % (struct["max_cols"], self.format_text(field["attrs"][0]))
            elif(field["is_spacer"]):
                html += "      <td colspan='%d' class='caption' style='border:0px;text-align:center;'>&nbsp;</td>\n"
            else:
                for attr in field["attrs"]:

                    #print attr
                    if(is_dict(attr)):
                        #print "IS DICT"
                        if(attr.has_key("textblock")):
                            attr = self.format_textblock(attr["textblock"])
                        else:
                            attr = attr["text"]
                    else:
                        attr = ''
                    #    print "Do I GET HERE? [%s]" % attr
                    #    attr = self.format_text(attr)

                    if(is_header):
                        html += "      <td colspan='%d' class='header'>%s</td>\n" % (1, attr)
                    elif(is_reserved):
                        html += "      <td colspan='%d' style='background-color:#eee; color:#999;'>%s</td>\n" % (1, attr)
                    else:
                        html += "      <td colspan='%d'>%s</td>\n" % (1, attr)
            
            html += "</tr>\n"

            i+=1
        
       
        html += "</table><br/>"

        html_example = self.format_object_example(struct)
        
        style = ''
        html = string.Template('''
<div class='bordered' $style>
<div style='background-color:#ccc;padding:10px;'><b>Struct:</b> ${name}$img</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Description:</div>
        <div style="margin-left:0px;margin-top:5px;margin-bottom:5px;">${desc}</div>
    </div>
</div>
<div>
    <div style="margin-left: 10px;">
        <div style="color: #396592; font-weight: bold;">Fields:</div>
        <div style="margin:0px;">${values}</div>
    </div>
</div>
${example}
</div><br/>''').substitute({
    "style"  : style,
    "img"    : img,
    "name"   : struct.name,
    "values" : html,
    "example": html_example,
    "desc"   : self.format_textblock(struct.description)})
        
        return html

    def _expand_links(self, matches):

        (source, label, external) = self._process_link(matches)

        return "<a href='%s'>%s</a>" % (source, label)
    
    def _expand_anchors(self, matches):

        (source, label, external) = self._process_link(matches)

        return "<a name='%s'>%s</a>" % (source, label)
    
    def _format_links(self, data):

        # Expand any anchors
        expr = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        data = expr.sub(self._expand_anchors, data)
           
        # Expand any links
        expr = re.compile("\[\[(.*?)\]\]", re.DOTALL)
        data = expr.sub(self._expand_links, data)

        return data

    def parse_style(self, data):
        data = style.strip()
        matches = re.search("style=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    def parse_caption(self, data):
        data = style.strip()
        matches = re.search("caption=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    def parse_href(self, data):
        data = style.strip()
        matches = re.search("href=\"(.*?)\"", data)

        if(matches != None):
            return matches.groups()[0]

        return ""

    def format_image(self, image):

        # Check to see if the image requires conversion such as
        # is the case with inkscape SVG files
        if(image.has_key("converter")):
            image = self.m_engine.convert_image(image)
            print "CONVERTED = [%s]" % image["name"]
        
        name = image["name"] + image["ext"]

        # If inlining is turned on then we need to embed the image
        # into the generated output HTML file.
        if(self.is_inline() == True):
            name = self.m_engine.inline_image(image)
        
        style = "";
        caption = ""
        href_start = ""
        href_end   = ""

        if(image.has_key("width")):
            style += "width:%s;" % image["width"]

        if(image.has_key("height")):
            style += "height:%s;" % image["height"]
        if(image.has_key("caption")):
            caption = image["caption"]

        if(image.has_key("href")):
            href_start = "<a style='text-decoration:none;' href='%s'>" % image["href"]
            href_end = "</a>"


        if(image.has_key("align") and (image["align"] == "center" or image["align"] == "right")):
            if(image["align"] == "center"):
            
                return """
%s
<center>
<table style='text-align:center;'>
    <tr><td><img src="%s" style=\"%s\" width=100 height=100/></td></tr>
    <tr><td><b>%s</b></td></tr>
</table>
</center>
%s
""" % (href_start, name, style, caption, href_end)
            elif(image["align"] == "right"):
                return """
%s
<table style='text-align:center;float:right;'>
    <tr><td><img src='%s' style=\"%s\"/></td></tr>
    <tr><td><b>%s</b></td></tr>
</table>
%s
""" % (href_start, name, style, caption, href_end)
                

        else:
            if(image.has_key("imagemap")):
                image_map = image["imagemap"]

                if(image.has_key("imagemap_name")):
                    image_map_link = " usemap = '#%s' " % image["imagemap_name"]
                else:
                    imagemap = self.m_engine.m_imagemaps[image["imagemap"]]
                    image_map = ""
                    image_map_link = " usemap = '#%s' " % imagemap["id"]

            else:
                image_map = ""
                image_map_link = ""

            return string.Template("""
$map
$href_start
<div class='image_inline'>
    <div style='float:left;'><img class="map" src='${name}' style=\"${style}\" $map_link/></div>
    <div style='float:left;'><b>${caption}</b></div>
    <div style='clear:both;'></div>
</div>
$href_end
""").substitute({"href_start" : href_start,
                 "name"       : name,
                 "style"      : style,
                 "caption"    : caption,
                 "href_end"   : href_end,
                 "map"        : image_map,
                 "map_link"   : image_map_link})

    
    def format_imagemap(self, imagemap):
        
        imagemap = imagemap.contents
        id = imagemap["id"]

        html = '''<map name="%s">
''' % id

        i = 0

        for row in imagemap["rows"]:

            if(i == 0):
                i += 1
                continue

            i += 1

            cols = row["cols"]

            shape = cols[0]["text"]
            coords = cols[1]["text"]
            label = cols[2]["text"]
            desc  = cols[3]["text"]

            html += '''<area shape="%s" coords="%s" href="#"
   onMouseover="ddrivetip('<b>%s</b><br/>%s')"
   onMouseOut="hideddrivetip()"
   
   >
''' % (shape, coords, javascriptize(label), javascriptize(desc))

        html += "</map>"
        
        return html


    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)
        image["inline"] = True

        return self.format_image(image)
    
    def format_embedded_object(self, tag):

        obj = tag.contents

        name = obj["name"] + obj["ext"]

        style = "margin-left:30px;"
        caption = ""
        href_start = ""
        href_end   = ""
        width  = 640
        height = 480

        if(obj.has_key("width")):
            width = "width:%s;" % obj["width"]
        if(obj.has_key("height")):
            height = "height:%s;" % obj["height"]
        if(obj.has_key("caption")):
            caption = obj["caption"]

        if(obj.has_key("href")):
            href_start = "<a style='text-decoration:none;' href='%s'>" % obj["href"]
            href_end = "</a>"

        return string.Template('''
      ${href_start}
      <object
        classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
        codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,42,0"
        id="${src}"
        width="${width}" height="${height}"
      >
        <param name="movie" value="${src}">
        <param name="bgcolor" value="#FFFFFF">
        <param name="quality" value="high">
        <param name="seamlesstabbing" value="false">
        <param name="allowscriptaccess" value="samedomain">
        <embed
          type="application/x-shockwave-flash"
          pluginspage="http://www.adobe.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"
          name="${src}"
          width="${width}" height="${height}"
          src="${src}"
          bgcolor="#FFFFFF"
          quality="high"
          seamlesstabbing="false"
          allowscriptaccess="samedomain"
        >
          <noembed>
          </noembed>
        </embed>
      </object>
      ${href_end}
''').substitute({"href_start" : href_start,
                 "href_end"   : href_end,
                 "src"        : name,
                 "width"      : width,
                 "height"     : height})
                

#        if(obj.has_key("align") and (obj["align"] == "center" or obj["align"] == "right")):
#            if(image["align"] == "center"):
#                return """
#%s
#<center>
#<table style='text-align:center;'>
#    <tr><td><img src="%s" style=\"%s\" width=100 height=100/></td></tr>
#    <tr><td><b>%s</b></td></tr>
#</table>
#</center>
#%s
#""" % (href_start, name, style, caption, href_end)
#            elif(image["align"] == "right"):
#                return """
#%s
#<table style='text-align:center;float:right;'>
#    <tr><td><img src='%s' style=\"%s\"/></td></tr>
#    <tr><td><b>%s</b></td></tr>
#</table>
#%s
#""" % (href_start, name, style, caption, href_end)
#                
#
#        else:
#            return """
#%s
#<span style='display:inline;'>
#<table style='display:inline;text-align:center;'>
#    <tr><td><img src='%s' style=\"%s\"/></td></tr>
#    <tr><td><b>%s</b></td></tr>
#</table>
#</span>
#%s
#""" % (href_start, name, style, caption, href_end)
    
    def format_wikiword(self, wikiword, link_word):
        '''This method is called to format a wikiword. It is called by
           the wikify method in the template base class'''

        # If the document is being inlined then need to get
        # rid of the link prefix and just use a local link
        if(self.is_inline()):
            output = "<a href='#%s'>%s</a>" % (wikiword.wikiword, wikiword.label)
        else:
            if(self.m_wikiword_path_prefix):
                output = "<a href='%s#%s'>%s</a>" % (self.get_output_path(wikiword.link), wikiword.label, wikiword.label)
            else:
                output = "<a href='%s'>%s</a>" % (wikiword.label, wikiword.label)

        return output


    def parse_inline_styling(self, matches):

        data = matches.groups()[0].strip()
        #print "DATA: [%s]" % data
        #print "data: %s" % data
        parts = data.split(",")
        if(len(parts) == 1):
            tag = parts[0]
            replace = tag
        elif(len(parts) > 1):
            tag = parts[0]
            replace = ''.join(parts[1:])

        replace = trim_leading_blank_lines(replace)
        #print "TAG: %s, REPLACE: %s" % (tag,replace)
        
        if(-1 != tag.find("+")):
            tags = tag.split("+")
        else:
            tags = [tag]

        prefix = ''
        postfix = ''

        for tag in tags:
            # Check if it's an inline styling block such as color
            #   @{color:00ff00,my text here}
            if(-1 != tag.find(":")):
                parts = tag.split(":")
                tag = parts[0].strip()
                parts.pop(0)
                qualifier = ":".join(parts)

            if(tag in ("b", "bold")):
                prefix += "<b>"
                postfix += "</b>"
            elif(tag == "pre"):
                prefix += "<pre style='margin-left:10px;'>"
                postfix += "</pre>"
            elif(tag == "u"):
                prefix += "<u>"
                postfix += "</u>"
            elif(tag == "i"):
                prefix += "<i>"
                postfix += "</i>"
            elif(tag == "br"):
                postfix += "<br/>"
            elif(tag == "color"):
                prefix += "<span style='color:#%s'>" % (qualifier)
                postfix += "</span>"
            elif(tag == "span"):
                prefix += "<span style='%s'>" % (qualifier)
                postfix += "</span>"
            elif(tag in ("cross","strike")):
                prefix += "<strike>"
                postfix += "</strike>"
            elif(tag in ("hl", "hilite", "highlight")):
                prefix += "<span style='background-color:yellow;'>"
                postfix += "</span>"
            elif(tag in ("done", "complete")):
                prefix += "<span style='color:green;'>"
                postfix += "</span>"
            elif(tag in ("star", "starred")):
                prefix += "<div class='star'>&nbsp;</div>"
                postfix += ""
            elif(tag in "table"):
                #print "PARSING INLINE TABLE"
                #print "===================="
                #print replace
                #print "===================="
                table = self.m_engine.m_parser.parse_table(replace, {}, col_separators=['|','!'])
                return self.format_table(replace, table)

            # Embed an inline note. This is useful when documenting
            # source code.
            elif(tag in ("note", "warning", "tbd", "question")):
                # We've already converted breaks so we need to unconvert them
                # to format the note properly.
                replace = replace.replace("<br/>", "\n")
                textblock = self.m_engine.m_parser.parse_textblock(replace)

                if(tag == "note"):
                    label = "Note"
                    img = "note.png"
                elif(tag == "warning"):
                    label = "Warning"
                    img = "warning.png"
                elif(tag == "tbd"):
                    label = "TBD"
                    img = "tbd.png"
                elif(tag == "question"):
                    label = "Question"
                    img = "question.png"

                return self.format_note(textblock, label, img)


        return prefix + replace + postfix


    def format_text(self, data, allow_wikify=True, exclude_wikify=[], expand_equals_block=False):

        if(data == None):
            return

        # Convert an < and > characters
        data = data.replace("<", "&lt;")   # re.sub("<", "&lt;", data)
        data = data.replace(">", "&gt;")   # re.sub(">", "&gt;", data)
        data = data.replace("-&gt;", "->") # re.sub("-&gt;", "->", data)
        data = trim_blank_lines(data)

        #print "DATA: [%s]" % data

        # Strip trailing lines

        data = re.sub("\n\s*\n", "<br/><br/>", data)

        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "<br/>", data)

        if(expand_equals_block):
            data = re.sub("==+", "<div style='style=float:left; width:20%;border-top:1px solid #ccc;height:1px;'></div>", data)
        
        ## Hilite any text between **** ****
        #hiliter = re.compile("\*\*\*\*(.*?)\*\*\*\*", re.DOTALL)
        #data = hiliter.sub("<font class='hilite'>\\1</font>", data)

        # Underline any text between __ __
        hiliter = re.compile("__(.*?)__", re.DOTALL)
        data = hiliter.sub("<u>\\1</u>", data)

        # DEBUG BRAD: Oldy Syntax
        #     Underline anything in <<<>>> brackets
        #     hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        #     data = hiliter.sub("<u>\\1</u>", data)
        
        # First make any links or references
        data = self._format_links(data)

        # Then insert any images. Make sure to add
        # them to the list of images that need to be
        # copied over.
        data = re.sub("&lt;&lt;(.*?),(.*?)(,(.*?))?&gt;&gt;", self.format_inline_image, data)
        data = re.sub("&lt;&lt;(.*?)&gt;&gt;", self.format_inline_image, data)

        # DEBUG BRAD: Old syntax
        #    # Now convert any ** to italics
        #    italics = re.compile("\*\*(.*?)\*\*", re.DOTALL)
        #    data = italics.sub("<i>\\1</i>", data)
        #    
        #    # Now convert any *phrase* to bold
        #    bold = re.compile("\*(.*?)\*", re.DOTALL)
        #    data = bold.sub("<b>\\1</b>", data)

        # New syntax
        #italics = re.compile("\/\/(.*?)\/\/", re.DOTALL)
        #data = italics.sub("<i>\\1</i>", data)
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*", re.DOTALL)
        data = bold.sub("<b>\\1</b>", data)

        # Convert any inline styling blocks
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)
        
        if(allow_wikify):
            data = self.wikify(data)

        return data
    
    def format_text_links(self, data):
        
        # Replace any \n's with a <br>
        data = re.sub("\\\\n", "<br>", data)

        # First make any links
        data = self._format_links(data)
        data = self.wikify(data)

        return data


    def append_header(self, tag, data, file):

        data = self.format_text(data, False)

        if(self.m_engine.get_config("html", "header_numbers") == "1"):
            if(tag == "h1"):
                self.m_contents.append("<h1>" + self.m_indexer.level1(tag, data.strip(), file) + ". " + data.strip() + "<a name='" + data.strip() + "'></a></h1>\n")

            elif(tag == "h2"):
                self.m_contents.append("<h2>" + self.m_indexer.level2(tag, data.strip(), file) + ". " + data.strip() + "<a name='" + data.strip() + "'></a></h2>\n")

            elif(tag == "h3"):
                self.m_contents.append("<h3>" + self.m_indexer.level3(tag, data.strip(), file) + ". " + data.strip() + "<a name='" + data.strip() + "'></a></h3>\n")

            elif(tag == "h4"):
                self.m_contents.append("<h4>" + self.m_indexer.level4(tag, data.strip(), file) + ". " + data.strip() + "<a name='" + data.strip() + "'></a></h4>\n")
            
            elif(tag == "h5"):
                self.m_contents.append("<h5>" + self.m_indexer.level5(tag, data.strip(), file) + ". " + data.strip() + "<a name='" + data.strip() + "'></a></h5>\n")

            elif(tag == "h"):
                self.m_contents.append("<h6>" + data.strip() + "</h6>\n")
        else:
            if(tag == "h1"):
                self.m_contents.append("<h1>" + data.strip() + "<a name='" + data.strip() + "'></a></h1>\n")

            elif(tag == "h2"):
                self.m_contents.append("<h2>" + data.strip() + "<a name='" + data.strip() + "'></a></h2>\n")

            elif(tag == "h3"):
                self.m_contents.append("<h3>" + data.strip() + "<a name='" + data.strip() + "'></a></h3>\n")

            elif(tag == "h4"):
                self.m_contents.append("<h4>" + data.strip() + "<a name='" + data.strip() + "'></a></h4>\n")
            
            elif(tag == "h5"):
                self.m_contents.append("<h5>" + data.strip() + "<a name='" + data.strip() + "'></a></h5>\n")
            
            elif(tag == "h"):
                self.m_contents.append("<h6>" + data.strip() + "</h6>\n")
    
     
    def append_source_code(self, tag):

        rc = self.format_source_code(tag.name, tag.contents)

        source = self.format_source_code_no_lines(tag.name, tag.contents)

        result = tag.result

        snippet_id = self.m_snippet_id
        self.m_snippet_id += 1

        if(result != None):
            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            nl = re.compile("\n")
            ws = re.compile(" ")

            result = lt.sub("&lt;", result)
            result = gt.sub("&gt;", result)
            result = nl.sub("<br>", result)
            result = ws.sub("&nbsp;", result)
            
            result = template_code_result.substitute({"result": result})
        else:
            result = ""

        if(self.m_show_code_headers["code"]):
            snippet_id = self.m_snippet_id
            self.m_snippet_id += 1
            code_header = self.m_template_code_header.substitute(
                    {"id" : snippet_id,
                     "style" : "margin-left:30px;margin-top:10px;width:100%;"})
            source = template_source.substitute({"id": snippet_id, "source": source})
        else:
            code_header = ""
            source = ""

        self.m_contents.append(template_code.substitute(
                {"contents"    : rc,
                 "source"      : source,
                 "code_header" : code_header,
                 "template"    : "code",
                 "result"      : result}))

    
    def append(self, tag):
        
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_contents.append("<p>" + self.format_text(tag.contents) + "</p>\n")
        elif(name == "text"):
            self.m_contents.append(self.format_textblock(tag))
        elif(name == "pre"):
            self.m_contents.append("<pre style='margin-left:10px;'>" + self.format_text(tag.contents) + "</pre>\n")
        elif(name == "note"):
            self.m_contents.append(self.format_note(tag, "Note", "note.png"))
        elif(name == "tbd"):
            self.m_contents.append(self.format_note(tag, "TBD", "tbd.png"))
        elif(name == "question"):
            self.m_contents.append(self.format_note(tag, "Question", "question.png"))
        elif(name == "warning"):
            self.m_contents.append(self.format_note(tag, "Warning", "warning.png"))
        elif(name == "table"):
            self.m_contents.append(self.format_table(tag.source, tag.contents))
        elif(name == "struct"):
            self.m_contents.append(self.format_struct(tag.source, tag.contents))
        elif(name == "define"):
            self.m_contents.append(self.format_define(tag))
        elif(name == "ul"):
            self.m_contents.append(self.format_list(tag.contents, False))
        elif(name == "ol"):
            self.m_contents.append(self.format_list(tag.contents, True))
        elif(name == "checklist"):
            self.m_contents.append(self.format_checklist(tag))
        elif(name == "image"):
            self.m_contents.append(self.format_image(tag.contents))
        elif(name == "imagemap"):
            self.m_contents.append(self.format_imagemap(tag))
        elif(name == "prototype"):
            self.m_contents.append(self.format_prototype(tag))
        elif(name == "testcase"):
            self.m_contents.append(self.format_testcase(tag))
        elif(name == "testcasesummary"):
            self.m_contents.append(self.format_testcase_summary(tag))
        elif(name == "enum"):
            self.m_contents.append(self.format_enum(tag))
        elif(name == "acronyms"):
            self.m_contents.append(self.format_acronyms(tag))
        elif(name == "questions"):
            self.m_contents.append(self.format_questions(tag))
        elif(name == "functionsummary"):
            #print "Processing function summary"
            self.m_contents.append(self.format_function_summary(tag))
        elif(name == "typesummary"):
            #print "Processing typesummary"
            self.m_contents.append(self.format_types_summary(tag))
        elif(name == "embed"):
            self.m_contents.append(self.format_embedded_object(tag))
        elif(name == "sequence"):
            self.m_contents.append(self.format_sequence(tag))
        elif(name == "columns"):
            self.m_contents.append("<div style='float:left;'>")
            pass
        elif(name == "endcolumns"):
            self.m_contents.append("</div><div style='clear:both;'></div>")
        elif(name == "column"):
            self.m_contents.append("</div><div style='float:left;'>")
            pass
        elif(name == "input"):
            self.m_contents.append(self.format_input(tag))
        else:
            print "Undefined tag: %s [%s]" % (name, tag.source); sys.exit(-1)
        

        #elif(tag == "pycairo"):
        #    self.m_contents += self.format_pycairo(file, data)
        #elif(tag == "pre"):
        #    self.m_contents += "<pre style='margin-left:40px;'>%s</pre>" % data
        #else:
        #    print "Undefined tag: %s [%s]" % (tag, data); sys.exit(-1);


    def get_contents(self):
        
        return ''.join(self.m_contents)
        
    def get_css(self, basepath=""):
        
        css = '''<link rel="stylesheet" type="text/css" media="all" href="%scss/%s.css" title="Default" />''' % (basepath, self.m_theme)

        theme = self.m_engine.get_theme()

        # Inline the CSS if necessary
        if(self.is_inline() == True):
            
            handle = open("%s/%s/%s.css" % (self.m_template_dir, theme, theme), "rt")
            css = handle.read()
            handle.close()

            css = '''
<style>
%s
</style>
''' % self._fix_css(css)

        return css

    def _load_template(self, template_name):
        
        if(self.is_inline() == True):
            handle = open(shorte_get_startup_path() + "/templates/html_inline/%s/%s" % (self.m_engine.get_theme(), template_name), "r")
        else:
            handle = open(shorte_get_startup_path() + "/templates/html/%s/%s" % (self.m_engine.get_theme(), template_name), "r")

        contents = handle.read()
        handle.close()

        return contents

    def format_page(self, page, output_file, source_file):
       
        title = page["title"]

        right_menu = ""
        for topic in index:
           indent = topic.m_vars["indent"]
           if(topic.m_vars["file"] == output_file):
              right_menu += "<div class='toc%d'><a href='#%s'>%s</a></div>" % (indent, topic.m_vars["name"], topic.m_vars["name"])

        vars = {}

        self.m_theme = self.m_engine.get_theme()

        vars["title"]    = page["title"]
        vars["subtitle"] = ""
        if(page.has_key("subtitle")):
            vars["subtitle"] = page["subtitle"]
        vars["contents"] = self.get_contents()

        # Reset the page contents cache if we're inlining the document
        # contents since we want to be able to grab it when we generate
        # the index page.
        if(self.is_inline() != True):
            self.m_contents = []

        vars["rightmenu"] = "" #right_menu
        vars["src"] = "<a href='%s'>%s</a>" % (os.path.basename(source_file), os.path.basename(source_file))
        vars["version"] = self.m_engine.get_doc_info().version();
        vars["theme"] = self.m_engine.get_theme();
        vars["date"] = self.m_engine.get_date()
        vars["css"] = self.get_css()
        vars["pdf"] = self.include_link("../" + self.get_pdf_name(), "css/")
        vars["link_index"] = "../index.html"
        vars["link_index_framed"] = "../index_framed.html"
        vars["link_legal"] = "legal.html"
        vars["link_revisions"] = "revisions.html"
        vars["html_tooltips"] = template_html_tooltips


        if(self.m_engine.get_config("html", "include_javascript") == "1"):
            vars["javascript"] = template_javascript
        else:
            vars["javascript"] = ""

        vars["links"] = ""

        for link in page["links"]:
            vars["links"] += "<li><a href='%s'><div>%s</div></a></li>" % (link["href"], link["name"])

        self.m_engine._mkdir(os.path.dirname(output_file))

        html = string.Template(self._load_template("index.html"))

        return html.substitute(vars)


    def get_index_name(self):

        return "index.html"

    def generate_toc_frame(self, title):

        cnts = ''

        for topic in self.m_indexer.m_topics:

            name = topic.m_vars["name"]
            indent = topic.m_vars["indent"]
            file = "content/" + os.path.basename(topic.m_vars["file"])

            # If the HTML is being inlined then we need to
            # make sure that all links point back to the
            # main document.
            if(self.is_inline() == True):
                file = "index.html"
            
            #print "indent = %s" % indent

            if(indent == 1):
                cnts += "<div class='toc1'><a href='%s#%s' target='main_page'>%s</a></div>" % (file, name, name)
            elif(indent == 2):
                cnts += "<div class='toc2'><a href='%s#%s' target='main_page'>%s</a></div>" % (file, name, name)
            elif(indent == 3):
                cnts += "<div class='toc3'><a href='%s#%s' target='main_page'>%s</a></div>" % (file, name, name)
            elif(indent == 4):
                cnts += "<div class='toc4'><a href='%s#%s' target='main_page'>%s</a></div>" % (file, name, name)
            elif(indent == 5):
                cnts += "<div class='toc5'><a href='%s#%s' target='main_page'>%s</a></div>" % (file, name, name)

        toc = string.Template('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<style>
* html {width: 500px;}
body {width: 500px;}
/* Table of Contents */
div.toc1 {margin-top:8px;margin-bottom:4px;}
div.toc1 a{margin-left:20px;font-size:1.1em;color:#666;}
div.toc2 {margin-top:4px;margin-bottom:2px;}
div.toc2 a{margin-left:40px;font-size:1.0em;color:#005CDB;}
div.toc3 {margin-top:4px;margin-bottom:2px;}
div.toc3 a{margin-left:50px;font-size:0.9em;color:#000;}
div.toc4 a{margin-left:70px;font-size:0.9em;color:#777;}
div.toc5 a{margin-left:90px;font-size:0.9em;color:#666;}
</style>
</head>
<body style="background-color: white;white-space:nowrap;font-weight:bold;">
$cnts
</body>
</html>
''').substitute({"css": self.get_css("content/"), "cnts" : cnts})

        file = open(self.m_engine.m_output_directory + "/toc.html", "w")
        file.write(self._cleanup_html(toc))
        file.close()



        html = '''
<HTML>
<HEAD>
<TITLE>%s</TITLE>
</HEAD>

<FRAMESET ROWS="1" COLS="20%%, *">
     <FRAME SRC="toc.html" NAME=TOC>
     <FRAME SRC="index.html" NAME=main_page>
</FRAMESET>

</HTML>
''' % title
        file = open(self.m_engine.m_output_directory + "/index_framed.html", "w")
        file.write(self._cleanup_html(html))
        file.close()
    
    def generate_revision_file(self):

        return True

    def generate_index(self, title, subtitle, theme, version, links, as_string=False):
        
        cnts = "<h1>Table of Contents</h1>"
        
        for topic in self.m_indexer.m_topics:

            name = topic.m_vars["name"]
            indent = topic.m_vars["indent"]
            file = os.path.basename(topic.m_vars["file"])

            # If the HTML is being inlined then we need to
            # make sure that all links point back to the
            # main document.
            if(self.is_inline() == True):
                file = "index.html"
            else:
                file = "content/" + file
            
            #print "indent = %s" % indent

            if(indent == 1):
                cnts += "<div class='toc1'><a href='%s#%s'>%s</a></div>\n" % (file, name, name)
            elif(indent == 2):
                cnts += "<div class='toc2'><a href='%s#%s'>%s</a></div>\n" % (file, name, name)
            elif(indent == 3):
                cnts += "<div class='toc3'><a href='%s#%s'>%s</a></div>\n" % (file, name, name)
            elif(indent == 4):
                cnts += "<div class='toc4'><a href='%s#%s'>%s</a></div>\n" % (file, name, name)
            elif(indent == 5):
                cnts += "<div class='toc5'><a href='%s#%s'>%s</a></div>\n" % (file, name, name)

        # If we're inlining everything we need to store the
        # entire document in the index file
        if(self.is_inline() == True):
            if(self.m_engine.get_config("html", "inline_toc") == "1"):
                cnts += "<br/><br/>" + self.get_contents()
            else:
                cnts = self.get_contents()
        
        html = string.Template(self._load_template("index.html"))

        txt_links = ''
        for link in links:
            txt_links += "<li><a href='%s'><div>%s</div></a></li>" % (link["href"], link["name"])

        if(self.m_engine.get_config("html", "include_javascript") == "1"):
            javascript = template_javascript
        else:
            javascript = ""

        contents = html.substitute(
            {"title" : title,
             "subtitle" : subtitle,
             "contents" : cnts,
             "rightmenu" : "",
             "src" : "",
             "date" : self.m_engine.get_date(),
             "version" : version,
             "css" : self.get_css("content/"),
             "pdf" : self.include_link(self.get_pdf_name(), "content/css"),
             "javascript" : javascript,
             "links" : txt_links,
             "link_index" : "index.html",
             "link_index_framed" : "index_framed.html",
             "link_legal" : "content/legal.html",
             "link_revisions" : "content/revisions.html",
             "html_tooltips" : template_html_tooltips
             })
        
        if(as_string):
            return contents

        file = open(self.m_engine.m_output_directory + "/index.html", "w")
        file.write(self._cleanup_html(contents))
        file.close()

        return True

    def set_template_dir(self, template_dir):
        #print "set_template_dir, template_dir=%s" % template_dir
        self.m_template_dir = shorte_get_startup_path() + "/templates/%s/" % template_dir
    

    def _fix_css(self, contents):

        css = string.Template(contents)
      
        image_priority = []

        for i in range(1,6):

            if(self.is_inline()):
                if(i == 1):
                    image = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAB3RJTUUH3gEdAw8oy5h7YQAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAABUSURBVHjaY2CgBQh67njR5p3+/5gnnrsoNYsFRFzhvfvtFvcjhg8sXz5SaiATtX07auCogaMGjhpIHwPB5aHfS7t335l/3BD9JfjrCsNdattBGQAAYroXWdCS3CwAAAAASUVORK5CYII=);"
                elif(i == 2):
                    image = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAB3RJTUUH3gEdAxAgCBn9zQAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAC2SURBVHjaY2CgBTj10efh8d9Wf2dstCqh1CwmEPGT/RnPd5ZjTL9Z37JSxUAGBkYgpA5gwRQSZjDiE2T5x/KP4cK7e3/IdCEE/P7992f3QuWE7ocSD/sva56g3IX/mf6xCL4TYhK4I8XKbcBNjoFM6AL//zH9g9DMf6liIKVg1MBRAweVgf+hJLDcARc8jGTaBc7LbD9FvzOzmDKw/mX4/+UZ24M/t5UO//3B9ZqB4TS1PUA6AADsozfbvru2LAAAAABJRU5ErkJggg==);"
                elif(i == 3):
                    image = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAB3RJTUUH3gEdAxARWcf99wAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAENSURBVHjaY2CgBfhz1ufB/4uWPx9sdVxPqVlMYIL5BQ8Dy3E2RqanHAwMLJQbyPAfxmVE5lBgIAoAGcoNxRAe2Qb++//vb7C9guC9Ldab7m2x3ZDgrSlGqnvRAozxv6jQb25FpeO+DAw8DEJ8/AWkehkjBv79AwbiX2DcMLD+/f+f9ADFG6U/fv3/vXWibbGcJLP+nz/Crw2j1hZTZOCfP0x/9TTu+cvIP7Vl+OX1FihE0EAmQgr+/GX8yfAXGBR/GH4Q42WCBpIKRg0ctAbCS4D/UNY/KEYGxGUacML+/1f0OyOTyb//fzl+MjC8ZGD4q/GdgYEZmPre/f//T+YXw18JYLnB/53aviEKAAAbdFjo7hw6xgAAAABJRU5ErkJggg==);"
                elif(i == 4):
                    image = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAB3RJTUUH3gEdAxAzjKe8EwAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAF+SURBVHjaY2CgMmAEEX86fR8w/3oj8foX52mxvlO2DF+/kG0gC4hg+vGch+H7GXamvypcDEyMFLmQCerQ/0gOpoaBSABsNCcQ84AtYKbEwP8M//9bywqyXS+1XfywwnL31DArh7/khCGymTysDCwqrFf9WJie8klxGi+m2MsgH/9lYPnJ8J+V4d9/BgwHEgplFnySv//++9XiZWAVqCGY+5WB+3He1huVJ27ewRsKTPgk//5n/KPG81pbi2t/hBHv+zgBHm6CcYTXQJD3/v5j/MPwD5j4/zP8+POXcBSxEFQBC9v///6LC4uy7MkNzGX791H4L4/cE8fOBdPINhBo4n8+Hl4WR7Fv5Uzf9okySGdcAYpiGMhEtIEQM4ER9f87OAj+/vtBchiSA4aMgf8hGQBa5gADi4EBZyaBK8JqIDiW/3OIfmNkNOH/94vrJwPDI4b/nLLfGZilGP6zMP9j+C/4l4FLEhgPwt/BpQeHwA8GRv3f/1m5f1Hbd1gBABu7hGqxxa64AAAAAElFTkSuQmCC);"
                else:
                    image = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAB3RJTUUH3gEdAxELvb41zAAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAHGSURBVHjatZTNaxNBGMbfndmPEBPDNklRsZroRdRGmgZCvGgUKQRDPAuC/4Pee7H0JtJL8xd4stdCwaLiKaQppSqe8uFJPQQie9hNZndeMxEk2a2G3aXvYZgPeOb5Pcw7AKdRdqXaxWLJ/HX33vFqelEJoyWLgfz8EYNWM0Iy2TPgOKHMkZmVJIWmJe4NFIOiAsTiAJQCDYI8radqGrRurWylAa9/BulN5d3behhBIITC1U77QeJb95qRL7QnMSAGRxbQDqUjMeOSxNxi8hzB/55zRKeavaK/uJx9ScfWd9hoc/3jh68+HU57Bb5kmgu5g8bTG18+PclEIhcDILtcCl1ZEeEKx9x97n5o8yKZKYbItquP7uQM4+FQ179vdDuv9o8OZy6Z63C6bImMSrHY2u33+8/Lw+GzcwtJzzP1JSgIbc7ZH7fc5N4E/CG7S5Vl8rp8/3EcMcm1CKvt7daDCyKgpqikNhhsRpuNS1Asid26X2SPqm3b1mTm2KY3w79d4Wo1zk9oPzxxOUHGVMqU8gXGo1ELej3A8xcs0HXA+FkG/T5iJmtJlCrj38dBVWVwcxl4ImGBYQAmkyas5Bmm02Y42n/Ub8QfojqXuKcBAAAAAElFTkSuQmCC);"

            else:
                image = "background: no-repeat url(pri_0%d.png);" % i

            image_priority.append('''
            div.pri_0%d
            {
                display:inline-block;
                position:relative;
                top:-10px;
                padding:0px;
                margin-right:-9px;
                margin-left:-9px;
                width:18px;
                height:18px;
                %s
            }
''' % (i,image))

        if(self.is_inline()):
            image_star = "background: no-repeat url(data:object/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAARCAYAAADQWvz5AAAAB3RJTUUH3gEcBA8VLgNGkAAAAAlwSFlzAAAewQAAHsEBw2lUUwAAAARnQU1BAACxjwv8YQUAAAKNSURBVHjaY2AgAJKDNUSTg1UkCKljIaRAT/mxMyPDP1YgczEFBjEzWBmyhv7+zQpU9xto0B+cKpnwGeNmycErL81gJyH628rRmIsXn1q8Bnnbcdtycn4Q4eT4KOJgwmBJtkEWBpzBjMxAD7L+ZzDV5fDHG0ZNOeJmksJf1f/+Y/j19y/L73//Wf8xMPz//vMX1285yXeeQA7Df6B1ynI//KZVCx//9+/Xf0YgYGL684+R8S8TIwMT89PXfLcY3ay4ubLCBPJsjN60s3P8YvjPCHHk//+MDIxMfxj+AV30BxjGjEDMxsoIlvsHsurvf4Yf3zkZjpwXrpy+6sMURpjTimO5DeL9/yySlPipywSMbCZgPIG8BfL8f5AqoEH//gLj7ieQ/5uB4dlzntPzNzAkTVn55QokfoEApO7Ypd8vDp/+P1dbiV9QTOCPGQPTP4hhbEAMNOwf0KAfX4AGfWP/c/w8Z3tqw/foXSd+vmREDyxGuAgzw4ouuYyPJ5n/vz/P8P/9RSC+xPD/9WmG/8/3M/xf3aOWD7EaRqLF2v//MIm/DMJCPCIsrH/BXgG54tcXiBzIhWJCDHoMDKwQPbiiHyShry7AqKH4PvI30JCfX4Fe+Sr248dn4Q//f0FUy4h/9vKxF+UhmI7CPbhM+Xnfa/34xsDw6YPs7QWbhO065rEaPH8hepwRGFvc3G8l7I3+2TEQAvvmck94d4T5/56ZEgvdLEXgNmsqcjBtmczX++og0//dM/jwZmAGexMWzttb5c8saFFLhuVnYIpDighGhqlVQiHX1stc8LQREkDWy4zMifEV1/z6Q+hKQvWt5aCEAzLg/3+YERCw7fD3azrqoveFBLjZ95969xymFwD5XuKCCC2f/AAAAABJRU5ErkJggg==);"
        else:
            image_star = "background: no-repeat url(star_small.png);"
        
        output = css.substitute({
            "common" : string.Template('''
  a {color: #FD4626;font-weight: bold;font-size:0.9em;}
  a:hover {color: #666;font-weight: bold;text-decoration: underline;}
  a img {border: none;}
  a.name {color: black;}
  
  h1{font-size: 1.3em;padding: 0px;padding-bottom: 3px;margin: 0px;margin-top:10px;margin-left: 5px;color:#666;}
  h2{font-size: 1.2em;font-weight: bold;color: #005CDB;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;}
  h3{font-size: 1.1em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: black;}
  h4{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: #666;}
  h5{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: #A67F00;}
  h6{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: black;text-decoration:underline;}
  
  p {margin-left: 20px;margin-bottom:10px;font-size: 1.0em;}
  p.caption {margin-left: 0px;text-align: center;margin-top: 5px;}

  
  div.tb
  {
      width:80%;
      margin:0px;
      padding:10px;
      margin-left:20px;
      border-radius: 15px;
      -moz-border-radius: 15px;
      border:4px solid #dfd3b3;
      background:#f5f4e5;
  }
  
  font.hilite
  {
      background-color:yellow;
      font-weight: bold;
  }
  
  
  /* Table of Contents */
  div.toc1 {margin-top:8px;margin-bottom:4px;}
  div.toc1 a{margin-left:20px;font-size:1.1em;color:#666;}
  div.toc2 {margin-top:4px;margin-bottom:2px;}
  div.toc2 a{margin-left:40px;font-size:1.0em;color:#005CDB;}
  div.toc3 {margin-top:4px;margin-bottom:2px;}
  div.toc3 a{margin-left:50px;font-size:0.9em;color:#000;}
  div.toc4 a{margin-left:70px;font-size:0.9em;color:#777;}
  div.toc5 a{margin-left:90px;font-size:0.9em;color:#666;}
  table {
      *border-collapse: collapse; /* IE7 and lower */
      border-spacing: 0;
  }
  
  .bordered {
      margin:10px;
      margin-left:20px;
      background-color:white;
      border: solid #ccc 4px;
      -moz-border-radius: 6px;
      -webkit-border-radius: 6px;
      border-radius: 6px;
  }
  
  .bordered td, .bordered th {
      border-left: 1px solid #ccc;
      border-top: 1px solid #ccc;
      padding: 4px;
      text-align: left;    
  }
  
  .bordered th {
      background-color:#396592;
      color: white;
      border-top: none;
  }
  
  .bordered tr.alternaterow {
      background-color:#f0f0f0;
  }
  .bordered tr.caption {
      background-color:#8C9CB8;
      color:white;
  }
  
  .bordered tr.header td {
      font-weight:bold;
      background-color:#ddd;
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  .bordered tr td.header {
      font-weight:bold;
      background-color:#ddd;
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  .bordered tr td.subheader {
      background-color:#E1E8EF;
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
  }
  .bordered tr td.reserved {
      background-color:#f0f0f0;
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
      color:#a0a0a0;
  }
  
  .bordered td:first-child, .bordered th:first-child {
      border-left: none;
  }
  
  .bordered th:first-child {
      -moz-border-radius: 3px 0 0 0;
      -webkit-border-radius: 3px 0 0 0;
      border-radius: 3px 0 0 0;
  }
  
  .bordered th:last-child {
      -moz-border-radius: 0 3px 0 0;
      -webkit-border-radius: 0 3px 0 0;
      border-radius: 0 3px 0 0;
  }
  
  .bordered th:only-child{
      -moz-border-radius: 3px 3px 0 0;
      -webkit-border-radius: 3px 3px 0 0;
      border-radius: 3px 3px 0 0;
  }
  
  .bordered tr:last-child td:first-child {
      -moz-border-radius: 0 0 0 3px;
      -webkit-border-radius: 0 0 0 3px;
      border-radius: 0 0 0 3px;
  }
  
  .bordered tr:last-child td:last-child {
      -moz-border-radius: 0 0 3px 0;
      -webkit-border-radius: 0 0 3px 0;
      border-radius: 0 0 3px 0;
  }
  
  .image_inline
  {
      display:inline;
  }
  .image_inline table
  {
      display:inline;
      text-align:center;
  }
  .image_inline img
  {
      border:0px;
      margin-left:20px;
  }
  /* Question and answer blocks */
  div.question
  {
      background-color:#ddd;
      padding:10px;
  }
  div.answer
  {
      padding:10px;
  }
  
  div.code
  {
      border-radius: 8px;
      -moz-border-radius: 8px;
      padding-top:6px;
      padding-bottom:6px;
      padding-left:3px;
      padding-right:3px;
  
      font-family: courier new;
      font-size: 0.9em;
      margin-bottom: 0px;
      margin-top: 4px;
      margin-left:25px;
      margin-right:10px;
      margin-bottom:10px;
      background-color:#f0f0f0;
      border:3px solid #ccc;
  }
  div.code2
  {
      font-family: courier new;
      font-size: 0.9em;
      margin-bottom: 10px;
      margin-top: 0px;
      margin-left:10px;
      margin-right:15px;
      background-color:#f0f0f0;
      border:1px solid #ccc;
  }
  div.code3
  {
      font-family: courier new;
      font-size: 0.9em;
  }
  
  div.code a
  {
      font-weight:normal;
  }
  div.prototype a
  {
      font-weight:normal;
  }
  
  div.source
  {
      visibility:hidden;
      display:block;
      height:0;
      width:0;
  }
  
  
  div.code_result
  {
     margin-left: 25px;
     color: #396592;
  }


  div.star
  {
      display:inline-block;
      position:relative;
      top:-10px;
      padding:0px;
      margin-right:-9px;
      margin-left:-9px;
      width:18px;
      height:18px;
      $star
  }

  ${priority}

  ''').substitute({
        "star" : image_star,
        "priority" : ''.join(image_priority)}),

            "print_only" : '''
body
{
    width:100%;margin:0;float:none;
    font-family:times;

}
div.container
{
    width:100%;margin:0;float:none;

}
div.header
{
    display:none;
}
div.menu_div
{
    display:none;
}

div.footer
{
    display:block;
}

div.footer a
{
    display:none;
}

div.code_header
{
    display:none;
}

object
{
    display:none;
}

/* Styling of code segments */
div.snippet span.operator {color: purple;}
div.snippet span.kw {font-weight:bold;color: blue;} /* keyword */
div.snippet span.str {color: #9933CC;}
div.snippet span.mstring {color: #9933CC;}
div.snippet span.cmt {font-style:italic;color: green;}
div.snippet span.ln {color: #C0C0C0;}

/* Styling of text blocks */
div.tblkps {margin:0px;padding:0px;margin-left:20px;}
div.tblkp  {margin:0px;padding:0px;}
''',

            "screen_only" : '''
  div.code_header
  {
      font-family: courier new;
      font-size: 0.9em;
      margin-bottom:0px;
      margin-top:10px;
      margin-left: 30px;
      background-color: white;
      border: 0px;
      width:100%;
      color:#ccc;
  }
  
  div.code_header a
  {
      text-decoration:none;
      color:#ccc;
  }

  /* Styling of code segments */
  div.snippet span.operator {color: purple;}
  div.snippet span.keyword {color: blue;}
  div.snippet span.kw {color: blue;}
  div.snippet span.str {color: #9933CC;}
  div.snippet span.mstring {color: #9933CC;}
  div.snippet span.cmt {color: green;}
  div.snippet span.ln {color: #C0C0C0;}

  /* Styling of text blocks */
  div.tblkps {margin-left:4px;margin-bottom:4px;font-size:1.0em;}
  div.tblkp  {margin-left:4px;padding:0px;margin-bottom:4px;font-size:1.0em;}
'''
            })

        return output


    
    def install_support_files(self, outputdir):
        
        #if(os.path.exists(outputdir)):
        #    shutil.rmtree(outputdir)
       
        if(os.path.exists(outputdir + "/css")):
            shutil.rmtree(outputdir + "/css")

        #os.makedirs(outputdir)

        #print "Theme: [%s]" % self.m_theme
        #print "Template dir: [%s]" % self.m_template_dir
        #print("Copying %s" % (self.m_template_dir + self.m_theme + "/" + self.m_theme))

        ignore_patterns=('*.html', '*.swp')
        shutil.copytree(self.m_template_dir + self.m_theme, outputdir + "/css", ignore=shutil.ignore_patterns(*ignore_patterns))

        # Update the CSS file to process any common definitions
        handle = open("%s/css/%s.css" % (outputdir, self.m_theme), "rt")
        contents = handle.read()
        handle.close()
        css = self._fix_css(contents)
        handle = open("%s/css/%s.css" % (outputdir, self.m_theme), "wt")
        handle.write(css)
        handle.close()

        outputdir += "/css/"

        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/pdf.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/txt.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/question.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/note.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/20x20/lock.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/20x20/icon_error.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/warning.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/50x50/tbd.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/star.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/star_small.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/pri_01.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/pri_02.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/pri_03.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/pri_04.png", outputdir)
        shutil.copy(shorte_get_startup_path() + "/templates/shared/pri_05.png", outputdir)


    def get_output_path(self, path):

        #print "INPUT: %s" % path
        #sys.stdout.flush()
        #if(path.endswith(".tpl")):
        #    output_file = path[0,-4] + ".html"

        #print "OUTPUT: %s" % output_file
        #sys.stdout.flush()
        #sys.exit(-1)
            
        # Strip off the extension
        output_file = re.sub(".tpl", ".html", path)

        return output_file

    def generate_source_file(self, input, output):
        
        handle = open(input, "rt")
        contents = handle.read()
        handle.close()
        
        language = "c"
        parser = self.m_engine.m_source_code_analyzer
        tags = parser.parse_source_code(language, contents)

        template = string.Template(self._load_template("index.html"))
        vars = {}
        vars["rightmenu"] = ""
        vars["src"] = ""
        vars["version"] = ""
        vars["theme"] = self.m_engine.get_theme()
        vars["date"] = datetime.date.today()
        vars["css"] = self.get_css()
        vars["pdf"] = ""
        vars["links"] = ""
        vars["contents"] = self.format_source_code(language, tags)
        vars["title"] = ""
        vars["javascript"] = ""
        vars["link_index"] = "../index.html"
        vars["link_index_framed"] = "../index_framed.html"
        vars["link_legal"] = "../legal.html"
        vars["link_revisions"] = "../revisions.html"
        vars["html_tooltips"] = template_html_tooltips

        html = template.substitute(vars)

        handle = open(output, "w")
        handle.write(self._cleanup_html(html))
        handle.close()

    def _cleanup_html(self, html):

        html = html.replace("", "'")
        html = html.replace("®", "&reg;")

        return html

        
    def generate_legal_page(self, output):
        
        template = string.Template(self._load_template("legal.html"))
        vars = {}
        vars["rightmenu"] = ""
        vars["src"] = ""
        vars["version"] = self.m_engine.get_doc_info().version();
        vars["theme"] = self.m_engine.get_theme()
        vars["date"] = datetime.date.today()
        vars["css"] = self.get_css()
        vars["pdf"] = ""
        vars["links"] = ""
        vars["title"] = "Cortina Legal Information"
        vars["link_index"] = "../index.html"
        vars["link_index_framed"] = "../index_framed.html"
        vars["link_legal"] = "legal.html"
        vars["link_revisions"] = "revisions.html"

        html = template.substitute(vars)

        handle = open(output, "w")
        handle.write(self._cleanup_html(html))
        handle.close()

    def generate_revision_history_page(self, output):
        
        history = self.m_engine.get_doc_info().revision_history()

        if(history != None):
            history["title"] = "Revision History"
            history = self.format_table("", history)
        else:
            history = ""

        template = string.Template(self._load_template("index.html"))
        vars = {}
        vars["rightmenu"] = ""
        vars["src"] = ""
        vars["version"] = self.m_engine.get_doc_info().version();
        vars["theme"] = self.m_engine.get_theme()
        vars["date"] = datetime.date.today()
        vars["css"] = self.get_css()
        vars["pdf"] = ""
        vars["links"] = ""
        vars["contents"] = history
        vars["html_tooltips"] = ""
        vars["javascript"] = ""
        vars["subtitle"] = "Document History"
        vars["title"] = "Revision History"
        vars["link_index"] = "../index.html"
        vars["link_index_framed"] = "../index_framed.html"
        vars["link_legal"] = "legal.html"
        vars["link_revisions"] = "revisions.html"

        html = template.substitute(vars)

        handle = open(output, "w")
        handle.write(self._cleanup_html(html))
        handle.close()

    def generate_string(self, theme, version, package):
        
        self.m_inline = True
        package = "html_inline"
        
        return self.generate(theme, version, package, True)

    def generate(self, theme, version, package, as_string=False):

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        
        # Create the content directory if it's not
        # an inline HTML doc.
        if(not self.is_inline()):
            self.m_engine._mkdir(self.get_content_dir())
        
        page_names = {}
        self.m_contents = []
        links = []

        for page in pages:

            tags = page["tags"]
            title = page["title"]
            source_file = page["source_file"]

            if(len(page["links"]) > len(links)):
                links = page["links"]

            # Strip off the extension
            output_file = re.sub(".tpl", "", source_file)
            output_file = os.path.basename(output_file)

            base = output_file

            # Now see if the page name already exists and modify
            # it as necessary
            cnt = 1
            while(page_names.has_key(base)):
                base = "%s_%d" % (output_file,cnt)
                cnt += 1

            page_names[base] = base
            output_file = base + ".html"

            path = self.get_content_dir() + "/" + output_file

            for tag in tags:

                #print "TAG: %s" % tag["name"]

                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag.name, tag.contents, output_file)

                elif(self.m_engine.tag_is_source_code(tag.name)):
                    self.append_source_code(tag)

                else:
                    self.append(tag)

            if(self.is_inline() != True):
                output = open(path, "w")
                html = self.format_page(page, output_file, source_file)
                output.write(self._cleanup_html(html))
                output.close()
        
            
        # Now generate the document index
        if(as_string):
            return self.generate_index(title=self.m_engine.get_title(), subtitle=self.m_engine.get_subtitle(), theme=self.m_engine.get_theme(), version=version, links=links, as_string=True)
        else:
            self.generate_index(title=self.m_engine.get_title(), subtitle=self.m_engine.get_subtitle(), theme=self.m_engine.get_theme(), version=version, links=links)
        
        # Generate the frameset index and TOC page
        if(self.is_inline() != True):
            self.generate_toc_frame(self.m_engine.get_title())

        # Generate the legal and revision history pages
        if(self.is_inline() != True):
            path_legal = self.get_content_dir() + "/legal.html"
            self.generate_legal_page(path_legal)
            
            path_revisions = self.get_content_dir() + "/revisions.html"
            self.generate_revision_history_page(path_revisions)


        #self.generate_source_file("build-output/code.c", "build-output/code_c.html")

        if(self.is_inline() != True):
            self.install_support_files(self.get_content_dir())
       
        # Copy output images - really only required if we're generating
        # an HTML document.
        if(self.is_inline() != True):
            pictures_copied = {}
            for image in self.m_engine.m_images:
            
                if(pictures_copied.has_key(image)):
                    continue

                parts = os.path.split(image)
                #print "IMAGE: [%s]" % image
                shutil.copy(image, self.get_content_dir() + "/" + parts[1])
                pictures_copied[image] = True

        print "Generating doc"  

