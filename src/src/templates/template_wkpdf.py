# -*- coding: iso-8859-15 -*-
"""This module contains the implementation of a PDF template generated
   using the wkhtmltopdf toolset
"""
import re
import os
import string
import shutil
import time
import subprocess
from string import Template;

from src.shorte_includes import *

from src.shorte_defines import *
from template import *

class template_wkpdf_t(template_t):

    def __init__(self, engine, indexer):

        template_t.__init__(self, engine, indexer)
    
    def get_index_name(self):
        title = self.m_engine.get_document_name()
        title = title.replace("©", "")
        title = title.replace("®", "")
        return "%s.pdf" % title

    def generate(self, theme, version, package):
        '''This method is called to generate the output
           PDF document using wkpdf

           @param self  [I] - The instance of the template class
           @param theme [I] - The name of theme to use to generate the output document.
                              This is used to find the .odt template file describing
                              the document.
           @param version [I] - The version number to use when generating the
                                document.
           @param package [I] - The package name to use when generating the document.
                                This could be "wpdf" or "wkpdf"
        '''

        scratchdir = shorte_get_config("shorte", "scratchdir")
        
        index_name = "index.html"
        if(self.m_engine.has_output_file()):
            index_name = self.m_engine.get_output_file()
        path_html = "%s" % (self.m_engine.get_output_dir() + os.sep + index_name)
        path_output = "%s" % (self.m_engine.get_output_dir() + os.sep + self.get_index_name())

        # If the output file already exists then make sure to remove it first
        if(os.path.exists(path_output)):
            os.unlink(path_output)

        print "CONVERTING VIA WPDF"

        # Convert HTML to PDF to generate the output document
        wkhtmltopdf = shorte_get_config("wkhtmltopdf", "args", expand_os=True)
        cmd_convert = [wkhtmltopdf, path_html, path_output]
        try:
            phandle = subprocess.Popen(cmd_convert, stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)

            while(phandle.poll() is None):
                result = phandle.stdout.read(1)
                time.sleep(1)

            print "Process complete"
            
            rc = phandle.returncode
        except:
            FATAL("Failed coverting document using wkhtmltpdf")

        INFO("Finished generating document")

