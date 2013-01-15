# -*- coding: iso-8859-15 -*-
#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   odt_template.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a template class that is used
#|   to generate OpenOffice documents from a Shorte template.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re
import os
import string
import shutil
import time
from string import Template;

try:
    import Image
except:
    print "WARNING: Failed to load Image library"

from shorte_defines import *
from template import *

EOL = "\r\n"

comment_style_c = 0
comment_style_python = 1
    

import sys, zipfile, os, os.path

def unzip_file_into_dir(file, dir):

    try:
        os.makedirs(dir)
    except:
        ignore_error = 1

    #os.mkdir(dir, 0777)
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        #name = os.path.normpath(name)

        if name.endswith('/'):
            try:
                os.makedirs(os.path.join(dir, name))
            except:
                ignore_error = 1
        else:
            try:
                os.makedirs(os.path.dirname(os.path.join(dir,name)))
            except:
                ignore_error = 1

            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
import zipfile, os
 
 
def zipper(dir, zip_file):
    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(dir))
    for root, dirs, files in os.walk(dir):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            #print f
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
    zip.close()
    return zip_file
 

class template_odt_t(template_t):

    def __init__(self, parser, indexer):

        template_t.__init__(self, parser, indexer)
   
        self.m_sections = []
        section = {}
        headings = []
        section["Headings"] = headings
        self.m_sections.append(section)

        # DEBUG BRAD: Add a fake heading in case the
        # document doesn't start with a header tag.
        heading = {}
        heading["Title"] = ""
        heading["Type"] = HEADING_DEFAULT 
        heading["Content"] = ""
        self.m_headptr = heading["Content"]
        self.m_header_id = 0
        self.m_sections[0]["Headings"].append(heading)

        self.m_image_id = 2

        self.m_wikify = True

        self.m_pictures = []

        self.m_styles = {}
        self.m_styles["note"] = "shorte_note"
        self.m_styles["bold"] = "bold"
        self.m_styles["highlight"] = "shorte_highlight"
        self.m_styles["underline"] = "shorte_underline"
        self.m_styles["italic"] = "shorte_italic"
        self.m_styles["table"] = {}
        self.m_styles["table"]["style"] = "shorte_table"
        self.m_styles["table"]["column"] = "shorte_table.A"
        self.m_styles["table"]["cell"] = {}
        self.m_styles["table"]["cell"]["title"] = "shorte_table.C1"
        self.m_styles["table"]["cell"]["title_text"] = "shorte_para_white_bold"
        self.m_styles["table"]["cell"]["header"] = "shorte_table.B1"
        self.m_styles["table"]["cell"]["header_text"] = "ShorteHeaderText"
        self.m_styles["table"]["cell"]["subheader"] = "shorte_table.subheader"
        self.m_styles["table"]["cell"]["subheader_text"] = "ShorteNormalText"
        self.m_styles["table"]["cell"]["reserved"] = "shorte_table.reserved"
        self.m_styles["table"]["cell"]["reserved_text"] = "reserved"
        self.m_styles["table"]["cell"]["normal"] = "shorte_table.B2"
        self.m_styles["table"]["cell"]["normal_text"] = "ShorteNormalText"
        

        self.m_styles["table"]["row"] = {}

        self.m_styles["para"] = {}

        self.m_styles["para"]["bold"] = "Bold"
        self.m_styles["para"]["pre"] = "shorte_para_pre"
        self.m_styles["para"]["code2"] = "shorte_code"
        self.m_styles["para"]["caption"] = "Caption"
        self.m_styles["para"]["note"] = "Note"
        self.m_styles["para"]["normal"] = "Standard"
        self.m_styles["para"]["code"] = "code3"
        self.m_styles["para"]["spacer"] = "shorte_spacer"
        self.m_styles["para"]["list_level"] = {}
        self.m_styles["para"]["list_level"][0] = "para_list_level0"
        self.m_styles["para"]["list_level"][1] = "para_list_level1"
        self.m_styles["para"]["list_level"][2] = "para_list_level2"
        self.m_styles["para"]["list_level"][3] = "para_list_level3"
        self.m_styles["para"]["list_level"][4] = "para_list_level4"
        self.m_styles["para"]["list_level"][5] = "para_list_level5"
        self.m_styles["para"]["list_level"][6] = "para_list_level6"
        
        self.m_styles["para"]["indent"] = {}
        self.m_styles["para"]["indent"][0] = "shorte_indent_0"

        self.m_styles["span"] = {}
        self.m_styles["span"]["pre"] = "code3"

        self.m_styles["span"]["code"] = "code"
        self.m_styles["span"]["code_keyword"] = "code_keyword"
        self.m_styles["span"]["code_line_numbers"] = "code_line_numbers"
        self.m_styles["span"]["code_comment"] = "code_comment"
        self.m_styles["span"]["code_string"] = "code_string"
        
        self.m_styles["list"] = {}
        self.m_styles["list"]["ordered"] = "L3"
        self.m_styles["list"]["unordered"] = "L4"
        
        
        self.m_styles["table"]["row"]["prototype"] = "shorte_tablePrototype.1"
        self.m_styles["table"]["row"]["prototype_section"] = "shorte_tablePrototype.7"
        self.m_styles["table"]["cell"]["prototype"] = "shorte_table_prototype_data"
        self.m_styles["table"]["cell"]["prototype_name"] = "shorte_table_prototype_name"
        self.m_styles["table"]["cell"]["prototype_param"] = "para_prototype_param"
        
        self.m_styles["table"]["cell"]["prototype_section"] = "shorte_table_prototype_definition"
        self.m_styles["table"]["cell"]["prototype_section_text"] = "para_prototype_section"

        self.m_styles["table"]["cell"]["fhier"] = "shorte_table_fhier"
        self.m_styles["table"]["cell"]["fname"] = "shorte_table_fname"
        self.m_styles["table"]["cell"]["fdesc"] = "shorte_table_fdesc"
        self.m_styles["para"]["fdesc"] = "shorte_table_fdesc_text"
        self.m_styles["para"]["cell_text"] = "shorte_table_cell_text"
        
        self.m_styles["span"]["prototype"] = {}
        self.m_styles["span"]["prototype"]["param_name"] = "prototype_param_name"

        self.m_styles["para"]["prototype"] = {}
        self.m_styles["para"]["prototype"]["param"] = "para_prototype_param"
        self.m_styles["para"]["prototype"]["param_name"] = "para_prototype_param_name"
        self.m_styles["para"]["prototype"]["param_name2"] = "para_prototype_name"
        self.m_styles["para"]["prototype"]["text"] = "para_prototype_text"
        self.m_styles["para"]["prototype"]["section"] = "para_prototype_section"

        self.m_styles["table"]["columns"] = {}
        self.m_styles["table"]["columns"]["prototype"] = {}
        self.m_styles["table"]["columns"]["prototype"][0] = "shorte_tablePrototype.A"
        self.m_styles["table"]["columns"]["prototype"][1] = "shorte_tablePrototype.B"
        self.m_styles["table"]["columns"]["prototype"][2] = "shorte_tablePrototype.C"
        self.m_styles["table"]["columns"]["prototype"][3] = "shorte_tablePrototype.D"
        
        self.m_styles["table"]["styles"] = {}
        self.m_styles["table"]["styles"]["prototype"] = "shorte_table_prototype"

        self.m_styles["headings"] = {}
        self.m_styles["headings"][HEADING1] = "Heading_20_1" #"shorte_heading_1"
        self.m_styles["headings"][HEADING2] = "Heading_20_2" #"shorte_heading_2"
        self.m_styles["headings"][HEADING3] = "Heading_20_3" #"shorte_heading_3"
        self.m_styles["headings"][HEADING4] = "Heading_20_4" #"shorte_heading_4"

        self.m_styles_extra = ''
        self.m_table_id = 0

    def get_styles(self):
        return '''
    <style:style style:name="shorte_heading_1" style:display-name="Heading 1" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:master-page-name="" style:default-outline-level="1">
      <style:paragraph-properties fo:margin-top="0.0835in" fo:margin-left="-0.15in" fo:margin-bottom="0.25in" fo:keep-together="always" style:page-number="auto" fo:break-before="page" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#0063A5" style:font-name="Arial2" fo:font-size="14pt" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-size-asian="14pt" style:font-weight-asian="bold" style:font-name-complex="Times New Roman" style:font-size-complex="14pt" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_2" style:display-name="Heading 2" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="2">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-left="-0.15in" fo:margin-bottom="0.1in" fo:keep-together="always" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#000000" style:font-name="Arial2" fo:font-size="13pt" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-size-asian="13pt" style:font-weight-asian="bold" style:font-size-complex="13pt" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_2_break" style:display-name="Heading 2 Break" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="2">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-left="-0.15in" fo:margin-bottom="0.1in" fo:keep-together="always" fo:break-before="page" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#000000" style:font-name="Arial2" fo:font-size="13pt" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-size-asian="13pt" style:font-weight-asian="bold" style:font-size-complex="13pt" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_3" style:display-name="Heading 3" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="3">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-left="-0.15in" fo:margin-bottom="0.1in" fo:keep-together="always" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#948a54" style:font-name="Arial2" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-weight-asian="bold" style:font-name-complex="Times New Roman" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_3_break" style:display-name="Heading 3 Break" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="3">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-left="-0.15in" fo:margin-bottom="0.1in" fo:keep-together="always" fo:break-before="page" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#948a54" style:font-name="Arial2" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-weight-asian="bold" style:font-name-complex="Times New Roman" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_4" style:display-name="Heading 4" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="4">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-bottom="0in" fo:margin-left="-0.15in" fo:keep-together="always" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#909090" style:font-name="Arial2" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-style-asian="italic" style:font-weight-asian="bold" style:font-name-complex="Times New Roman" style:font-style-complex="italic" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_4_break" style:display-name="Heading 4 Break" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="4">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-bottom="0in" fo:margin-left="-0.15in" fo:keep-together="always" fo:break-before="page" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#909090" style:font-name="Arial2" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-style-asian="italic" style:font-weight-asian="bold" style:font-name-complex="Times New Roman" style:font-style-complex="italic" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="shorte_heading_5" style:display-name="Heading 5" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="5">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-bottom="0in" fo:keep-together="always" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#243f60" style:font-name="Cambria" style:font-name-asian="Times New Roman" style:font-name-complex="Times New Roman"/>
    </style:style>
    <style:style style:name="shorte_heading_5_break" style:display-name="Heading 5 Break" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text" style:default-outline-level="5">
      <style:paragraph-properties fo:margin-top="0.139in" fo:margin-bottom="0in" fo:keep-together="always" fo:break-before="page" fo:keep-with-next="always"/>
      <style:text-properties fo:color="#243f60" style:font-name="Cambria" style:font-name-asian="Times New Roman" style:font-name-complex="Times New Roman"/>
    </style:style>

    <style:style style:name="shorte_table" style:family="table">
      <style:table-properties style:width="6.5in" table:align="margins" style:writing-mode="lr-tb" fo:margin-bottom="0.1282in"/>
    </style:style>
    <style:style style:name="shorte_table.A" style:family="table-column">
      <style:table-column-properties style:column-width="3.25in" style:rel-column-width="32767*"/>
    </style:style>
    <style:style style:name="shorte_table.A1" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#c0c0c0" fo:padding="0.0382in" fo:border-left="0.0007in solid #000000" fo:border-right="none" fo:border-top="0.0007in solid #000000" fo:border-bottom="0.0007in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.B1" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#c0c0c0" fo:padding="0.0382in" fo:border="0.0007in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.subheader" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#e0e0e0" fo:padding="0.0382in" fo:border="0.0007in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.reserved" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#f0f0f0" fo:padding="0.0382in" fo:border="0.0007in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.C1" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#005CDB" fo:padding="0.0382in" fo:border="0.0007in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.A2" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0382in" fo:border-left="0.0007in solid #000000" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.0007in solid #000000"/>
    </style:style>
    <style:style style:name="shorte_table.B2" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0382in" fo:border-left="0.0007in solid #000000" fo:border-right="0.0007in solid #000000" fo:border-top="none" fo:border-bottom="0.0007in solid #000000"/>
    </style:style>
    <style:style style:name="P1" style:family="paragraph" style:parent-style-name="Header">
      <style:paragraph-properties fo:background-color="transparent" fo:padding-left="0in" fo:padding-right="0in" fo:padding-top="0in" fo:padding-bottom="0.0138in" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.0071in solid #999999">
        <style:background-image/>
      </style:paragraph-properties>
      <style:text-properties fo:color="#999999"/>
    </style:style>
    <style:style style:name="P2" style:family="paragraph" style:parent-style-name="Footer">
      <style:paragraph-properties fo:margin-left="0in" fo:margin-right="0in" fo:text-align="end" style:justify-single-word="false" fo:text-indent="0.9846in" style:auto-text-indent="false" fo:padding-left="0in" fo:padding-right="0in" fo:padding-top="0.0138in" fo:padding-bottom="0in" fo:border-left="none" fo:border-right="none" fo:border-top="0.0071in solid #666666" fo:border-bottom="none" style:shadow="none"/>
    </style:style>
    <style:style style:name="P3" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:text-align="center" style:justify-single-word="false"/>
      <style:text-properties fo:font-size="24pt" style:font-size-asian="24pt" style:language-asian="en" style:country-asian="CA" style:font-size-complex="24pt"/>
    </style:style>
    <style:style style:name="P4" style:family="paragraph" style:parent-style-name="Standard">
      <style:text-properties fo:color="#365f91" style:font-name="Cambria" fo:font-size="14pt" fo:font-weight="bold" style:font-name-asian="Times New Roman" style:font-size-asian="14pt" style:font-weight-asian="bold" style:font-size-complex="14pt" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="P5" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:text-align="center" style:justify-single-word="false"/>
      <style:text-properties fo:font-size="10pt" style:font-size-asian="10pt" style:language-asian="en" style:country-asian="CA" style:font-size-complex="10pt"/>
    </style:style>
    <style:style style:name="P6" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:text-align="center" style:justify-single-word="false"/>
      <style:text-properties fo:color="#948a54" fo:font-size="10pt" style:font-size-asian="10pt" style:language-asian="en" style:country-asian="CA" style:font-size-complex="10pt"/>
    </style:style>
    <style:style style:name="P7" style:family="paragraph" style:parent-style-name="Contents_20_1">
      <style:paragraph-properties>
        <style:tab-stops>
          <style:tab-stop style:position="6.5in" style:type="right" style:leader-style="dotted" style:leader-text="."/>
        </style:tab-stops>
      </style:paragraph-properties>
    </style:style>
    <style:style style:name="P8" style:family="paragraph" style:parent-style-name="Title" style:master-page-name="First_20_Page">
      <style:paragraph-properties style:page-number="auto"/>
      <style:text-properties fo:language="zxx" fo:country="none" fo:font-weight="bold" style:language-asian="zxx" style:country-asian="none" style:font-weight-asian="bold"/>
    </style:style>
    <style:style style:name="ShorteNormalText" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
    </style:style>
    <style:style style:name="ShorteHeaderText" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    
    <style:style style:name="shorte_spacer" style:family="paragraph">
      <style:paragraph-properties fo:padding-top="0in" fo:padding-bottom="0in" fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:font-size="3px"/>
    </style:style>

    <style:style style:name="shorte_note" style:family="paragraph" style:parent-style-name="Standard">
        <style:paragraph-properties
            fo:margin-left="0.254cm"
            fo:margin-right="0cm"
            fo:margin-bottom="0cm"
            fo:padding-bottom="0cm"
            fo:text-indent="0cm"
            style:auto-text-indent="false"
            fo:background-color="#f0f0f0"
            fo:padding="0.102cm"
            fo:border-left="0.002cm solid #000000"
            fo:border-right="none"
            fo:border-top="none"
            fo:border-bottom="none" style:shadow="none">
            <style:background-image/>
        </style:paragraph-properties>
    </style:style>

    <style:style style:name="para_list_level1" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_1"/>
    <style:style style:name="para_list_level2" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_2">
      <style:paragraph-properties fo:margin-left="0.5in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
    </style:style>
    <style:style style:name="para_list_level3" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_3">
      <style:paragraph-properties fo:margin-left="0.7in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
    </style:style>
    <style:style style:name="para_list_level4" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_4">
      <style:paragraph-properties fo:margin-left="0.9in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
    </style:style>
    <style:style style:name="para_list_level5" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_5">
      <style:paragraph-properties fo:margin-left="1.1in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
    </style:style>
    <style:style style:name="para_list_level6" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_6">
      <style:paragraph-properties fo:margin-left="1.3in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
    </style:style>

    <style:style style:name="reserved" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#909090"/>
    </style:style>

    <style:style style:name="shorte_table_prototype" style:family="table">
      <style:table-properties fo:margin="0in" fo:background-color="transparent" style:shadow="none" style:writing-mode="lr-tb">
        <style:background-image/>
      </style:table-properties>
    </style:style>

    <style:style style:name="shorte_tablePrototype.A" style:family="table-column">
      <style:table-column-properties style:column-width="0.503cm"/>
    </style:style>

    <style:style style:name="shorte_tablePrototype.B" style:family="table-column">
      <style:table-column-properties style:column-width="2.699cm"/>
    </style:style>

    <style:style style:name="shorte_tablePrototype.C" style:family="table-column">
      <style:table-column-properties style:column-width="0.682cm"/>
    </style:style>
    <style:style style:name="shorte_tablePrototype.D" style:family="table-column">
      <style:table-column-properties style:column-width="12.309cm"/>
    </style:style>
    <style:style style:name="shorte_tablePrototype.1" style:family="table-row">
      <style:table-row-properties style:min-row-height="0.503cm"/>
    </style:style>
    <style:style style:name="shorte_table_prototype_name" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#b3b3b3" fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="0.002cm solid #000000" fo:border-bottom="0.002cm solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_prototype_data" style:family="table-cell">
      <style:table-cell-properties fo:background-color="transparent" fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_prototype_definition" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#e6e6e6" fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_tablePrototype.7" style:family="table-row">
      <style:table-row-properties style:min-row-height="0.531cm"/>
    </style:style>


    <style:style style:name="para_prototype_name" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#ffffff" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    <style:style style:name="para_prototype_text" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-left="0.3cm" fo:margin-right="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
      <style:text-properties fo:font-size="10pt" style:font-size-asian="10pt" style:font-size-complex="10pt"/>
    </style:style>
    <style:style style:name="para_prototype_section" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>

    <style:style style:name="para_prototype_code" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#000000" fo:font-weight="bold" style:font-name="Courier New" fo:font-size="9pt"/>
    </style:style>

    <style:style style:name="para_prototype_param_name" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#0000ff" fo:font-weight="bold" style:font-name="Courier New" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="para_prototype_param" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#000000" font-name="Courier New" fo:font-size="9pt"/>
    </style:style>
    

    <text:list-style style:name="L3">
            <text:list-level-style-number text:level="1" text:style-name="Numbering_20_Symbols" style:num-prefix=" " style:num-suffix="." style:num-format="1">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.27cm" fo:text-indent="-0.635cm" fo:margin-left="0.9cm"/>
                </style:list-level-properties>
            </text:list-level-style-number>
            <text:list-level-style-number text:level="2" text:style-name="Numbering_20_Symbols" style:num-prefix=" " style:num-suffix="." style:num-format="1" text:display-levels="2">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.905cm" fo:text-indent="-0.635cm" fo:margin-left="1.905cm"/>
                </style:list-level-properties>
            </text:list-level-style-number>
            <text:list-level-style-number text:level="3" text:style-name="Numbering_20_Symbols" style:num-prefix=" " style:num-suffix=")" style:num-format="a">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.54cm" fo:text-indent="-0.635cm" fo:margin-left="2.54cm"/>
                </style:list-level-properties>
            </text:list-level-style-number>
            <text:list-level-style-bullet text:level="4" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.175cm" fo:text-indent="-0.635cm" fo:margin-left="3.175cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="5" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.81cm" fo:text-indent="-0.635cm" fo:margin-left="3.81cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="6" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="4.445cm" fo:text-indent="-0.635cm" fo:margin-left="4.445cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="7" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.08cm" fo:text-indent="-0.635cm" fo:margin-left="5.08cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="8" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.715cm" fo:text-indent="-0.635cm" fo:margin-left="5.715cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="9" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.35cm" fo:text-indent="-0.635cm" fo:margin-left="6.35cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="10" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.985cm" fo:text-indent="-0.635cm" fo:margin-left="6.985cm"/>
                </style:list-level-properties>
                <style:text-properties style:font-name="StarSymbol"/>
            </text:list-level-style-bullet>
        </text:list-style>
        <text:list-style style:name="L4">
            <text:list-level-style-bullet text:level="1" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.27cm" fo:text-indent="-0.635cm" fo:margin-left="1.27cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="2" text:style-name="Bullet_20_Symbols" text:bullet-char="◦">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.905cm" fo:text-indent="-0.635cm" fo:margin-left="1.905cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="3" text:style-name="Bullet_20_Symbols" text:bullet-char="▪">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.54cm" fo:text-indent="-0.635cm" fo:margin-left="2.54cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="4" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.175cm" fo:text-indent="-0.635cm" fo:margin-left="3.175cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="5" text:style-name="Bullet_20_Symbols" text:bullet-char="◦">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.81cm" fo:text-indent="-0.635cm" fo:margin-left="3.81cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="6" text:style-name="Bullet_20_Symbols" text:bullet-char="▪">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="4.445cm" fo:text-indent="-0.635cm" fo:margin-left="4.445cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="7" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.08cm" fo:text-indent="-0.635cm" fo:margin-left="5.08cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="8" text:style-name="Bullet_20_Symbols" text:bullet-char="◦">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.715cm" fo:text-indent="-0.635cm" fo:margin-left="5.715cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="9" text:style-name="Bullet_20_Symbols" text:bullet-char="▪">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.35cm" fo:text-indent="-0.635cm" fo:margin-left="6.35cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            <text:list-level-style-bullet text:level="10" text:style-name="Bullet_20_Symbols" text:bullet-char="•">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.985cm" fo:text-indent="-0.635cm" fo:margin-left="6.985cm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
        </text:list-style>
    
    <style:style style:name="shorte_para_white_bold" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#ffffff" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>

    <style:style style:name="code3" style:family="paragraph" style:parent-style-name="Standard" style:master-page-name="">
        <style:paragraph-properties fo:margin-left="0.255cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:line-height="100%" fo:text-indent="0cm" style:auto-text-indent="false" style:page-number="auto" fo:background-color="#f2f2f2" fo:keep-with-next="auto">
            <style:background-image/>
        </style:paragraph-properties>
        <style:text-properties style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="8pt" style:font-size-complex="8pt"/>
    </style:style>

    <style:style style:name="code" style:family="text">
        <style:text-properties style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="8pt" style:font-size-complex="8pt"/>
    </style:style>
    <style:style style:name="code_line_numbers" style:display-name="code_line_numbers" style:family="text">
        <style:text-properties fo:color="#c0c0c0" style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="10pt" style:font-size-complex="8pt"/>
    </style:style>
    <style:style style:name="code_string" style:display-name="code_string" style:family="text">
        <style:text-properties fo:color="#ff00ff" style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="10pt" style:font-size-complex="8pt"/>
    </style:style>
    <style:style style:name="code_comment" style:display-name="code_comment" style:family="text">
        <style:text-properties fo:color="#54c571" style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="10pt" style:font-size-complex="8pt"/>
    </style:style>
    <style:style style:name="code_keyword" style:display-name="code_keyword" style:family="text">
        <style:text-properties fo:color="#0000ff" style:font-name="Courier New" fo:font-size="8pt" style:font-size-asian="10pt" style:font-size-complex="8pt"/>
    </style:style>
    <style:style style:name="hyperlink" style:display-name="hyperlink" style:family="text">
        <style:text-properties fo:color="#ff0000"/>
    </style:style>

    <style:style style:name="shorte_enum_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3200cm*"/>
    </style:style>
    <style:style style:name="shorte_enum_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="800*"/>
    </style:style>
    <style:style style:name="shorte_enum_col3" style:family="table-column">
    <style:table-column-properties style:rel-column-width="4200*"/>
    </style:style>
    
    
    <style:style style:name="shorte_acronym_col1" style:family="table-column">
    <!--<style:table-column-properties style:rel-column-width="5000*"/>-->
    <style:table-column-properties style:use-optimal-column-width="true"/>
    </style:style>
    <style:style style:name="shorte_acronym_col2" style:family="table-column">
    <!--<style:table-column-properties style:rel-column-width="5000*"/>-->
    <style:table-column-properties style:use-optimal-column-width="true"/>
    </style:style>
    
    <style:style style:name="shorte_func_summary_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="2000*"/>
    </style:style>
    <style:style style:name="shorte_func_summary_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3000*"/>
    </style:style>
    
    <style:style style:name="shorte_type_summary_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="300*"/>
    </style:style>
    <style:style style:name="shorte_type_summary_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3000*"/>
    </style:style>
    
    <style:style style:name="shorte_testcase_summary_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="300*"/>
    </style:style>
    <style:style style:name="shorte_testcase_summary_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3000*"/>
    </style:style>
    <style:style style:name="shorte_testcase_summary_col3" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3000*"/>
    </style:style>
    <style:style style:name="shorte_testcase_summary_col4" style:family="table-column">
    <style:table-column-properties style:rel-column-width="3000*"/>
    </style:style>

    
    <style:style style:name="shorte_table_fhier" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#f0f0f0"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none"
        fo:border-top="0.002cm solid #C0C0C0" fo:border-bottom="0.002cm solid #C0C0C0">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table_fname" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#fafafa"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none"
        fo:border-top="none" fo:border-bottom="0.002cm solid #e0e0e0">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_fdesc" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#fafafa"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none"
        fo:border-top="none" fo:border-bottom="0.002cm solid #A0A0A0">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table_fdesc_text" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>

    <style:style style:name="shorte_table_test" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#fafafa"
        fo:padding="0.097cm"
        fo:border-left="0.002cm solid #e0e0e0"
        fo:border-bottom="0.002cm solid #e0e0e0"
        fo:border-right="none">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_test2" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#fafafa"
        fo:padding="0.097cm"
        fo:border-left="none"
        fo:border-bottom="0.002cm solid #e0e0e0"
        fo:border-right="none">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    
    <style:style style:name="shorte_code" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
        <style:text-properties fo:color="#000000" style:font-name="Courier New" fo:font-size="9pt" style:font-size-asian="10pt" style:font-size-complex="9pt"/>
    </style:style>
    
    <style:style style:name="shorte_para_pre" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-left="0.25cm" fo:margin-bottom="0cm" style:shadow="none"/>
        <style:text-properties fo:color="#000000" style:font-name="Courier New" fo:font-size="9pt" style:font-size-asian="10pt" style:font-size-complex="9pt"/>
    </style:style>


    <style:style style:name="shorte_underline" style:family="text">
        <style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>
    
    <style:style style:name="shorte_span_color_0000ff" style:family="text">
        <style:text-properties fo:color="#0000ff"/>
    </style:style>

    <style:style style:name="shorte_italic" style:family="text">
        <style:text-properties fo:font-style="italic" style:font-style-asian="italic" style:font-style-complex="italic"/>
    </style:style>
    
    <style:style style:name="shorte_indent_0" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties
        fo:margin-left="0.1846in"
        style:auto-text-indent="false"
        fo:padding-top="0.0138in"/>
    </style:style>
    
    <style:style style:name="shorte_page_break" style:family="paragraph" style:parent-style-name="Standard">
        <style:paragraph-properties fo:break-after="page"/>
    </style:style>
    
    <style:style style:name="shorte_highlight" style:family="text">
        <style:text-properties fo:background-color="#ffff00"/>
    </style:style>
    
    ''' + self.m_styles_extra
                   
    def format_wikiword(self, link, link_word, label, is_bookmark):
        '''This method is called to format a wikiword. It is called by
           the wikify method in the template base class'''

        if(is_bookmark):
            tmp = '''<text:a xlink:type="simple" xlink:href="#%s" office:name="%s">%s</text:a>''' % (link_word, label, label)
        else:
            tmp = '''<text:a xlink:type="simple" xlink:href="#%s|outline" office:name="%s">%s</text:a>''' % (link_word, label, label)
        output = '''<text:span text:style-name="hyperlink">%s</text:span>''' % tmp

        return output


    def get_index_name(self):
        title = self.m_engine.get_document_name()
        title = title.replace("©", "")
        title = title.replace("®", "")
        return "%s.odt" % title

    def get_title(self):
        title = self.m_engine.get_title()
        title = title.replace("©", "")
        title = title.replace("®", "&#174;")
        return title

    def get_title_short(self):
        title = self.m_engine.get_title()
        title = title.replace("©", "")
        title = title.replace("®", "")
        title = title.replace("Cortina Systems", "")
        title = title.strip()
        return title
    
    def append_page(self, pages, title, source_file):

        return ""

    def append_header(self, tag):

        name = tag["name"]
        data = tag["contents"]
        break_before = False

        if(tag.has_key("break_before")):
            break_before = tag["break_before"]
        elif(tag.has_key("is_prototype")):
            break_before = int(self.m_engine.get_config("odt", "prototype_break_before"))

        data = self.format_text(data, False)

        if(name == "h1"):
            
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING1
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_headptr = heading["Content"]
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)

        elif(name == "h2"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING2
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
        
        elif(name == "h3"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING3
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
        
        elif(name == "h4"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING4
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
    
    def _expand_links(self, matches):

        (source, label, external) = self._process_link(matches)
       
        # DEBUG BRAD: This is a temporary hack to get links of the format -> to work
        source = re.sub(".*?#(.*)", "\\1", source)
        label = re.sub(".*?#(.*)", "\\1", label)
        #print "SOURCE = %s, LABEL = %s" % (source, label)
        #source.replace("-&amp;gt;", "")
        #label = label.replace("-&gt;", "")

        if(source[0:4] == "http" or external == True):
            if(source[0:4] != "http"):
                output_path = self.m_engine.get_output_dir()
                if(sys.platform == "cygwin" or sys.platform == "win32"):
                    output_path = output_path.replace("/cygdrive/c/", "C:/")
                source = "file:///%s/%s" % (output_path, source)
            return '''<text:a xlink:type="simple" xlink:href="%s" office:name="%s">%s</text:a>''' % (source, label, label)
        else:
            hyperlink = '''<text:a xlink:type="simple" xlink:href="#%s|outline" office:name="%s">%s</text:a>''' % (source, label, label)
            return '''<text:span text:style-name="hyperlink">%s</text:span>''' % hyperlink
    
    def _expand_anchors(self, matches):

        (source, label, external) = self._process_link(matches)
        
        return '''
<text:bookmark-start text:name="%s"/>
    <text:a xlink:type="simple" xlink:href="" office:name="%s">%s</text:a>
<text:bookmark-end text:name="%s"/>''' % (source, label, label, label)
    
    def _format_links(self, data):
        
        # Expand any anchors
        expr = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        data = expr.sub(self._expand_anchors, data)
        
        # Expand any links
        expr = re.compile("\[\[(.*?)\]\]", re.DOTALL)
        data = expr.sub(self._expand_links, data)
       
        return data
    

    def format_image(self, image):
        
        # Check to see if the image requires conversion such as
        # is the case with inkscape SVG files
        if(image.has_key("converter")):
            image = self.m_engine.convert_image(image)

        #print "image: [%s]" % image["src"]

        data = encode_image(image["src"])

        style = ""

        # DEBUG BRAD: Should use the PIL module to figure out the
        #             dimentions of the image and insert them into
        #             the document. Otherwise the images get inserted
        #             as small images
        width = 0
        height = 0
        if(image.has_key("width")):
            width = image["width"]
            width = re.sub("px", "", width)
            width = int(width)

        if(image.has_key("height")):
            height = image["height"] 
            height = re.sub("px", "", height)
            height = int(height)
            
        im = Image.open(image["src"])
        width = im.size[0]
        height = im.size[1]

        #print "width: %d" % width
        #print "height: %d" % height

        max_width = 460.0
        max_height = 640.0

        #if(width < max_width):
        #width = width / 2
        #height = height / 2

        if(height > max_height):
            new_height = max_height
            new_width = (max_height/height) * width
            
            height = new_height
            width = new_width
        
        if(width > max_width):
            new_width = max_width
            new_height = (max_width/width) * height
            height = new_height
            width = new_width

        #print "width2: %d" % width
        #print "height2: %d" % height

        dpi = 72.0
        width = "%fin" % (width/dpi)
        height = "%fin" % (height/dpi)

        height = "svg:height=\"%s\"" % height
        width = "svg:width=\"%s\"" % width

        #print "HEIGHT: %s" % height
        #print "WIDTH: %s" % width

        tag_start = ""
        tag_end = ""

        if(image.has_key("inline")):
            tag_start = "</text:p>"
            tag_end   = "<text:p text:style-name=\"Standard\">"

        caption = ""
        if(image.has_key("caption")):
            caption = self.format_bold(image["caption"])
            

        self.m_pictures.append(image)
        basename = image["name"] + image["ext"]

        data = """
%s
<text:p text:style-name="Standard">
<draw:frame draw:style-name="fr1" draw:name="graphics1" text:anchor-type="character" %s %s draw:z-index="0">
    <draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
</draw:frame>
</text:p>
%s
%s
""" % (tag_start, width, height, basename, caption, tag_end)
        
#        data = """
#</text:p>
#<text:p text:style-name="Standard">
#<draw:frame draw:style-name="fr3" draw:name="graphics3" text:anchor-type="character" %s %s draw:z-index="0">
#    <draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
#</draw:frame>
#</text:p>
#<text:p text:style-name="Standard">
#""" % (width, height, image["name"])

        self.m_image_id += 1

        return data

    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)
        image["inline"] = True

        return self.format_image(image)
    
    def parse_inline_styling(self, matches):
        data = matches.groups()[0].strip()
        parts = data.split(",")
        if(len(parts) == 1):
            tag = parts[0]
            replace = ''
        elif(len(parts) == 2):
            tag = parts[0]
            replace = parts[1]
       
        # Check if it's an inline styling block such as color
        #   @{color:00ff00,my text here}
        if(-1 != tag.find(":")):
            parts = tag.split(":")
            tag = parts[0].strip()
            qualifier = parts[1].strip()

        if(tag == "b"):
            return "<text:span text:style-name=\"%s\">%s</text:span>" % (self.m_styles["bold"], replace)
        elif(tag == "u"):
            return "<text:span text:style-name=\"%s\">%s</text:span>" % (self.m_styles["underline"], replace)
        elif(tag == "i"):
            return "<text:span text:style-name=\"%s\">%s</text:span>" % (self.m_styles["italic"], replace)
        elif(tag == "br"):
            return '<text:line-break/>'
        elif(tag == "color"):
            color = qualifier
            self.m_styles_extra += self.create_style_color(color)
            return "<text:span text:style-name=\"%s\">%s</text:span>" % ("shorte_span_color_%s" % color, replace)
        # Don't fully support span yet, need to figure out a way to support it
        elif(tag == "span"):
            return "<text:span>%s</text:span>" % (replace)
        elif(tag == "hl"):
            return '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["highlight"], replace)

        return replace

    def xmlize(self, data):

        # Convert an < and > characters
        data = re.sub("&", "&amp;", data)
        data = re.sub("'", "&apos;", data)
        data = re.sub("’", "&apos;", data)
        data = re.sub("<", "&lt;", data)
        data = re.sub(">", "&gt;", data)

        data = re.sub("®", "&#174;", data)

        return data


    def format_text(self, data, allow_wikify=True, exclude_wikiwords=[]):

        # Trim leading and trailing whitespace
        data = data.strip()
        data = data.replace("\n", " ")
        data = re.sub("->", "#", data)
            
        # Convert an < and > characters
        data = re.sub("&", "&amp;", data)
        data = re.sub("'", "&apos;", data)
        data = re.sub("’", "&apos;", data)
        data = re.sub("<", "&lt;", data)
        data = re.sub(">", "&gt;", data)

        data = re.sub("®", "&#174;", data)
        
        # Hilite any text between **** **** 
        hiliter = re.compile("\*\*\*\*(.*?)\*\*\*\*", re.DOTALL)
        data = hiliter.sub("\\1", data)

        # Underline anything in <<<>>> brackets
        hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        data = hiliter.sub("\\1", data)
        
        # First make any links
        data = self._format_links(data)

        # Collapse multiple spaces
        data = re.sub("  +", " ", data)
        
        ## Now convert any [[[phrase]]] to highlighted text
        #highlight = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        #data = highlight.sub("<w:rPr><w:b/><w:highlight w:val=\"yellow\"/></w:rPr><w:t>\\1</w:t></w:r><w:r><w:t>", data)
        
        # First convert any underlines
        underline = re.compile("\*\*(.*?)\*\*")
        data = underline.sub("<text:span text:style-name=\"%s\">\\1</text:span>" % self.m_styles["underline"], data)

        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*")
        data = bold.sub("<text:span text:style-name=\"%s\">\\1</text:span>" % self.m_styles["bold"], data)

        data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
        data = re.sub("&lt;&lt;(.*?)&gt;&gt;", self.format_inline_image, data)
        
        # Convert any inline styling blocks
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)
        data = re.sub(' *<text:line-break/> *', '<text:line-break/>', data)

        if(allow_wikify):
            data = self.wikify(data)

        return data
    
    def format_questions(self, tag):    
        
        xml = ''
        questions = tag["contents"]

        for question in questions:

            if(question["answer"] != ""):
                xml += string.Template(
'''
<text:p text:style-name="$note"><text:span text:style-name="$bold">Q: </text:span>$question</text:p>
<text:p text:style-name="$note"><text:span text:style-name="$bold">A: </text:span>$answer</text:p>
<text:p text:style-name="shorte_spacer"></text:p>
''').substitute({"note" : self.m_styles["note"],
                 "bold" : self.m_styles["bold"],
                 "question" : question["question"],
                 "answer" : question["answer"]})

            else:
                xml += string.Template(
'''
<text:p text:style-name="$note"><text:span text:style-name="$bold">Q: </text:span>$question</text:p>
<text:p></text:p>
''').substitute({"note": self.m_styles["note"],
                 "bold": self.m_styles["bold"],
                 "question" : question["question"]})

        xml += '''<text:p></text:p>'''

        return xml

    def __table_get_style(self, name):

        table = {}
        table["title"] = {
                "cell" : "shorte_table.C1",
                "text" : "shorte_para_white_bold"
                }
        table["header"] = {
                "cell" : "shorte_table.B1",
                "text" : "ShorteHeaderText"
                }
        table["subheader"] = {
                "cell" : "shorte_table.subheader",
                "text" : "ShorteNormalText"
                }
        table["reserved"] = {
                "cell" : "shorte_table.reserved",
                "text" : "reserved"
                }
        table["default"] = {
                "cell" : "shorte_table.B2",
                "text" : "ShorteNormalText"
                }

        return table


    def __table_format_title(self, table, style):
        '''This is an internal method used to format the
           table title'''

        if('title' in table):
            odt = '''
<table:table-row>
    <table:table-cell table:style-name="%s" office:value-type="string" table:number-columns-spanned="%d">
        <text:p text:style-name="%s">%s</text:p>
    </table:table-cell>
</table:table-row>
''' % (style["title"]["cell"],
       table["max_cols"],
       style["title"]["text"],
       table["title"])
        else:
            odt = ''

        return odt

    def __table_format_column_styles(self, table, style, title):
        '''This is an internal method used to format the column
           styles section of the table'''

        if(table.has_key("column-styles")):
            col_styles = ''
            i = 0

            for col in range(0, table["max_cols"]):
                col_styles += ''' 
<table:table-column table:style-name="%s"/>
''' % table["column-styles"][i]
                i += 1
        else:
            col_styles = '''
<table:table-column table:style-name="%s" table:number-columns-repeated="%d"/>
''' % (self.m_styles["table"]["column"], table["max_cols"])
        
        
        odt = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
%s
%s
''' % (self.m_table_id, self.m_styles["table"]["style"], col_styles, title)

        return odt

    def __format_table_cell(self, col, style, cell_type, cell_text):

        if(cell_type == "is_header"):
            cell_style = style["header"]["cell"]
            text_style = style["header"]["text"]
        elif(cell_type == "is_subheader"):
            cell_style = style["subheader"]["cell"]
            text_style = style["subheader"]["text"]
        elif(cell_type in ("is_reserved", "is_crossed")):
            cell_style = style["reserved"]["cell"]
            text_style = style["reserved"]["text"]
        else:
            cell_style = style["default"]["cell"]
            if(col.has_key("style")):
                cell_style = col["style"]
            text_style = style["default"]["text"]
            if(col.has_key("text-style")):
                text_style = col["text-style"]


        xml = '''
          <table:table-cell table:style-name="%s" office:value-type="string" table:number-columns-spanned="%d">
            <text:p text:style-name="%s">%s</text:p>
          </table:table-cell>
''' % (cell_style,
       col["span"],
       text_style,
       cell_text)

        return xml

            
    def __format_table(self, source, table, format_text=True, table_style_name="default"):    
        '''This method is called to format the contents of a table and
           generate the XML output necessary for inserting into the ODT
           document'''
        
        xml = ''
        title = ''
        
        # get the style information associated with the style name
        style = self.__table_get_style(table_style_name)

        title = self.__table_format_title(table, style)
        xml += self.__table_format_column_styles(table, style, title)

        self.m_table_id += 1

        for row in table["rows"]:

            # Skip any embedded captions for now in ODT documents
            if(row["is_caption"]):
                continue
            
            xml += '''
    <table:table-row>
'''
            for col in row["cols"]:                     

                cell_text = col["text"]
                if(format_text):
                    cell_text = self.format_text(cell_text)

                #print "T.CELL: [%s]" % cell_text

                if(row["is_header"]):
                    xml += self.__format_table_cell(col, style, "is_header", cell_text)
                elif(row["is_subheader"]):
                    xml += self.__format_table_cell(col, style, "is_subheader", cell_text)
                elif(row["is_reserved"] or row["is_crossed"]):
                    xml += self.__format_table_cell(col, style, "is_reserved", cell_text)
                else:
                    xml += self.__format_table_cell(col, style, "default", cell_text)

            xml += "</table:table-row>\n"

        xml += "</table:table>"

        # If the table has a caption then output the caption
        if "caption" in table:
            xml += self.format_caption("Caption: %s" % table["caption"])

        #xml += "<text:p></text:p>"

        return xml
    
    def format_define(self, tag):
        
        define = tag["contents"]
        name   = self.format_text(define["name"])
        value  = self.format_text(define["value"])
        desc   = self.format_text(define["desc"])

        xml = '''
<text:p text:style-name="%s">%s = %s</text:p>
      <text:p text:style-name="%s">%s</text:p>
      <text:p text:style-name="%s"/>
''' % (self.m_styles["para"]["bold"],
       name, value,
       self.m_styles["para"]["normal"],
       desc,
       self.m_styles["para"]["normal"]
       )

        return xml
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|    format_struct()
    #|
    #| DESCRIPTION:
    #|    This method is called to format the contents of a table and generate
    #|    the XML output necessary for inserting into the word document.
    #| 
    #| PARAMETERS:
    #|    source (I) - The input table source to parse. 
    #| 
    #| RETURNS:
    #|    None.
    #|
    #+-----------------------------------------------------------------------------
    def format_struct(self, source, struct, style_name="default"):    
        
        xml = ''
        
        # get the style information associated with the style name
        style = self.__table_get_style(style_name)

        title = self.__table_format_title(struct, style)
        xml += self.__table_format_column_styles(struct, style, title)

        self.m_table_id += 1
            
        xml += '''<table:table-row>'''
        xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Type       ")
        xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Field Name")
        xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Description")
        xml += "</table:table-row>\n"

        for field in struct["fields"]:
            
            xml += '''
    <table:table-row>
'''
            for col in field["attrs"]:                     
                
                # DEBUG BRAD: cells for a structure are currently not formatted
                #             the same way as a table - need to convert them
                #             into a dictionary for the time being - need to fix
                #             this in future releases for easier maintainability.
                cell_text = self.format_text(col)

                #print "S.CELL: [%s]" % cell_text

                if(field["is_header"]):
                    xml += self.__format_table_cell({"span" : 1}, style, "is_header", cell_text)
                elif(field["is_subheader"]):
                    xml += self.__format_table_cell({"span" : 1}, style, "is_subheader", cell_text)
                elif(field["is_reserved"]):
                    xml += self.__format_table_cell({"span" : 1}, style, "is_reserved", cell_text)
                else:
                    xml += self.__format_table_cell({"span" : 1}, style, "default", cell_text)


            xml += "</table:table-row>\n"

        xml += "</table:table>"

        # If the table has a caption then output the caption
        if "caption" in struct:
            xml += self.format_caption("Caption: %s" % struct["caption"])

        return xml


    def format_enum(self, tag, style_name="default"):

        table = tag["contents"]
        
        
        if(self.m_engine.get_config("html", "show_enum_values") == "1"):
            show_enum_vals = True
            max_cols = table["max_cols"]
        else:
            show_enum_vals = False
            max_cols = table["max_cols"] - 1

        # get the style information associated with the style name
        style = self.__table_get_style(style_name)

        title = self.__table_format_title(table, style)


        if(show_enum_vals):
            xml = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
%s
''' % (self.m_table_id, self.m_styles["table"]["style"],
       "shorte_enum_col1",
       "shorte_enum_col2",
       "shorte_enum_col3",
       title)

        else:
            xml = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
%s
''' % (self.m_table_id, self.m_styles["table"]["style"],
       "shorte_enum_col1",
       "shorte_enum_col2",
       title)

        self.m_table_id += 1

        i = 0

        for row in table["rows"]:
            
            xml += '''
    <table:table-row>
'''
            col_index = 0

            for col in row["cols"]:

                is_header = True
                # Don't attempt to wikify or format the acronym name. Instead
                # create a link to it
                if(col_index == 0):
                    if(row["is_header"] or row["is_subheader"]):
                        text = col["text"]
                    else:
                        word = col["text"]
                        text = '''
<text:bookmark-start text:name="%s"/>
    <text:a xlink:type="simple" xlink:href="" office:name="%s">%s</text:a>
<text:bookmark-end text:name="%s"/>''' % (word, word, word, word)
                        #text = '<a name="%s"></a>%s' % (col["text"], col["text"])
                else:
                    text = self.format_text(col["text"])

                if(col_index == 1 and (not show_enum_vals)):
                    col_index += 1
                    continue

                colspan = col["span"]
                
                if(row["is_header"]):
                    xml += self.__format_table_cell(col, style, "is_header", text)

                elif(row["is_subheader"]):
                    xml += self.__format_table_cell(col, style, "is_subheader", text)
                else:   
                    xml += self.__format_table_cell(col, style, "default", text)

                col_index += 1
            
            xml += "</table:table-row>\n"

            i+=1

        xml += "</table:table>"
        
        if("caption" in table):
            xml += self.format_caption("Caption: %s" % table["caption"])
        
        return xml


    def format_acronyms(self, tag, style_name="default"):

        table = tag["contents"]
        
        # get the style information associated with the style name
        style = self.__table_get_style(style_name)

        title = self.__table_format_title(table, style)

        xml = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
%s
''' % (self.m_table_id, self.m_styles["table"]["style"],
       #self.m_styles["table"]["column"],
       "shorte_acronym_col1",
       "shorte_acronym_col2",
       title)

        self.m_table_id += 1

        i = 0

        for row in table["rows"]:
            
            xml += '''
    <table:table-row>
'''
            col_index = 0

            for col in row["cols"]:
                is_header = True
                # Don't attempt to wikify or format the acronym name. Instead
                # create a link to it
                if(col_index == 0):
                    if(row["is_header"] or row["is_subheader"]):
                        text = col["text"]
                    else:
                        word = col["text"]
                        text = '''
<text:bookmark-start text:name="%s"/>
    <text:a xlink:type="simple" xlink:href="" office:name="%s">%s</text:a>
<text:bookmark-end text:name="%s"/>''' % (word, word, word, word)
                        #text = '<a name="%s"></a>%s' % (col["text"], col["text"])
                else:
                    text = self.format_text(col["text"])

                colspan = col["span"]
                
                if(row["is_header"]):
                    xml += self.__format_table_cell(col, style, "is_header", text)
                elif(row["is_subheader"]):
                    xml += self.__format_table_cell(col, style, "is_subheader", text)
                else:
                    xml += self.__format_table_cell(col, style, "default", text)
                
                col_index += 1
            
            xml += "</table:table-row>\n"

            i+=1

        xml += "</table:table>"
        
        if("caption" in table):
            xml += self.format_caption("Caption: %s" % table["caption"])
        
        return xml


    def format_bold(self, input):

        xml = '''<text:p text:style-name="%s">%s</text:p>''' % (
            self.m_styles["para"]["bold"], input)

        return xml
    
    def format_textblock(self, tag):

        paragraphs = tag["contents"]

        xml = ''
        
        for p in paragraphs:
            indent  = p["indent"]
            text    = p["text"]
            is_code = p["code"]
            is_list = p["list"]

            if(p["text"] == ""):
                continue

            if(is_code):
                xml += self.format_pre(text, "code")
                xml += '<text:p text:style-name="shorte_spacer"></text:p>'
            elif(is_list):
                xml += self.format_list(p["text"], False)
            elif(indent > 0):
                xml += '''<text:p text:style-name="%s">%s</text:p>''' % (self.m_styles["para"]["indent"][0], self.format_text(text.strip()))
                xml += '<text:p text:style-name="shorte_spacer"></text:p>'
            else:
                xml += '''<text:p text:style-name="%s">%s</text:p>''' % (self.m_styles["para"]["normal"], self.format_text(text.strip()))
       
        return xml
    
    def format_pre(self, source, style="pre"):

        # Trim any trailing blank lines
        i = len(source) - 1
        while(i >= 0):
            if(source[i] == ' ' or
               source[i] == '\n' or
               source[i] == '\r'):
                i -= 1
            else:
                break

        end = i + 1
        i = 0


        text = ''

        #while i < end:
        #    if(source[i] == "\n"):
        #        #output += '</text:span></text:p><text:p text:style-name="%s"><text:span>' % (
        #        #        self.m_styles["para"][style])
        #        text += '<text:line-break/>'
        #    else:
        #        text += source[i]
        #    i += 1
        
        text = source
        text = self.wikify(text)
        text = text.replace("\n", "<text:line-break/>")
        
        output = '<text:p text:style-name="%s"><text:span text:style-name="%s">' % (
                self.m_styles["para"][style],
                self.m_styles["span"][style])
        output += text
        output += '</text:span>'
        output += '</text:p>'

        return output

    
    def format_caption(self, input):

        xml = '''<text:p text:style-name="%s">%s</text:p>''' % (self.m_styles["para"]["caption"], input)

        return xml

    def format_note(self, source):
        
        xml = '''
<text:p text:style-name="%s">Note:</text:p>
      <text:p text:style-name="%s">%s</text:p>
      <text:p text:style-name="%s"/>
''' % (self.m_styles["para"]["bold"],
       self.m_styles["para"]["note"],
       source,
       self.m_styles["para"]["normal"])

        return xml
    
    def format_tbd(self, tag):
        
        source = tag["contents"]
        xml = '''
<text:p text:style-name="%s">TBD:</text:p>
      <text:p text:style-name="%s">%s</text:p>
      <text:p text:style-name="%s"/>
''' % (self.m_styles["para"]["bold"],
       self.m_styles["para"]["note"],
       source,
       self.m_styles["para"]["normal"])

        return xml
    
    def format_question(self, source):
        
        xml = '''
<text:p text:style-name="%s">Question:</text:p>
      <text:p text:style-name="%s">%s</text:p>
      <text:p text:style-name="%s"/>
''' % (self.m_styles["para"]["bold"],
       self.m_styles["para"]["note"],
       source,
       self.m_styles["para"]["normal"])

        return xml
        
    
    def format_keywords(self, language, source, exclude_wikiwords=[]):

        keywords = self.m_engine.get_keyword_list(language)

        output = ''
        keyword = ''
        pos_start = 0

        #print "input = %s" % source

        for i in range(0, len(source)):

            c = source[i]

            #if((ord(c) >= 97 and ord(c) < 122) or (ord(c) == 95)):
            #    keyword += c 
            if((ord(c) >= 65 and ord(c) < 91) or (ord(c) >= 48 and ord(c) < 58) or (ord(c) >= 97 and ord(c) <= 122) or (ord(c) == 95) or (c == '.')):
                keyword += c 
            else:
                if(keyword != ''):
                    #print "  keyword1: {%s}" % keyword
                    #print "  substr:   {%s}" % source[pos_start:i]
                    if(keywords.has_key(keyword)):
                        #output += source[pos_start:i]
                        output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_keyword"], keyword)
                    else:
                        output += self.wikify(keyword, exclude_wikiwords)
                        #output += keyword

                    keyword = ''
                
                pos_start = i+1
                output += "%c" % c


        if(keyword != ''):
            #output += source[pos_start:i+1]
            if(keywords.has_key(keyword)):
                #output += source[pos_start:i]
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_keyword"], keyword)
            else:
                #output += keyword
                output += self.wikify(keyword, exclude_wikiwords)
            #print "  keyword2 = %s" % keyword

        #print "output = %s\n" % output

        return output
   

    def __replace_whitespace(self, matches):
        return '''<text:s text:c="%d"/>''' % len(matches.groups()[0])

    
    def format_source_code(self, language, tags, exclude_wikiwords=[], show_line_numbers=True, show_frame=True):

        line = 1

        output = ''

        if(show_frame):
            output = '<text:p text:style-name="%s">' % self.m_styles["para"]["code"]

        if(show_line_numbers):
            output += '<text:span text:style-name="%s">%04d </text:span>' % (self.m_styles["span"]["code_line_numbers"], line)
        
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
                source = self.format_keywords(language, source, exclude_wikiwords)
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code"], source)
            elif(type == TAG_TYPE_COMMENT or type == TAG_TYPE_MCOMMENT):
                source = re.sub("(^ +)", self.__replace_whitespace, source)
                #source.replace(" ", "<text:s text:c=\"1\"/>")
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_comment"], source)
            elif(type == TAG_TYPE_WHITESPACE):
                output += '<text:s text:c="1"/>'
            elif(type == TAG_TYPE_STRING):
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_string"], source)
            elif(type == TAG_TYPE_NEWLINE):
                line += 1
                output += '<text:line-break/>'
                
                if(show_line_numbers):
                    output += '<text:span text:style-name="%s">%04d </text:span>' % (self.m_styles["span"]["code_line_numbers"], line)
            
        if(show_frame):
            output += '</text:p>'

        return output
    
    
    def format_list_child(self, elem, style, level):

        source = ''
        if(elem.has_key("children")):
            source += '''<text:list-item>
               <text:p text:style-name="%s">%s</text:p>
               <text:list text:style-name="%s">''' % (
                   self.m_styles["para"]["list_level"][level], self.format_text(elem["text"]), style)
            
#            source += '''
#    <text:list-item>
#            <text:p text:style-name="%s">%s</text:p>
#    </text:list-item>
#''' % (
#                   self.m_styles["para"]["list_level"][level], self.format_text(elem["text"]))

            num_children = len(elem["children"])
            for i in range(0, num_children):
                source += self.format_list_child(elem["children"][i], style, level+1) 
            
            source += "</text:list></text:list-item>"
        else:
            source += '''
    <text:list-item>
        <text:p text:style-name="%s">%s</text:p>
    </text:list-item>
''' % (self.m_styles["para"]["list_level"][level], self.format_text(elem["text"]))

        return source
    
    def format_list(self, list, ordered=False):

        if(not ordered):
            style = self.m_styles["list"]["unordered"]
        else:
            style = self.m_styles["list"]["ordered"]

        source = "<text:list text:style-name=\"%s\">" % style
        
        
        for elem in list:
            source += self.format_list_child(elem, style, 1)

        source += '</text:list>'

        return source
    
    
    def format_checklist(self, tag):

        style = self.m_styles["list"]["unordered"]

        source = "<text:list text:style-name=\"%s\">" % style

        list = tag["contents"]

        for elem in list:

            check = ''

            source += '''<text:list-item>
  <text:p text:style-name="%s">%s%s</text:p>
</text:list-item>
''' % (self.m_styles["para"]["list_level"][1], check, elem["name"])

        source += '</text:list>'

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
            rt += " " + prototype[0]["data"]
            prototype.pop(0)
            prototype.pop(0)

        prototype = self.format_source_code("c", prototype, [], False, False)
        return (self.wikify(rt), prototype)

    def __format_summary(self, tag, summary_type):

        if(summary_type == "functions"):
            tags = self.m_engine.get_function_summary(tag)
            max_cols = 2
            col_styles = ["shorte_type_summary_col1",
                          "shorte_type_summary_col2"]
        elif(summary_type == "types"):
            tags = self.m_engine.get_types_summary(tag)
            max_cols = 2
            col_styles = ["shorte_type_summary_col1",
                          "shorte_type_summary_col2"]
        elif(summary_type == "testcases"):
            tags = self.m_engine.get_testcase_summary(tag)
            max_cols = 4 
            #col_styles = ["shorte_testcase_summary_col1",
            #              "shorte_testcase_summary_col2",
            #              "shorte_testcase_summary_col3",
            #              "shorte_testcase_summary_col4"]
            col_styles = ["shorte_type_summary_col2",
                          "shorte_type_summary_col2",
                          "shorte_type_summary_col2",
                          "shorte_type_summary_col2"]
        
        table = {}
        table["max_cols"] = max_cols
        table["column-styles"] = col_styles
        table["rows"] = []

        hierarchy = ''
    
        for tag in tags:
            obj = tag["contents"]

            style = self.m_styles["table"]["cell"]["fhier"]
            text_style = self.m_styles["para"]["fdesc"]

            if(summary_type == "testcases"):
                if(tag["category"] != hierarchy):
                    hierarchy = tag["category"]
                    row = self._table_row()

                    cols = []
                    cols.append({"span":max_cols, 'text': hierarchy, "style": style, "text-style": text_style})
                    row["cols"] = cols
                    table["rows"].append(row)
            else:
                if(tag["hierarchy"] != hierarchy):
                    hierarchy = tag["hierarchy"]
                    row = self._table_row()

                    cols = []
                    cols.append({"span":max_cols, 'text': hierarchy, "style": style, "text-style": text_style})
                    row["cols"] = cols
                    table["rows"].append(row)

            row = self._table_row()

            cols = []

            if(summary_type == "functions"):
                name = obj["function_name"]
                tmp = obj["function_prototype"]["parsed"]
                (returns, prototype) = self.htmlize_prototype(tmp)
            
                style = self.m_styles["table"]["cell"]["fname"]
                text_style = self.m_styles["para"]["fdesc"]
                cols.append({"span":1, 'text':returns,   "style": style, "text-style": text_style})
                cols.append({"span":1, 'text':prototype, "style": style, "text-style": text_style})
                row["cols"] = cols
                table["rows"].append(row)

                row = self._table_row()
                cols = []

                style = self.m_styles["table"]["cell"]["fdesc"]
                cols.append({"span":1, 'text':'', "style": style, "text-style": text_style})

                text_style = self.m_styles["para"]["fdesc"]
                function_desc = ''
                if(obj.has_key("function_desc")):
                    function_desc = obj["function_desc"]
                cols.append({"span":1, 'text':xmlize(function_desc), "style": style, "text-style": text_style})
            
            elif(summary_type == "types"):
                name = ''
                if(obj.has_key("title")):
                    name = obj["title"]
                text = self.wikify(name)

                style = self.m_styles["table"]["cell"]["fname"]
                text_style = self.m_styles["para"]["fdesc"]
                text_style_code = self.m_styles["para"]["code2"]

                cols.append({"span":1, 'text':tag["name"], "style": style, "text-style": text_style})
                cols.append({"span":1, 'text':text, "style" : style, "text-style": text_style})
                row["cols"] = cols
                table["rows"].append(row)

                row = self._table_row()
                cols = []

                style = self.m_styles["table"]["cell"]["fdesc"]
                cols.append({"span":1, 'text':'', "style": style, "text-style": text_style})

                desc = ''
                if(obj.has_key("caption")):
                    desc = obj["caption"]
                text_style = self.m_styles["para"]["fdesc"]
                cols.append({"span":1, 'text':self.xmlize(desc), "style": style, "text-style": text_style})
            elif(summary_type == "testcases"):

                name = obj["name"]
                duration = obj["duration"]

                style = "" #self.m_styles["table"]["cell"]["fname"]
                text_style = self.m_styles["para"]["cell_text"]
                text_style_code = "" #self.m_styles["para"]["code2"]

                style = "shorte_table_test2"
                cols.append({"span":1, 'text':self.wikify(name), "style": style, "text-style": text_style})
                style = "shorte_table_test"
                cols.append({"span":1, 'text':obj["status"], "style" : style, "text-style": text_style})
                cols.append({"span":1, 'text':duration, "style" : style, "text-style": text_style})
                cols.append({"span":1, 'text':self.format_text("[[->Status: %s]]" % name), "style": style, "text-style": text_style})

            row["cols"] = cols

            table["rows"].append(row)

        return self.__format_table("", table, False)

    def format_function_summary(self, tag):

        summary = self.__format_summary(tag, "functions")
        #print summary

        return summary

    def create_style_color(self, color):

        xml = '''
        <style:style style:name="shorte_span_color_%s" style:family="text">
            <style:text-properties fo:color="#%s"/>
        </style:style>
        ''' % (color, color)

        return xml

    
    def format_type_summary(self, tag):

        return self.__format_summary(tag, "types")

    def format_testcase_summary(self, tag):

        return self.__format_summary(tag, "testcases")

    def format_testcase(self, tag):

        testcase = tag["contents"]
        table = {}
        table["max_cols"] = 2
        table["column-styles"] = ["shorte_func_summary_col1", "shorte_func_summary_col2"]
        table["rows"] = []

        hierarchy = ''
    
        style = self.m_styles["table"]["cell"]["fhier"]
        text_style = self.m_styles["para"]["fdesc"]

        row = self._table_row()

        cols = []

        vars = {}
        vars["desc"] = "</text:p>" + self.format_textblock(testcase["desc"]) + "<text:p>"
        vars["name"] = testcase["name"]
        vars["status"] = testcase["status"]
            
        style = self.m_styles["table"]["cell"]["prototype_section"]
        text_style = self.m_styles["table"]["cell"]["prototype_section_text"]
        cols.append({"span":2, 'text':"Test Case: " + vars["name"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table["rows"].append(row)
        
        row = self._table_row()
        cols = []

        text_style = self.m_styles["para"]["normal"]
        style = self.m_styles["table"]["cell"]["fdesc"]
        cols.append({"span":1, 'text':'Status:', "style": style, "text-style": text_style})

        text_style = self.m_styles["para"]["normal"]
        cols.append({"span":1, 'text': vars["status"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table["rows"].append(row)

        row = self._table_row()
        cols = []

        style = self.m_styles["table"]["cell"]["fdesc"]
        cols.append({"span":1, 'text':'Desc:', "style": style, "text-style": text_style})

        text_style = self.m_styles["para"]["normal"]
        cols.append({"span":1, 'text': vars["desc"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table["rows"].append(row)
            
        return self.__format_table("", table, False)


    def format_prototype(self, tag):
        
        prototype = tag["contents"]
        
        file = "blah"
        function = {}
        function["function_name"] = prototype["function_name"]
        function["function_example"] = ''
        function["function_pseudocode"] = ''
        function["function_prototype"] = ''
        function["function_desc"] = ''
        function["function_params"] = ''
        function["function_returns"] = ''
        function["function_see_also"] = ''
        wikiwords = []
        wikiwords.append(function["function_name"])

        if(prototype.has_key("function_desc")):
            function["function_desc"] = self.xmlize(prototype["function_desc"])

        if(prototype.has_key("function_prototype")):
            language = prototype["function_prototype"]["language"]
            example = prototype["function_prototype"]["parsed"]
            function["function_prototype"] = self.format_source_code(language, example, wikiwords, False, False)

        if(prototype.has_key("function_params")):
            params = prototype["function_params"]

            table = {}
            table["max_cols"] = 4 
            table["rows"] = []


            param_template = string.Template("""
        <table:table-row table:style-name="$table_row_prototype">
          <table:table-cell table:style-name="$table_cell_prototype" office:value-type="string">
            <text:p text:style-name="$para_prototype_param"></text:p>
          </table:table-cell>
          <table:table-cell table:style-name="$table_cell_prototype" office:value-type="string">
            <text:p text:style-name="$para_prototype_param_name">${param_name}</text:p>
          </table:table-cell>
          <table:table-cell table:style-name="$table_cell_prototype" office:value-type="string">
            <text:p text:style-name="$para_prototype_param">[${param_io}]</text:p>
          </table:table-cell>
          <table:table-cell table:style-name="$table_cell_prototype" office:value-type="string">
            <text:p text:style-name="$para_prototype_param">${param_desc}</text:p>
          </table:table-cell>
        </table:table-row>
                        """)

            output = ''
            for param in params:
            
                row = {}
                row["is_header"] = False
                row["cols"] = []
                row["cols"].append(param["param_name"])
                row["cols"].append(param["param_io"])
                row["cols"].append("-")
                row["cols"].append(param["param_desc"])

                table["rows"].append(row)

                tmp = ''
                for val in param["param_desc"]:
                    if(len(val) == 2):
                        tmp += '''
                            <text:span text:style-name="%s">%s</text:span>
                            <text:span>%s</text:span>
                            <text:line-break/>
                        ''' % (self.m_styles["span"]["prototype"]["param_name"],
                               val[0],
                               self.format_text(val[1]))
                    else:
                        tmp += self.format_text(val)

                param["param_desc"] = tmp

                param["table_row_prototype"] = self.m_styles["table"]["row"]["prototype"]
                param["table_cell_prototype"] = self.m_styles["table"]["cell"]["prototype"]
                param["para_prototype_param"] = self.m_styles["para"]["prototype"]["param"]
                param["para_prototype_param_name"] = self.m_styles["para"]["prototype"]["param_name"]

                output += param_template.substitute(param)

            function["function_params"] = output
            #function["function_params"] = self.__format_table("", table)
            
            #print "output = %s" % output

        if(prototype.has_key("function_returns")):
        
            xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">Returns:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${param_style}">${function_returns}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "function_returns" : prototype["function_returns"],
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["function_returns"] = xml

        if(prototype.has_key("function_see_also")):
            xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">See Also:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${param_style}">${see_also}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "see_also" : self.format_text(prototype["function_see_also"]),
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["function_see_also"] = xml

        if(prototype.has_key("function_example")):

            language = prototype["function_example"]["language"]
            example = prototype["function_example"]["parsed"]

            example = self.format_source_code(language, example)

            xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">Example:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${param_style}">The following example demonstrates the usage of this method:</text:p>
            <text:p text:style-name="${param_style}"></text:p>
            ${example}
            <text:p text:style-name="${param_style}"></text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "example" : example,
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["function_example"] = xml
        
        
        if(prototype.has_key("function_pseudocode")):

            language = prototype["function_pseudocode"]["language"]
            example = prototype["function_pseudocode"]["parsed"]
            example = self.format_source_code(language, example)
        
            xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">Pseudocode:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${param_style}">The following pseudocode describes the implementation of this method:</text:p>
            <text:p text:style-name="${param_style}"></text:p>
            ${example} 
            <text:p text:style-name="${param_style}"></text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "example" : example,
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["function_pseudocode"] = xml


        topic = topic_t({"name"   : prototype["function_name"],
                         "file"   : file,
                         "indent" : 3});
        index.append(topic)

        
        template = string.Template("""
<table:table table:name="shorte_table_prototype_${id}" table:style-name="${style_table}">
        <table:table-column table:style-name="${style_col0}"/>
        <table:table-column table:style-name="${style_col1}"/>
        <table:table-column table:style-name="${style_col2}"/>
        <table:table-column table:style-name="${style_col3}"/>
        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section_name}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_name}">Function: ${function_name}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>

        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section_data}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_text}">${function_desc}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        
        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_section}">Prototype:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>

        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section_data}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_text}">${function_prototype}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>

        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_section}">Parameters:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>

        ${function_params}
        ${function_returns}
        ${function_example}
        ${function_pseudocode}
        ${function_see_also}
</table:table>
<text:p text:style-name="${style_para_normal}"></text:p>
""")

        function["style_table"] = self.m_styles["table"]["styles"]["prototype"]

        function["style_row"] = self.m_styles["table"]["row"]["prototype"]
        function["style_section"] = self.m_styles["table"]["cell"]["prototype_section"]
        function["style_section_name"] = self.m_styles["table"]["cell"]["prototype_name"]
        function["style_section_data"] = self.m_styles["table"]["cell"]["prototype"]

        function["style_para_name"] = self.m_styles["para"]["prototype"]["param_name2"]
        function["style_para_text"] = self.m_styles["para"]["prototype"]["text"]
        function["style_para_section"] = self.m_styles["para"]["prototype"]["section"]
        function["style_para_normal"] = self.m_styles["para"]["normal"]
        
        function["style_col0"] = self.m_styles["table"]["columns"]["prototype"][0]
        function["style_col1"] = self.m_styles["table"]["columns"]["prototype"][1]
        function["style_col2"] = self.m_styles["table"]["columns"]["prototype"][2]
        function["style_col3"] = self.m_styles["table"]["columns"]["prototype"][3]
        function["id"] = self.m_table_id
        self.m_table_id += 1

        xml = template.substitute(function)

        return xml


    
    def append_source_code(self, tag):

        output = ''

        output += self.format_source_code(tag["name"], tag["contents"])
        result = tag["result"]

        if(result != None):
            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            ws = re.compile(" ")
            nl = re.compile("\\\\n")

            result = lt.sub("&lt;", result)
            result = gt.sub("&gt;", result)
            result = nl.sub("__NEWLINE__", result)
        
            output += self.format_bold("Result:")
            output += self.format_pre(result)
        
        self.m_sections[0]["Headings"][self.m_header_id]["Content"] += output

    def format_sequence(self, tag):

        image = tag["contents"]
        output = self.format_image(image)
        output += self.__format_table("", tag["contents"]["html"])

        return output

    def append(self, tag):
        
        name = tag["name"]

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += "<text:p>%s</text:p>" % self.format_text(tag["contents"])
        elif(name in "text"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_textblock(tag)
        elif(name in "pre"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_pre(tag["contents"])
        elif(name == "note"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(self.format_text(tag["contents"]))
        elif(name == "tbd"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_tbd(tag)
        elif(name == "question"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_question(self.format_text(tag["contents"]))
        elif(name == "questions"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_questions(tag)
        elif(name == "table"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.__format_table(tag["source"], tag["contents"])
        elif(name == "ul"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag["contents"], False)
        elif(name == "ol"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag["contents"], True)
        elif(name == "checklist"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_checklist(tag)
        elif(name == "image"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_image(tag["contents"])
        elif(name == "struct"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_struct(tag["source"], tag["contents"])
        elif(name == "define"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_define(tag)
        elif(name == "prototype"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_prototype(tag)
        elif(name == "testcase"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_testcase(tag)
        elif(name == "testcasesummary"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_testcase_summary(tag)
        elif(name == "functionsummary"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_function_summary(tag)
        elif(name == "typesummary"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_type_summary(tag)
        elif(name == "acronyms"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_acronyms(tag)
        elif(name == "enum"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_enum(tag)
        elif(name == "sequence"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_sequence(tag)
        # These tags are not supported in OTD documents
        elif(name in ("imagemap", "embed", "input", "columns", "column", "endcolumns")):
            print "WARNING: %s tag not supported in ODT documents" % name
        else:
            print "Undefined tag: %s [%s]" % (name, tag["source"]); sys.exit(-1)
    

    def _doc_pages_to_xml(self):

        # Add the document body
        xml = ""
    
        for section in self.m_sections:
        
            margin_top = "735pt"
            
            for heading in section["Headings"]:

                header_type = ""

                postfix = ''
                if(heading.has_key("break_before") and True == heading["break_before"]):
                    #postfix = '_20_Break'
                    #if(heading["Type"] == HEADING1):
                    #    postfix = '_20_Break'
                    #else:
                    #    print "DO I GET HERE? heading = %d (%s)" % (heading["Type"], heading["Title"])
                    xml += '<text:p text:style-name="shorte_page_break"/>'


                if(heading["Type"] == HEADING1):
                    header_type = self.m_styles["headings"][HEADING1]
                elif(heading["Type"] == HEADING2):
                    header_type = "%s%s" % (self.m_styles["headings"][HEADING2], postfix)
                elif(heading["Type"] == HEADING3):
                    header_type = "%s%s" % (self.m_styles["headings"][HEADING3], postfix)
                elif(heading["Type"] == HEADING4):
                    header_type = "%s%s" % (self.m_styles["headings"][HEADING4], postfix)
                elif(heading["Type"] == HEADING_DEFAULT):
                    header_type = "Normal"
                else:
                    print "Unsupported heading type"
                    sys.exit(-1)

                xml += '''
<text:h text:style-name="%s" text:outline-level="%s">%s</text:h>
''' % (header_type, heading["Type"], heading["Title"])

                if(heading.has_key("Content")):
                    xml += heading["Content"]
        
        return xml
        

    def __load_template(self):
        
        handle = open(g_startup_path + "/templates/odt/%s.odt" % self.m_engine.get_theme(), "r")
        contents = handle.read()
        handle.close()
        return contents

    def __format_revision_history(self, tag, replace_paragraph=True):

        table = tag

        if(table != None):
            table["title"] = "Revision History"
            table["column-styles"] = ["shorte_type_summary_col2", "shorte_type_summary_col2", "shorte_type_summary_col2"]
            if(replace_paragraph):
                output = self.__format_table("", tag)
            else:
                output = "</text:p>" + self.__format_table("", tag) + "<text:p>"

            return output
        
        return ""


    def generate_index(self, title, theme, version):

        scratchdir = self.m_engine.get_config("shorte", "scratchdir")

        #print "Theme: %s" % self.m_engine.m_theme

        shutil.copy(g_startup_path + "/templates/odt/%s.odt" % (self.m_engine.m_theme), scratchdir + os.path.sep + 'odt')
       
        unzip_file_into_dir("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme), scratchdir + "/odt")

        os.unlink("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme))

        handle = open("%s/odt/content.xml" % scratchdir)
        xml = handle.read()
        handle.close()

        xml = re.sub("DOCUMENT_SHORTTITLE", self.get_title_short(), xml)
        xml = re.sub("DOCUMENT_TITLE", self.get_title(), xml)
        xml = re.sub("DOCUMENT_SUBTITLE", self.m_engine.get_subtitle(), xml)
        xml = re.sub("DOCUMENT_VERSION", self.m_engine.get_version(), xml)
        xml = re.sub("CURRENT_DATE", self.m_engine.get_date(), xml)
        xml = re.sub("DOCUMENT_NO", self.m_engine.get_doc_number(), xml)
        xml = re.sub("<text:p text:style-name=\"[A-Za-z0-9_]+\">DOCUMENT_REVISION_HISTORY</text:p>", self.__format_revision_history(self.m_engine.get_doc_revision_history()), xml)
        #xml = re.sub("DOCUMENT_REVISION_HISTORY", self.__format_revision_history(self.m_engine.get_doc_revision_history(), False), xml)

        pages = self._doc_pages_to_xml()

        # Insert the contents into the document
        str = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">[[INSERT_CONTENTS_HERE]]</text:h>'''
        pos = xml.find(str)
        start = pos
        end = pos + len(str)
        tmp = xml[0:start]
        tmp += pages
        tmp += xml[end:len(xml)]
        xml = tmp

        # Replace the automatic styles
        start = xml.find("<office:automatic-styles>")
        end   = xml.find("</office:automatic-styles>")

        prefix = xml[0:start+25]
        styles = xml[start+25:end]
        postfix = xml[end:]

        xml = prefix + styles + self.get_styles() + postfix

        xml = re.sub("__NEWLINE__", '\\\\n', xml)
        handle = open("%s/odt/content.xml" % scratchdir, "wt")
        handle.write(xml)
        handle.close()

        # Copy any pictures into the document archive
        #os.mkdir("scratch/Pictures")
        pictures = ""
        pictures_copied = {}
        for picture in self.m_pictures:

            if(pictures_copied.has_key(picture["src"])):
                continue
            else:
                shutil.copy(picture["src"], "%s/odt/Pictures/." % scratchdir)
                pictures += "<manifest:file-entry manifest:media-type=\"image/png\" manifest:full-path=\"Pictures/%s\"/>\n" % (picture["name"] + picture["ext"])
                pictures_copied[picture["src"]] = True

        handle = open("%s/odt/styles.xml" % scratchdir)
        xml = handle.read()
        handle.close()

        xml = re.sub("DOCUMENT_SHORTTITLE", self.get_title_short(), xml)
        xml = re.sub("DOCUMENT_TITLE", self.get_title(), xml)
        xml = re.sub("DOCUMENT_SUBTITLE", self.m_engine.get_subtitle(), xml, 0)
        xml = re.sub("DOCUMENT_VERSION", self.m_engine.get_version(), xml)
        xml = re.sub("CURRENT_DATE", self.m_engine.get_date(), xml)
        xml = re.sub("DOCUMENT_NO", self.m_engine.get_doc_number(), xml)
        handle = open("%s/odt/styles.xml" % scratchdir, "wt")
        handle.write(xml)
        handle.close()

        handle = open("%s/odt/META-INF/manifest.xml" % scratchdir)
        xml = handle.read()
        handle.close()

        xml = re.sub("</manifest:manifest>", "%s</manifest:manifest>" % pictures, xml)
        handle = open("%s/odt/META-INF/manifest.xml" % scratchdir, "wt")
        handle.write(xml)
        handle.close()

        #zip = "%s" % (self.m_engine.m_output_directory + "/" + self.get_index_name())
        pwd=os.getcwd()
        zipname = self.m_engine.m_output_directory + os.path.sep + self.get_index_name()
        zipper("%s%sodt%s" % (scratchdir, os.path.sep, os.path.sep), zipname)

        return xml
   

    def generate(self, theme, version, package):
        global g_startup_path

        scratchdir = self.m_engine.get_config("shorte", "scratchdir")
        
        try:
            shutil.rmtree(scratchdir + os.path.sep + 'odt')
        except:
            # Ignore errors
            errors = 0 
        
        os.makedirs(scratchdir + os.path.sep + 'odt')

        pages = self.m_engine.m_parser.get_pages()

        for page in pages:
            
            tags = page["tags"]

            for tag in tags:
            
                if(self.m_engine.tag_is_header(tag["name"])):
                    self.append_header(tag)
            
                elif(self.m_engine.tag_is_source_code(tag["name"])):
                    self.append_source_code(tag)
                else:
                    self.append(tag)

        # Now generate the document index
        self.generate_index(self.m_engine.get_title(), theme, version)

        # If we're generating an ODT document make sure we update
        # the table of contents
        pwd=os.getcwd()
        pwd = re.sub('\\\\', '/', pwd)

        if(sys.platform == "cygwin" or sys.platform == "win32"):
            startup_path = g_startup_path.replace("/cygdrive/c/", "C:\\")
            startup_path = startup_path.replace("/", "\\")
            path_oowriter = self.m_engine.get_config("shorte", "path.oowriter.win32")
        else:
            startup_path = g_startup_path
            path_oowriter = self.m_engine.get_config("shorte", "path.oowriter.linux")

        if(package == PACKAGE_TYPE_ODT):
            input = "%s" % (self.m_engine.get_output_dir() + "/" + self.get_index_name())
            input_path = input.replace("/cygdrive/c/", "C:\\")
            output = "%s.copy" % (input)
            cmd = "%s -nologo -nofirststartwizard -norestore -nodefault -headless -hidden -invisible -nolockcheck \"%s/templates/odt/convert_to_pdf.odt\" \"macro://convert_to_pdf/Standard.Module1.UpdateTOC(\\\"%s\\\")\"" % (path_oowriter, startup_path, input_path)
            print "output = %s, input = %s" % (input, output)

            for i in range(0, 5):
                try:
                    rc = os.system(cmd)
                    if(rc != 0):
                        print "Failed converting document, retrying"
                    else:
                        break
                except:
                    print "Failed converting document, retrying"

            shutil.move(output, input)
        
        if(package == PACKAGE_TYPE_PDF):
            input = self.m_engine.get_output_dir() + "/" + self.get_index_name()
            input = input.replace("/cygdrive/c/", "C:\\")
            input = input.replace("/", "\\")

            #print "INPUT = %s" % input

            params = "-nologo -nofirststartwizard -norestore -nodefault -headless -hidden -invisible -nolockcheck"
            params = "-nologo -nofirststartwizard -norestore -nodefault -headless -nolockcheck"

            cmd = "%s %s \"%s/templates/odt/convert_to_pdf.odt\" \"macro://convert_to_pdf/Standard.Module1.ConvertToPDF(\\\"%s\\\", \\\"1.0\\\", \\\"blah\\\")\"" % (path_oowriter, params, startup_path, input)
            print cmd
            os.system(cmd)
            
            #for i in range(0, 5):
            #    try:
            #        rc = os.system(cmd)
            #        if(rc != 0):
            #            print "Failed converting document, retrying"
            #        else:
            #            break
            #    except:
            #        print "Failed converting document, retrying"

