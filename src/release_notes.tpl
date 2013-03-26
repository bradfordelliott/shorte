@doctitle The shorte shorthand language
@docsubtitle Release Notes

@body

@h1 Releases
@p This document describes the release history of the Shorte parser

@h2 To do List
@text
- Get rid of the requirement for the @text after a header - it should
  be implicit
- Make conditionals flow down hierarchically on a heading so that I don't
  have to do everything below the heading
- Add text substitution support so I can get rid of keywords like Leeds
- Fix enums to obey the @private keyword
- Bring the word template up to spec
- Update the HTML template to add copyright info and other changes
  suggested by Techdocs
- Add tag support for test case documentation
- Concatenate all documents into a single file
- Add support for @example doxygen code so that I include examples
  of how to use particular methods
- Add support for case independant wikify.
- Update to support checking for broken internal links when wikifying.
- Update to support change bars (this might be difficult)
- Update to support drawing timeline diagrams
- Update sequence diagrams to draw the sequence table after the diagram
  in PDFs
- Add support for imagemaps at least for HTML generated documents.
- Add support for drawing a grid over any images in order to assist
  in creating imagemaps.
- Would be nice to have a shortcut for \<\?result=CHIP?>. Perhaps something
  like \$CHIP. Behavior should be try to expand it but if we can't then
  generate a warning and leave it be.

@h2 Bugs
@text
- Keywords don't seem to get hyperlinked inside comments within
  code snippets.
- Shorte doesn't properly handle function pointers inside function
  prototypes:

{{
    cs_status cs_t100_ptp_timewheel_training(
        cs_t100_handle_t  vp,
        cs_boolean        unmask_interrupt,
        void (*wait_pps_compare_ready_callback)(cs_t100_handle_t  vp))
}}
- cpp extensions don't work - When I parse main.cpp I get an output
  file called mainpp.tpl instead of main.tpl.
- Need to update the parser to not extract defines if they aren't
  commented. Right now they show up regardless.
- Need better support for the @example tag in function headers. Comments
  aren't currently showing up. Also should support an include
  mechanism

@h3 Version 1.0.52
- Removed requirement for batik for generating diagrams
- Source code cleanup

@h3 Version 1.0.51
- Added support for parsing prototypes in C++ header files
- Added support for the @deprecated tag in C++ files
- Some patches to the HTML and ODT templates

@h3 Version 1.0.50
- Added a cortina_no_background template (HTML only) that has
  no border. This is used for generating documents like the release
  notes for the GUI where I don't want the framed background.

@h3 Version 1.0.49
- Fixed a minor issue with inline styling in the ODT template
- Decreased size of HTML source code snippets
- Added expansion of equals block

@h3 Version 1.0.48
- Updated the SQL template to support enumerations.

@h3 Version 1.0.47
- Fixed the wiki formatting within function prototypes in the ODT
  template.

@h3 Version 1.0.46
- Added support for mediawiki
- Moved all the templates to a src directory to decrease clutter
- Made the template class names consistent
- Updated the mergefile template to fix handling of @text tags
- Created an examples directory and moved some of the existing examples
  to it.
- Added a tests target so that I can start building an automated
  tests library to at least validate the parser.
- Reworked the bullet points in ODT and PDF documents for ordered
  and unordered lists.
- Added subtitles to the HTML template.
- Enhanced the C++ comment parser to support some wiki syntax

@h3 Version 1.0.45
- Updated to support relative links in ODT/PDF template.

@h3 Version 1.0.44
- Changed java to headless when generating sequence diagrams to avoid
  an error with Batik

@h2 Version 1.0.43
- Added support for structures and enums in the sql package.
- Added flag to control suppression of path in HTML wiki-words in order
  to make wikiwords work in the SQL package.

@h2 Version 1.0.42
- Started meshing out the "sql" package that coverts prototypes
  into an SQL database that can be loaded by other tools.

@h2 Version 1.0.41
- Temporary update to labview_template.py to temporarily
  remove the @seealso support because it is causing the
  Leeds build to fail.

@h2 Version 1.0.40
- Minor tweak to the search and replace mechanism to allow
  input modules not named snr.py

@h2 Version 1.0.39
- Added basic support for define preprocessor macro in C code
- Cleaned up handling of structures and embedded images in ODT template
- Fixed escaping quotes in tag modifiers

@h2 Version 1.0.38
- Improved the print output of HTML using CSS
- Cleanup of the handling of CSS

@h2 Version 1.0.37
- Changed the structure of the HTML output to put everything
  except the index files in a contents subdirectory for readability
- Fixed the CSS styles of mouse overs in the HTML inline template
- Updated the sequence diagram generator to support generating the
  description table for formats other than HTML.
- Added support for the @see tag in function prototypes.
- Updated to allow line breaks in function descriptions. 
- Some minor cleanup to the word template
- Some minor cleanup to the HTML template for drawing structures.
- Some minor enhancements to the inline styling to allow for @{hl,tags}

@h2 Version 1.0.36
- Some cleanups to the CSS for the HTML output

@h2 Version 1.0.35
@text
- Removed the old perl sequence diagram generator
  because I can't get it to work. Switched over to
  a python based generator.
- Added batik library for converting sequence diagrams from SVG.

@h2 Version 1.0.34
@text
- Added library code for generating line and bar graphs. Still
  needs some work in order to properly integrate them so that they
  can be generated in a document.
- Started conversion of sequence diagram generator from perl
  into python so that I can incorporate it into the tool.
- Added automatic insertion of @text tags after headers so that
  I don't have to explicitly add them all the time.
- Added a few missing keywords

@h2 Version 1.0.33
@text
- Updated the copyright date in the ODT and HTML templates 

@h2 Version 1.0.32
@text
- Added support for excluding the script support in the inlined HTML output
- Fixed an issue with the cascading of tag exclusions. Should not
  have excluded @include tags.
- Started adding support for image maps in documentation.
- Added support for sequence diagrams.
- Added support for multi-column output.

@h2 Version 1.0.31
@text
- Added support for highlighting text in the ODT output.

@h2 Version 1.0.30
@text
- Added cleanup method in the HTML template to replace any characters that
  are not HTML safe such as the trademark symbol in some of the documentation.

@h2 Version 1.0.29
@text
- Performed some cleanup of the tag formats that require output
  as tables such as acronymns, enums, tables. This was done for
  maintainability.
- Added support for conditional to flow down exclusion of "if" modifiers
  on header tags so that entire headings can be excluded instead
  of just individual tags.
- Added support for the @embed tag for embedding .swf files. Probably
  will only ever work in HTML
- Added support for the @sequence tag for embedding sequence diagrams
  in documentation. This is an alpha version of the tag that I would
  like to enhance.

@h2 Version 1.0.28
@text
- Fixed a minor issue parsing structure field definitions. The cpp_parser::parse_struct_fields
  method really needs to be updated to use a more solid parser but implementing
  a temporary patch for now.

@h2 Version 1.0.27
@text
- Fixed bug in wikify feature broken in previous release.
- Updated to fix the path to swriter in Linux and move it
  to the config file.

@h2 Version 1.0.26
@text
- Fixed wiki word issue in the ODT template that was fixed in the HTML
  template in last release.
- Moved the wikify() method in the HTML and ODT templates to the base
  class for better maintainability.
- Fixed a failure parsing the @testcase tag introduced in the last
  version.
- Minor cleanup of the word template to stop it crashing parsing
  the copyright and trademark symbols.

@h2 Version 1.0.25
@text
- Fixed some escaping issues in the ODT template. Also fixed issue with
  code formatting.
- Fixed an issue with code formatting and wiki word linking in the HTML template.
- Added some enhancements to the C parser to allow it to parse
  extern "C" blocks and also to cleanup the way that enums
  are parsed.

@h2 Version 1.0.24
@text
- Fixed the invalid characters in the legal notice in the HTML document.
- Wrapped the call to openoffice to try to work around the exceptions
  it sometimes throws.

@h2 Version 1.0.23
@text
- Added legal info to the Cortina HTML template.
- Created public template for HTML that has different legal information.

@h2 Version 1.0.22
@text
- Updated to add the @docfilename tag allowing user to specify
  the name of the output file. This is currently only used for
  the OpenOffice and Word templates
- Fixed the word template so it would at least render though
  it needs a ton of updating.
- Updated the makefile to automatically install shorte so I don't
  have to do it manually any more.

@h2 version 1.0.21
@text
- Updated to enhance the way that includes are parsed
  to allow multiple includes separated by newlines. This
  makes it easier to manage the generated documentation.

@h2 Version 1.0.20
@text
- Corrected a issue with macro expansion in include files and
  also added built-in macros. Currently only support one built-in
  macro which is SHORTE_DOC_TITLE. This is expanded to the
  document title. 

@h2 Version 1.0.19
@text
- Restored support for the @docversion tag instead of
  requiring it be supplied from the command line. Command
  line can still override it.

@h2 Version 1.0.18
@text
- ODT template
    - Fixed up issue with the revision history tag
    - Fixed up some formatting issues with tables based on the
      recent change to the way that tables are formatted.
    - Fixed issue with page breaks in the documentation.
- HTML template
    - Fixed the target in the HTML template for links in
      the menu.

@h2 Version 1.0.17
@text
- ODT template
    - Fixed the heading numbers in the ODT template
    - Fixed wiki word linking in pre tag
    - Implemented the revision history tag
- Few minor bug fixes
    - Added include tag to the syntax highlighter for VIM

@h2 Version 1.0.16
@text
- Added some enhancements to the @testcase tag and also
  started meshing out the @testcasesummary tag.

@h2 Version 1.0.15
@text
- Added support for the @testcase tag used for creating test
  reports. This required support in the HTML, ODT, and parser
  classes.
- Added some cleanup for the C code generation to support
  the API header file required to send to customers

@h2 Version 1.0.14
@text
- Created mergefile or book template that concatenates a series shorte
  template files into one large book for easier distribution.
- Added support for search and replace strings
- HTML template
    - Added support for copyright and tm symbols
    - Added switch to turn on or off display of enum values
    - Fixed the date in the footer
    - Added place holders for revision info and copyright info
- ODT template
    - Started cleaning up the style handling to try to push more to
      the template file rather than hard-coded in python code
    - Added support to turn on or off display of enum values
    - Removed redundant captions on enums/structs
    - Added support for copyright and tm symbols
    - Cleanup for the function and type summaries
    - Added support for revisionhistory tag
- Config file
    - Few new options for handling enums and structures
    

@h2 Version 1.0.13
@text
- Shorte
    - Added dumb comment handling to the input file list - needs to be improved
      in next release.
- C Parser
    - Made sure to obey the @private tag for structures
- HTML template
    - Added inline styling with this type syntax @{u,my text here}
- ODT template
    - Decreased the font size of code snippets to make them fit better
      in the generated documentation.

@h2 Version 1.0.12
@text
- ODT Template
    - Changed the ODT template to not copy convert_to_pdf.odt but reference it from
      the templates directory.
    - Cleaned up the function summary and type summary
    - Cleaned up the @text handling and added dynamic styling
      to support the color tagging.
    - Fixed the -> internal links
    - Cleaned up the graphics on the front and back pages of the
      Cortina template.
    - Automated the table column width setup - doesn't work
      the best. Need to consider doing it on my own.
- Word Template
    - Some cleanup to the Cortina template though it is still
      way out of date.


@h2 Version 1.0.11
@text
- Fixed a bug in the CPP parser that wasn't getting doxygen
  headers if there were spaces between the function declaration
  and the comment.
- Added a header back to the function summary in the HTML template.
- Added conditional defines to the input file list
- Added better parsing of embedded PHP style code 

@h2 Version 1.0.10
@text
- Updated the ODT template for Cortina to fit the corporate standard.
- Converted line endings in sources to unix style.
- Made a few enhancements to the C parser to get better output
- Added types summary @typesummary tag and fixed a few formatting issues in
  the HTML template.
- Added wiki word support to the ODT template.
- Added support for @h5 tag.
- Fixed up the HTML template for Cortina.

@h2 Version 1.0.9
@text
- Fixed the function summary in include files
- Cleaned up the prototype formatting in HTML docs
- Added wiki words support to the ODT template to allow
  for cross referencing.
- Fixed an error with the handling of - in tables
- Fixed an error with the @functionsummary when there was no page title

@h2 Version 1.0.8
@text
- Cleaned up the HTML for the function summary
- Cleaned up some of the CPP parsing to shorte files
- Added frameset support similar to doxygen for the HTML output
- Fixed a firefox issue with the rounded corners
- Started adding project files for input files
- Added python snippets to the LabVIEW output
- Fixed the wikifying of functions in the format class.name.

@h2 Version 1.0.7
@text
- ODT Support
    - Updated to allow modifying the ODT template in OpenOffice
    - Updated the Cortina template to add document information
- Condition Defines
    - Updated the conditional tag defines to support boolean operations
      so that I can handle different document SKUs
- Added docnumber tag to the header to support assigning document
  numbers to different documents.

@h2 Version 1.0.6
@text
- LabView:
    - Updated the labview template and the CPP parser to extract and
      output HTML from the CPP source rather than having to convert
      to shorte format first.
    - Fixed an issue parsing structures in the LabView template


@h2 Version 1.0.5
@text
- Output Templates
    - HTML Template:
        - Updated the HTML template to control whether or not the code
          header is output in places such as codes snippets or function
          prototypes
        - Reworked the HTML to decrease the size of generated output
          code.
    - C Template:
        - Fixed code output for records if the header style is Doxygen
    - Updates to LabView template:
        - Fixed header file in LabView output template.
        - Fixed up the HTML for the html output in the labview template


@h2 Version 1.0.4
@text
- Output Templates
    - Fixed an output problem generating PDFs/ODT from within cygwin
    - Updated the Q/A output under HTML,Text, and ODT templates
    - Fixed an issue with converting images for word docs
    - Replaced invalid characters in the parser instead of the output formatters
    - Updated the CSS for the inline HTML generation to support
      code snippet changes and Q/A changes.
    - Fixed a bug in the word template related to backslashes
    - Changed the output font to courier new in the HTML template
      to get better output
    - Removed the extraneous - in structure output in HTML template
    - Changed anchors in HTML output so that the link is before the
      text so they don't get highlighted.
    - Removed bolding of keywords in the code snippets to try to
      make them easier to read.
    - Fixed the CSS output in the HTML inline template
- Parser Changes
    - Updated the shorte_parser.py class to stop outputting the
      backslash character in escape sequences unless it is a source
      code snippet.
    - Updated to only support tags that are at the beginning
      of a line so that the @ character doesn't have to always
      be escaped.
    - Add conditional inclusion with the if modifier on output tags.
      For example:
          @c: if="CUG"
      will only output data if -m "CUG=1" is defined at the command
      line.
    - Updated to parse the document header similar to the way that
      the body is parsed and added conditional inclusion on the
      header tags.
- Syntax Highlighting
    - Added syntax highlighting for code blocks within {{ }}
- C++ Parser
    - Added option to extract private functions
    - Added option to not extract code as pseudocode
    - Added primitive capability to parse enum definitions
      for source files in order to re-construct them in
      an output file.
    - Added primitive capability to parse struct definitions
      in order to re-construct them in output file. Right now
      can't handle nested types = need to do some work
      in this area

@h2 Version 1.0.3
@text
- Output Templates
    - Cleaned up the text template
        - Added support for source code snippets
        - Fixed output of @h1 header
        - Added support for numbered list and set it up so
          that it switched between numbers and letters
    - Patched a bug in the ODT output related to copying
      multiple instances of the same image
    - Patched the same bug in the HTML output related to
      copying multiple instances of the same image
- Misc Changes
    - Fixed an error parsing lists with a - within them.
      Was incorrectly treating it as a new list item. New items
      should only be dashes with only spaces before them up till
      the newline

@h2 Version 1.0.2
@text
- Build Changes
    - Updated to allow building cairo plugin under Cygwin
- Misc Changes
    - Updated lists to support a variable length depth rather
      than the two level depth in previous releases (only works in ODT, HTML, and Word at the moment)
    - Cleaned up the text block
        - Fixed the indenting issue
        - Cleaned up the list handling
        - Cleaned up the code block handling
    - Fixed the function summary tag to restrict to a single file
- Output Templates
    - HTML Output
        - Added "View Source" and "Print" options to the HTML output for the Cortina template
    - C Template
        - Updated C output to add formatting for doxygen headers



@h2 Version 1.0.1
@text
- Added links to the table of contents in the OpenOffice and PDF generation.
- Added doxygen parsing and output format for comments
- Added version number to HTML documentation
- Added version.inc file for managing version number of the tool
- Added support for the text tag to the txt template

@h2 Version 1.0
@text
- This was the first release of shorte. It included a basic framework



@h1 Installation Notes

@h2 Cygwin Information
@text
You need to compile PIL from source so make sure you have gcc installed (in cygwin).
There’s a handy installation helper in the cygwin setup package list called,
‘gcc: C compiler upgrade helper’. Install this, and it grabs the dependencies.

*PIL Python Imaging Library*

Get the PIL source from here, and unpack the archive to your sources folder (I use /home/rich/sources).

Now, if you run python setup.py install, the installation hangs (for me anyway).
Googling reveals that this is not uncommon. What you need to do is ‘rebase’!
Sound like a crack issue maybe it is?

Here’s the magic command (and don’t ask me why this works):

{{rebase -b 0x1000000000 /bin/tk84.dll}}

So, close cygwin and open up task manager, kill any gcc.exe or
python.exe processes that are hanging around. Next, run the
above command. You should then be able to install using setup.py as normal.

    {{python setup.py install}}

