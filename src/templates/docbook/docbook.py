# -*- coding: iso-8859-15 -*-
"""This module defines the stylesheet used for generating PDFs via
   docbook. The Apache FOP project is used to manage generating the
   actual PDF content.
"""
import string

from src.shorte_defines import *
import templates.themes

class docbook_styles(object):
    """The base class for docbook stylesheets. Individual
       templates can derive from this class to customize the
       generated output."""

    def __init__(self, theme="shorte"):
        self.m_theme = theme
        self.colors = templates.themes.theme().get_colors(theme)
        
        self.header_logo_height = "0.75in"

        self.footer_middle_text = ""

        self.hrule_color = self.colors["heading.2"].fg

    def format_admonition_styles(self):
    
        graphics_path = shorte_get_startup_path() + "/templates/shared/"
        return string.Template("""
<!-- Turn on admonition graphics -->
<xsl:param name="admon.graphics">1</xsl:param>
<xsl:param name="admon.graphics.path">${graphics_path}</xsl:param>

<xsl:template match="note" mode="admon.graphic.width">
    <xsl:text>36pt</xsl:text>
</xsl:template>

<xsl:template name="graphical.admonition">
  <xsl:variable name="id">
    <xsl:call-template name="object.id"/>
  </xsl:variable>
  <xsl:variable name="graphic.width">
     <xsl:apply-templates select="." mode="admon.graphic.width"/>
  </xsl:variable>

  <fo:block id="{$$id}"
            space-before.minimum="1em"
            space-before.optimum="1em"
            space-before.maximum="1.2em"
            start-indent="0in"
            end-indent="0in"
            border-top="0.5pt solid #c0c0c0"
            border-bottom="0.5pt solid #c0c0c0"
            padding-top="5pt"
            padding-bottom="5pt"

            xsl:use-attribute-sets="graphical.admonition.properties">
    <fo:list-block provisional-distance-between-starts="{$$graphic.width} + 12pt"
                    provisional-label-separation="12pt">
      <fo:list-item>
          <fo:list-item-label end-indent="label-end()">
            <fo:block>
              <fo:external-graphic width="auto" height="auto"
                                         content-width="{$$graphic.width}" >
                <xsl:attribute name="src">
                  <xsl:call-template name="admon.graphic"/>
                </xsl:attribute>
              </fo:external-graphic>
            </fo:block>
          </fo:list-item-label>
          <fo:list-item-body start-indent="body-start()">
            <xsl:if test="$$admon.textlabel != 0 or title or info/title">
              <fo:block xsl:use-attribute-sets="admonition.title.properties">
                <xsl:apply-templates select="." mode="object.title.markup">
                  <xsl:with-param name="allow-anchors" select="1"/>
                </xsl:apply-templates>
              </fo:block>
            </xsl:if>
            <fo:block xsl:use-attribute-sets="admonition.properties">
              <xsl:apply-templates/>
            </fo:block>
          </fo:list-item-body>
      </fo:list-item>
    </fo:list-block>
  </fo:block>
</xsl:template>
""").substitute({"graphics_path" : graphics_path})

    def format_code_styles(self):
        """This method returns the default properties for syntax highlighting
           code blocks

           @return The XSL for syntax highlighting
        """
        return string.Template("""
<!-- Syntax Highlighting -->

<!-- Code font and size -->
<xsl:attribute-set name="monospace.verbatim.properties">
  <xsl:attribute name="font-family">Courier</xsl:attribute>
  <xsl:attribute name="font-size">9pt</xsl:attribute>
  <xsl:attribute name="keep-together.within-column">always</xsl:attribute>
</xsl:attribute-set>

<!-- Code box -->
<xsl:param name="shade.verbatim" select="1"/>
<xsl:attribute-set name="shade.verbatim.style">
  <xsl:attribute name="background-color">#f0f0f0</xsl:attribute>
  <xsl:attribute name="border-width">0.5pt</xsl:attribute>
  <xsl:attribute name="border-style">solid</xsl:attribute>
  <xsl:attribute name="border-color">#c0c0c0</xsl:attribute>
  <xsl:attribute name="padding">0pt</xsl:attribute>
  <xsl:attribute name="margin">0pt</xsl:attribute>
</xsl:attribute-set>

<!-- Emphasis styles used for code highlighting -->
<xsl:template match="emphasis">
  <xsl:variable name="depth">
    <xsl:call-template name="dot.count">
      <xsl:with-param name="string">
        <xsl:number level="multiple"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:variable>
  <xsl:choose>
      <xsl:when test="@role='bold' or @role='strong'">
        <xsl:call-template name="inline.boldseq"/>
      </xsl:when>
      <xsl:when test="@role='underline'">
        <fo:inline text-decoration="underline">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='strikethrough'">
        <fo:inline text-decoration="line-through">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_object_title'">
        <fo:inline color="#000000" font-style="normal" font-weight="bold" font-size="13pt">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_object_section_title'">
        <fo:inline color="${color_codeblock_section}" font-style="normal" font-weight="bold" font-size="12pt">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_default'">
        <fo:inline color="#000000" font-style="normal">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_comment'">
        <fo:inline color="#009900">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_string'">
        <fo:inline color="#9933CC">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:when test="@role='code_keyword'">
        <fo:inline color="#0000ff">
          <xsl:call-template name="inline.charseq"/>
        </fo:inline>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$$depth mod 2 = 1">
            <fo:inline font-style="normal">
              <xsl:apply-templates/>
            </fo:inline>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="inline.italicseq"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    
  </xsl:choose>
</xsl:template>

""").substitute({"color_codeblock_section" : self.colors["codeblock.section"].fg})

    def format_hyperlink_styles(self):
        return string.Template("""
<xsl:attribute-set name="xref.properties">
    <xsl:attribute name="color">${hyperlink_color}</xsl:attribute>
    <xsl:attribute name="text-decoration">underline</xsl:attribute>
    <xsl:attribute name="font-weight">normal</xsl:attribute>
</xsl:attribute-set>
""").substitute({"hyperlink_color" : self.colors["hyperlink"].fg})

    def format_page_footer_styles(self):
        return string.Template("""
<xsl:param name="footer.column.widths">1 2.5 1</xsl:param>

<xsl:template name="footer.content">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="position" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <fo:block
      font-family="Helvetica"
      font-size="8pt"
      color="#c0c0c0"
    >

    <!-- pageclass can be front, body, back -->
    <!-- sequence can be odd, even, first, blank -->
    <!-- position can be left, center, right -->
    
        <xsl:choose>
          <xsl:when test="$$position = 'left' and $$pageclass != 'back'">
            <fo:block>
              <xsl:value-of select="ancestor-or-self::book/titleabbrev"/>
            </fo:block>
          </xsl:when>
          <xsl:when test="$$position = 'center' and $$pageclass != 'back'">
            <fo:block>
              ${middle}
            </fo:block>
          </xsl:when>
          <xsl:when test="$$position = 'center' and $$pageclass = 'back'">
            <fo:block font-weight="bold" color="#000000" font-size="9pt">
              ${middle}
            </fo:block>
            <fo:block/>
            <fo:block font-weight="bold" color="#000000" font-size="9pt">
              ~ End of Document ~
            </fo:block>
          </xsl:when>
          <xsl:when test="$$position = 'right' and $$pageclass != 'back'">
            <fo:block>
              <xsl:text>Page </xsl:text>
              <fo:page-number/>
              <xsl:text> of </xsl:text>
              <fo:page-number-citation ref-id="END_OF_DOCUMENT"/>
            </fo:block>
          </xsl:when>
        </xsl:choose>
  </fo:block>
</xsl:template>

<!-- Draw the border on the footer -->
<xsl:template name="foot.sep.rule">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <xsl:if test="$$footer.rule != 0 and $$pageclass != 'back'">
      <xsl:attribute name="border-top-width">0.5pt</xsl:attribute>
      <xsl:attribute name="border-top-style">solid</xsl:attribute>
      <xsl:attribute name="border-top-color">#c0c0c0</xsl:attribute>
  </xsl:if>
</xsl:template>
""").substitute({"middle" : self.footer_middle_text})

    
    def format_page_header_styles(self):
        return string.Template("""<xsl:template name="header.content">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="position" select="''"/>
  <xsl:param name="gentext-key" select="''"/>
<!-- Was verdana -->
  <fo:block
      font-family="Helvetica"
      font-size="8pt"
      color="#c0c0c0"
    >

    <!-- sequence can be odd, even, first, blank -->
    <!-- position can be left, center, right -->
    <xsl:choose>

      <xsl:when test="$$position='left' and $$pageclass!='back'">
        <!-- Same for odd, even, empty, and blank sequences -->
        <fo:block>
          <!-- 27133 replaces the title in the header with titleabbrev
          <xsl:value-of select="ancestor-or-self::book/title"/> -->
          <xsl:value-of select="ancestor-or-self::book/titleabbrev"/>
          <!-- 27133 end -->
        </fo:block>
        <fo:block>
          <xsl:value-of select="ancestor-or-self::book/subtitle"/>
        </fo:block>
        <fo:block>
          <xsl:value-of select="ancestor-or-self::book/bookinfo/productnumber"/>,
          <xsl:call-template name="gentext.space"/>Revision
          <xsl:call-template name="gentext.space"/>
          <xsl:value-of select="ancestor-or-self::book/bookinfo/edition"/>
        </fo:block>
        <fo:block>
          <xsl:value-of select="ancestor-or-self::book/bookinfo/date"/>
        </fo:block>
      </xsl:when>

      <!-- 27133 adds the logo to the header -->
      <xsl:when test="$$position='center' and $$pageclass!='back'">
        <fo:external-graphic content-height="${header_logo_height}">
          <xsl:attribute name="src">
            <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$$header.image.filename"/>
            </xsl:call-template>
          </xsl:attribute>
        </fo:external-graphic>
      </xsl:when>

      <!-- 27133 end -->
      <!-- 27133 adds the section name to the header -->
      <xsl:when test="$$position='right' and $$pageclass!='back'">
        <fo:block>
            <xsl:apply-templates select="." mode="object.title.markup"/>
        </fo:block>
      </xsl:when>
      <!-- 27133 end -->
    </xsl:choose>
  </fo:block>
</xsl:template>

<!-- Draw the border on the header -->
<xsl:template name="head.sep.rule">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <xsl:if test="$$header.rule != 0 and $$pageclass != 'back'">
      <xsl:attribute name="border-bottom-width">0.5pt</xsl:attribute>
      <xsl:attribute name="border-bottom-style">solid</xsl:attribute>
      <xsl:attribute name="border-bottom-color">#c0c0c0</xsl:attribute>
  </xsl:if>
</xsl:template>
""").substitute({"header_logo_height" : self.header_logo_height})


    def format_quote_styles(self):
        return '''<!-- Quote block properties -->
<xsl:attribute-set name="blockquote.properties">
    <xsl:attribute name="margin-left">0.5em</xsl:attribute>
    <xsl:attribute name="padding-left">0.5em</xsl:attribute>
    <xsl:attribute name="border-left">2pt solid #c0c0c0</xsl:attribute>
</xsl:attribute-set>
'''
    def format_revision_history_styles(self):
        return '''

<!-- Revision history formatting -->
<xsl:attribute-set name="revhistory.title.properties">
  <xsl:attribute name="font-size">18pt</xsl:attribute>
  <xsl:attribute name="font-weight">bold</xsl:attribute>
  <xsl:attribute name="text-align">center</xsl:attribute>
  <xsl:attribute name="padding">0px</xsl:attribute>
  <xsl:attribute name="break-before">page</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="revhistory.table.properties">
  <xsl:attribute name="border">0.5pt solid #c0c0c0</xsl:attribute>
  <xsl:attribute name="width">50%</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="revhistory.table.cell.properties">
  <xsl:attribute name="border">0.5pt solid #c0c0c0</xsl:attribute>
  <xsl:attribute name="font-size">9pt</xsl:attribute>
  <xsl:attribute name="padding">4pt</xsl:attribute>
</xsl:attribute-set>

<!-- Override the styles for the revision history table -->
<xsl:template match="revhistory" mode="titlepage.mode">

  <xsl:variable name="explicit.table.width">
    <xsl:call-template name="pi.dbfo_table-width"/>
  </xsl:variable>

  <xsl:variable name="table.width">
    <xsl:choose>
      <xsl:when test="$explicit.table.width != ''">
        <xsl:value-of select="$explicit.table.width"/>
      </xsl:when>
      <xsl:when test="$default.table.width = ''">
        <xsl:text>100%</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$default.table.width"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

 <fo:table table-layout="fixed" width="{$table.width}" xsl:use-attribute-sets="revhistory.table.properties">
    <fo:table-column column-number="1" column-width="proportional-column-width(1)"/>
    <fo:table-column column-number="2" column-width="proportional-column-width(2)"/>
    <fo:table-column column-number="3" column-width="proportional-column-width(1)"/>
    <fo:table-column column-number="4" column-width="proportional-column-width(6)"/>
    <fo:table-body start-indent="0pt" end-indent="0pt">
      <fo:table-row>
        <fo:table-cell number-columns-spanned="4" background-color="#c0c0c0" xsl:use-attribute-sets="revhistory.table.cell.properties">
          <fo:block xsl:use-attribute-sets="revhistory.title.properties">
            <xsl:choose>
              <xsl:when test="title|info/title">
                  <xsl:apply-templates select="title|info/title" mode="titlepage.mode"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:call-template name="gentext">
                  <xsl:with-param name="key" select="'RevHistory'"/>
                </xsl:call-template>
              </xsl:otherwise>
            </xsl:choose>
          </fo:block>
        </fo:table-cell>
      </fo:table-row>
      <xsl:apply-templates select="*[not(self::title)]" mode="titlepage.mode"/>
    </fo:table-body>
  </fo:table>

</xsl:template>


<xsl:template match="revhistory/revision" mode="titlepage.mode">
  <xsl:variable name="revnumber" select="revnumber"/>
  <xsl:variable name="revdate"   select="date"/>
  <xsl:variable name="revauthor" select="authorinitials|author"/>
  <xsl:variable name="revremark" select="revremark|revdescription"/>
  <xsl:variable name="bgcolor">
    <xsl:call-template name="pi.dbfo_bgcolor"/>
  </xsl:variable>
  
  <fo:table-row>
    <fo:table-cell xsl:use-attribute-sets="revhistory.table.cell.properties">
      <xsl:if test="$bgcolor != ''">
        <xsl:attribute name="background-color">
          <xsl:value-of select="$bgcolor"/>
        </xsl:attribute>
      </xsl:if>
      <fo:block>
        <xsl:if test="$revnumber">
            <!--<xsl:call-template name="gentext">
            <xsl:with-param name="key" select="'Revision'"/>
          </xsl:call-template>
          <xsl:call-template name="gentext.space"/>
          -->
          <xsl:apply-templates select="$revnumber[1]" mode="titlepage.mode"/>
        </xsl:if>
      </fo:block>
    </fo:table-cell>
    <fo:table-cell xsl:use-attribute-sets="revhistory.table.cell.properties">
      <xsl:if test="$bgcolor != ''">
        <xsl:attribute name="background-color">
          <xsl:value-of select="$bgcolor"/>
        </xsl:attribute>
      </xsl:if>
      <fo:block>
        <xsl:apply-templates select="$revdate[1]" mode="titlepage.mode"/>
      </fo:block>
    </fo:table-cell>
    <fo:table-cell xsl:use-attribute-sets="revhistory.table.cell.properties">
      <xsl:if test="$bgcolor != ''">
        <xsl:attribute name="background-color">
          <xsl:value-of select="$bgcolor"/>
        </xsl:attribute>
      </xsl:if>
      <fo:block>
        <xsl:for-each select="$revauthor">
          <xsl:apply-templates select="." mode="titlepage.mode"/>
          <xsl:if test="position() != last()">
            <xsl:text>, </xsl:text>
          </xsl:if>
        </xsl:for-each>
      </fo:block>
    </fo:table-cell>
  <xsl:if test="$revremark">
      <fo:table-cell xsl:use-attribute-sets="revhistory.table.cell.properties">
        <xsl:if test="$bgcolor != ''">
          <xsl:attribute name="background-color">
            <xsl:value-of select="$bgcolor"/>
          </xsl:attribute>
        </xsl:if>
        <fo:block>
          <xsl:apply-templates select="$revremark[1]" mode="titlepage.mode"/>
        </fo:block>
      </fo:table-cell>
  </xsl:if>
    </fo:table-row>
</xsl:template>

<!-- customize this template to add row properties -->
<xsl:template name="revhistory.table.revision.properties">

  <xsl:variable name="row-height">
    <xsl:if test="processing-instruction('dbfo')">
      <xsl:call-template name="pi.dbfo_row-height"/>
    </xsl:if>
  </xsl:variable>

  <xsl:if test="$row-height != ''">
    <xsl:attribute name="block-progression-dimension">
      <xsl:value-of select="$row-height"/>
    </xsl:attribute>
  </xsl:if>

  <xsl:variable name="bgcolor">
    <xsl:call-template name="pi.dbfo_bgcolor"/>
  </xsl:variable>

  <xsl:if test="$bgcolor != ''">
    <xsl:attribute name="background-color">
      <xsl:value-of select="$bgcolor"/>
    </xsl:attribute>
  </xsl:if>

  <!-- Keep header row with next row -->
  <xsl:if test="ancestor::thead">
    <xsl:attribute name="keep-with-next.within-column">always</xsl:attribute>
  </xsl:if>

</xsl:template>

<xsl:template match="revision/revnumber" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="revision/date" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="revision/authorinitials" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="revision/author" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="revision/revremark" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="revision/revdescription" mode="titlepage.mode">
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>
'''

    def format_table_styles(self):
        return '''
<xsl:attribute-set name="table.cell.padding">
    <xsl:attribute name="padding-left">0.05in</xsl:attribute>
    <xsl:attribute name="padding-right">0.05in</xsl:attribute>
    <xsl:attribute name="padding-top">0.05in</xsl:attribute>
    <xsl:attribute name="padding-bottom">0.05in</xsl:attribute>
</xsl:attribute-set>
'''


    def format_titlepage_styles(self):
        return string.Template('''
<xsl:template name="book.titlepage.recto">
  <!-- 27133: Big logo on the titlepage -->
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/mediaobject"/>
  <!-- 27133 end -->
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/mediaobject"/>
  <xsl:choose>
    <xsl:when test="bookinfo/title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/title"/>
    </xsl:when>
    <xsl:when test="info/title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/title"/>
    </xsl:when>
    <xsl:when test="title">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="title"/>
    </xsl:when>
  </xsl:choose>

  <xsl:choose>
    <xsl:when test="bookinfo/subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/subtitle"/>
    </xsl:when>
    <xsl:when test="info/subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="info/subtitle"/>
    </xsl:when>
    <xsl:when test="subtitle">
      <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="subtitle"/>
    </xsl:when>
  </xsl:choose>
  <fo:block>
    <fo:leader
      leader-length="100%"
      leader-pattern="rule"
      rule-style="solid"
      rule-thickness="0.25in"
      color="${hr_color}"/>
  </fo:block>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/date"/>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/productnumber"/>
  <xsl:apply-templates mode="book.titlepage.recto.auto.mode" select="bookinfo/edition"/>
</xsl:template>

<xsl:template match="edition" mode="titlepage.mode">
  Revision <xsl:call-template name="gentext.space"/>
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>

<xsl:template match="productnumber" mode="titlepage.mode">
  Document Number<xsl:call-template name="gentext.space"/>
  <xsl:apply-templates mode="titlepage.mode"/>
</xsl:template>
''').substitute({"hr_color" : self.hrule_color})


    def get_template(self, status):
        
        xml = self.format_admonition_styles()
        xml += self.format_code_styles()
        xml += self.format_hyperlink_styles()
        xml += self.format_page_header_styles()
        xml += self.format_page_footer_styles()
        xml += self.format_quote_styles()
        xml += self.format_revision_history_styles()
        xml += self.format_table_styles()
        xml += self.format_titlepage_styles()

        xsl_title_page = shorte_get_startup_path() + "/templates/docbook/titlepage.xsl"

        xml_status = ""
        if(status == "draft"):
            xml_status = """
<!-- 27133: Turn on the watermark -->
<xsl:param name="draft.mode">yes</xsl:param>
<xsl:param name="draft.watermark.image">draft.png</xsl:param>
<!-- 27133 end -->
"""
        
        docbook_xsl_path = shorte_get_config("docbook", "path.docbook.xsl", True)

        return string.Template("""<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format">

<xsl:import href="${docbook_xsl_path}"/>

<xsl:import href="${titlepage}"/>

<!-- 27133: Turn off full justification -->
<xsl:attribute-set name="root.properties">
  <xsl:attribute name="text-align">left</xsl:attribute>
</xsl:attribute-set>
<!-- 27133 end -->

<!-- 27133: Filename of the logo that goes in the header -->
<xsl:param name="header.image.filename">logo.png</xsl:param>
<!-- 27133 end -->

<xsl:param name="ignore.image_scaling" select="0"></xsl:param>

${status}

<!-- Turn off indenting body text -->
<xsl:param name="body.start.indent">0pt</xsl:param>

<xsl:attribute-set name="colophon.properties">
  <xsl:attribute name="text-align">center</xsl:attribute>
</xsl:attribute-set>

<!-- Change section title color -->
<xsl:attribute-set name="component.title.properties">
  <xsl:attribute name="color">${h1_color}</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="section.title.level1.properties">
  <xsl:attribute name="color">${h2_color}</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="section.title.level2.properties">
  <xsl:attribute name="color">${h3_color}</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="section.title.level3.properties">
  <xsl:attribute name="color">${h4_color}</xsl:attribute>
</xsl:attribute-set>
<xsl:attribute-set name="section.title.level4.properties">
  <xsl:attribute name="color">${h5_color}</xsl:attribute>
</xsl:attribute-set>

<xsl:param name="body.margin.top">1.0in</xsl:param>
<xsl:param name="body.font.family">Helvetica</xsl:param>
<xsl:param name="body.font.master">11</xsl:param>
<xsl:param name="section.autolabel">1</xsl:param>
<xsl:param name="section.label.includes.component.label">1</xsl:param>
<xsl:param name="toc.section.depth">5</xsl:param>

<!-- Don't show hyperlink target URLs in the document -->
<xsl:param name="ulink.show">0</xsl:param>

<!-- This turns on PDF bookmarks when run on 10.243.10.2 -->
<xsl:param name="fop1.extensions">1</xsl:param>

<xsl:template name="initial.page.number">auto</xsl:template>
<xsl:template name="page.number.format">1</xsl:template>

<xsl:template match="para[@align]">
    <fo:block text-align="{@align}">
        <xsl:apply-templates/>
    </fo:block>
</xsl:template>

${styles}

</xsl:stylesheet>
""").substitute({"styles" : xml,
                 "status" : xml_status,
                 "h1_color" : self.colors["heading.1"].fg,
                 "h2_color" : self.colors["heading.2"].fg,
                 "h3_color" : self.colors["heading.3"].fg,
                 "h4_color" : self.colors["heading.4"].fg,
                 "h5_color" : self.colors["heading.5"].fg,
                 "titlepage" : xsl_title_page,
                 "docbook_xsl_path" : docbook_xsl_path})


