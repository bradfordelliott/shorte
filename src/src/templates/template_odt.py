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

from src.shorte_defines import *

import sys
sys.path.append("libs")
try:
    from PIL import Image
except:
    WARNING("Failed to load Image library. Try installing it using the command 'pip install Pillow'")

from src.shorte_defines import *
from template import *

EOL = "\r\n"

comment_style_c = 0
comment_style_python = 1
    

import sys, zipfile, os, os.path

def unzip_file_into_dir(file, dir):

    #print "unzip_file_into_dir\n"
    #print "  FILE: %s" % file
    #print "  DIR:  %s" % dir

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
            #print "  outfile = %s" % outfile
            outfile.write(zfobj.read(name))
            outfile.close()

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
        self.m_frame_id = 10

        self.m_styles = {}
        self.m_styles["note"] = "shorte_note"
        self.m_styles["bold"] = "bold"
        self.m_styles["highlight"] = "shorte_highlight"
        self.m_styles["strikethru"] = "shorte_strikethru"
        self.m_styles["underline"] = "shorte_underline"
        self.m_styles["italic"] = "shorte_italic"
        self.m_styles["table"] = {}
        self.m_styles["table"]["style"] = "shorte_table"
        self.m_styles["table"]["column"] = "shorte_table.A"
        self.m_styles["table"]["cell"] = {}
        self.m_styles["table"]["row"] = {}

        self.m_styles["para"] = {}

        self.m_styles["para"]["bold"] = "shorte_para_bold"
        self.m_styles["para"]["bold_underline"] = "shorte_para_bold_underline"
        self.m_styles["para"]["pre"] = "shorte_para_pre"
        self.m_styles["para"]["code2"] = "shorte_code"
        self.m_styles["para"]["caption"] = "Caption"
        self.m_styles["para"]["note"] = "shorte_para_note"
        self.m_styles["para"]["normal"] = "shorte_standard"
        self.m_styles["para"]["code"] = "shorte_code3"
        self.m_styles["para"]["spacer"] = "shorte_spacer"
        self.m_styles["para"]["list_level"] = {}
        self.m_styles["para"]["list_level"][0] = "para_list_level0"
        self.m_styles["para"]["list_level"][1] = "para_list_level1"
        self.m_styles["para"]["list_level"][2] = "para_list_level2"
        self.m_styles["para"]["list_level"][3] = "para_list_level3"
        self.m_styles["para"]["list_level"][4] = "para_list_level4"
        self.m_styles["para"]["list_level"][5] = "para_list_level5"
        self.m_styles["para"]["list_level"][6] = "para_list_level6"
        self.m_styles["para"]["list_level"][7] = "para_list_level7"
        
        self.m_styles["para"]["indent"] = {}
        self.m_styles["para"]["indent"][0] = "shorte_indent_0"
        
        # Styles for function/type summaries
        self.m_styles["para"]["summary_indent"] = {}
        self.m_styles["para"]["summary_indent"][0] = "shorte_summary_table_indent_0"
        
        self.m_styles["para"]["summary_list_level"] = {}
        self.m_styles["para"]["summary_list_level"][0] = "shorte_summary_list_level0"
        self.m_styles["para"]["summary_list_level"][1] = "shorte_summary_list_level1"
        self.m_styles["para"]["summary_list_level"][2] = "shorte_summary_list_level2"
        self.m_styles["para"]["summary_list_level"][3] = "shorte_summary_list_level3"
        self.m_styles["para"]["summary_list_level"][4] = "shorte_summary_list_level4"
        self.m_styles["para"]["summary_list_level"][5] = "shorte_summary_list_level5"
        self.m_styles["para"]["summary_list_level"][6] = "shorte_summary_list_level6"
        self.m_styles["para"]["summary_list_level"][7] = "shorte_summary_list_level7"

        self.m_styles["span"] = {}
        self.m_styles["span"]["pre"] = "shorte_code3"

        self.m_styles["span"]["code"] = "code"
        self.m_styles["span"]["code_keyword"] = "code_keyword"
        self.m_styles["span"]["code_line_numbers"] = "code_line_numbers"
        self.m_styles["span"]["code_comment"] = "code_comment"
        self.m_styles["span"]["code_comment_tag"] = "code_comment_tag"
        self.m_styles["span"]["code_preprocessor"] = "code_preprocessor"
        self.m_styles["span"]["code_string"] = "code_string"
        
        self.m_styles["list"] = {}
        self.m_styles["list"]["ordered"] = "shorte_ordered_list"
        self.m_styles["list"]["unordered"] = "shorte_unordered_list"
        
        
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
        #self.m_styles["headings"][HEADING1] = "shorte_heading_1"
        #self.m_styles["headings"][HEADING2] = "shorte_heading_2"
        #self.m_styles["headings"][HEADING3] = "shorte_heading_3"
        #self.m_styles["headings"][HEADING4] = "shorte_heading_4"
        #self.m_styles["headings"][HEADING5] = "shorte_heading_5"
        #self.m_styles["headings"][HEADING6] = "shorte_heading_6"
        self.m_styles["headings"][HEADING1] = "Heading_20_1"
        self.m_styles["headings"][HEADING2] = "Heading_20_2"
        self.m_styles["headings"][HEADING3] = "Heading_20_3"
        self.m_styles["headings"][HEADING4] = "Heading_20_4"
        self.m_styles["headings"][HEADING5] = "Heading_20_5"
        self.m_styles["headings"][HEADING6] = "Heading_20_6"

        self.m_styles_extra = ''
        self.m_table_id = 0
        
        
        scratchdir = shorte_get_config("shorte", "scratchdir")
        
        try:
            shutil.rmtree(scratchdir + os.path.sep + 'odt')
        except:
            # Ignore errors
            errors = 0 
        
        os.makedirs(scratchdir + os.path.sep + 'odt')

        template_file = shorte_get_startup_path() + "/templates/odt/%s.odt" % (self.m_engine.m_theme)
        #print "TEMPLATE_FILE: %s" % template_file
        #print "OUTPUT DIR: %s" % scratchdir + os.path.sep + 'odt'
        shutil.copy(template_file, scratchdir + os.path.sep + 'odt')
       
        unzip_file_into_dir("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme), scratchdir + "/odt/.")

        os.unlink("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme))

        handle = open("%s/odt/content.xml" % scratchdir)
        xml = handle.read()
        handle.close()

        self.extract_styles(xml);

        # For tracking custom column styles
        self.m_column_styles = {}
        self.m_unique_col_id = 0

    def get_styles(self):
        path = shorte_get_startup_path() + "/templates/odt/"
        if(not path in sys.path):
            sys.path.append(path)
    
        module = shorte_get_startup_path() + "/templates/odt/%s.py" % (self.m_engine.m_theme)
        basename = os.path.basename(module)
        module = os.path.splitext(basename)[0]
        import_str = "from templates.odt.%s import *" % module
        #print "IMPORT_STR: %s" % import_str
        exec(import_str)
        
        custom_styles = custom_styles()

        doc_styles = {}
        doc_styles["outline"] = custom_styles.outline_styles()
        doc_styles["custom"] = custom_styles.custom_styles() + '''
    <style:style style:name="shorte_table.A" style:family="table-column">
      <style:table-column-properties style:column-width="3.25in" style:rel-column-width="32767*"/>
    </style:style>
    <style:style style:name="shorte_table.A1" style:family="table-cell">
      <style:table-cell-properties
        fo:background-color="#c0c0c0"
        fo:padding="0.0182in"
        fo:border-left="0.008in solid #C0C0C0"
        fo:border-right="none"
        fo:border-top="0.008in solid #C0C0C0"
        fo:border-bottom="0.008in solid #C0C0C0">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.A2" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0182in"
          fo:border-left="0.008in solid #C0C0C0" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.008in solid #C0C0C0"/>
    </style:style>

    <style:style style:name="shorte_table_rounded.top_left" style:family="table-cell">
        <style:table-cell-properties style:vertical-align="middle" fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_blue.png" xlink:type="simple" xlink:actuate="onLoad" style:position="top left" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.top_center_first" style:family="table-cell">
        <style:table-cell-properties style:vertical-align="middle" fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_blue.png" xlink:type="simple" xlink:actuate="onLoad" style:position="top center" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.top_center" style:family="table-cell">
        <style:table-cell-properties style:vertical-align="middle" fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="0.05pt solid #c0c0c0" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_blue.png" xlink:type="simple" xlink:actuate="onLoad" style:position="top center" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.top_right" style:family="table-cell">
        <style:table-cell-properties style:vertical-align="middle" fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_blue.png" xlink:type="simple" xlink:actuate="onLoad" style:position="top right" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>

    <style:style style:name="shorte_table_rounded.center_left" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.3cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_left_right.png" xlink:type="simple" xlink:actuate="onLoad" style:position="center left" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.center_center_first" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.3cm" fo:border-left="none" fo:border-right="none" fo:border-top="0.05pt solid #c0c0c0" fo:border-bottom="0.05pt solid #c0c0c0">
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.center_center" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.3cm" fo:border-left="0.05pt solid #c0c0c0" fo:border-right="none" fo:border-top="0.05pt solid #c0c0c0" fo:border-bottom="0.05pt solid #c0c0c0">
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.center_right" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.3cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.05pt solid #c0c0c0">
            <style:background-image xlink:href="Pictures/table_left_right.png" xlink:type="simple" xlink:actuate="onLoad" style:position="center right" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>

    <style:style style:name="shorte_table_rounded.bottom_left" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.0cm" fo:border="none">
            <style:background-image xlink:href="Pictures/table_white.png" xlink:type="simple" xlink:actuate="onLoad" style:position="bottom left" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.bottom_center_first" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="none">
            <style:background-image xlink:href="Pictures/table_white.png" xlink:type="simple" xlink:actuate="onLoad" style:position="bottom center" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.bottom_center" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="0.05pt solid #c0c0c0" fo:border-right="none" fo:border-top="none" fo:border-bottom="none">
            <style:background-image xlink:href="Pictures/table_white.png" xlink:type="simple" xlink:actuate="onLoad" style:position="bottom center" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_rounded.bottom_right" style:family="table-cell">
        <style:table-cell-properties fo:background-color="transparent" fo:padding="0.0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="none">
            <style:background-image xlink:href="Pictures/table_white.png" xlink:type="simple" xlink:actuate="onLoad" style:position="bottom right" style:repeat="no-repeat"/>
        </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table_rounded.column_edge" style:family="table-column">
      <style:table-column-properties style:column-width="2.51cm" style:rel-column-width="1600*"/>
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
      <style:paragraph-properties fo:margin-top="0in" fo:padding-top="0in" fo:padding-bottom="0in" fo:margin-bottom="0in"/>
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

    <style:style style:name="reserved" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#C0C0C0"/>
    </style:style>

    
    <style:style style:name="shorte_para_white_bold" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#ffffff" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>

    <style:style style:name="shorte_frame_note" style:family="graphic" style:parent-style-name="Graphics">
        <style:graphic-properties style:run-through="foreground" style:wrap="run-through" style:number-wrapped-paragraphs="no-limit" style:vertical-pos="from-top" style:vertical-rel="paragraph" style:horizontal-pos="from-left" style:horizontal-rel="paragraph" style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)" draw:luminance="0%" draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%" draw:color-inversion="false" draw:image-opacity="100%" draw:color-mode="standard"/>
    </style:style>
    
    <style:style style:name="fr2" style:family="graphic" style:parent-style-name="Graphics">
        <style:graphic-properties style:run-through="foreground" style:wrap="run-through" style:number-wrapped-paragraphs="no-limit" style:vertical-pos="from-top" style:vertical-rel="paragraph" style:horizontal-pos="from-left" style:horizontal-rel="paragraph" style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)" draw:luminance="0%" draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%" draw:color-inversion="false" draw:image-opacity="100%" draw:color-mode="standard"/>
    </style:style>

    <style:style style:name="shorte_para_bold" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    
    <style:style style:name="shorte_para_bold_underline" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
    </style:style>

    <style:style style:name="shorte_para_note" style:family="paragraph" style:parent-style-name="Standard">
        <style:paragraph-properties fo:margin-left="0.554cm" fo:margin-right="0cm" fo:text-indent="0cm" style:auto-text-indent="false" fo:background-color="#e0e0e0" fo:padding="0.002cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="none" style:shadow="none">
            <style:background-image/>
        </style:paragraph-properties>
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
    
    <style:style style:name="shorte_struct_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="1400*"/>
    </style:style>
    <style:style style:name="shorte_struct_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="2600cm*"/>
    </style:style>
    <style:style style:name="shorte_struct_col3" style:family="table-column">
    <style:table-column-properties style:rel-column-width="4200*"/>
    </style:style>
    
    
    <style:style style:name="shorte_acronym_col1" style:family="table-column">
    <style:table-column-properties style:rel-column-width="2000*"/>
    </style:style>
    <style:style style:name="shorte_acronym_col2" style:family="table-column">
    <style:table-column-properties style:rel-column-width="5000*"/>
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
    
    <style:style style:name="shorte_summary_table_indent_0" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties
        fo:margin-left="0.1846in"
        style:auto-text-indent="false"
        fo:padding-top="0.0138in"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    
    <style:style style:name="shorte_summary_list_level1" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_1">
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level2" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_2">
      <style:paragraph-properties fo:margin-left="0.5in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level3" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_3">
      <style:paragraph-properties fo:margin-left="0.7in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level4" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_4">
      <style:paragraph-properties fo:margin-left="0.9in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level5" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_5">
      <style:paragraph-properties fo:margin-left="1.1in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level6" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_6">
      <style:paragraph-properties fo:margin-left="1.3in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="shorte_summary_list_level7" style:family="paragraph" style:parent-style-name="Standard" style:list-style-name="List_20_7">
      <style:paragraph-properties fo:margin-left="1.5in" fo:margin-right="0in" fo:text-indent="-0.1575in" style:auto-text-indent="false"/>
      <style:text-properties fo:color="#A0A0A0" style:font-name="Times New Roman" fo:font-size="9pt"/>
    </style:style>

    
    <style:style style:name="shorte_page_break" style:family="paragraph" style:parent-style-name="Standard">
        <style:paragraph-properties fo:break-after="page"/>
    </style:style>
    
    <style:style style:name="shorte_highlight" style:family="text">
        <style:text-properties fo:background-color="#ffff00"/>
    </style:style>
    
    <style:style style:name="shorte_strikethru" style:family="text"><style:text-properties style:text-line-through-style="solid"/>
    </style:style>
    
<style:style style:name="T8" style:family="text">
      <style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color" fo:font-weight="bold" officeooo:rsid="000885f5" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>

    <style:style style:name="Frame_20_contents" style:display-name="Frame contents" style:family="paragraph" style:parent-style-name="Standard" style:class="extra"/>

    <style:style style:name="shorte_note_frame" style:family="graphic" style:parent-style-name="Frame">
      <style:graphic-properties style:vertical-pos="top" style:vertical-rel="paragraph-content" style:horizontal-pos="left" style:horizontal-rel="paragraph" fo:background-color="#f8f7cf" style:background-transparency="0%" draw:fill="solid"
        fo:border-left="0.002cm solid #e0e0e0"
        fo:border-bottom="0.002cm solid #e0e0e0"
        fo:border-top="0.002cm solid #e0e0e0"
        fo:border-right="0.002cm solid #e0e0e0"
      >
        <style:background-image/>
      </style:graphic-properties>
    </style:style>

<!-- This style is used to inline images such as the star icon inline with a particular character -->
<style:style style:name="fr_inline" style:family="graphic" style:parent-style-name="Graphics">
    <style:graphic-properties style:run-through="background" style:wrap="run-through"
        style:number-wrapped-paragraphs="no-limit" style:vertical-pos="from-top"
        style:vertical-rel="char" style:horizontal-pos="from-left"
        style:horizontal-rel="char" fo:background-color="transparent"
        style:background-transparency="100%" draw:fill="solid" style:shadow="none"
        style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)" draw:luminance="0%"
        draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%"
        draw:color-inversion="false" draw:image-opacity="100%"
        draw:color-mode="standard"><style:background-image/>
    </style:graphic-properties>
</style:style>

<!-- This style is used to generate notes, TBD's and warnings -->
<style:style style:name="fr_note" style:family="graphic" style:parent-style-name="Frame">
    <style:graphic-properties fo:margin-left="0.5cm" fo:margin-right="0cm" fo:margin-top="0cm"
        fo:margin-bottom="0cm" style:vertical-pos="top" style:vertical-rel="baseline" style:horizontal-pos="center"
        style:horizontal-rel="paragraph-content" fo:background-color="#ffffcc" style:background-transparency="0%"
        draw:fill="solid" fo:padding-left="0.101cm" fo:padding-right="0.101cm" fo:padding-top="0cm"
        fo:padding-bottom="0.101cm" fo:border="0.06pt solid #b2b2b2" style:shadow="none"
        draw:shadow-opacity="100%"><style:background-image/>
    </style:graphic-properties>
</style:style>

<style:style style:name="fr_note_img" style:family="graphic" style:parent-style-name="Graphics">
    <style:graphic-properties style:wrap="run-through" style:number-wrapped-paragraphs="no-limit" style:vertical-pos="from-top"
        style:vertical-rel="frame" style:horizontal-pos="from-left" style:horizontal-rel="frame"
        fo:background-color="transparent" style:background-transparency="100%" draw:fill="solid"
        style:shadow="none" draw:shadow-opacity="100%" style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)"
        draw:luminance="0%" draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%"
        draw:gamma="100%" draw:color-inversion="false" draw:image-opacity="100%"
        draw:color-mode="standard"><style:background-image/>
    </style:graphic-properties>
</style:style>

<style:style style:name="fr_inline_table" style:family="graphic" style:parent-style-name="Graphics">
    <style:graphic-properties style:vertical-pos="from-top" style:vertical-rel="paragraph"
    style:horizontal-pos="from-left"
    style:horizontal-rel="paragraph" style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)" draw:luminance="0%"
    draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%" draw:color-inversion="false"
    draw:image-opacity="100%" draw:color-mode="standard"/>
</style:style>

    
    ''' + self.m_styles_extra
        
        for style in self.m_column_styles:
            doc_styles["custom"] += self.m_column_styles[style]

        return doc_styles
                   
    def format_wikiword(self, wikiword, link_word):
        '''This method is called to format a wikiword. It is called by
           the wikify method in the template base class'''

        #if("width" in label):
        #print "WIKIWORD: [%s]" % label

        label = self.xmlize(wikiword.label)
        link_word = self.xmlize(wikiword.label)
        is_bookmark = wikiword.is_bookmark

        if(is_bookmark):
            tmp = '''<text:a xlink:type="simple" xlink:href="#%s" office:name="%s">%s</text:a>''' % (link_word, label, label)
        else:
            tmp = '''<text:a xlink:type="simple" xlink:href="#%s|outline" office:name="%s">%s</text:a>''' % (link_word, label, label)

        output = '''<text:span text:style-name="hyperlink">%s</text:span>''' % tmp
        
        return output

    def insert_inline_image(self, x, y, height, width, src):
        self.m_image_id += 1
        return '''<draw:frame draw:style-name="fr_inline" draw:name="graphics%d" text:anchor-type="char" svg:x="%fcm" svg:y="%fcm" svg:width="%fcm" svg:height="%fcm" draw:z-index="22">
                   <draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
               </draw:frame>''' % (self.m_image_id+10, x, y, width, height, src)


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
        title = title.replace("®", "&#174;")
        title = title.replace("Cortina Systems", "")
        title = title.strip()
        return title

    def get_footer_title(self):
        title = self.m_engine.get_doc_info().footer_title()
        title = title.replace("©", "")
        title = title.replace("®", "&#174;")
        title = title.strip()
        return title
    
    def get_footer_subtitle(self):
        title = self.m_engine.get_doc_info().footer_subtitle()
        title = title.replace("©", "")
        title = title.replace("®", "&#174;")
        title = title.strip()
        return title

    
    def append_page(self, pages, title, source_file):

        return ""

    def append_header(self, tag):

        name = tag.name
        data = tag.contents
        break_before = False

        if(tag.break_before):
            break_before = tag.break_before
        elif(tag.is_prototype):
            break_before = int(shorte_get_config("odt", "prototype_break_before"))

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
        
        elif(name == "h5"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING5
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)
        
        elif(name == "h"):
            heading = {}
            heading["Title"] = data
            heading["Type"] = HEADING6
            heading["Content"] = ""
            heading["break_before"] = break_before
            self.m_header_id += 1

            self.m_sections[0]["Headings"].append(heading)

    def unxmlize(self, xml):
        xml = xml.replace("&amp;", "&")
        xml = xml.replace("&apos;", "'")
        xml = xml.replace("&lt;", "<")
        xml = xml.replace("&gt;", ">")
        xml = xml.replace("&quot;", '"') 

        return xml
    
    def _expand_links(self, matches):

        (source, label, external) = self._process_link(matches)

        if(source.startswith("#")):
            temp = source[1:]
            if(self.m_engine.is_wiki_word(temp)):
                return temp

        # DEBUG BRAD: This is a temporary hack to get links of the format -> to work
        source = re.sub(".*?#(.*)", "\\1", source)
        label = re.sub(".*?#(.*)", "\\1", label)
        #print "SOURCE = %s, LABEL = %s" % (source, label)
        #source.replace("-&amp;gt;", "")
        #label = label.replace("-&gt;", "")

        # Unconvert any XML in case it has already been
        # converted by format_text()
        label = self.unxmlize(label)

        # Now make the label XML safe again
        label = self.xmlize(label)

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
        label = self.xmlize(label)
        
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
       
    def format_object_section_title(self, title):
        xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">${title}:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        ''').substitute({"row_style"     : self.m_styles["table"]["row"]["prototype_section"],
                         "cell_style"    : self.m_styles["table"]["cell"]["prototype_section"],
                         "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
                         "title"         : title})

        return xml
    
    def format_object_construct(self, obj, construct, format_as_table_row=False, show_title=True):
        xml = ''
        title = construct.title()

        if(construct == "example"):
            if(obj.example != None):
                language = obj.example.get_language()
                example  = obj.example.get_parsed()
                example  = self.format_source_code(language, example)

                xml = string.Template('''
            <text:p text:style-name="${param_style}">The following example demonstrates the usage of this method:</text:p>
            <text:p text:style-name="${param_style}"></text:p>
            ${example}
            <text:p text:style-name="${param_style}"></text:p>
''').substitute({
    "example" : example,
    "param_style" : "ShorteNormalText"
    })
        elif(construct == "since"):
            if(obj.has_since()):
                xml = self.format_textblock(obj.get_since())
        
        elif(construct == "deprecated"):
            if(obj.has_deprecated()):
                xml = self.format_textblock(obj.get_deprecated())
        
        elif(construct == "requires"):
            if(obj.has_requirements()):
                xml = self.format_textblock(obj.get_requirements())

        elif(construct == 'see'):
            if(obj.has_see_also()):
                style = self.m_styles["para"]["prototype"]["param"]
                xml = '<text:p text:style-name="%s">%s</text:p>' % (style, self.format_text(obj.get_see_also()))

        elif(construct == 'description'):
            if(obj.has_description()):
                xml = self.format_textblock(obj.get_description())
                
        if(len(xml) > 0 and format_as_table_row):
            xml_title = ''
            if(show_title):
                xml_title = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">${title}:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({"row_style" : self.m_styles["table"]["row"]["prototype_section"],
                 "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
                 "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
                 "title" : title})

            xml = string.Template('''
        ${xml_title}
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            ${xml}
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "xml"           : xml,
    "xml_title"     : xml_title,
    "row_style"     : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style"    : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2"   : self.m_styles["table"]["cell"]["prototype"],
    "param_style"   : self.m_styles["para"]["prototype"]["param"]
    })

        return xml

    def format_image(self, image):
        
        # Check to see if the image requires conversion such as
        # is the case with inkscape SVG files
        if(image.has_key("converter")):
            image = self.m_engine.convert_image(image)

        #print "image: [%s]" % image["src"]

        if(image.has_key("height") or image.has_key("width")):
            (image,height,width) = self.m_engine.scale_image(image)
        else:
            im = Image.open(image["src"])
            width = im.size[0]
            height = im.size[1]

        data = encode_image(image["src"])

        style = ""

        #print "width: %d" % width
        #print "height: %d" % height
        max_width = 700 #460.0
        max_height = 700 #640.0

        if(height > max_height):
            new_height = max_height
            new_width = (max_height/(1.0*height)) * width
            
            height = new_height
            width = new_width
        
        if(width > max_width):
            new_width = max_width
            new_height = (max_width/(1.0*width)) * height
            height = new_height
            width = new_width
        
        dpi = 96.0
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
<text:p text:style-name="shorte_standard_indented">
<draw:frame draw:style-name="fr_inline" draw:name="graphics%d" text:anchor-type="character" %s %s draw:z-index="0">
    <draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
</draw:frame>
</text:p>
%s
%s
""" % (tag_start, self.m_image_id+10, width, height, basename, caption, tag_end)
        
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

        #print data
        return data

    def format_inline_image(self, matches):

        image = self.m_engine.m_parser.parse_inline_image(matches)
        image["inline"] = True

        return self.format_image(image)

    def format_inline_image_str(self, data):
        image = self.m_engine.m_parser.parse_inline_image_str(data)
        image["inline"] = True
        return self.format_image(image)
        
    
    def parse_inline_styling(self, matches):
        data = matches.groups()[0].strip()
        parts = data.split(",")
        if(len(parts) == 1):
            tag = parts[0]
            replace = ''
        elif(len(parts) > 1):
            tag = parts[0]
            replace = ''.join(parts[1:])
        
        replace = trim_leading_blank_lines(replace)

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
                qualifier = parts[1].strip()

            if(tag in ("b","bold")):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["bold"]
                postfix += "</text:span>"
            elif(tag in ("u", "ul", "underline")):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["underline"]
                postfix += "</text:span>"
            elif(tag == "i"):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["italic"]
                postfix += "</text:span>"
            elif(tag == "br"):
                postfix += '<text:line-break/>'
            elif(tag == "pre"):
                replace = replace.rstrip(" \r\n")
                #print "PRE: [%s]" % replace
                output = "</text:p>"
                output += self.format_pre(replace, "pre")
                output += "<text:p text:style-name='shorte_standard'>"
                return output
            elif(tag == "color"):
                color = qualifier
                self.m_styles_extra += self.create_style_color(color)
                return "<text:span text:style-name=\"%s\">%s</text:span>" % ("shorte_span_color_%s" % color, replace)
            # Don't fully support span yet, need to figure out a way to support it
            elif(tag == "span"):
                return "<text:span>%s</text:span>" % (replace)
            elif(tag in ("hl", "hilite", "highlight")):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["highlight"]
                postfix += "</text:span>"
            elif(tag in ("done", "complete")):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["highlight"]
                postfix += "</text:span>"
            elif(tag in ("cross","strike")):
                prefix += "<text:span text:style-name=\"%s\">" % self.m_styles["strikethru"]
                postfix += "</text:span>"
            elif(tag in ("star", "starred")):
                prefix += self.insert_inline_image(x=-0.2, y=0.7, height=0.515, width=0.515, src="star_small.png")
                
            elif(tag in ("img", "image")):
                xml = self.format_inline_image_str(replace)
                return xml
                
            elif(tag == "table"):
                table = self.m_engine.m_parser.parse_table(replace, {}, col_separators=['!', '|'])
                #xml = "</text:p>"
                
                xml = ''
                xml = '''<draw:frame draw:style-name="fr_inline_table" draw:name="Frame%d" text:anchor-type="character" svg:x="0cm" svg:y="0cm" svg:width="12.088cm" draw:z-index="27">''' % (self.m_frame_id + 10)
                self.m_frame_id += 1
                xml += '''<draw:text-box>'''
        
                #print "REPLACE[%s]" % replace
                xml += self.__format_table(replace, table)

                xml += '''</draw:text-box>'''
                xml += '''</draw:frame>'''

                #xml += "<text:p text:style-name=\"shorte_standard\">"
                return xml

            # Embed an inline note. This is useful when documenting
            # source code.
            elif(tag in ("note", "warning", "tbd", "question")):
                # DEBUG BRAD:
                #   We've already converted breaks so we need to unconvert them
                #   to format the note properly. This needs to be done better.
                replace = replace.replace("&apos;", "'")
                replace = replace.replace("<text:line-break/>", "\n")
                xml = "</text:p>"
                textblock = textblock_t(replace)
                
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
                xml += self.format_note(textblock, type=tag, label=label, image=img)

                xml += "<text:p text:style-name=\"shorte_standard\">"
                return xml


        return prefix + replace + postfix

    def xmlize(self, data):

        # Convert an < and > characters
        data = re.sub("&", "&amp;", data)
        data = re.sub("'", "&apos;", data)
        #data = re.sub("", "&apos;", data)
        data = re.sub("<", "&lt;", data)
        data = re.sub(">", "&gt;", data)
        data = re.sub('"', "&quot;", data)

        data = re.sub("®", "&#174;", data)

        return data

    def xmlize(self, data):
        
        data = re.sub("", "&apos;", data)
        data = re.sub("", "&apos;", data)
        data = re.sub("®", "&#174;", data)

        output = ''
        STATE_NORMAL = 0
        STATE_INLINE_STYLING = 1
        state = STATE_NORMAL

        for i in range(0, len(data)):
            if(state == STATE_NORMAL):
                if(data[i] == '@' and data[i+1] == '{'):
                    output += data[i]
                    state = STATE_INLINE_STYLING
                    continue

                if(data[i] == '&'):
                    output += '&amp;'
                elif(data[i] == "'"):
                    output += '&apos;'
                elif(data[i] == '<'):
                    output += '&lt;'
                elif(data[i] == '>'):
                    output += '&gt;'
                elif(data[i] == '"'):
                    output += '&quot;'
                else:
                    output += data[i]

            else:
                if(data[i] == '}'):
                    state = STATE_NORMAL
                output += data[i]

        return output
                
        ## Convert an < and > characters
        #data = re.sub("&", "&amp;", data)
        #data = re.sub("'", "&apos;", data)
        ## Replace some characters that OpenOffice doesn't like in XML
        #data = re.sub("", "&apos;", data)
        #data = re.sub("", "&apos;", data)
        #data = re.sub("<", "&lt;", data)
        #data = re.sub(">", "&gt;", data)
        #data = re.sub('"', "&quot;", data)

        #data = re.sub("®", "&#174;", data)
       
        #return data

    def format_text(self, data, allow_wikify=True, exclude_wikiwords=[], expand_equals_block=False):

        # Trim leading and trailing whitespace
        data = data.strip()
        #data = re.sub("->", "#", data)
        
        # Replace any \\ with a single \
        if("\\" in data):
            data = re.sub(r"\\([^\\])", "\\1", data)

        data = self.xmlize(data)

        if(expand_equals_block):
            data = re.sub("\n\s*\n", "<text:line-break/><text:line-break/>", data)
            #data = re.sub("==+", "<text:line-break/><text:span>========================</text:span>", data)
            #data = re.sub("==+", "<text:line-break/><text:span>========================</text:span>", data)
            data = re.sub("===+", "<text:line-break/>====================<text:line-break/>", data)
        
        #data = data.replace("\n", " ")
        
        ## Hilite any text between **** **** 
        #hiliter = re.compile("\*\*\*\*(.*?)\*\*\*\*", re.DOTALL)
        #data = hiliter.sub("\\1", data)

        ## Underline anything in <<<>>> brackets
        #hiliter = re.compile("\<\<\<(.*?)\>\>\>", re.DOTALL)
        #data = hiliter.sub("\\1", data)
        

        # Collapse multiple spaces
        data = re.sub("  +", " ", data)
        
        # Now convert any [[[phrase]]] to highlighted text
        #highlight = re.compile("\[\[\[(.*?)\]\]\]", re.DOTALL)
        #data = highlight.sub("<w:rPr><w:b/><w:highlight w:val=\"yellow\"/></w:rPr><w:t>\\1</w:t></w:r><w:r><w:t>", data)
        
        # First convert any underlines
        underline = re.compile("__(.*?)__")
        data = underline.sub("<text:span text:style-name=\"%s\">\\1</text:span>" % self.m_styles["underline"], data)
        
        # Now convert any //phrase// to italics
        bold = re.compile("\/\/(.*?)\/\/")
        data = bold.sub("<text:span text:style-name=\"%s\">\\1</text:span>" % self.m_styles["italic"], data)
        
        # Now convert any *phrase* to bold
        bold = re.compile("\*(.*?)\*")
        data = bold.sub("<text:span text:style-name=\"%s\">\\1</text:span>" % self.m_styles["bold"], data)

        data = re.sub("<<(.*?),(.*?)(,(.*?))?>>", self.format_inline_image, data)
        data = re.sub("&lt;&lt;(.*?)&gt;&gt;", self.format_inline_image, data)
        
        # Convert any inline styling blocks
        expr = re.compile("@\{(.*?)\}", re.DOTALL)
        data = expr.sub(self.parse_inline_styling, data)
        data = re.sub(' *<text:line-break/> *', '<text:line-break/>', data)
        
        # First make any links
        data = self._format_links(data)
        
        if(allow_wikify):
            data = self.wikify(data)
        #print "FINAL: [%s]" % data


        return data
    
    def format_questions(self, tag):    
        
        xml = ''
        questions = tag.contents

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
<text:p text:style-name='shorte_standard'></text:p>
''').substitute({"note": self.m_styles["note"],
                 "bold": self.m_styles["bold"],
                 "question" : question["question"]})

        xml += '''<text:p text:style-name="shorte_standard"></text:p>'''

        return xml

    def __table_get_style(self, name):

        table = {}

        if(name == "default"):
            table["title"] = {
                    "cell" : "shorte_table.title",
                    "text" : "shorte_table_title" # "shorte_table.title_text"
                    }
            table["header"] = {
                    "cell" : "shorte_table.header",
                    "text" : "shorte_table_heading" # "shorte_table.header_text"
                    }
            table["subheader"] = {
                    "cell" : "shorte_table.subheader",
                    "text" : "shorte_table_subheading" # "shorte_table.normal_text"
                    }
            table["reserved"] = {
                    "cell" : "shorte_table.reserved",
                    "text" : "shorte_table_reserved" # "shorte_table.reserved_text"
                    }
            table["default"] = {
                    "cell" : "shorte_table.normal_cell",
                    "text" : "shorte_table_standard" # "shorte_table.normal_text"
                    }

            # For objects types like structure fields or
            # enum values.
            table["code_header"] = {
                    "cell" : "shorte_table.code_header",
                    "text" : "shorte_table_standard" # "shorte_table.normal_text"
                    }
            table["code_cell"] = {
                    "cell" : "shorte_table.code_cell",
                    "text" : "shorte_table_standard" # "shorte_table.normal_text"
                    }
            table["alternate_code_cell"] = {
                    "cell" : "shorte_table.alternate_code_cell",
                    "text" : "shorte_table_standard" # "shorte_table.normal_text"
                    }
        else:
            table["title"] = {
                    "cell" : "shorte_table.title",
                    "text" : "shorte_table_title_%s" % name
                    }
            table["header"] = {
                    "cell" : "shorte_table.header",
                    "text" : "shorte_table_heading_%s" % name
                    }
            table["subheader"] = {
                    "cell" : "shorte_table.subheader",
                    "text" : "shorte_table_subheading_%s" % name
                    }
            table["reserved"] = {
                    "cell" : "shorte_table.reserved",
                    "text" : "shorte_table_reserved_%s" % name
                    }
            table["default"] = {
                    "cell" : "shorte_table.normal_cell",
                    "text" : "shorte_table_standard_%s" % name
                    }

        return table


    def __table_format_title(self, table, style):
        '''This is an internal method used to format the
           table title'''

        if(table.has_title()):
            odt = '''
<table:table-row>
    <table:table-cell table:style-name="%s" office:value-type="string" table:number-columns-spanned="%d">
        <text:p text:style-name="%s">%s</text:p>
    </table:table-cell>
</table:table-row>
''' % (style["title"]["cell"],
       table.get_max_cols(),
       style["title"]["text"],
       table.get_title())
        else:
            odt = ''

        return odt
    
    def __table_format_column_styles(self, table, style, title):
        '''This is an internal method used to format the column
           styles section of the table'''

        if(table.table_style_name and table.table_style_name == "shorte_table_rounded"):
            col_styles = '''
<table:table-column table:style-name="shorte_table_rounded.column_edge" table:number-columns-repeated="1"/>
'''
        else:
            col_styles = ''

        if(table.has_column_styles()):
            col_styles = ''
            i = 0

            for col in range(0, table.get_max_cols()):
                col_styles += ''' 
<table:table-column table:style-name="%s"/>
''' % table.get_column_styles()[i]
                i += 1
        else:
            col_styles += '''
<table:table-column table:style-name="%s" table:number-columns-repeated="%d"/>
''' % (self.m_styles["table"]["column"], table.get_max_cols())
        
        if(table.table_style_name and table.table_style_name == "shorte_table_rounded"):
            col_styles += '''
<table:table-column table:style-name="shorte_table_rounded.column_edge" table:number-columns-repeated="1"/>
'''
        
        if(table.table_style_name and table.table_style_name == "shorte_table_rounded"):
            if(table.has_title()):
                table_title = self.format_bold(table.get_title)
            else:
                table_title = ''

            odt = '''
%s
<table:table table:name="shorte_table_%d" table:style-name="%s">
%s
''' % (table_title, self.m_table_id, self.m_styles["table"]["style"], col_styles)
        else:
            odt = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
%s
%s
''' % (self.m_table_id, self.m_styles["table"]["style"], col_styles, title)

        return odt

    def __format_table_cell(self, col, style, cell_type, cell_text, frame_paragraph=True):

        if(cell_type == "is_title"):
            cell_style = style["title"]["cell"]
            text_style = style["title"]["text"]
        elif(cell_type == "is_header"):
            cell_style = style["header"]["cell"]
            text_style = style["header"]["text"]
        elif(cell_type == "is_subheader"):
            cell_style = style["subheader"]["cell"]
            text_style = style["subheader"]["text"]
        elif(cell_type in ("is_reserved", "is_crossed")):
            cell_style = style["reserved"]["cell"]
            text_style = style["reserved"]["text"]
        else:
            cell_style = style[cell_type]["cell"]
            if(col.has_key("style")):
                cell_style = col["style"]
            text_style = style[cell_type]["text"]
            if(col.has_key("text-style")):
                text_style = col["text-style"]

        if(col.has_key("table_style") and col["table_style"] == "shorte_table_rounded"):
            if(col["row_index"] == 0):
                if(col["col_index"] == 0):
                    cell_style = "shorte_table_rounded.top_center_first"
                else:
                    cell_style = "shorte_table_rounded.top_center"

            elif(col["row_index"] == col["max_rows"]-1):
                if(col["col_index"] == 0):
                    cell_style = "shorte_table_rounded.bottom_center_first"
                else:
                    cell_style = "shorte_table_rounded.bottom_center"
            else:
                if(col["col_index"] == 0):
                    cell_style = "shorte_table_rounded.center_center_first"
                else:
                    cell_style = "shorte_table_rounded.center_center"

        if(frame_paragraph):
            xml = '''
          <table:table-cell table:style-name="%s" office:value-type="string" table:number-columns-spanned="%d">
            <text:p text:style-name="%s">%s</text:p>
          </table:table-cell>
''' % (cell_style,
       col["span"],
       text_style,
       cell_text)
        else:
            xml = '''
          <table:table-cell table:style-name="%s" office:value-type="string" table:number-columns-spanned="%d">
            %s
          </table:table-cell>
''' % (cell_style,
       col["span"],
       cell_text)


        return xml

    def add_column_styles(self, widths, title):
        '''This method is used to create new custom column styles
           to be added to the custom stylesheet

           @param widths [I] - The list of column widths
           @param title  [I] - The title associated with the table

           @return The table columns to insert into the document.
        '''
        total_width = 0
        for width in widths:
            total_width += width
        
        #print "Total width: %f" % total_width

        output = ''
        styles = ''
        col_index = 0
        for width in widths:
            style_name = "shorte_col%d_%d" % (self.m_unique_col_id, col_index)

            relative_width = (width/(total_width * 1.0)) * 1000
            #print "Relative width of %f: %f" % (width,relative_width)

            styles += '''
            <style:style style:name="%s" style:family="table-column">
                <style:table-column-properties style:rel-column-width="%fcm*"/>
            </style:style>
''' % (style_name, relative_width)
            
            output += '<table:table-column table:style-name="%s"/>' % style_name

            col_index += 1

        self.m_column_styles[self.m_unique_col_id] = styles

        self.m_unique_col_id += 1
            
        xml = '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
%s
%s
''' % (self.m_table_id, self.m_styles["table"]["style"], output, title)

        return xml


    def __format_table(self, source, table, format_text=True, table_style_name="default", extra_rows=''):    
        '''This method is called to format the contents of a table and
           generate the XML output necessary for inserting into the ODT
           document'''

        xml = ''
        title = ''
        self.m_table_id += 1

        # DEBUG BRAD: Uncomment this to test out the new rounded table support
        #table_style_name = "shorte_table_rounded"
        
        # get the style information associated with the style name
        if(table.has_style()):
            style = self.__table_get_style(table.get_style())
        else:
            style = self.__table_get_style(table_style_name)

        table.table_style_name = table_style_name
        
        #xml += self.format_caption("Caption: %s" % table["caption"])

        title = self.__table_format_title(table, style)

        if(table.has_widths()):
            xml += self.add_column_styles(table.get_widths(), title)
        else:
            xml += self.__table_format_column_styles(table, style, title)
        #xml += self.__table_format_column_styles(table, style, title)


        row_index = 0
        col_index = 0
        max_cols = table.get_max_cols()
        max_rows = table.get_num_rows()

        for row in table.get_rows():

            # Skip any embedded captions for now in ODT documents
            if(row["is_caption"]):
                continue
            
            xml += '''
    <table:table-row>
'''

            col_index = 0

            if(table_style_name == "shorte_table_rounded"):
                if(row_index == 0):
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.top_left" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''
                elif(row_index == (max_rows-1)):
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.bottom_left" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''
                else:
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.center_left" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''
            
            col_max = len(row["cols"])
            for col in row["cols"]:                     

                cell_text = ''
                if(col.has_key("text")):
                    cell_text = col["text"]

                frame_para = True
                if(col.has_key("textblock")):
                    tag = tag_t()
                    tag.contents = col["textblock"]

                    if(row["is_reserved"]):
                        cell_text = self.format_textblock(
                            tag,
                            style=style["reserved"]["text"])
                    elif(row.has_key("is_title") and row["is_title"]):
                        cell_text = self.format_textblock(
                            tag,
                            style=style["title"]["text"])
                    elif(row["is_header"]):
                        cell_text = self.format_textblock(
                            tag,
                            style=style["header"]["text"])
                    elif(row["is_subheader"]):
                        cell_text = self.format_textblock(
                            tag,
                            style=style["subheader"]["text"])
                    else:
                        cell_text = self.format_textblock(
                            tag,
                            style=style["default"]["text"])
                    frame_para = False

                #print "T.CELL: [%s]" % cell_text
                col["row_index"] = row_index
                col["col_index"] = col_index
                col["max_cols"] = max_cols
                col["max_rows"] = max_rows
                col["table_style"] = table_style_name

                col_index += col["span"]

                if(row.has_key("is_title") and row["is_title"]):
                    xml += self.__format_table_cell(col, style, "is_title", cell_text, frame_paragraph=frame_para)
                elif(row["is_header"]):
                    xml += self.__format_table_cell(col, style, "is_header", cell_text, frame_paragraph=frame_para)
                elif(row["is_subheader"]):
                    xml += self.__format_table_cell(col, style, "is_subheader", cell_text, frame_paragraph=frame_para)
                elif(row["is_reserved"] or row["is_crossed"]):
                    xml += self.__format_table_cell(col, style, "is_reserved", cell_text, frame_paragraph=frame_para)
                else:
                    xml += self.__format_table_cell(col, style, "default", cell_text, frame_paragraph=frame_para)
            
            if(table_style_name == "shorte_table_rounded"):
                if(row_index == 0):
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.top_right" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''
                elif(row_index == (max_rows-1)):
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.bottom_right" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''
                else:
                    xml += '''<table:table-cell table:style-name="shorte_table_rounded.center_right" office:value-type="string" table:number-columns-spanned="1"></table:table-cell>'''

            row_index += 1

            xml += "</table:table-row>\n"

        xml += extra_rows

        xml += "</table:table>"
        
        # If the table has a caption then output the caption
        if(table.has_caption()):
            xml += self.format_bold("Caption:")
            xml += self.format_textblock(table.get_caption(), style="shorte_standard_indented")


        #xml += "<text:p></text:p>"

        return xml
    
    def format_define(self, tag):

        define = tag.contents

        table = table_t()
        table.max_cols = 2
        table.title = "Define: %s" % define.name
        table.rows = []
        table.widths = [40,60]
        
        name   = self.format_text(define.name)
        value  = define.value
        desc   = define.get_description(textblock=True)

        style = "shorte_table.normal_cell"

        cols = []
        cols.append({"span":2, 'text': "Description:", "style": "shorte_table.header", "text-style": self.m_styles["para"]["bold"]})
        row = self._table_row()
        row["cols"] = cols
        table.rows.append(row)
        
        cols = []
        cols.append({"span":2, 'textblock': desc, "style": style, "text-style": "shorte_indent_0"})
        row = self._table_row()
        row["cols"] = cols
        table.rows.append(row)
        
        cols = []
        cols.append({"span":2, 'text': "Value:", "style": "shorte_table.header", "text-style": self.m_styles["para"]["bold"]})
        row = self._table_row()
        row["cols"] = cols
        table.rows.append(row)
        
        cols = []
        cols.append({"span":2, 'textblock': value, "style": style, "text-style": "shorte_indent_0"})
        row = self._table_row()
        row["cols"] = cols
        table.rows.append(row)
        
        extra_rows = ''
        
        obj_see_also = self.format_object_construct(define, 'see', True)
        if(len(obj_see_also) > 0):
            extra_rows += obj_see_also
        obj_since = self.format_object_construct(define, 'since', True)
        if(len(obj_since) > 0):
            extra_rows += obj_since

        return self.__format_table("", table, True, table_style_name='shorte_table_prototype', extra_rows=extra_rows)

        

        xml = string.Template('''
<text:p text:style-name="${style}">Description:</text:p>
${desc}
<text:p text:style-name="${style}">Value:</text:p>
<text:p text:style-name="${style}">$name = $value</text:p>
''').substitute({
    "style" : self.m_styles["para"]["bold"],
    "name"  : name,
    "value" : value,
    "desc"  : desc})

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
    def format_struct(self, tag, style_name="default"):    
        '''This method is called to format a structure definition
           into a block of open office text

           @param self       [I] - The class instance
           @param tag        [I] - The tag containing the structure object
           @param style_name [I] - The open office style

           @return The XML defining the structure
        '''

        source = tag.source
        struct = tag.contents
        label = tag.name.title()
        
        xml = ''

        # get the style information associated with the style name
        style = self.__table_get_style(style_name)

        table = table_t()
        table.title = "Structure: %s" % struct.get_name()
        table.max_cols = struct.get_max_cols()

        title = self.__table_format_title(table, style)
        xml += '''
<table:table table:name="shorte_table_%d" table:style-name="%s">
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
<table:table-column table:style-name="%s"/>
%s
''' % (self.m_table_id, "shorte_table_prototype", #self.m_styles["table"]["style"],
       "shorte_struct_col1",
       "shorte_struct_col2",
       "shorte_struct_col3",
       title)
        #xml += self.__table_format_column_styles(struct, style, title)

        self.m_table_id += 1
            
        xml += self.format_object_construct(struct, "description", True, show_title=False) 
        xml += self.format_object_section_title("Fields")

        xml += '''<table:table-row>'''
        xml += self.__format_table_cell({"span" : 1}, style, "code_header", "Field Type")
        xml += self.__format_table_cell({"span" : 1}, style, "code_header", "Field Name")
        xml += self.__format_table_cell({"span" : 1}, style, "code_header", "Description")
        xml += "</table:table-row>\n"
        

        i = 0
        for field in struct.get_fields():
            
            xml += '''
    <table:table-row>
'''
            if((i & 1) == 1):
                theme = "code_cell"
            else:
                theme = "alternate_code_cell"
            i += 1

            frame_paragraph = True
            if(field.get_is_spacer()):
                xml += self.__format_table_cell({"span" : 3}, style, theme, "", frame_paragraph)
            else:
                ftype = self.format_text(field.get_type())
                xml += self.__format_table_cell({"span" : 1}, style, theme, ftype, frame_paragraph)
                xml += self.__format_table_cell({"span" : 1}, style, theme, field.get_name(), frame_paragraph)

                desc = self.format_textblock(field.get_description())
                xml += self.__format_table_cell({"span" : 1}, style, theme, desc, False)

            xml += "</table:table-row>\n"
        
        xml += self.format_object_construct(struct, "example", True) 
        xml += self.format_object_construct(struct, "see", True) 
        xml += self.format_object_construct(struct, "since", True) 
        xml += self.format_object_construct(struct, "deprecated", True) 
        xml += self.format_object_construct(struct, "requires", True) 

        xml += "</table:table>"
        

        return xml


    def format_enum(self, tag, style_name="default"):
        '''This method is called to format an enum for display within an
           Open Office document.

           @param self       [I] - The template class instance
           @param tag        [I] - The tag defining the enum to convert to HTML.
           @param style_name [I] - The style to use to format the enum.

           @return The XML snippet defining the enum
        '''

        enum = tag.contents
        
        if(shorte_get_config("shorte", "show_enum_values") == "1"):
            show_enum_vals = True
            max_cols = enum.max_cols
        else:
            show_enum_vals = False
            max_cols = enum.max_cols - 1

        # get the style information associated with the style name
        style = self.__table_get_style(style_name)

        table = table_t()
        table.title = "Enum: " + enum.name
        table.max_cols = enum.max_cols

        title = self.__table_format_title(table, style)
        
        xml = ''

        xml += self.format_textblock(enum.description)

        if(show_enum_vals):
            table.widths = [30,10,50]

            xml += self.add_column_styles(table.get_widths(), title)
            xml += '''<table:table-row>'''
            xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Enum")
            xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Value")
            xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Description")
            xml += "</table:table-row>\n"

        else:
            table.widths = [30,70]
            xml += self.add_column_styles(table.get_widths(), title)

            xml += '''<table:table-row>'''
            xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Enum")
            xml += self.__format_table_cell({"span" : 1}, style, "is_header", "Description")
            xml += "</table:table-row>\n"

        self.m_table_id += 1

        i = 0
        

        for row in enum.values:
            
            # If this is the first row and it is a header
            # then skip it as it is likely just the table
            # header.
            if(i == 0 and row["is_header"]):
                i+=1
                continue
            
            xml += '''
    <table:table-row>
'''
            col_index = 0

            for col in row["cols"]:

                is_header = True

                # Normally we want to include the paragraph frame
                # around the cell text. However, if the text is a textblock
                # then we don't want to include this.
                frame_paragraph = True
            

                # Don't attempt to wikify or format the acronym name. Instead
                # create a link to it
                if(col_index == 0):
                    if(row["is_header"] or row["is_subheader"]):
                        text = self.xmlize(col["text"])
                    else:
                        word = self.xmlize(col["text"])
                        text = '''
<text:bookmark-start text:name="%s"/>
    <text:a xlink:type="simple" xlink:href="" office:name="%s">%s</text:a>
<text:bookmark-end text:name="%s"/>''' % (word, word, word, word)
                        #text = '<a name="%s"></a>%s' % (col["text"], col["text"])
                else:
                    if(col.has_key("textblock")):
                        text = self.format_textblock(col["textblock"])
                        frame_paragraph = False
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
                    xml += self.__format_table_cell(col, style, "default", text, frame_paragraph)

                col_index += 1
            
            xml += "</table:table-row>\n"

            i+=1

        xml += "</table:table>"
        
        
        return xml


    def format_acronyms(self, tag, style_name="default"):

        table = tag.contents
        
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

        for row in table.rows:
            
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
        
        if(table.has_caption()):
            xml += self.format_caption("Caption: %s" % table.get_caption())
        
        return xml


    def format_bold(self, input):

        xml = '''<text:p text:style-name="%s">%s</text:p>''' % (
            self.m_styles["para"]["bold"], input)

        return xml
    
    def format_textblock(self, tag,
        style="shorte_standard",
        indent_style="indent",
        list_style="list_level"):

        if(tag == None):
            return ''

        if(isinstance(tag, tag_t)):
            textblock = tag.contents
        else:
            textblock = tag

        if(isinstance(textblock, textblock_t)):
            paragraphs = textblock.paragraphs
        else:
            paragraphs = textblock

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
                #xml += '<text:p text:style-name="shorte_spacer"></text:p>'
            elif(is_list):
                xml += self.format_list(p["text"], False,list_style=list_style)
            elif(indent > 0):
                lcl_style = self.m_styles["para"][indent_style][0]
                xml += '''<text:p text:style-name="%s">%s</text:p>''' % (lcl_style, self.format_text(text.strip(), expand_equals_block=True))
            else:
                if(text.strip() != ""):
                    xml += '''<text:p text:style-name="%s">%s</text:p>''' % (style, self.format_text(text.strip(),expand_equals_block=True))
       
        # Strip any blank paragraphs that got added
        #xml = xml.replace("<text:p text:style-name=\"shorte_standard\"></text:p>", "<text:p text:style-name=\"shorte_standard\">empty2</text:p>")
        xml = xml.replace("<text:p text:style-name=\"shorte_standard\"></text:p>", "")

        #print "TEXTBLOCK\n[%s]" % xml
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
        
        text = self.xmlize(source)
        #text = source
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

    def format_note(self, tag, type="note", label="Note", image="note.png"):

        #print "format_note, image=%s, label=%s\n" % (image, label)

        # DEBUG BRAD: the @note is having an issue when you use an inline
        #             note in source code snippets as if you end up with
        #             a cross reference it ends up causing a corrupt document
        save_wikify = self.m_wikify
        self.m_wikify = False
        source = self.format_textblock(tag, style="shorte_standard")
        self.m_wikify = save_wikify

        xml = '''
<text:p text:style-name="shorte_standard">
    <draw:frame draw:style-name="fr_note" draw:name="Frame%d"
                text:anchor-type="as-char" svg:width="14.051cm" style:rel-width="85%%" draw:z-index="8">
        <draw:text-box fo:min-height="1.499cm"><draw:frame draw:style-name="fr_note_img" draw:name="Graphic%d" text:anchor-type="paragraph"
            svg:x="-0.507cm" svg:y="-0.231cm" svg:width="1.03cm" svg:height="1.03cm" draw:z-index="9">
            <draw:image xlink:href="Pictures/%s" xlink:type="simple" xlink:show="embed"
                xlink:actuate="onLoad"/></draw:frame><text:p text:style-name="shorte_note_title">
                <text:span><text:s text:c="6"/></text:span><text:span>%s:</text:span></text:p>
                %s
        </draw:text-box>
    </draw:frame>
</text:p>
''' % (self.m_frame_id + 10, self.m_image_id+10, image, label, source)

        self.m_frame_id += 1
        self.m_image_id += 1

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
            output += '<text:span text:style-name="%s">%03d </text:span>' % (self.m_styles["span"]["code_line_numbers"], line)
        
        lt = re.compile("<")
        gt = re.compile(">")
        nl = re.compile("\\\\n")
        ws = re.compile(" ")
        amp = re.compile("&")
        
        for tag in tags:

            type = tag.type
            source = tag.data
        
            source = amp.sub("&amp;", source)
            source = lt.sub("&lt;", source)
            source = gt.sub("&gt;", source)
            source = re.sub("( +)", self.__replace_whitespace, source)

            if(type == TAG_TYPE_CODE):
                source = self.format_keywords(language, source, exclude_wikiwords)
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code"], source)
            elif(type in (TAG_TYPE_COMMENT, TAG_TYPE_MCOMMENT, TAG_TYPE_XMLCOMMENT)):
                #print "tag: [%s]" % source
                source = re.sub("(@[^ \t\n]+)", """</text:span><text:span text:style-name="%s">\\1</text:span><text:span text:style-name="%s">""" % (self.m_styles['span']['code_comment_tag'], self.m_styles['span']['code_comment']), source)
                #source.replace(" ", "<text:s text:c=\"1\"/>")
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_comment"], source)
            elif(type == TAG_TYPE_PREPROCESSOR):
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_preprocessor"], source)
            elif(type == TAG_TYPE_WHITESPACE):
                output += '<text:s text:c="1"/>'
            elif(type == TAG_TYPE_STRING):
                output += '<text:span text:style-name="%s">%s</text:span>' % (self.m_styles["span"]["code_string"], source)
            elif(type == TAG_TYPE_NEWLINE):
                line += 1
                output += '<text:line-break/>'
                
                if(show_line_numbers):
                    output += '<text:span text:style-name="%s">%03d </text:span>' % (self.m_styles["span"]["code_line_numbers"], line)
            
        if(show_frame):
            output += '</text:p>'

        return output
    
    
    def format_list_child(self, elem, style, list_style, level):

        source = ''
        if(elem.children != None):

            prefix = ''

            if(elem.starred == True):
                prefix += self.insert_inline_image(-0.4, 0.5, 0.4, 0.4, "star_small.png")
            elif(elem.priority > 0):
                prefix += self.insert_inline_image(-0.4, 0.5, 0.4, 0.4, "pri_0%d.png" % elem.priority)


            if(elem.type in ("checkbox", "action")):
                x = -1.2

                if(elem.checked == True):
                    prefix += self.insert_inline_image(x, 0.5, 0.5, 0.5, "checked.png")
                else:
                    prefix += self.insert_inline_image(x, 0.5, 0.5, 0.5, "unchecked.png")

            source += '''<text:list-item>
               <text:p text:style-name="%s">%s</text:p>
               <text:list text:style-name="%s">''' % (
                   list_style, prefix + self.format_text(elem.get_text()), style)
            
            num_children = len(elem.children)
            for i in range(0, num_children):
                source += self.format_list_child(elem.children[i], style, list_style, level+1) 
            
            source += "</text:list></text:list-item>"
        else:
            prefix = ''
            
            if(elem.starred == True):
                prefix += self.insert_inline_image(-0.4, 0.5, 0.4, 0.4, "star_small.png")
            elif(elem.priority > 0):
                prefix += self.insert_inline_image(-0.4, 0.5, 0.4, 0.4, "pri_0%d.png" % elem.priority)

            if(elem.type in ("checkbox", "action")):
                x = -1.2

                if(elem.checked == True):
                    prefix += self.insert_inline_image(x, 0.5, 0.5, 0.5, "checked.png")
                else:
                    prefix += self.insert_inline_image(x, 0.5, 0.5, 0.5, "unchecked.png")

            source += '''
    <text:list-item>
        <text:p text:style-name="%s">%s</text:p>
    </text:list-item>
''' % (list_style, prefix + self.format_text(elem.get_text()))

        return source
    
    def format_list(self,
        list,
        ordered=False,
        style="list",
        list_style="list_level"):
        '''This method is called to format a list into a format
           suitable for Open Office'''

        if(not ordered):
            style = self.m_styles["list"]["unordered"]
            list_style = "shorte_unordered_list_item"
        else:
            style = self.m_styles["list"]["ordered"]
            list_style = "shorte_ordered_list_item"

        source = "<text:list text:style-name=\"%s\">" % style
        
        for elem in list:
            source += self.format_list_child(elem, style, list_style, 1)

        source += '</text:list>'

        return source
    
    
    def format_checklist(self, tag):

        style = self.m_styles["list"]["unordered"]

        source = "<text:list text:style-name=\"%s\">" % style

        checklist = tag.contents

        for elem in checklist.get_items():

            check = ''

            source += '''<text:list-item>
  <text:p text:style-name="%s">%s%s</text:p>
</text:list-item>
''' % (self.m_styles["para"]["list_level"][1], check, elem.get_name())

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

        rt = return_type.data
        
        if(return_type.data == "const"):
            rt += " " + prototype[0].data
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
        
        table = table_t()
        table.max_cols = max_cols
        table.column_styles = col_styles
        table.rows = []

        hierarchy = ''
    
        for tag in tags:
            obj = tag.contents

            style = self.m_styles["table"]["cell"]["fhier"]
            text_style = self.m_styles["para"]["fdesc"]

            if(summary_type == "testcases"):
                if(tag.category != hierarchy):
                    hierarchy = tag.category
                    row = self._table_row()

                    cols = []
                    cols.append({"span":max_cols, 'text': hierarchy, "style": style, "text-style": text_style})
                    row["cols"] = cols
                    table.rows.append(row)
            else:
                if(tag.hierarchy != hierarchy):
                    hierarchy = tag.hierarchy
                    row = self._table_row()

                    cols = []
                    cols.append({"span":max_cols, 'text': hierarchy, "style": style, "text-style": text_style})
                    row["cols"] = cols
                    table.rows.append(row)

            row = self._table_row()

            cols = []

            if(summary_type == "functions"):
                name = obj.get_name()
                tmp = obj.get_prototype().get_parsed()
                
                (returns, prototype) = self.htmlize_prototype(tmp)
            
                style = self.m_styles["table"]["cell"]["fname"]
                text_style = self.m_styles["para"]["fdesc"]
                cols.append({"span":1, 'text':returns,   "style": style, "text-style": text_style})
                cols.append({"span":1, 'text':prototype, "style": style, "text-style": text_style})
                row["cols"] = cols
                table.rows.append(row)

                row = self._table_row()
                cols = []

                style = self.m_styles["table"]["cell"]["fdesc"]
                cols.append({"span":1, 'text':'', "style": style, "text-style": text_style})

                text_style = self.m_styles["para"]["fdesc"]

                if(obj.has_description(textblock=True)):
                    function_desc = obj.get_description(textblock=True)
                    cols.append({"span":1, 'textblock':function_desc, "style": style, "text-style": text_style})
                else:
                    function_desc = ''
                    cols.append({"span":1, 'text':function_desc, "style": style, "text-style": text_style})

            
            elif(summary_type == "types"):
                name = ''

                name = obj.name
                text = self.wikify(name)

                style = self.m_styles["table"]["cell"]["fname"]
                text_style = self.m_styles["para"]["fdesc"]
                text_style_code = self.m_styles["para"]["code2"]

                cols.append({"span":1, 'text':tag.name, "style": style, "text-style": text_style})
                cols.append({"span":1, 'text':text, "style" : style, "text-style": text_style})
                row["cols"] = cols
                table.rows.append(row)

                row = self._table_row()
                cols = []

                style = self.m_styles["table"]["cell"]["fdesc"]
                cols.append({"span":1, 'text':'', "style": style, "text-style": text_style})

                desc = obj.description

                #    desc = '</text:p>' + self.format_textblock(obj["caption"], style=text_style, indent_style="summary_indent", list_style="summary_list_level") + "<text:p>"
                #elif("description" in obj):
                #    desc = '</text:p>' + self.format_textblock(obj["description"], style=text_style, indent_style="summary_indent", list_style="summary_list_level") + "<text:p>"

                text_style = self.m_styles["para"]["fdesc"]
                cols.append({"span":1, 'textblock':desc, "style": style, "text-style": text_style})

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

            table.rows.append(row)

        return self.__format_table("", table, True)

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

        testcase = tag.contents
        table = table_t()
        table.max_cols = 2
        table.column_styles = ["shorte_func_summary_col1", "shorte_func_summary_col2"]
        table.rows = []

        hierarchy = ''
    
        style = self.m_styles["table"]["cell"]["fhier"]
        text_style = self.m_styles["para"]["fdesc"]

        row = self._table_row()

        cols = []

        vars = {}
        vars["desc"] = "</text:p>" + self.format_textblock(testcase["desc"]) + "<text:p text:style-name=\"shorte_standard\">"
        vars["name"] = testcase["name"]
        vars["status"] = testcase["status"]
            
        style = self.m_styles["table"]["cell"]["prototype_section"]
        text_style = self.m_styles["table"]["cell"]["prototype_section_text"]
        cols.append({"span":2, 'text':"Test Case: " + vars["name"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table.rows.append(row)
        
        row = self._table_row()
        cols = []

        text_style = self.m_styles["para"]["normal"]
        style = self.m_styles["table"]["cell"]["fdesc"]
        cols.append({"span":1, 'text':'Status:', "style": style, "text-style": text_style})

        text_style = self.m_styles["para"]["normal"]
        cols.append({"span":1, 'text': vars["status"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table.rows.append(row)

        row = self._table_row()
        cols = []

        style = self.m_styles["table"]["cell"]["fdesc"]
        cols.append({"span":1, 'text':'Desc:', "style": style, "text-style": text_style})

        text_style = self.m_styles["para"]["normal"]
        cols.append({"span":1, 'text': vars["desc"], "style": style, "text-style": text_style})
        row["cols"] = cols
        table.rows.append(row)
            
        return self.__format_table("", table, False)


    def format_prototype(self, tag):
        
        prototype2 = tag.contents
        
        file = "blah"
        function = {}
        function["name"] = prototype2.get_name()
        function["example"] = ''
        function["pseudocode"] = ''
        function["prototype"] = ''
        function["desc"] = ''
        function["params"] = ''
        function["returns"] = ''
        function["see_also"] = ''
        function["deprecated"] = ''

        is_deprecated = False

        wikiwords = []
        wikiwords.append(prototype2.get_name())

        # Lookup the styles for formatting a prototypes
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

        # Format the description
        function["desc"] = self.format_textblock(prototype2.get_description())

        if(prototype2.has_prototype()):
            language = prototype2.get_prototype().get_language()
            example  = prototype2.get_prototype().get_parsed()
            function["prototype"] = self.format_source_code(language, example, wikiwords, False, False)

        if(prototype2.has_params()):
            params = prototype2.get_params()

            table = {}
            table["max_cols"] = 4 
            table["rows"] = []

            param_template = string.Template("""
<!-- The first row is the parameter name -->
<table:table-row table:style-name="$table_row_prototype">
  <table:table-cell table:style-name="shorte_table_prototype_parameter_header" office:value-type="string">
    <text:p text:style-name="$para_prototype_param"></text:p>
  </table:table-cell>
  <table:table-cell table:style-name="shorte_table_prototype_parameter_header" office:value-type="string" table:number-columns-spanned="3">
    <text:p text:style-name="$para_prototype_param_name">${name}</text:p>
  </table:table-cell>
</table:table-row>
<!-- The second row contains the parameter attributes -->
<table:table-row table:style-name="$table_row_prototype">
  <table:table-cell table:style-name="shorte_table_prototype_parameter_data" office:value-type="string">
    <text:p text:style-name="$para_prototype_param"></text:p>
  </table:table-cell>
  <table:table-cell table:style-name="shorte_table_prototype_parameter_data" office:value-type="string">
    <text:p text:style-name="$para_prototype_param"></text:p>
  </table:table-cell>
  <table:table-cell table:style-name="shorte_table_prototype_parameter_io" office:value-type="string">
    <text:p text:style-name="$para_prototype_param">${io}</text:p>
  </table:table-cell>
  <table:table-cell table:style-name="shorte_table_prototype_parameter_data" office:value-type="string">${desc}</table:table-cell>
</table:table-row>
""")
            
            output = ''
            for p in params:

                param = {}
            
                row = {}
                row["is_header"] = False
                row["cols"] = []
                row["cols"].append(p.get_name())

                if(p.has_io()):
                    row["cols"].append(p.get_io())
                else:
                    row["cols"].append('')

                row["cols"].append("-")
                pstyle = self.m_styles['para']['prototype']['param']
                row["cols"].append(self.format_textblock(p.get_description(), style=pstyle))

                table["rows"].append(row)

                param["table_row_prototype"] = self.m_styles["table"]["row"]["prototype"]
                param["table_cell_prototype"] = self.m_styles["table"]["cell"]["prototype"]
                param["para_prototype_param"] = self.m_styles["para"]["prototype"]["param"]
                param["para_prototype_param_name"] = self.m_styles["para"]["prototype"]["param_name"]

                param["name"] = p.get_name()

                if(p.has_io()):
                    param["io"] = "[%s]" % p.get_io()
                else:
                    param["io"] = ''
                param["desc"] = self.format_textblock(p.get_description(), style=pstyle)

                output += param_template.substitute(param)

            if(len(output) > 0):
                function["params"] = string.Template('''<table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${style_para_section}">Parameters:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>${params}''').substitute({"style_section" : function["style_section"],
                                           "style_row"              : function["style_row"],
                                           "style_para_section"     : function["style_para_section"],
                                           "params"                 : output})

        if(prototype2.has_returns()):
        
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
            <text:p text:style-name="${param_style}">${returns}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "returns" : self.format_text(prototype2.get_returns()),
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["returns"] = xml

        if(prototype2.has_see_also()):
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
    "see_also" : self.format_text(prototype2.get_see_also()),
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["see_also"] = self.format_object_construct(prototype2, 'see', True)
        
        
        if(prototype2.get_deprecated()):
            is_deprecated = True

            xml = string.Template('''
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style}" table:number-columns-spanned="4" office:value-type="string">
            <text:p text:style-name="${section_style}">Deprecated:</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
        <table:table-row table:style-name="${row_style}">
          <table:table-cell table:style-name="${cell_style2}" table:number-columns-spanned="4" office:value-type="string">
            ${deprecated}
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>
''').substitute({
    "deprecated" : self.format_textblock(prototype2.get_deprecated()),
    "row_style" : self.m_styles["table"]["row"]["prototype_section"],
    "cell_style" : self.m_styles["table"]["cell"]["prototype_section"],
    "section_style" : self.m_styles["table"]["cell"]["prototype_section_text"],
    "cell_style2" : self.m_styles["table"]["cell"]["prototype"],
    "param_style" : self.m_styles["para"]["prototype"]["param"]
    })

            function["deprecated"] = xml

        if(prototype2.has_example()):

            language = prototype2.get_example().get_language()
            example  = prototype2.get_example().get_parsed()

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

            function["example"] = xml
        
        
        if(prototype2.has_pseudocode()):

            language = prototype2.get_pseudocode().get_language()
            example  = prototype2.get_pseudocode().get_parsed()
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

            function["pseudocode"] = xml


        topic = topic_t({"tag"    : tag,
                         "name"   : prototype2.get_name(),
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
            <text:p text:style-name="${style_para_name}">Function: ${name}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>

        <table:table-row table:style-name="${style_row}">
          <table:table-cell table:style-name="${style_section_data}" table:number-columns-spanned="4" office:value-type="string">
            ${desc}
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
            <text:p text:style-name="${style_para_text}">${prototype}</text:p>
          </table:table-cell>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
          <table:covered-table-cell/>
        </table:table-row>


        ${params}
        ${returns}
        ${example}
        ${pseudocode}
        ${see_also}
        ${deprecated}
</table:table>
<text:p text:style-name="${style_para_normal}"></text:p>
""")

        function["id"] = self.m_table_id
        self.m_table_id += 1

        if(is_deprecated):
            function["name"] += " (THIS METHOD IS DEPRECATED)"
            function["style_table"] = "shorte_table_prototype_deprecated"

        xml = template.substitute(function)

        return xml


    
    def append_source_code(self, tag):

        output = ''

        output += self.format_source_code(tag.name, tag.contents)
        output += self.format_pre('')

        if(tag.has_result()):
            result = tag.get_result()
            
            # Convert any HTML tags in the input source
            lt = re.compile("<")
            gt = re.compile(">")
            ws = re.compile(" ")
            nl = re.compile("\\\\n")

            if(result.has_compile_result()):
                label = "Compile:"
                rrc = result.get_compile_rc()
                if(rrc != 0):
                    label += " (Failed: rc=%d)" % rrc
                    
                output += self.format_bold(label)
                tmp = lt.sub("&lt;", result.get_compile_result())
                tmp = gt.sub("&gt;", tmp)
                tmp = nl.sub("__NEWLINE__", tmp)
                output += self.format_pre(tmp)

            if(result.has_run_result()):
                rrc = result.get_run_rc()
                label = "Result:"
                if(rrc != 0):
                    label += " (Failed: rc=%d)" % rrc
                    
                output += self.format_bold(label)
                tmp = lt.sub("&lt;", result.get_run_result())
                tmp = gt.sub("&gt;", tmp)
                tmp = nl.sub("__NEWLINE__", tmp)
                output += self.format_pre(tmp)
        
            if(result.has_image()):
                image = {}
                image["src"] = result.get_image()

                iname = os.path.basename(image["src"])
                (iname,iext) = os.path.splitext(iname)
                image['ext']  = iext
                image['name'] = iname

                output += self.format_image(image)
                
        output += self.format_pre('')
        
        self.m_sections[0]["Headings"][self.m_header_id]["Content"] += output

    def format_sequence(self, tag):

        image = tag.contents
        output = self.format_image(image)
        output += self.__format_table("", tag.contents["html"])

        return output

    def append(self, tag):
        
        name = tag.name

        #print("Appending tag %s" % name)

        if(name == "#"):
            return
        if(name in "p"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += "<text:p text:style-name=\"shorte_standard\">%s</text:p>" % self.format_text(tag.contents)
        elif(name in "text"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_textblock(tag)
        elif(name in "pre"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_pre(tag.contents)
        elif(name == "note"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(tag, type="note", label="Note")
        elif(name == "tbd"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(tag, type="tbd", label="TBD", image="tbd.png")
        elif(name == "question"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(tag, type="question", label="Question", image="question.png")
        elif(name == "warning"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_note(tag, type="warning", label="Warning", image="warning.png")
        elif(name == "questions"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_questions(tag)
        elif(name == "table"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.__format_table(tag.source, tag.contents)
        elif(name == "ul"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag.contents, False)
        elif(name == "ol"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_list(tag.contents, True)
        elif(name == "checklist"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_checklist(tag)
        elif(name == "image"):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_image(tag.contents)
        elif(name in ("struct", "register")):
            self.m_sections[0]["Headings"][self.m_header_id]["Content"] += self.format_struct(tag)
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
        elif(name == "class"):
            WARNING("Classes not supported in OTD documents yet")
        # These tags are not supported in OTD documents
        elif(name in ("imagemap", "embed", "input", "columns", "column", "endcolumns", "gallery")):
            #print "WARNING: %s tag not supported in ODT documents" % name
            pass
        else:
            FATAL("Undefined tag: %s [%s]" % (name, tag.source))
    

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
                elif(heading["Type"] == HEADING5):
                    header_type = "%s%s" % (self.m_styles["headings"][HEADING5], postfix)
                elif(heading["Type"] == HEADING6):
                    header_type = "%s%s" % (self.m_styles["headings"][HEADING6], postfix)
                elif(heading["Type"] == HEADING_DEFAULT):
                    header_type = "Normal"
                    #header_type = "%s%s" % (self.m_styles["headings"][HEADING6], postfix)
                    #add_to_toc = False
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
        
        handle = open(shorte_get_startup_path() + "/templates/odt/%s.odt" % self.m_engine.get_theme(), "r")
        contents = handle.read()
        handle.close()
        return contents

    def __format_revision_history(self, tag, replace_paragraph=True):

        table = tag

        if(table != None):
            table.title = "Revision History"
            table.widths = [10,30,60]
            #table["column-styles"] = ["shorte_type_summary_col2", "shorte_type_summary_col2", "shorte_type_summary_col2"]
            if(replace_paragraph):
                output = self.__format_table("", tag)
            else:
                output = "</text:p>" + self.__format_table("", tag) + "<text:p text:style-name=\"shorte_standard\">"

            return output
        
        return ""
    
    def extract_template(self, xml, content_variable):
        # Find the start of the CONTENT field
        pos = xml.find("CONTENT")
        if(pos == -1):
            print "extract_template: can't find content"
            sys.exit(-1)
            return xml

        # Search for the ending </text:p> tag
        end = xml.find("</text:p>", pos)

        if(end == -1):
            print "extract_template: can't find end of content"
            sys.exit(-1)

        # Search for the beginning <text:p tag
        begin = xml.rfind("<text:p", 0, pos)

        if(begin == -1):
            print "extract_template: can't find beginning of content"

        output = xml[0:begin] + content_variable + xml[end+9:]

        #print "TEMPLATE for %s" % content_variable
        #print output
        #print "===="

        return output
    
    def extract_style_section(self, xml, start, end):

        pos_start = xml.find(start)

        # Now find the end of the paragraph
        pos_start_style = xml.find("</text:p>", pos_start)
        pos_start_style += 9

        pos_end = xml.find(end)
        pos_end_style = xml.rfind("<text:p", 0, pos_end)

        return xml[pos_start_style:pos_end_style]
         

    def extract_styles(self, xml):
        self.styles = {}

        matches = re.search("(<text:p.*?>\[\[STYLES.TEMPLATES.START\]\]</text:p>.*?<text:p.*?>\[\[STYLES.TEMPLATES.END\]\]</text:p>)", xml, re.DOTALL)

        if(matches != None):
            styles = matches.groups()[0]

            # print "STYLES"
            # print styles
            # print "======="

            style = self.extract_style_section(xml, "STYLES.NOTE.BEGIN", "STYLES.NOTE.END")
            self.styles["note"] = self.extract_template(style, "$NOTE_CONTENT")

            # print "NOTE"
            # print style
            # print "===="

            style = self.extract_style_section(xml, "STYLES.WARNING.BEGIN", "STYLES.WARNING.END")
            self.styles["warning"] = self.extract_template(style, "$WARNING_CONTENT")
            # print "WARNING"
            # print style
            # print "===="
            
            style = self.extract_style_section(xml, "STYLES.TBD.BEGIN", "STYLES.TBD.END")
            self.styles["tbd"] = self.extract_template(style, "$TBD_CONTENT")
            
            style = self.extract_style_section(xml, "STYLES.QUESTION.BEGIN", "STYLES.QUESTION.END")
            self.styles["question"] = self.extract_template(style, "$QUESTION_CONTENT")

    def walk_backwards(self, contents, text, pos=0):

        start = contents.rfind(contents, text, pos)

        if(start != -1):
            return start
        return None

    #def update_attribute(self, xml, name, block, attribute):

    def generate_index(self, title, theme, version):

        scratchdir = shorte_get_config("shorte", "scratchdir")

        #print "Theme: %s" % self.m_engine.m_theme

        shutil.copy(shorte_get_startup_path() + "/templates/odt/%s.odt" % (self.m_engine.m_theme), scratchdir + os.path.sep + 'odt')
       
        unzip_file_into_dir("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme), scratchdir + "/odt")

        os.unlink("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme))

        handle = open("%s/odt/content.xml" % scratchdir)
        xml = handle.read()
        handle.close()

        self.extract_styles(xml);

        xml = re.sub("DOCUMENT_SHORTTITLE", self.get_title_short(), xml)
        xml = re.sub("DOCUMENT_TITLE", self.get_title(), xml)
        xml = re.sub("DOCUMENT_SUBTITLE", self.m_engine.get_subtitle(), xml)
        xml = re.sub("DOCUMENT_VERSION", self.m_engine.get_doc_info().version(), xml)
        xml = re.sub("DOCUMENT_CUSTOMER", self.m_engine.get_doc_info().customer(), xml)
        xml = re.sub("CURRENT_DATE", self.m_engine.get_date(), xml)
        xml = re.sub("DOCUMENT_NO", self.m_engine.get_doc_info().number(), xml)
        xml = re.sub("DOCUMENT_FOOTER_TITLE", self.get_footer_title(), xml)
        xml = re.sub("DOCUMENT_FOOTER_SUBTITLE", self.get_footer_subtitle(), xml)
        xml = re.sub("DOCUMENT_COPYRIGHT_DATE", self.m_engine.get_doc_info().copyright_date(), xml)

        xml = re.sub("<text:p text:style-name=\"[A-Za-z0-9_]+\">DOCUMENT_REVISION_HISTORY</text:p>", self.__format_revision_history(self.m_engine.get_doc_info().revision_history()), xml)
        #xml = re.sub("DOCUMENT_REVISION_HISTORY", self.__format_revision_history(self.m_engine.get_doc_revision_history(), False), xml)

        pages = self._doc_pages_to_xml()
        #print pages
        #sys.exit(-1)

        # Insert the contents into the document
        str = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">[[INSERT_CONTENTS_HERE]]</text:h>'''
        pos = xml.find(str)
        if(pos == -1):
            print "WTF!!!"
            sys.exit(-1)
        start = pos
        end = pos + len(str)
        tmp = xml[0:start]
        tmp += pages
        tmp += xml[end:len(xml)]
        xml = tmp

        # Search for the styles to strip. The expression looks like this:
        #   re.sub("<text:p.*?>\[\[STYLES.TEMPLATES.START\]\].*?\[\[STYLES.TEMPLATES.END\]\]</text:p>", "", xml)
        start = xml.find("[[STYLES.TEMPLATES.START]]", 0)
        #print "START: %d" % start
        start = xml.find("<text:p", start - 100)
        end = xml.find("[[STYLES.TEMPLATES.END]]", start)
        end = xml.find("</text:p>", end)
        #print "END: %d" % end
        end += 9

        tmp = xml[0:start]
        tmp += xml[end:]

        xml = tmp

        #print "TEMPLATE"
        #print xml
        #sys.exit(0)


        # Replace the automatic styles
        start = xml.find("<office:automatic-styles>")
        end   = xml.find("</office:automatic-styles>")

        prefix = xml[0:start+25]
        prefix += "\n\n"
        #print "PREFIX"
        #print prefix

        styles = xml[start+25:end]
        styles += "\n\n"
        
        #print "STYLES" 
        #print styles

        postfix = xml[end:]
        postfix += "\n\n"

        #print "POSTFIX"
        #print postfix

        doc_styles = self.get_styles()

        #print "DOCSTYLES"
        #print doc_styles["custom"]
        #sys.exit(0)

        xml = prefix + styles + doc_styles["custom"] + postfix
        #xml = prefix + styles + postfix
        

        # Now remove any blank paragraphs that got accidentally added
        #xml = xml.replace("<text:p text:style-name='shorte_standard'></text:p>", "<text:p text:style-name='shorte_standard'>empty</text:p>")
        xml = xml.replace("<text:p text:style-name='shorte_standard'></text:p>", "")

        #print "XML"
        #print xml
        #sys.exit(0)

        xml = re.sub("__NEWLINE__", '\\\\n', xml)
        handle = open("%s/odt/content.xml" % scratchdir, "wt")
        handle.write(xml)
        handle.close()
        
        #print xml
        #sys.exit(-1)


        images = ["note", "tbd", "question", "warning", "star_small", "checked", "unchecked", "pri_01", "pri_02", "pri_03", "pri_04", "pri_05", "deprecated"]
        for path in images:
            # Add the note.png file
            png = shorte_get_startup_path() + "/templates/shared/%s.png" % path
            image = {}
            image["src"] = png
            image["name"] = path
            image["ext"] = ".png"
            self.m_pictures.append(image)

        images = ["table_blue", "table_left_right", "table_white"]
        for path in images:
            # Add the note.png file
            png = shorte_get_startup_path() + "/templates/shared/odt/%s.png" % path
            image = {}
            image["src"] = png
            image["name"] = path
            image["ext"] = ".png"
            self.m_pictures.append(image)

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
        xml = re.sub("DOCUMENT_VERSION", self.m_engine.get_doc_info().version(), xml)
        xml = re.sub("DOCUMENT_CUSTOMER", self.m_engine.get_doc_info().customer(), xml)
        xml = re.sub("CURRENT_DATE", self.m_engine.get_date(), xml)
        xml = re.sub("DOCUMENT_NO", self.m_engine.get_doc_info().number(), xml)
        xml = re.sub("DOCUMENT_FOOTER_TITLE", self.get_footer_title(), xml)
        xml = re.sub("DOCUMENT_FOOTER_SUBTITLE", self.get_footer_subtitle(), xml)
        xml = re.sub("DOCUMENT_COPYRIGHT_DATE", self.m_engine.get_doc_info().copyright_date(), xml)

        xml = re.sub("<text:outline-style style:name=\"Outline\">.*?</text:outline-style>", doc_styles["outline"], xml)
        
        ## Replace the automatic styles
        #start = xml.find("<office:automatic-styles>")
        #end   = xml.find("</office:automatic-styles>")

        #prefix = xml[0:start+25]
        #styles = xml[start+25:end]
        #postfix = xml[end:]

        #xml = prefix + styles + self.get_styles() + postfix


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
        '''This method is called to generate the output
           ODT or PDF document

           @param self  [I] - The instance of the template class
           @param theme [I] - The name of theme to use to generate the output document.
                              This is used to find the .odt template file describing
                              the document.
           @param version [I] - The version number to use when generating the
                                document.
           @param package [I] - The package name to use when generating the document.
                                This could be "odt" or "pdf" depending on whether
                                or not we are creating a PDF file or not.
        '''

        scratchdir = shorte_get_config("shorte", "scratchdir")
        #print "Theme: %s" % self.m_engine.m_theme
        shutil.copy(shorte_get_startup_path() + "/templates/odt/%s.odt" % (self.m_engine.m_theme), scratchdir + os.path.sep + 'odt')
        unzip_file_into_dir("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme), scratchdir + "/odt")
        os.unlink("%s/odt/%s.odt" % (scratchdir, self.m_engine.m_theme))
        handle = open("%s/odt/content.xml" % scratchdir)
        xml = handle.read()
        handle.close()
        self.extract_styles(xml);

        try:
            shutil.rmtree(scratchdir + os.path.sep + 'odt')
        except:
            # Ignore errors
            errors = 0 
        
        outdir = scratchdir + os.path.sep + 'odt'
        if(not os.path.exists(outdir)):
            os.makedirs(scratchdir + os.path.sep + 'odt')

        pages = self.m_engine.m_parser.get_pages()

        # The skip_if_pdf attribute is a modifier that can be used
        # to exclude sections
        skip_if_pdf = False # True if the skip_if_pdf attribute is set
        skipped_tag = None  # The type of tag that had the skip_if_pdf attribute set

        for page in pages:
            
            tags = page["tags"]
            for tag in tags:
                #print "TAG: %s" % tag.name
                #if(self.m_engine.tag_is_header(tag.name)):
                #    print "  %s" % tag.source

                # If there currently is a skip tag set then see if
                # it the current tag is at or above it. If it is then unset
                # the skip_in_pdf attribute
                if(skipped_tag != None):
                    # If this tag is equal to or greater priority than the skipped tag
                    # then unset the skip attribute
                    if(not self.m_engine.m_parser.is_child_tag(tag.name, skipped_tag)):
                        skipped_tag = None
                        skip_if_pdf = False

                # Now see if the current tag has a skip attribute set and record it
                if(tag.modifiers.has_key("skip_if_pdf")):
                    skip_if_pdf = True
                    # If there is currently a skip set then see if this one outweights
                    # the one that is set.
                    if(skipped_tag != None):
                        if(not self.m_engine.m_parser.is_child_tag(tag.name, skipped_tag)):
                            skipped_tag = tag.name
                    else:
                        skipped_tag = tag.name

                # Only output the tag if the skip_in_pdf flag is not set.
                if(skip_if_pdf):
                    continue

                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag)
            
                elif(self.m_engine.tag_is_source_code(tag.name)):
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
            path_startup = shorte_get_startup_path()
            path_startup = path_startup.replace("/", "\\")
                
            path_oowriter = shorte_get_config("shorte", "path.oowriter.win32")

        elif(sys.platform == "darwin"):
            path_startup = shorte_get_startup_path()
            path_oowriter = shorte_get_config("shorte", "path.oowriter.osx")
        else:
            path_startup = shorte_get_startup_path()
            path_oowriter = shorte_get_config("shorte", "path.oowriter.linux")
        
        if(os.environ.has_key("PATH_OOWRITER")):
            path_oowriter = os.environ["PATH_OOWRITER"]

        if(not os.path.exists(path_oowriter)):
            FATAL("Cannot generate ODT files, swriter not found at %s\n"
                  "Try seeing PATH_OOWRITER environment variable or updating path in shorte.cfg" % path_oowriter)

        #print "PACKAGE: %s" % package
        
        params_oowriter = "--writer --nologo --nofirststartwizard --norestore --nodefault --headless --invisible --nolockcheck"
            
        path_converter = "%s/templates/odt/convert_to_pdf.odt" % path_startup
        path_input = "%s" % (self.m_engine.get_output_dir() + "/" + self.get_index_name())
        #print "PLATFORM: %s" % sys.platform

        if(sys.platform in ("cygwin")):

            params_oowriter = ""

            path_oowriter = path_oowriter
            path_oowriter = path_oowriter.replace("\\", "/")
            path_oowriter = path_oowriter.replace("C:/", "/cygdrive/c/")

            path_input = path_input.replace("/cygdrive/c/", "C:\\")
            path_input = path_input.replace("\\", "/")

            path_converter = path_converter.replace("\\", "/")

        elif(sys.platform in "win32"):
            params_oowriter = ""

            path_oowriter = path_oowriter
            path_oowriter = path_oowriter.replace("/", "\\")
            path_input = path_input.replace("/cygdrive/c/", "C:\\")
            path_input = path_input.replace("/", "\\")
            path_converter = path_converter.replace("/", "\\")


        if(package == PACKAGE_TYPE_ODT):

            path_output = path_input
            path_output = path_output.replace(".odt", "")

            path_output = path_output + "_copy.odt"

            cmd = '''"%s" %s \"%s\" \"macro://convert_to_pdf/Standard.Module1.UpdateTOC(\\\"%s\\\")\"''' % (
                path_oowriter,
                params_oowriter,
                path_converter,
                path_input)

            os.system(cmd)

            shutil.move(path_output, path_input)

            return path_input
        
        if(package == PACKAGE_TYPE_PDF):

            #print "PATH_OOWRITER: %s" % path_oowriter
            import subprocess

            cmd = '''"%s" %s \"%s\" \"macro://convert_to_pdf/Standard.Module1.ConvertToPDF(\\\"%s\\\")\"''' % (
                    path_oowriter,
                    params_oowriter,
                    path_converter,
                    path_input)
            #print "Command: %s" % cmd
            #if(sys.platform == "cygwin"):
            #    os.system(cmd)
            #else:
            #    subprocess.call(cmd)
            try:
                if(sys.platform == "win32"):
                    subprocess.call(cmd)
                else:
                    subprocess.call(cmd, shell=True)
            except:
                print sys.exc_info()
                raise
            
            # If the output file doesn't exist then generate a failure since the macro failed
            path_output = path_input.replace("odt", "pdf")
            if(not os.path.exists(path_output)):
                FATAL("Failed converting document to [%s], try manually opening the ODT file to see if there was a corruption\n\n" % path_output)
            
            return path_output
    
    def generate_string(self, theme, version, package):
       path_output = self.generate(theme, version, package)

       #print "Output: %s" % path_output

       handle = open(path_output, "rb")
       contents = handle.read()
       handle.close()

       #print path_output

       return base64.encodestring(contents)

       #return "TBD"
