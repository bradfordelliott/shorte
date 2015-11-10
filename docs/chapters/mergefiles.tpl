@body
@h1 Merge Files and Diffing Documents
Merge files are a way of merging a series of shorte files into
one single file. This is useful for creating deltas between different
versions of a shorte document rather than having to diff
multiple source files.

    shorte -f "chapters/commnad_line.tpl chapters/mergefiles.tpl" -p mergefile --output=. --output_file=merge.tpl

This concatenates the multiple source files into one single document @{b,merge.tpl} that
can then be more easily diffed for changes between document versions.

@note
Currently it is not possible to diff included images. In the
future the merge file may contain a hash to determine whether or not
embedded images have been modified.

