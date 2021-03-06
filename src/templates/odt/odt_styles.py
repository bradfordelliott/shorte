import string
import templates.themes

class styles():
    def __init__(self):
        
        self.table_indent = 0
        self.list_bullet_indent  = 0.75

        # This is the indent for the text after a bullet point
        #self.list_bullet_text_indent = 1.2

        # If you don't care to use checkboxes or images
        # in lists then this can be changed to 0.4 - 0.5   
        self.list_bullet_text_indent = 0.7

        # This is the common indent for the entire document
        self.standard_indent = 0

        # This is the indent for code blocks
        self.code_indent = 0.255
        
        self.colors = templates.themes.theme().get_colors("shorte")

    def outline_styles(self):
        '''This method defines the outline style of the document. This
           is inserted into the style.xml file'''
        outline_styles = '''
    <text:outline-style style:name="Outline">
    '''
        for level in [1,2,3,4,5,6,7,8,9,10]:
            if(level == 1):
                display_levels = ""
            else:
                display_levels = 'text:display-levels="%d"' % level
            tab_stop = 'text:list-tab-stop-position="0cm"'
            #tab_stop = ""
    
            outline_styles += string.Template('''
    <text:outline-level-style text:level="${level}" text:style-name="Numbering_20_Symbols" style:num-prefix=" " style:num-suffix=".0: " style:num-format="1" ${display_levels}>
    </text:outline-level-style>
    ''').substitute({"level" : level, "display_levels" : display_levels, "tabstop" : tab_stop})
    
        outline_styles += '''
    </text:outline-style>
    '''
    
        return outline_styles

    def get_common_styles(self):



        paragraph_styles = '''
<!-- Common Paragraph Styles -->
<style:style style:name="shorte_para_bold_white" style:family="paragraph" style:parent-style-name="shorte_standard">
  <style:paragraph-properties
      fo:margin-left="0.2cm" fo:margin-top="0cm"/>
  <style:text-properties fo:color="#ffffff" fo:font-weight="bold"/>
</style:style>
'''
        
        #############################################
        #
        # Textblock Styling
        #
        #############################################

        # Indented Code Blocks in Textblocks
        paragraph_styles += '''
<style:style style:name="shorte_indented_code_block" style:family="paragraph" style:parent-style-name="shorte_standard">
  <style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.4cm"
      fo:margin-left="0.5cm"
      fo:margin-right="0.5cm"
      fo:border="0.01in solid #c0c0c0"
      fo:padding="0.2cm"
      fo:background-color="#f2f2f2"/>
  <style:text-properties style:font-name="Courier New" fo:color="#000000" fo:font-size="8.5pt"/>
</style:style>
''' 
    
        # Highlighted text spans
        paragraph_styles += '''
        <style:style style:name="shorte_highlight" style:family="text">
            <style:text-properties fo:background-color="#ffff00"/>
        </style:style>
'''
    
        # Striked text spans
        paragraph_styles += '''
<style:style style:name="shorte_strikethru" style:family="text"><style:text-properties style:text-line-through-style="solid"/>
</style:style>
'''

        # Inline code spans
        paragraph_styles += '''
    <style:style style:name="shorte_inline_code_span" style:family="text">
        <style:text-properties
            fo:background-color="#F2F2F2"
            fo:border="0.01in solid #c0c0c0"
            fo:padding="0.04cm"
            fo:padding-top="0.01cm"
            fo:padding-bottom="0.01cm"
        />
    </style:style>
'''
        
        # Quote styles
        indents = [self.standard_indented,
                   self.standard_indented + 0.5,
                   self.standard_indented + 0.9,
                   self.standard_indented + 1.1,
                   self.standard_indented + 1.5,
                   self.standard_indented + 1.9]

        for i in xrange(0, len(indents)):
            name = "shorte_quote_l%d" % i
            indent = indents[i]
            paragraph_styles += string.Template('''
<style:style style:name="${name}" style:family="paragraph" style:parent-style-name="shorte_standard">
  <style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.4cm"
      fo:margin-left="${indent}cm"
      fo:border-left="0.020in solid #c0c0c0"
      fo:padding-left="0.2in"/>
  <style:text-properties fo:color="#000000" fo:font-style="italic"/>
</style:style>
''').substitute({"name"   : name,
                 "indent" : indent})

        return string.Template('''
    <!-- Styling for hyperlinks -->
    <style:style style:name="hyperlink" style:family="text">
        <style:text-properties fo:color="${color_hyperlink}"/>
    </style:style>
    
    <!-- Paragraph Styles -->
    ${paragraph_styles}
    ''').substitute({"color_hyperlink"  : self.colors["hyperlink"].fg,
                     "paragraph_styles" : paragraph_styles})
      
    def create_table_paragraph_styles(self, name, font_size):

        table = string.Template('''
<style:style style:name="shorte_table.title.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
  <style:text-properties
      fo:color="${color_table_title_fg}"
      fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"
      ${font_size}
  />
</style:style>
    
<style:style style:name="shorte_table.header.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
  <style:text-properties
      fo:color="${color_table_header_fg}"
      fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"
      ${font_size}
  />
</style:style>
    
<style:style style:name="shorte_table.subheader.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
  <style:text-properties
      fo:color="${color_table_subheader_fg}"
      fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"
      ${font_size}
  />
</style:style>
    
<style:style style:name="shorte_table.reserved.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
  <style:text-properties
      fo:color="${color_table_rsvd_fg}"
      ${font_size}
  />
</style:style>
    
<style:style style:name="shorte_table.caption.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in" fo:margin-left="0.4in"/>
  <style:text-properties
      fo:color="${color_table_caption_fg}"
      fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"
      ${font_size}
  />
</style:style>

<style:style style:name="shorte_table.caption.title.text${name}" style:family="paragraph" style:parent-style-name="shorte_standard">
  <style:paragraph-properties
      fo:margin-left="0.2cm" fo:margin-top="0cm"/>
  <style:text-properties
      fo:color="#ffffff"
      fo:font-weight="bold"
      ${font_size}
  />
</style:style>

<style:style style:name="shorte_table.standard.text${name}" style:family="paragraph" style:parent-style-name="Standard">
  <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
  <style:text-properties
      fo:color="${color_table_normal_fg}"
      ${font_size}
  />
</style:style>

''').substitute({"name"                     : name,
                 "font_size"                : font_size,
                 "color_table_title_bg"     : self.colors["table"]["title"].bg,
                 "color_table_title_fg"     : self.colors["table"]["title"].fg,
                 "color_table_header_bg"    : self.colors["table"]["header"].bg,
                 "color_table_header_fg"    : self.colors["table"]["header"].fg,
                 "color_table_subheader_bg" : self.colors["table"]["subheader"].bg,
                 "color_table_subheader_fg" : self.colors["table"]["subheader"].fg,
                 "color_table_rsvd_bg"      : self.colors["table"]["reserved"].bg,
                 "color_table_rsvd_fg"      : self.colors["table"]["reserved"].fg,
                 "color_table_normal_bg"    : self.colors["table"]["normal"].bg,
                 "color_table_normal_fg"    : self.colors["table"]["normal"].fg,
                 "color_table_caption_bg"   : self.colors["table"]["caption"].bg,
                 "color_table_caption_fg"   : self.colors["table"]["caption"].fg})

        return table


    def get_table_styles(self):

        default = self.create_table_paragraph_styles(name=".default",font_size='')
        micro   = self.create_table_paragraph_styles(name=".micro",  font_size='fo:font-size="7pt"')
        blank   = self.create_table_paragraph_styles(name="",        font_size='')

        return string.Template('''
    <!-- The standard table format -->
    <style:style style:name="shorte_table" style:display-name="shorte_table" style:family="table" style:master-page-name="">
        <style:table-properties
            fo:margin-left="${table_indent}cm"
            style:page-number="auto"
            fo:break-before="auto"
            fo:break-after="auto"
            table:align="left"
            style:shadow="none"
            fo:keep-with-next="auto"
            style:may-break-between-rows="true"
            style:writing-mode="lr-tb"
            table:border-model="collapsing"/>
    </style:style>
    
    <!-- Table Cell Styles -->
    <style:style style:name="shorte_table.title.cell" style:family="table-cell">
      <style:table-cell-properties fo:background-color="${color_table_title_bg}" fo:padding="0.0282in"
        fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>

    <style:style style:name="shorte_table.header.cell" style:family="table-cell">
      <style:table-cell-properties
            fo:background-color="${color_table_header_bg}"
            fo:padding="0.0182in"
            fo:border="0.002in solid #000000" >
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table.subheader.cell" style:family="table-cell">
      <style:table-cell-properties
         fo:background-color="${color_table_subheader_bg}"
         fo:padding="0.0182in"
         fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>


    <style:style style:name="shorte_table.reserved.cell" style:family="table-cell">
        <style:table-cell-properties
            fo:background-color="${color_table_rsvd_bg}" fo:padding="0.0182in"
            fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    

    <style:style style:name="shorte_table.normal.cell" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0in"
          fo:border="0.002in solid #000000" fo:background-color="${color_table_normal_bg}"/>
    </style:style>
    
    <style:style style:name="shorte_table.code.cell" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0in"
          fo:border-top="0.002in solid #c0c0c0"
          fo:border-bottom="0.002in solid #c0c0c0"
          fo:background-color="${color_table_normal_bg}"/>
    </style:style>
    
    <style:style style:name="shorte_table.code.header.cell" style:family="table-cell">
      <style:table-cell-properties
            fo:background-color="${color_table_header_bg}"
            fo:padding="0.0182in"
            fo:border-top="0.002in solid #000000" >
            fo:border-bottom="0.002in solid #000000" >
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table.caption.cell" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0in"
          fo:border="0.002in solid #000000" fo:background-color="${color_table_caption_bg}"/>
    </style:style>

    <style:style style:name="shorte_table.alternate.code.cell" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0in"
          fo:border-top="0.002in solid #c0c0c0"
          fo:border-bottom="0.002in solid #c0c0c0"
          fo:background-color="#f0f0f0"/>
    </style:style>
    
    <style:style style:name="shorte_table_standard" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="${color_table_normal_fg}"/>
    </style:style>
    
    ${style_blank}
    ${style_default}
    ${style_micro}
    
    ''').substitute({"table_indent"             : self.table_indent,
                     "color_table_title_bg"     : self.colors["table"]["title"].bg,
                     "color_table_title_fg"     : self.colors["table"]["title"].fg,
                     "color_table_header_bg"    : self.colors["table"]["header"].bg,
                     "color_table_header_fg"    : self.colors["table"]["header"].fg,
                     "color_table_subheader_bg" : self.colors["table"]["subheader"].bg,
                     "color_table_subheader_fg" : self.colors["table"]["subheader"].fg,
                     "color_table_rsvd_bg"      : self.colors["table"]["reserved"].bg,
                     "color_table_rsvd_fg"      : self.colors["table"]["reserved"].fg,
                     "color_table_normal_bg"    : self.colors["table"]["normal"].bg,
                     "color_table_normal_fg"    : self.colors["table"]["normal"].fg,
                     "color_table_caption_bg"   : self.colors["table"]["caption"].bg,
                     "color_table_caption_fg"   : self.colors["table"]["caption"].fg,
                     "style_micro"              : micro,
                     "style_default"            : default,
                     "style_blank"              : blank})


    def get_list_styles(self):
        
        list_styles = ''
        # List bullet styles
        #   defines the indent level of the bullet styles for
        #   an ordered or unordered list. It does not control the
        #   indent between the bullet and the text of each list entry
        list_styles += '''
    <style:style style:name="shorte_unordered_list_item" style:family="paragraph" style:parent-style-name="shorte_standard" style:list-style-name="shorte_unordered_list">
    </style:style>
    <style:style style:name="shorte_ordered_list_item" style:family="paragraph" style:parent-style-name="shorte_standard" style:list-style-name="shorte_ordered_list">
    </style:style>
    '''
        
        unordered_list_style = '''
        <text:list-style style:name="shorte_unordered_list">
        '''

        ordered_list_style = '''
        <text:list-style style:name="shorte_ordered_list">
        '''
        for level in [1,2,3,4,5,6,7]:
            bullet = '&#176;'
            if(level & 1):
                bullet = '&#8226;'

            #self.list_bullet_text_indent = 0.5

            # DEBUG BRAD: This controls the indent after the bullet
            indent = self.standard_indent + self.list_bullet_text_indent + (self.list_bullet_indent * (level-1))

            text_indent = -0.635
            unordered_list_style += '''
            <text:list-level-style-bullet text:level="%d" text:style-name="Bullet_20_Symbols" text:bullet-char="%s">
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="%fcm" fo:text-indent="%fcm" fo:margin-left="%fcm"/>
                </style:list-level-properties>
            </text:list-level-style-bullet>
            ''' % (level, bullet, indent, text_indent, indent)

            display_levels = ''
            if(level > 1):
                display_levels = 'text:display-levels="%d"' % (1)

            text_indent = -0.735

            indent = self.standard_indent + self.list_bullet_text_indent + (self.list_bullet_indent * (level-1))

            if(level in [1,4,7]):
                num_format = '1'
            elif(level in [2,5,8]):
                num_format = 'a'
            else:
                num_format = 'i'
                
            ordered_list_style += '''
            <text:list-level-style-number text:level="%d" text:style-name="Numbering_20_Symbols" style:num-prefix=" " style:num-suffix=".  " style:num-format="%s" %s>
                <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
                    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="%fcm" fo:text-indent="%fcm" fo:margin-left="%fcm"/>
                </style:list-level-properties>
            </text:list-level-style-number>
            ''' % (level, num_format, display_levels, indent, text_indent, indent)


        unordered_list_style += '''
        </text:list-style>
'''
        ordered_list_style += '''
        </text:list-style>
'''

        #styles = '''
        #    <text:list-style style:name="shorte_unordered_list">
        #      <text:list-level-style-bullet text:level="1" text:style-name="Bullet_20_Symbols" text:bullet-char="&#176;">
        #        <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #          <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.27cm" fo:text-indent="-0.635cm" fo:margin-left="1.27cm"/>
        #        </style:list-level-properties>
        #      </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="2" text:style-name="Bullet_20_Symbols" text:bullet-char="&#8226;">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.905cm" fo:text-indent="-0.635cm" fo:margin-left="1.905cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="3" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.54cm" fo:text-indent="-0.635cm" fo:margin-left="2.54cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="4" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.175cm" fo:text-indent="-0.635cm" fo:margin-left="3.175cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="5" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.81cm" fo:text-indent="-0.635cm" fo:margin-left="3.81cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="6" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="4.445cm" fo:text-indent="-0.635cm" fo:margin-left="4.445cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="7" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.08cm" fo:text-indent="-0.635cm" fo:margin-left="5.08cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="8" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="5.715cm" fo:text-indent="-0.635cm" fo:margin-left="5.715cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="9" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.35cm" fo:text-indent="-0.635cm" fo:margin-left="6.35cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    <text:list-level-style-bullet text:level="10" text:style-name="Bullet_20_Symbols" text:bullet-char="-">
        #    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
        #    <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="6.985cm" fo:text-indent="-0.635cm" fo:margin-left="6.985cm"/>
        #    </style:list-level-properties>
        #    </text:list-level-style-bullet>
        #    </text:list-style>
        #    '''

        # DEBUG BRAD: This works
        #return styles + ordered_list_style + list_styles

        return unordered_list_style + ordered_list_style + list_styles

    def get_source_code_styles(self):
        return string.Template('''
    <!-- Source code styling -->
    <style:style style:name="shorte_code3" style:family="paragraph" style:parent-style-name="shorte_standard" style:master-page-name="">
        <style:paragraph-properties fo:margin-left="${code_indent}cm"
            fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:line-height="100%" fo:text-indent="0cm"
            style:auto-text-indent="false" style:page-number="auto" fo:background-color="#f2f2f2" fo:keep-with-next="auto">
            <style:background-image/>
        </style:paragraph-properties>
        <style:text-properties style:font-name="Courier New" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    
    <style:style style:name="code" style:family="text">
        <style:text-properties style:font-name="Courier New" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_line_numbers" style:display-name="code_line_numbers" style:family="text">
        <style:text-properties fo:color="#c0c0c0" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_string" style:display-name="code_string" style:family="text">
        <style:text-properties fo:color="#9933CC" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_comment" style:display-name="code_comment" style:family="text">
        <style:text-properties fo:color="#009900" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_comment_tag" style:display-name="code_comment" style:family="text">
        <style:text-properties fo:color="#00dd00" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_preprocessor" style:display-name="code_preprocessor" style:family="text">
        <style:text-properties fo:color="#660000" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    <style:style style:name="code_keyword" style:display-name="code_keyword" style:family="text">
        <style:text-properties fo:color="#0000ff" style:font-name="${font_family}" fo:font-size="${font_size}" style:font-size-asian="${font_size}" style:font-size-complex="${font_size}"/>
    </style:style>
    
    <!-- This style is used for formatting pre blocks -->
    <style:style style:name="shorte_para_pre" style:family="paragraph" style:parent-style-name="shorte_standard_indented">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-left="${code_indent}cm" fo:margin-bottom="0cm"/>
        <style:text-properties style:font-name="Courier New" fo:font-size="9pt"/>
    </style:style>
    ''').substitute({"font_family" : "Courier New",
                     "font_size"   : "8.5pt",
                     "code_indent" : self.code_indent})
        

    def get_prototype_styles(self):
        
        return string.Template('''
    <!-- The background color of the table -->
    <style:style style:name="shorte_table_prototype" style:family="table">
      <style:table-properties fo:margin="0in" fo:background-color="#FAFAFA" style:shadow="none" style:writing-mode="lr-tb">
        <style:background-image/>
      </style:table-properties>
    </style:style>
    
    <style:style style:name="shorte_table_prototype_deprecated" style:family="table">
      <style:table-properties fo:margin="0in" fo:background-color="#FAFAFA" style:shadow="none" style:writing-mode="lr-tb">
        <style:background-image xlink:href="Pictures/deprecated.png" xlink:type="simple" xlink:actuate="onLoad"/>
      </style:table-properties>
    </style:style>

    <!-- The column widths for the prototype table. -->
    <style:style style:name="shorte_tablePrototype.A" style:family="table-column">
      <style:table-column-properties style:column-width="0.303cm"/>
    </style:style>

    <style:style style:name="shorte_tablePrototype.B" style:family="table-column">
      <style:table-column-properties style:column-width="0.499cm"/>
    </style:style>

    <!-- This is currently the column style for the parameter I/O definitions -->
    <style:style style:name="shorte_tablePrototype.C" style:family="table-column">
      <style:table-column-properties style:column-width="1.782cm"/>
    </style:style>
    <style:style style:name="shorte_tablePrototype.D" style:family="table-column">
      <style:table-column-properties style:column-width="14.009cm"/>
    </style:style>

    <style:style style:name="shorte_tablePrototype.1" style:family="table-row">
      <style:table-row-properties style:min-row-height="0.503cm"/>
    </style:style>
    <style:style style:name="shorte_table_prototype_name" style:family="table-cell">
      <style:table-cell-properties fo:background-color="${color_table_title}"
            fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="0.002cm solid #000000" fo:border-bottom="0.002cm solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_prototype_data" style:family="table-cell">
      <style:table-cell-properties fo:background-color="transparent"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table_prototype_parameter_header" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#e0e0e0"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.001cm solid #d0d0d0">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    
    <style:style style:name="shorte_table_prototype_parameter_data" style:family="table-cell">
      <style:table-cell-properties fo:background-color="transparent"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="none">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table_prototype_parameter_io" style:family="table-cell">
      <style:table-cell-properties fo:background-color="transparent"
        fo:padding="0.097cm" fo:border-left="none" fo:border-right="0.001cm solid #e0e0e0" fo:border-top="none" fo:border-bottom="none">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>

    <!-- This controls the cell for each section like 'Prototype', 'Parameters', 'Returns' -->
    <style:style style:name="shorte_table_prototype_definition" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#a0a0a0" fo:padding="0.097cm"
          fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000">
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
      <style:text-properties/>
    </style:style>

    <!-- This is the text of each section like 'Prototype', 'Parameters', 'Returns' -->
    <style:style style:name="para_prototype_section" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties
        fo:color="#ffffff"
        fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>

    <style:style style:name="para_prototype_code" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#000000" fo:font-weight="bold" style:font-name="Courier New" fo:font-size="10pt"/>
    </style:style>

    <style:style style:name="para_prototype_param_name" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#000000" fo:font-weight="bold" style:font-name="Courier New" fo:font-size="10pt"/>
    </style:style>
    <style:style style:name="para_prototype_param" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm" style:shadow="none"/>
      <style:text-properties fo:color="#000000" font-name="Courier New" />
    </style:style>
''').substitute({"color_table_title" : self.colors["table"]["title"].bg})
