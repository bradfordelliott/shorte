# -*- coding: iso-8859-15 -*-
import string

from src.shorte_defines import *

class docbook_styles():

    def format_code_styles(self):
        """This method returns the default properties for syntax highlighting
           code blocks

           @return The XSL for syntax highlighting
        """
        return """
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
        <fo:inline color="#ff0000" font-style="normal" font-weight="bold" font-size="12pt">
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
          <xsl:when test="$depth mod 2 = 1">
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

"""

    def format_page_footer_styles(self):
        return """
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
          <xsl:when test="$position = 'left' and $pageclass != 'back'">
            <fo:block>
              <xsl:value-of select="ancestor-or-self::book/titleabbrev"/>
            </fo:block>
<!--            <fo:block>
            </fo:block>-->
          </xsl:when>
          <xsl:when test="$position = 'center' and $pageclass != 'back'">
            <fo:block>
              Inphi Corporation Proprietary and Confidential - Under NDA
            </fo:block>
          </xsl:when>
          <xsl:when test="$position = 'center' and $pageclass = 'back'">
            <fo:block font-weight="bold" color="#000000" font-size="9pt">
              Inphi Corporation Proprietary and Confidential - Under NDA
            </fo:block>
            <fo:block/>
            <fo:block font-weight="bold" color="#000000" font-size="9pt">
              ~ End of Document ~
            </fo:block>
          </xsl:when>
          <xsl:when test="$position = 'right' and $pageclass != 'back'">
            <fo:block>
              <xsl:text>Page </xsl:text>
              <fo:page-number/>
              <xsl:text> of </xsl:text>
              <fo:page-number-citation ref-id="END_OF_DOCUMENT"/>
            </fo:block>
<!--            <fo:block>
            </fo:block>-->
          </xsl:when>
        </xsl:choose>


<!--      <xsl:otherwise>
      </xsl:otherwise>
    </xsl:choose>-->
  </fo:block>
</xsl:template>

<!-- Draw the border on the footer -->
<xsl:template name="foot.sep.rule">
  <xsl:param name="pageclass" select="''"/>
  <xsl:param name="sequence" select="''"/>
  <xsl:param name="gentext-key" select="''"/>

  <xsl:if test="$footer.rule != 0 and $pageclass != 'back'">
      <xsl:attribute name="border-top-width">0.5pt</xsl:attribute>
      <xsl:attribute name="border-top-style">solid</xsl:attribute>
      <xsl:attribute name="border-top-color">#c0c0c0</xsl:attribute>
  </xsl:if>
</xsl:template>
"""
    
    def format_page_header_styles(self):
        return """<xsl:template name="header.content">
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

      <xsl:when test="$position='left' and $pageclass!='back'">
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
      <xsl:when test="$position='center' and $pageclass!='back'">
        <fo:external-graphic content-height="0.75in">
          <xsl:attribute name="src">
            <xsl:call-template name="fo-external-image">
                <xsl:with-param name="filename" select="$header.image.filename"/>
            </xsl:call-template>
          </xsl:attribute>
        </fo:external-graphic>
      </xsl:when>

      <!-- 27133 end -->
      <!-- 27133 adds the section name to the header -->
      <xsl:when test="$position='right' and $pageclass!='back'">
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

  <xsl:if test="$header.rule != 0 and $pageclass != 'back'">
      <xsl:attribute name="border-bottom-width">0.5pt</xsl:attribute>
      <xsl:attribute name="border-bottom-style">solid</xsl:attribute>
      <xsl:attribute name="border-bottom-color">#c0c0c0</xsl:attribute>
  </xsl:if>
</xsl:template>
"""


    def format_quote_styles(self):
        return '''<!-- Quote block properties -->
<xsl:attribute-set name="blockquote.properties">
    <xsl:attribute name="margin-left">0.5em</xsl:attribute>
    <xsl:attribute name="padding-left">0.5em</xsl:attribute>
    <xsl:attribute name="border-left">2pt solid #c0c0c0</xsl:attribute>
</xsl:attribute-set>
'''

    def get_template(self):
        xml = """
"""
        xml += self.format_page_header_styles()
        xml += self.format_page_footer_styles()
        xml += self.format_code_styles()
        xml += self.format_quote_styles()

        return xml


