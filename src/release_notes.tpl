@doctitle The shorte language
@docsubtitle Release Notes

@body

@h1 Releases
This document describes the release history of the Shorte language.

@h3 Version 1.0.71 (Dec 12, 2014)
- Fixed a bug in the formatting of defines in the open document
  template that causes special characters like & to not be escaped
  properly.
- Minor cleanup of the enums example.
- Fixed performance issues in the clang parser. It should now be
  comparable or better than the old cpp parser.
- Checked in pre-built binaries of the cairo plugin and the 
  clang plugin to make distribution easier on Linux.

@h3 Version 1.0.70 (Dec 5, 2014)
Minor bug fix release that allows the table of contents
to be styled differently in HTML documents. Also removed
missed reference to vendor name in the footer title.

@h3 Version 1.0.69 (Dec 3, 2014)
Bug fix release that addresses the following issues:
- Issue with wikification in the @note keyword in source
  code cross references. This issue needs to be debugged
- SQL template doesn't inline images so they don't show
  up properly.

@h3 Version 1.0.68 (Dec 3, 2014)
This is the first release attempting to remove any vendor specific
templates and allow them to be included from a different source. Also
added clang as a parser option and many more enhancements.

@h3 Version 1.0.67 (Aug 14, 2014)
This is a general cleanup release to push some cleanup work
to Shorte.

- ODT
    - Added support for PATH_OOWRITER environment variable. Shorte
      will look for swriter in this varible. If it isn't defined it
      will fall back to the path in the shorte.cfg file.
    - Fixed list indentation issues and wrapping of long list items
    - Switched the note back to use stying defined in template_odt.py
      instead of the OpenDocument template as it is easier to
      handle.
- Inline Styles
    - Added support for inline styling of @note, @warning, @tbd
- HTML
    - Updated the styling of checkboxes to grey them out when
      they are checked.
- Text
    - Some cleanup on the text template (-p txt)
- Packages
    - Added 'reveal.js+pdf' and 'reveal.js+txt' output bundles.
- Graphing
    - Meshed out the @gnuplot tag to support integration with
      gnuplot.
    - Meshed out the @graph tag for native rendering of graphs.
      Currently only line graphs and bar graphs are supported.
- Templates
    - Cleaned up the shorte template and made the styles
      a bit easier to modify for different themes.

@h3 Version 1.0.66 (Apr 22, 2014)
- Enums
    - Fixed issue parsing enumerations caused by some enhancements
      to the parser.
- HTML
    - Fixed the HTML template to correctly handle spaces in the
      javascript popup window. They are converted to &nbsp;

@h3 Version 1.0.65 (Apr 21, 2014)
- Templates
    - Re-worked the ODT templates to remove the differences between the
      public and private Cortina templates. Added new document header
      tags to support the footer attributes required by the RTP team. 
- Other
    - Added framework to change verbosity of output. Still needs more work.
    - Added footer attributes to the document header section. Re-worked the
      heading management to be slightly more maintainable

@h3 Version 1.0.64 (Apr 21, 2014)
- Build issues
    - Cleaned up cross-platform build environment, primarily for windows
-

@h3 Version 1.0.63 (Apr 21, 2014)
- Templates
    - Cleaned up some of the images and added icons for text doc links
    - ODT/PDF
        - Re-worked the ODT template to move some of the styles out into
          python modules to accomodate the changes for alternate templates
        - Added the "widths" attribute to tables to allow for user control
          of column widths.
    - HTML
        - Removed the jquery from the HTML templates
        - Scaled some of the images for tags like @note to fix poor
          scaling in IE
    - Added support for "html+txt" template
- Shortify
    - Prototype editor for shorte (to work on Scintilla lexer)
- Graphing
    - Minor tweaks to the paths of the graphing scripts
- Parsers
    - Some cleanup of the parsers to make them more maintainable
      by converting programming types to classes.
- Syntax
    - Updated tables to add a "widths" attribute to specify column widths
      in the HTML/ODT/PDF templates
    - Reworked programming types (enum, struct, define) to be more maintainable
      and support similar attributes (still a work in progress).


@h3 Version 1.0.62 (Mar 13, 2014)
Minor bug fix release

- Syntax:
    - Added support for checkboxes in lists similar to github
        - Added support for actions within lists using the [a] and [ax]
          prefixes.
        - Added support for starred items using the [*] syntax
        - Added support for priorities using the [1-5] syntax. For
          example:
              -[a3] is a priority 3 action where > is higher priority.
    - Added the skip_if_pdf modifier/attribute to tags so that a section
      can be skipped in PDF documents. This is done because large PDFs
      currently take a long time to generate and some sections can be
      skipped and left only in the HTML version.
    - Fixed issue with the inlined tables and the use of the | character
      as a divider. Updated to use ! as divider instead until I can
      figure out a better way
    - Added support for examples associated with structure definitions.
    - Added support for multi-line comments via the \<!-- --> syntax
    - Lexers
        - Updated the VIM lexer (syntax/vim/syntax/tpl.vim) to improve
          some of the parsing.
- Themes
    - Updated to support mixing themes for individual packages. For
      example, you can now do this:
          - --theme="html=cortina_web;pdf=cortina"
- HTML template
    - Tidied up the formatting of C defines
    - Moved icons into the css directory to de-clutter
      the content directory.
    - Converted some string handling to use list comprehension
      for performance
- ODT/PDF template
    - Updated convert_to_pdf.odt to add a status bar when
      generating the output document. Also add arguments to skip
      certain steps in the conversion.
    - Started moving some of the styles into the template document
      itself to make them user-customizable instead of hard-coded
      in src/templates/template_odt.py.
- SQL template
    - Cross referenced structure fields so that they are searchable.
    - Added *Add to Script* and *Copy to Clipboard* options on the prototype
      and examples to make them more usable within CS Explorer.
- Cleanup of the sources to move some of the includes into the src subdirectory
- Added support for XML-RPC server for web integration
    - example file in server_test.py
    - support for generating inline HTML docs (html_inline)
      and PDF documents (pdf). More support will be added
      to future releases.
    - Support for zipping generated results for cases where
      there are multiple files in a package like (html+pdf)
- Performance Profiling
    - Updated to start profiling the parsers to improve performance
- Shortify
    - Started creation of an IDE for demonstrating the capabilities
      of shorte.

@table: title="Closed bugs"
- Bug | Description
- 54  | Issue with parsing of inline tables inside another structure
        like a table. Dealt with this by introducing the ! separator
        for inline tables until I can come up with a better syntax.
- 73  | Fixed an issue where the latest few sections of an ODT document
        are not stripped correctly.

@h3 Version 1.0.61 (Nov 25, 2013)
Minor bug fix release.

- Added inline version of the "cortina_web" HTML template
- Fixed the encoding of images. This can be done using the following command:
    python shorte.py --info="encode_images" -f "templates/html/cortina_web/images/sl1-bg2.jpg templates/html/cortina_web/images/menu.png" > files.txt
- Added a new @warning tag similar to @note to warn users about
  potential issues.

@table: title="Closed bugs"
- Bug | Description
- 47  | Cleaned up the mediawiki template to use the tag class.
- 49  | Updated to address a problem with the g_startup_path global variable. Replaced
        it with a shorte_get_startup_path() method instead and fixed issue under Cygwin.

@h3 Version 1.0.60 (Nov 8, 2013)
Minor bug fix release.

@table: title="Closed Bugs"
- Bug | Description
- 15  | Worked on cleaning up the format for the @note template. Replaced the
        old icons with my own since I don't know where they came from so I probably
        should use something I know I have a license for.
- 28  | Fixed issue with . and other punctuation marks being included
        as part of wikiwords. This was intended to hyperlink class identifiers
        like WikiWord.member but it doesn't work very well because it doesn't
        understand a period following WikiWord.
- 31  | Fixed issues with the mergefile package that got broken
        in the 1.0.59 release.
- 33  | Updated to remove spurious debug message when generating ODT
        documents instead of PDFs.
- 34  | Checked in a zip file of the cairo dependencies to simplify
        building on Windows. In future may want to change this so that
        it downloads them from the web.
- 35  | Resolved issue with latest version of LibreOffice because
        multiple pictures are using the same draw:name tag. This causes
        LibreOffice to complain and a PDF can't be generated.
- 36  | Updated the mergefile package to include a placeholder document header.
- 37  | Updated the mergefile package to include an @body tag.
- 38  | Updated the SQL template to turn on transactions for faster
        performance.
- 40  | Fixed an issue with @note tag in the ODT/PDF template. This is the
        same issue as Bug 35.
- 45  | Created a new theme for shorte that will eventually become the default
        instead of using the Cortina template.
- 46  | Added a new option to the info command line parameter to base64 encode
        images to simplify creating inline HTML templates.

@h3 Version 1.0.59 (Oct 23, 2013)
Minor release to address the following issues:
- Issues with parsing inline tables in function
  headers
- Partial fix to allow escaping characters with the \
  character in text blocks. This is useful for preventing
  the - getting expanded as a list.
- Converted the existing tag dictionary to a class object
  to make the source easier to maintain.

@table: title="Closed/Partially Closed Bugs"
- Bug | Description
- 29  | Fixed issues parsing embedded tags like tables in
        function prototypes caused by converting first from
        C to shorte and then from shorte to HTML/PDF. Had to
        change the @prototype tag to use -- to separate sections
        since the parser is not very smart.
- 27  | Fixed the escaping of the - character in text blocks
        so that it is not expanded to a list if it is preceded
        by an escape character '\'.
       
        This bug partially resolved but still needs some more
        effort to be properly closed.



@h3 Version 1.0.58 (Oct 15, 2013)
Minor release that adds:
- support for assigning wiki-words to headings in order to
  control automatic hyperlinking
- revision history for HTML documents
- minor restructuring of the code tree

@table: title="Closed Bugs"
- Bug | Description
- 22  | Added support for assigning a wikiword to document headings.
- 23  | Added hyperlink in the version number in the document header
        to the revision history of a document in the HTML template.
- 24  | Resolved issue when @ is encountered within a text block. It
        was being parsed as an inline tag which should only happen
        if it is followed by {.
- 25  | Added support for @xml tag for source code snippets.
- 26  | Fixed escaping of conditional php style tags within HTML
        documents.

@h3 Version 1.0.57
This is another bug fix release to address template issues in the
ODT template related to the header layout.

@table: title="Closed Bugs"
- Bug | Description
- 20  | Fixed issue with header layout. I broke it trying to fix
        issue 6 in release 1.0.56.
- 21  | Reverted the defaulting of the document number to address
        a issue reported in the 1.0.56 release.

@h3 Version 1.0.56
This is a bug fix version to address some issues reported by users. The
following list of bugs have been closed as part of this release:

@table: title="Closed Bugs"
- Bug | Description
- 1   | Documented support for the @include_child tag which is used
        to handle including files that obey the header cascading for
        conditional text.
- 2   | Updated convert_to_pdf.odt to fix the trapping of open office
        errors. This should prevent a bug that causes it OpenOffice to
        hang when generating a document that has an uncaught syntax
        error in it.
- 3   | Fixed up use of text block for struct, enum and function
        prototype sections. Could probably use some more validation.
- 4   | Fixed up the display of function descriptions in the function
        summary section.
- 6   | Fixed issue with title wrapping in PDF documents. This was done
        by modifying the margin of the title and subtitle. Instead of wrapping
        they will collide with the Cortina logo instead which is a more
        noticible problem to the user.
- 13   | Fixed up the formatting of @h5 tags in ODT/PDF documents to be
         a little nicer. Colors could probably be a bit more consistent
         though.
- 14   | Fixed the indent of the @h tag to be in line with the other
         headers.
- 18   | Fixed processing of quotes inside links in ODT documents in
         text blocks to prevent double escaping of the link label.

@h3 Version 1.0.55
- Added support for @sql tag
- Fixed a parsing issue with spanned columns in table headers
- Added the ability to @include a .c or .h file
- Fixed styling of keywords in HTML
- Changed style of @note tag in HTML template



@h3 Version 1.0.54
- Added new tag @include_child to support includes which
  are conditionally included based on the header hierachy.
  The old tag @include ignores the conditional inclusion
- Fixed a path problem related to finding Libre Office under
  Windows

@h3 Version 1.0.53
- Attempt at fixing permissions issue in the installed files

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

@h3 Version 1.0.43
- Added support for structures and enums in the sql package.
- Added flag to control suppression of path in HTML wiki-words in order
  to make wikiwords work in the SQL package.

@h3 Version 1.0.42
- Started meshing out the "sql" package that coverts prototypes
  into an SQL database that can be loaded by other tools.

@h3 Version 1.0.41
- Temporary update to labview_template.py to temporarily
  remove the @seealso support because it is causing the
  Leeds build to fail.

@h3 Version 1.0.40
- Minor tweak to the search and replace mechanism to allow
  input modules not named snr.py

@h3 Version 1.0.39
- Added basic support for define preprocessor macro in C code
- Cleaned up handling of structures and embedded images in ODT template
- Fixed escaping quotes in tag modifiers

@h3 Version 1.0.38
- Improved the print output of HTML using CSS
- Cleanup of the handling of CSS

@h3 Version 1.0.37
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

@h3 Version 1.0.36
- Some cleanups to the CSS for the HTML output

@h3 Version 1.0.35
@text
- Removed the old perl sequence diagram generator
  because I can't get it to work. Switched over to
  a python based generator.
- Added batik library for converting sequence diagrams from SVG.

@h3 Version 1.0.34
@text
- Added library code for generating line and bar graphs. Still
  needs some work in order to properly integrate them so that they
  can be generated in a document.
- Started conversion of sequence diagram generator from perl
  into python so that I can incorporate it into the tool.
- Added automatic insertion of @text tags after headers so that
  I don't have to explicitly add them all the time.
- Added a few missing keywords

@h3 Version 1.0.33
@text
- Updated the copyright date in the ODT and HTML templates 

@h3 Version 1.0.32
@text
- Added support for excluding the script support in the inlined HTML output
- Fixed an issue with the cascading of tag exclusions. Should not
  have excluded @include tags.
- Started adding support for image maps in documentation.
- Added support for sequence diagrams.
- Added support for multi-column output.

@h3 Version 1.0.31
@text
- Added support for highlighting text in the ODT output.

@h3 Version 1.0.30
@text
- Added cleanup method in the HTML template to replace any characters that
  are not HTML safe such as the trademark symbol in some of the documentation.

@h3 Version 1.0.29
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

@h3 Version 1.0.28
@text
- Fixed a minor issue parsing structure field definitions. The cpp_parser::parse_struct_fields
  method really needs to be updated to use a more solid parser but implementing
  a temporary patch for now.

@h3 Version 1.0.27
@text
- Fixed bug in wikify feature broken in previous release.
- Updated to fix the path to swriter in Linux and move it
  to the config file.

@h3 Version 1.0.26
@text
- Fixed wiki word issue in the ODT template that was fixed in the HTML
  template in last release.
- Moved the wikify() method in the HTML and ODT templates to the base
  class for better maintainability.
- Fixed a failure parsing the @testcase tag introduced in the last
  version.
- Minor cleanup of the word template to stop it crashing parsing
  the copyright and trademark symbols.

@h3 Version 1.0.25
@text
- Fixed some escaping issues in the ODT template. Also fixed issue with
  code formatting.
- Fixed an issue with code formatting and wiki word linking in the HTML template.
- Added some enhancements to the C parser to allow it to parse
  extern "C" blocks and also to cleanup the way that enums
  are parsed.

@h3 Version 1.0.24
@text
- Fixed the invalid characters in the legal notice in the HTML document.
- Wrapped the call to openoffice to try to work around the exceptions
  it sometimes throws.

@h3 Version 1.0.23
@text
- Added legal info to the Cortina HTML template.
- Created public template for HTML that has different legal information.

@h3 Version 1.0.22
@text
- Updated to add the @docfilename tag allowing user to specify
  the name of the output file. This is currently only used for
  the OpenOffice and Word templates
- Fixed the word template so it would at least render though
  it needs a ton of updating.
- Updated the makefile to automatically install shorte so I don't
  have to do it manually any more.

@h3 version 1.0.21
@text
- Updated to enhance the way that includes are parsed
  to allow multiple includes separated by newlines. This
  makes it easier to manage the generated documentation.

@h3 Version 1.0.20
@text
- Corrected a issue with macro expansion in include files and
  also added built-in macros. Currently only support one built-in
  macro which is SHORTE_DOC_TITLE. This is expanded to the
  document title. 

@h3 Version 1.0.19
@text
- Restored support for the @docversion tag instead of
  requiring it be supplied from the command line. Command
  line can still override it.

@h3 Version 1.0.18
@text
- ODT template
    - Fixed up issue with the revision history tag
    - Fixed up some formatting issues with tables based on the
      recent change to the way that tables are formatted.
    - Fixed issue with page breaks in the documentation.
- HTML template
    - Fixed the target in the HTML template for links in
      the menu.

@h3 Version 1.0.17
@text
- ODT template
    - Fixed the heading numbers in the ODT template
    - Fixed wiki word linking in pre tag
    - Implemented the revision history tag
- Few minor bug fixes
    - Added include tag to the syntax highlighter for VIM

@h3 Version 1.0.16
@text
- Added some enhancements to the @testcase tag and also
  started meshing out the @testcasesummary tag.

@h3 Version 1.0.15
@text
- Added support for the @testcase tag used for creating test
  reports. This required support in the HTML, ODT, and parser
  classes.
- Added some cleanup for the C code generation to support
  the API header file required to send to customers

@h3 Version 1.0.14
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
    

@h3 Version 1.0.13
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

@h3 Version 1.0.12
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


@h3 Version 1.0.11
@text
- Fixed a bug in the CPP parser that wasn't getting doxygen
  headers if there were spaces between the function declaration
  and the comment.
- Added a header back to the function summary in the HTML template.
- Added conditional defines to the input file list
- Added better parsing of embedded PHP style code 

@h3 Version 1.0.10
@text
- Updated the ODT template for Cortina to fit the corporate standard.
- Converted line endings in sources to unix style.
- Made a few enhancements to the C parser to get better output
- Added types summary @typesummary tag and fixed a few formatting issues in
  the HTML template.
- Added wiki word support to the ODT template.
- Added support for @h5 tag.
- Fixed up the HTML template for Cortina.

@h3 Version 1.0.9
@text
- Fixed the function summary in include files
- Cleaned up the prototype formatting in HTML docs
- Added wiki words support to the ODT template to allow
  for cross referencing.
- Fixed an error with the handling of - in tables
- Fixed an error with the @functionsummary when there was no page title

@h3 Version 1.0.8
@text
- Cleaned up the HTML for the function summary
- Cleaned up some of the CPP parsing to shorte files
- Added frameset support similar to doxygen for the HTML output
- Fixed a firefox issue with the rounded corners
- Started adding project files for input files
- Added python snippets to the LabVIEW output
- Fixed the wikifying of functions in the format class.name.

@h3 Version 1.0.7
@text
- ODT Support
    - Updated to allow modifying the ODT template in OpenOffice
    - Updated the Cortina template to add document information
- Condition Defines
    - Updated the conditional tag defines to support boolean operations
      so that I can handle different document SKUs
- Added docnumber tag to the header to support assigning document
  numbers to different documents.

@h3 Version 1.0.6
@text
- LabView:
    - Updated the labview template and the CPP parser to extract and
      output HTML from the CPP source rather than having to convert
      to shorte format first.
    - Fixed an issue parsing structures in the LabView template


@h3 Version 1.0.5
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


@h3 Version 1.0.4
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

@h3 Version 1.0.3
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

@h3 Version 1.0.2
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



@h3 Version 1.0.1
@text
- Added links to the table of contents in the OpenOffice and PDF generation.
- Added doxygen parsing and output format for comments
- Added version number to HTML documentation
- Added version.inc file for managing version number of the tool
- Added support for the text tag to the txt template

@h3 Version 1.0
@text
- This was the first release of shorte. It included a basic framework


