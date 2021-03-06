import string

from templates.odt.odt_styles import *
import templates.themes

class custom_styles(styles):
    def __init__(self):
        styles.__init__(self)
        
        self.table_indent = 0.5
        #self.table_indent = 0.65
        #self.list_bullet_indent  = 0.2
        #self.list_bullet_base    = 2.5
        self.standard_indent = 0
        self.standard_indented = 0.25
        
        self.colors = templates.themes.theme().get_colors("shorte")

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
        <style:text-properties fo:color="${color_heading}" style:font-name="Arial2" fo:font-family="Arial"
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
                "font_size"     : font_size,
                "color_heading" : self.colors["heading.%d" % heading].fg})
    
        list_styles = self.get_list_styles()

        common_styles = self.get_common_styles()

        # Table Styles
        table_styles = self.get_table_styles()

        prototype_styles = self.get_prototype_styles()

        source_code_styles = self.get_source_code_styles()
    
        custom_styles = string.Template('''
    <style:style style:name="shorte_standard" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.4cm" fo:margin-left="${standard_indent}cm"/>
      <style:text-properties style:font-name="Helvetica Neue" fo:color="#000000" fo:font-size="11.5pt"/>
    </style:style>
    <style:style style:name="shorte_standard_indented" style:family="paragraph" style:parent-style-name="shorte_standard">
      <style:paragraph-properties fo:margin-top="0.4cm" fo:margin-bottom="0.4cm" fo:margin-left="${standard_indented}cm"/>
      <style:text-properties fo:color="#000000"/>
    </style:style>

    ${common_styles}
    
    ${heading_styles}
    
    $table_styles
    
    <!-- List styles -->
    $list_styles

    <!-- Prototype styles -->
    $prototype_styles
    
    $source_code_styles

    ''').substitute({
         "heading_styles"       : heading_styles,
         "list_styles"          : list_styles,
         "table_styles"         : table_styles,
         "prototype_styles"     : prototype_styles,
         "standard_indent"      : self.standard_indent,
         "standard_indented"    : self.standard_indented,
         "common_styles"        : common_styles,
         "source_code_styles"   : source_code_styles})
    
        return custom_styles
