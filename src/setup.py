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
cairo=find_data_files('libs/win32','libs/win32',[
        '*.pyd',
        '*.dll',
        '*.py'])
clang=find_data_files("3rdparty/clang/windows", "3rdparty/clang/windows",[
        '*.dll'])
clangpy=find_data_files("3rdparty/clang/windows/clang", "3rdparty/clang/windows/clang",[
        '*.py'])

examples=find_data_files('examples','examples',[
        '*.tpl',
        '*.png',
        '*.svg',
        '*.swf',
        '*.c',
        '*.h'])
syntax=find_data_files('syntax','syntax',[
        'vim/*',
        'vim/syntax/*'])
templates=find_data_files('templates','templates',[
        '*.py',
        'c/*',
        'html/*.py',
        'html/cortina/*',
        'html/cortina/images/*',
        'html/cortina_public/*',
        'html/cortina_public/images/*',
        'html/cortina_web/*',
        'html/cortina_web/images/*',
        'html/inphi/*',
        'html/inphi/images/*',
        'html/shorte/*',
        'html/shorte/images/*',
        'html_inline/*.py',
        'html_inline/cortina/*',
        'html_inline/cortina_public/*',
        'html_inline/cortina_web/*',
        'html_inline/inphi/*',
        'html_inline/shorte/*',
        'reveal.js/shorte/*',
        'reveal.js/shorte/css/*',
        'shared/*',
        'shared/odt/*',
        'shared/50x50/*',
        'shared/20x20/*',
        'shorte/*',
        'odt/*'])
files = examples
files.extend(templates)
files.extend(syntax)
files.extend(cairo)
files.extend(clang)
files.extend(clangpy)
files.extend(["version.inc"])

setup(
    options = {"py2exe": {
                   "packages": ["PIL"], # For everything
                   "includes": ["PIL.Image", # Or here for bits and pieces 
                                "PIL.PngImagePlugin"]}},
    console=['shorte.py'],
    data_files=files
)
