#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
from clang.cindex import *

def list_includes(translation_unit):
  """ Find all includes within the given TranslationUnit
  """
  cursor = translation_unit.cursor

  includes = []

  for child in cursor.get_children():
    # We're only interested in preprocessor #include directives
    #
    if child.kind == CursorKind.INCLUSION_DIRECTIVE:
      # We don't want Cursors from files other than the one belonging to
      # translation_unit otherwise we get #includes for every file found
      # when clang parsed the input file.
      #
      if child.location.file != None and child.location.file.name == cursor.displayname:
        includes.append( child.displayname )

  return includes

# The name of the file in which to look for #include statements
#
source_file = sys.argv[1]

# This can be a list of compiler flags, [ '-Iinclude_path', '-DDEBUG', ]
#
parse_arguments = None

# Slightly quicker to parse as we are not interested in the contents of functions
#
parse_flags = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES

source_translation_unit = TranslationUnit.from_source(
  source_file,
  parse_arguments,
  None,
  parse_flags,
  None)

source_includes = list_includes(source_translation_unit)
for include in source_includes:
  print(include)
