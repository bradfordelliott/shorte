"""This module provides the implementation of the document header
   in every shorte document."""

class shorte_header_t():
    """This class defines the header of a shorte document"""

    def __init__(self):
        """This is the constructor for the shorte document header class"""
        self.start = 0
        self.title = ""
        self.subtitle = ""
        self.version = ""
        self.toc = False
        self.numbered = False
        self.number = ""
        self.revision_history = None
        self.filename = None
        self.sourcedir = None
        self.outdir = None
        self.line = 0
        self.footer_title = None
        self.footer_subtitle = None
        self.doc_info = None
        self.author = None
        self.csource = None
        self.template = None

    def get_start(self):
        """Return the start position of the document body
        
           @return The position of the start of the document body
        """
        return self.start

    def get_line(self):
        """Return the line number of the document body

           @return The line number of the start of the document body
        """
        return self.line

    def get_title(self):
        """Return the title associated with the document

           @return The document title
        """
        return self.title

    def get_subtitle(self):
        """Return the subtitle associated with the document

           @return The document subtitle
        """
        return self.subtitle

    def get_toc(self):
        """This is intended to determine whether or not the 
           output document should contain a table of contents but
           it doesn't work yet.
        """
        return self.toc

    def get_numbered(self):
        """This is intended to determine whether or not
           heading numbers are shown numbered but it doesn't
           work yet"""
        return self.numbered

    def get_version(self):
        """Get the document version number specified at the command
           line or via the doc.version tag

           @return The document version string
        """
        return self.version

    def get_number(self):
        """Get the document number string specified by the
           doc.number tag

           @return The document number string
        """
        return self.number

    def get_revision_history(self):
        """Get the document revision history specified by the @doc.revisions
           tag.

           @return The document revision history as a table_t object
        """
        return self.revision_history

    def get_author(self):
        """Get the document author string specified by the @doc.author
           tag.

           @return The document author string
        """
        return self.author

    def has_author(self):
        """Check to see if the document has an author assigned to it
           via the doc.author tag.

           @return True if the author property exists, False otherwise
        """
        if(self.author != None):
            return True
        return False

    def has_filename(self):
        """Check to see if the document has been assigned an output
           file name.

           @return True if the file name was assiged, False otherwise
        """
        if(self.filename != None):
            return True
        return False

    def get_filename(self):
        """Fetch the file name associated with the document

           @return The name associated with the document
        """
        return self.filename

    def has_csource(self):
        """This is not currently used"""
        if(self.csource != None):
            return True
        return False

    def get_csource(self):
        """This is not currently used"""
        return self.csource

    def __str__(self):
        """This method is called to convert the shorte header object into
           a human readable format"""

        output  = "Shorte Document Header\n"
        output += "======================\n"
        output += "  author:   %s\n" % self.author
        if(self.filename != None):
            output += "  file:     %s\n" % self.filename
        output += "  line:     %d\n" % self.line
        output += "  title:    %s\n" % self.title
        output += "  subtitle: %s\n" % self.subtitle
        output += "  version:  %s\n" % self.version
        output += "  number:   %s\n" % self.number

        if(self.revision_history != None):
            output += "  revision history: %s\n" % self.revision_history

        output += "  info:\n"
        output += "    %s\n" % self.doc_info
        
        output += "  footer:\n"
        output += "    title:    %s\n" % self.footer_title
        output += "    subtitle: %s\n" % self.footer_subtitle

        output += "  snippets/templates:\n"
        output += "    %s\n" % self.template   

        output += "  output directory:\n"
        output += "    %s\n" % self.outdir

        return output

        
