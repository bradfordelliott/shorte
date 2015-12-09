# -*- coding: iso-8859-15 -*-
import string

from src.shorte_defines import *
from templates.docbook.docbook import docbook_styles

class custom_styles(docbook_styles):

    def __init__(self):

        docbook_styles.__init__(self, "shorte")
        self.header_logo_height = "0.35in"
        self.footer_middle_text = "https://github.com/bradfordelliott/shorte"

    def format_title_page(self, engine, doc_info, revision_history):
        logo = shorte_path_to_url(shorte_get_startup_path() + "/templates/docbook/shorte/shorte.png")

        return string.Template('''
<bookinfo>
    <title>${title_long}</title>
    <date>${date}</date>
    <titleabbrev>${title_short}</titleabbrev>
    <subtitle>${subtitle}</subtitle>
    <copyright>
        <year>${year}</year>
        <holder>Brad Elliott, All rights reserved.</holder>
    </copyright>
    <legalnotice>
        <para><emphasis role="strong">This section is TBD</emphasis></para>
    </legalnotice>
    <edition>${doc_version}</edition>
    <productnumber>${doc_number}</productnumber>
    ${revision_history}
    <mediaobject>
      <imageobject>
        <imagedata fileref="${logo}" width="5in" format="PNG"/>
      </imageobject>
    </mediaobject>
</bookinfo>
''').substitute({"date"        : engine.get_date(),
                 "year"        : engine.get_year(),
                 "title_long"  : engine.get_title(),
                 "title_short" : engine.get_title(),
                 "subtitle"    : engine.get_subtitle(),
                 "doc_number"  : doc_info.number(),
                 "doc_version" : doc_info.version(),
                 "revision_history" : revision_history,
                 "logo"        : logo})

    
    def format_last_page(self):
        """This method formats the final page of the document. It uses the
           <colophon> tag to style the page.
           
           @return The contents of the final page
        """
        
        logo = shorte_path_to_url(shorte_get_startup_path() + "/templates/docbook/shorte/shorte.png")

        return string.Template("""
<colophon id="END_OF_DOCUMENT">
<title></title>
<mediaobject align="center">
  <imageobject align="center">
    <imagedata fileref="${logo}" align="center" width="4in" format="PNG"/>
  </imageobject>
</mediaobject>
<para></para>
<para></para>
<para align="center"><emphasis role="strong">For more information see:</emphasis></para>
<para></para>
<para></para>
<para align="center"><ulink url="https://github.com/bradfordelliott/shorte">https://github.com/bradfordelliott/shorte</ulink></para>
</colophon>
""").substitute({"logo" : logo})


