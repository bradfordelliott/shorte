" Vim syntax file
" Language:	RELAX NG Compact Syntax
" Maintainer:	Hans Fugal <hans@fugal.net>
" Last Change:	$Date: 2003/06/22 03:32:14 $
" $Id: rnc.vim,v 1.7 2003/06/22 03:32:14 fugalh Exp $


if version < 600
    syntax clear
elseif exists ("b:current_syntax")
    finish
endif

syn include @PYTHON syntax/python.vim

" add the character '@' iskeyword.
"set iskeyword+=64


syn region Values start=/"/ end=/"/ contained
syn region Keys start=/[ :][A-Za-z]*/ end=/=/ contained
syn region Tags start=/^@\(acronyms\|\|define\|struct\|enum\|vector\|inkscape\|embed\|image\|python\|text\|perl\|code\|checklist\|c\|shell\|table\|ul\|prototype\|note\|questions\|question\|bash\|vera\|verilog\|tcl\|java\|pre\|ol\|functionsummary\|testcasesummary\|testcase\|include\|typesummary\|sequence\)/ end=/$/ contains=Keys,Values keepend
syn region Headings excludenl start=/^@\(h1\|h2\|h3\|h4\|h5\)/ end=/$/ keepend contains=Keys,Values

" Highlighting for single line tags such as @p that don't take any
" modifiers.
syn match LineTag /^@\(p \|body\)/


" Comments
syn match Comment /#.*$/
syn match Headers /^@\(title\|toc\|snippet\|url\|doctitle\|docsubtitle\|link\).*$/
syn match DocHeader /^@\(doctitle\|docsubtitle\|docnumber\|docversion\|docfilename\|docrevisions\).*$/
syn match Links /\[\[\|\]\]/
syn match TagSections /^:[A-Za-z]*:/
syn match EmbeddedStyles /@{.*}/
syn region CodeBlocks start=/{{/ end=/}}/
syn region CodeBlocks start=/<?/ end=/?>/ contains=@PYTHON


" Literals
"syn region literalSegment start=/"/ end=/"/ 

"syn match patternSpecial /[,&|?*+\\]/
"syn match Identifier /\k\+\s*\(&=\|=\||=\)\@=/ nextgroup=assignMethod
"syn match assignMethod /&=\|=\||=/
"syn match namespace /\k\+\(:\(\k\|\*\)\)\@=/
"syn region Annotation excludenl start=/\[/ end=/\]/ contains=ALLBUT,Identifier,patternName

" named patterns (element and attribute)
"syn keyword patternKeyword element attribute nextgroup=patternName skipwhite skipempty 
"syn match patternName /\k\+/ contained


"" Links
"hi link patternKeyword keyword
"hi link patternName Identifier
"hi link grammarContentKeyword keyword
"hi link startKeyword keyword
"hi link datatypeNameKeyword keyword
"hi link namespaceUriKeyword keyword
"hi link inheritKeyword keyword
"hi link declKeyword keyword
"
hi link literalSegment String
hi link Documentation Type
hi link Headers Type
hi link TplTags String 
hi link Links String
hi link CodeBlocks Identifier
hi link TagSections Operator
hi link EmbeddedStyles Operator
hi link DocHeader Special

hi link Keys Type
hi link Values Special
hi link Tags String
hi link Headings Type
hi link LineTag String 

"
"hi link patternSpecial Special
"hi link namespace Type

let b:current_syntax = "tpl"
" vim: ts=8 sw=4 smarttab
