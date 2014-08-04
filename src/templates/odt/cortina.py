import string

from templates.odt.odt_styles import *

class custom_styles(styles):
    def __init__(self):
        styles.__init__(self)
        
        #self.list_bullet_indent  = 0.2
        #self.list_bullet_base    = 2.5
        self.standard_indent = 0.5
        self.table_indent = 0.5

    def custom_styles(self):

        heading_styles = ''
    
        # Heading Styles
        for heading in [1,2,3,4,5,6]:
            break_before = ''
            if(heading == 1):
                break_before = 'fo:break-before="page"'
    
            margin_bottom = 'fo:margin-bottom="0.235cm"'
            margin_left   = 'fo:margin-left="-0.3cm"'
    
            if(heading == 1):
                font_size     = 'fo:font-size="14pt"'
            elif(heading == 2):
                font_size     = 'fo:font-size="13pt"'
            else:
                font_size     = 'fo:font-size="12pt"'
    
    
            heading_styles += string.Template('''
    <style:style style:name="Heading_20_${level}" style:display-name="Heading ${level}" style:family="paragraph"
            style:parent-style-name="Standard" style:next-style-name="Standard" style:default-outline-level="${level}" style:class="text" style:master-page-name="">
    	<style:paragraph-properties ${margin_left} fo:margin-right="0cm" fo:margin-top="0.212cm" ${margin_bottom}
            style:contextual-spacing="false" fo:keep-together="always" fo:text-indent="0cm" style:auto-text-indent="false"
            style:page-number="auto"
            ${break_before} fo:keep-with-next="always">
    		<style:tab-stops/>
    	</style:paragraph-properties>
    	<style:text-properties fo:color="#0063a5" style:font-name="Arial2" fo:font-family="Arial"
            style:font-style-name="Bold" style:font-family-generic="swiss" style:font-pitch="variable"
            ${font_size} fo:font-weight="bold" style:font-name-asian="Times New Roman"
            style:font-family-asian="&apos;Times New Roman&apos;" style:font-family-generic-asian="roman"
            style:font-name-complex="Times New Roman" style:font-family-complex="&apos;Times New Roman&apos;" 
            />
    </style:style>
    ''').substitute({
                "level" : heading,
                "break_before" : break_before,
                "margin_bottom" : margin_bottom,
                "margin_left"   : margin_left,
                "font_size"     : font_size})
    
        list_styles = self.get_list_styles()

        # Table Styles
        table_styles = self.get_table_styles()
    
        custom_styles = string.Template('''
    <style:style style:name="shorte_standard" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.4cm" fo:margin-left="${standard_indent}cm"/>
      <style:text-properties fo:color="#000000"/>
    </style:style>
    
    ${heading_styles}
    
    $table_styles
    
    <!-- List styles -->
    $list_styles
    ''').substitute(
            {
         "heading_styles" : heading_styles,
         "list_styles" : list_styles,
         "table_styles" : table_styles,
         "standard_indent" : self.standard_indent})
    
        return custom_styles
