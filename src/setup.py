from distutils.core import setup
import py2exe
import os
import glob

def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

#from glob import glob
#  data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
#  setup(
#    data_files=data_files,
#    console=['shorte.py']
#  )


#data_files = find_data_files('templates', 'templates', ['*'])
examples=find_data_files('examples','examples',[
        '*.tpl',
        '*.c',
        '*.h'])
syntax=find_data_files('syntax','syntax',[
        'vim/*',
        'vim/syntax/*'])
templates=find_data_files('templates','templates',[
        'c/*',
        'html/cortina/*',
        'html/cortina_public/*',
        'html_inline/cortina/*',
        'html_inline/cortina_public/*',
        'shared/*',
        'odt/*'])
files = examples
files.extend(templates)
files.extend(syntax)

setup(
    console=['shorte.py'],
    data_files=files
)
