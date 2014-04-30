import string

class styles():
    def __init__(self):
        
        self.table_indent = 0
        self.list_bullet_indent  = 0.75

        self.list_bullet_base  = 0

        # This is the indent for the text after a bullet point
        #self.list_bullet_text_indent = 1.2

        # If you don't care to use checkboxes or images
        # in lists then this can be changed to 0.4 - 0.5   
        self.list_bullet_text_indent = 0.7

        # This is the common indent for the entire document
        self.standard_indent = 0
    
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
       

    def get_table_styles(self):
        # Table Styles
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
    <style:style style:name="shorte_table.header" style:family="table-cell">
      <style:table-cell-properties
            fo:background-color="#D0D0D0"
            fo:padding="0.0182in"
            fo:border="0.002in solid #000000" >
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.subheader" style:family="table-cell">
      <style:table-cell-properties
         fo:background-color="#E1E8EF"
         fo:padding="0.0182in"
         fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.reserved" style:family="table-cell">
        <style:table-cell-properties
            fo:background-color="#f0f0f0" fo:padding="0.0182in"
            fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.title" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#0057A6" fo:padding="0.0282in"
        fo:border="0.002in solid #000000">
        <style:background-image/>
      </style:table-cell-properties>
    </style:style>
    <style:style style:name="shorte_table.normal_cell" style:family="table-cell">
      <style:table-cell-properties fo:padding="0.0182in"
          fo:border="0.002in solid #000000"/>
    </style:style>
    
    
    <!-- Table Cell Paragraph Styles -->
    <style:style style:name="shorte_table_title" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#ffffff" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    
    <style:style style:name="shorte_table_heading" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#000000" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    
    <style:style style:name="shorte_table_subheading" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#000000" fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
    </style:style>
    
    <style:style style:name="shorte_table_standard" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#000000"/>
    </style:style>
    
    <style:style style:name="shorte_table_reserved" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0in" fo:margin-bottom="0in"/>
      <style:text-properties fo:color="#000000"/>
    </style:style>
    
    ''').substitute({"table_indent" : self.table_indent})


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

            # DEBUG BRAD: This controls the indent after the bullet
            indent = self.standard_indent + self.list_bullet_base + self.list_bullet_text_indent + (self.list_bullet_indent * (level-1))

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

            indent = self.standard_indent + self.list_bullet_base + self.list_bullet_text_indent + (self.list_bullet_indent * (level-1))

            if(level in [1,4,7]):
                num_format = '1'
            elif(level in [2,5,8]):
                num_format = 'a'
            else:
                num_format = 'i'
                
            text_indent = -0.935
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

