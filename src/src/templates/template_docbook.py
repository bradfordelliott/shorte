# -*- coding: iso-8859-15 -*-
import re
import os
import string
import subprocess
from string import Template

from src.shorte_defines import *
from template_markdown import *

class template_docbook_t(template_markdown_t):
    def __init__(self, engine, indexer):
        template_markdown_t.__init__(self, engine, indexer)

        self.list_indent_per_level=2
        self.m_contents = ''
    
    def get_index_name(self):
        name = self.m_engine.get_document_name()
        return "%s" % name
    
    def format_revision_history(self):
        
        history = self.m_engine.get_doc_info().revision_history()
        #if(history != None):
        #    history.title = "Revision History"
        #    history = self.format_table("", history)
        #else:
        #    history = ""

        return '''<revhistory>
      <revision>
        <revnumber>0.5</revnumber>
        <date>January 17, 2011</date>
        <authorinitials>RS</authorinitials>
        <revremark>Initial release.</revremark>
      </revision>
      <revision>
        <revnumber>0.6</revnumber>
        <date>March 31, 2011</date>
        <authorinitials>CW</authorinitials>
        <revremark>Updates corresponding to release 0.6 of the software API.</revremark>
      </revision>
      <revision>
        <revnumber>0.7</revnumber>
        <date>May 16, 2011</date>
        <authorinitials>CW</authorinitials>
        <revremark>Updates corresponding to release of the software API.</revremark>
      </revision>
      <revision>
        <revnumber>1.0</revnumber>
        <date>July 1, 2011</date>
        <authorinitials>CW</authorinitials>
        <revremark>Updates corresponding to release 1.0 of the software API.</revremark>
      </revision>
      <revision>
        <revnumber>1.0.1</revnumber>
        <date>September 2, 2011</date>
        <authorinitials>CW</authorinitials>
        <revremark>Updates corresponding to release 1.0.1 of the software API.</revremark>
      </revision>
      <revision>
        <revnumber>1.0.2</revnumber>
        <date>October 12, 2011</date>
        <authorinitials>CW</authorinitials>
        <revremark>Updates corresponding to release 1.0.2 of the software API.</revremark>
      </revision>
        <revision>
        <revnumber>1.9.0</revnumber>
        <date>February 5, 2013</date>
        <authorinitials>CW</authorinitials>
        <revremark>Removed empty subsections and chapters</revremark>
      </revision>

    </revhistory>
    '''

    def generate_index(self, title, theme, version):
        
        cnts = ''

        if(True == to_boolean(shorte_get_config("markdown", "include_toc"))):
            cnts += '''
# Table of Contents
'''
            for topic in self.m_indexer.m_topics:
                name = topic.get_name()
                indent = topic.get_indent()
                file = os.path.basename(topic.get_file())

                if(True == self.m_inline):
                    file = self.get_index_name()

                link = name.lower()
                link = re.sub(" +", "-", link)

                if(indent == 1):
                    cnts += "- [%s](#%s)\n" % (name,link)
                elif(indent == 2):
                    cnts += "  - [%s](#%s)\n" % (name,link)
                elif(indent == 3):
                    cnts += "    - [%s](#%s)\n" % (name,link)
                elif(indent == 4):
                    cnts += "      - [%s](#%s)\n" % (name,link)
                elif(indent == 5):
                    cnts += "        - [%s](#%s)\n" % (name,link)

            cnts += "\n\n"

        cnts = ''

        cnts += self.get_contents()

        output_file = self.m_engine.m_output_directory + os.sep + self.get_index_name()
        markdown_file = output_file + ".md"
        docbook_file  = output_file + ".xml"
        pdf_file      = output_file + ".pdf"
        xsl_file = "templates/docbook/inphi/inphi.xsl"
        
        file = open(markdown_file, "wb")
        file.write(cnts)
        file.close()

        # Now use pandoc to convert to docbook
        cmd = ["/opt/local/bin/pandoc", "-s", "-S", "-t", "docbook", markdown_file, "-o", docbook_file]

        phandle = subprocess.Popen(cmd, stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)
        result = phandle.stdout.read()
        #result += phandle.stderr.read()
        phandle.wait()
  

        title_page = string.Template('''
<bookinfo>
    <title>${title_long}</title>
    <date>${date}</date>
    <titleabbrev>${title_short}</titleabbrev>
    <subtitle>${subtitle}</subtitle>
    <copyright>
        <year>${year}</year>
        <holder>Inphi Corporation, Inc. All rights reserved.</holder>
    </copyright>
    <legalnotice>
        <para><emphasis role="strong">Inphi Corporation Proprietary and Confidential—Under NDA</emphasis></para>
        <para>This document contains information proprietary to Inphi Corporation, Inc. (Inphi). Any use or disclosure, in whole or in part, of this information to any unauthorized party, for any purposes other than that for which it is provided is expressly prohibited except as authorized by Inphi in writing. Inphi reserves its rights to pursue both civil and criminal penalties for copying or disclosure of this material without authorization.</para>
        <para><emphasis role="strong">INFORMATION IN THIS DOCUMENT IS PROVIDED IN CONNECTION WITH INPHI CORPORATION® PRODUCTS.</emphasis></para>
        <para><emphasis role="strong">NO LICENSE, EXPRESS OR IMPLIED, BY ESTOPPEL OR OTHERWISE, TO ANY INTELLECTUAL PROPERTY RIGHTS IS GRANTED BY THIS DOCUMENT.</emphasis></para>
        <para><emphasis role="strong">EXCEPT AS PROVIDED IN INPHI’S TERMS AND CONDITIONS OF SALE OF SUCH PRODUCTS, INPHI ASSUMES NO LIABILITY WHATSOEVER, AND INPHI DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTY RELATING TO THE SALE AND/OR USE OF INPHI PRODUCTS, INCLUDING LIABILITY OR WARRANTIES RELATING TO FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR INFRINGEMENT OF ANY PATENT, COPYRIGHT OR OTHER INTELLECTUAL PROPERTY RIGHT.</emphasis></para>
        <para>Inphi products are not intended for use in medical, life saving, life sustaining, critical control or safety systems, or in nuclear facility applications.</para>
        <para>INPHI CORPORATION®, INPHI®, and the Inphi Logo are trademarks or registered trademarks of Inphi Corporation, Inc. or its subsidiaries in the US and other countries. Any other product and company names are the trademarks of their respective owners.</para>
    </legalnotice>
    <edition>${doc_version}</edition>
    <productnumber>${doc_number}</productnumber>
    ${revision_history}
    <mediaobject>
      <imageobject>
        <imagedata fileref="${logo}" width="6in" format="PNG"/>
      </imageobject>
    </mediaobject>
</bookinfo>
''').substitute({"date"        : self.m_engine.get_date(),
                 "year"        : self.m_engine.get_year(),
                 "title_long"  : self.m_engine.get_title(),
                 "title_short" : self.m_engine.get_title(),
                 "subtitle"    : self.m_engine.get_subtitle(),
                 "doc_number"  : "N/A",
                 "doc_version" : "N/A",
                 "revision_history" : self.format_revision_history(),
                 "logo"        : shorte_get_startup_path() + os.sep + "templates" + os.sep + "docbook" + os.sep + "inphi" + os.sep + "inphi.png"})

        handle = open(docbook_file, "rt")
        contents = handle.read()
        handle.close()

        handle = open(docbook_file, "w")
        contents = re.sub("""<articleinfo>
    <title></title>
  </articleinfo>
""", title_page, contents)
        contents = re.sub("<sect1 ", '<sect1 status="draft" ', contents)


        contents = re.sub("</article>", "", contents) 

        contents += '<appendix>'
        contents += "<title>Colophon</title>"
        contents += "<para>For Additional Product and Ordering Information:</para>"
        contents += "<para>http:/www.inphi.com</para>"
        contents += "</appendix>"
        contents += "</book>"

        handle.write(contents)
        handle.close()

        
        cmd = ["/Users/belliott/fop/fop-2.0/fop", "-c", "/Users/belliott/fop/fop-2.0/conf/fop.xconf",
                "-param", "template_path", shorte_get_startup_path() + "/templates/docbook",
                "-param", "header.image.filename", "/Users/belliott/Dropbox/shorte/src/templates/docbook/inphi/inphi_banner.png",
                "-param", "draft.watermark.image", "/Users/belliott/Dropbox/shorte/src/templates/shared/draft2.png",
                "-xml", docbook_file,
                "-xsl", xsl_file, "-pdf", pdf_file]
        phandle = subprocess.Popen(cmd, stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)
        result = phandle.stdout.read()
        #result += phandle.stderr.read()
        phandle.wait()

        #print result

        return True

    def generate(self, theme, version, package):
        
        self.m_package = package
        self.m_inline = True

        # Format the output pages
        pages = self.m_engine.m_parser.get_pages()
        self.m_contents = ''

        for page in pages:

            tags = page["tags"]
            source_file = page["source_file"]
            output_file = re.sub(".tpl", ".markdown", source_file)
            path = self.m_engine.get_output_dir() + "/" + output_file

            for tag in tags:

                if(self.m_engine.tag_is_header(tag.name)):
                    self.append_header(tag, output_file)

                elif(self.m_engine.tag_is_source_code(tag.name)):
                    self.append_source_code(tag)

                else:
                    self.append(tag)

        # Now generate the document index
        self.generate_index(self.m_engine.get_title(), self.m_engine.get_theme(), version)

        #if(self.m_inline != True):
        #    self.install_support_files(self.m_engine.get_output_dir())
       
        ## Copy output images - really only required if we're generating
        ## an HTML document.
        #if(self.m_inline != True):
        #    for image in self.m_engine.m_parser.m_images:
        #        shutil.copy(image, self.m_engine.get_output_dir() + "/" + image)

        INFO("Generating docbook document")
