---------------------------------------------------------------------
--
-- Python Lexer
--
---------------------------------------------------------------------
INSERT INTO Settings (key,value,description) VALUES('lexer.python.keywords.0',
'
and      del       from      not       while 
as        elif      global    or        with 
assert    else      if        pass      yield 
break     except    import    print 
class     exec      in        raise 
continue  finally   is        return 
def       for       lambda    try 
', 'Python keywords');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.0',  '0x000000', 'Default');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.1',  '0x008000', 'Comment Line');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.2',  '0x336699', 'Number');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.3',  '0xff00ff', 'String');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.4',  '0xff00ff', 'Character');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.5',  '0x800000', 'Word');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.6',  '0xff00ff', 'Triple quotes');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.7',  '0xff00ff', 'Triple double???');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.8',  '0x000000', 'Class name');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.9',  '0x000000', 'Def name???');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.10', 'bold=1',   'Operator');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.11', '0x000000', 'Identifier');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.12', '0x008000', 'Comment block');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.13', '0x0000ff', 'String EOL');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.14', 'hotspot=1;color=0xff0000', 'Hyperlinks');
INSERT INTO Settings (key,value,description) VALUES('lexer.python.15', '0x000000', 'Decorator???');


---------------------------------------------------------------------
--
-- C++ Lexer
--
---------------------------------------------------------------------
INSERT INTO Settings (key,value,description) VALUES('lexer.cpp.keywords.0', '
and and_eq asm auto bitand bitor bool break 
case catch char class compl const const_cast continue 
default delete do double dynamic_cast else enum explicit export extern false float for 
friend goto if inline int long mutable namespace new not not_eq 
operator or or_eq private protected public 
register reinterpret_cast return short signed sizeof static static_cast struct switch 
template this throw true try typedef typeid typename union unsigned using 
virtual void volatile wchar_t while xor xor_eq
', 'C++ Keywords');

INSERT INTO Settings (key,value,description) VALUES('lexer.c++.0',  '0x000000', 'Default');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.1',  '0x008000', 'Multi-line comment');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.2',  '0x008000', 'Single-line comment');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.3',  '0x008000', 'Doxygen style comment');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.4',  '0x336699', 'Number');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.5',  '0x800000', 'Words');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.6',  '0xff00ff', 'Strings');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.7',  '0xff00ff', 'Characters');
--#define SCE_C_UUID 8
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.9',  '0x800000', 'Preprocessor');
--#define SCE_C_PREPROCESSOR 9
--#define SCE_C_OPERATOR 10
--#define SCE_C_IDENTIFIER 11
--#define SCE_C_STRINGEOL 12
--#define SCE_C_VERBATIM 13
--#define SCE_C_REGEX 14
--#define SCE_C_COMMENTLINEDOC 15
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.16',  'hotspot=1;color=0xff0000', 'Hyperlinked words');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.17',  '0x00ff00', 'Doxygen style comment keywords');
INSERT INTO Settings (key,value,description) VALUES('lexer.c++.18',  '0x00ff00', 'Doxygen style comment keyword errors');
--#define SCE_C_GLOBALCLASS 19
--#define SCE_C_STRINGRAW 20
--#define SCE_C_TRIPLEVERBATIM 21
--#define SCE_C_HASHQUOTEDSTRING 22
--#define SCE_C_PREPROCESSORCOMMENT 23
--#define SCE_C_PREPROCESSORCOMMENTDOC 24
--#define SCE_C_USERLITERAL 25;


---------------------------------------------------------------------
--
-- Shorte Lexer
--
---------------------------------------------------------------------
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.keywords.2',
'
@doctitle @docsubtitle @docauthor @docnumber @docrevisions @docversion @docfilename 
@body @h1 @h2 @h3 @h4 @h5 @h @include 
@input @columns @column @testcasesummary @testcase @functionsummary @typesummary 
@questions 
@pre @p @text @table @ol @ul @embed @endcolumns 
@perl @inkscape @sequence @bash @java @c @vera @python @verilog @tcl @checklist @vector @struct @prototype @acronyms @enum @imagemap @image 
@note @warning @tbd @question 
', 'Shorte Keywords');

INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.keywords.3',
'
@perl @python @bash @java @c @vera @python @verilog @tcl @code
', 'Shorte code blocks');


INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.0',  '0x000000', 'Default style');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.1',  'fore=0x008000;', 'Shorte comment');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.2',  '0x008000', 'Shorte comment block');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.3',  '0x336699', 'Number');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.4',  'hotspot=1;color=0xff0000', 'Function');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.5',  '0xff0000', 'Keyword');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.6',  'bold=1;color=0x800000', 'Macro');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.7',  '0xff00ff', 'String');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.8',  'bold=1',   'Operator');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.9',  'bold=1',   'Variable');
-- #define SCE_SHORTE_SENT 10
-- #define SCE_SHORTE_PREPROCESSOR 11
-- #define SCE_SHORTE_SPECIAL 12
-- #define SCE_SHORTE_EXPAND 13
-- #define SCE_SHORTE_COMOBJ 14
-- #define SCE_SHORTE_UDF 15
-- #define SCE_SHORTE_CONDITIONAL_EVAL 16
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.16',  '0x00ff00',   'Conditional eval');
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.17',  '0x66AA22',   'Code blocks');
-- #define SCE_SHORTE_CODE_BLOCK 17
-- #define SCE_SHORTE_LINK 18
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.18',  'hotspot=1;color=0x00ff00',   'Hyperlink');

-- #define SCE_SHORTE_INLINE_TAG 19
INSERT INTO Settings (key,value,description) VALUES('lexer.shorte.19',  '0xff0000', 'Keyword');


---------------------------------------------------------------------
--
-- HTML Lexer
--
---------------------------------------------------------------------
INSERT INTO Settings (key,value,description) VALUES('lexer.html.keywords.0',
-- HTML elements and attributes
'a abbr acronym address applet area b base basefont 
bdo big blockquote body br button caption center 
cite code col colgroup dd del dfn dir div dl dt em 
fieldset font form frame frameset h1 h2 h3 h4 h5 h6 
head hr html i iframe img input ins isindex kbd label 
legend li link map menu meta noframes noscript 
object ol optgroup option p param pre q s samp 
script select small span strike strong style sub sup 
table tbody td textarea tfoot th thead title tr tt u ul 
var xml xmlns 
abbr accept-charset accept accesskey action align alink 
alt archive axis background bgcolor border 
cellpadding cellspacing char charoff charset checked cite 
class classid clear codebase codetype color cols colspan 
compact content coords 
data datafld dataformatas datapagesize datasrc datetime 
declare defer dir disabled enctype event 
face for frame frameborder 
headers height href hreflang hspace http-equiv 
id ismap label lang language leftmargin link longdesc 
marginwidth marginheight maxlength media method multiple 
name nohref noresize noshade nowrap 
object onblur onchange onclick ondblclick onfocus 
onkeydown onkeypress onkeyup onload onmousedown 
onmousemove onmouseover onmouseout onmouseup 
onreset onselect onsubmit onunload 
profile prompt readonly rel rev rows rowspan rules 
scheme scope selected shape size span src standby start style 
summary tabindex target text title topmargin type usemap 
valign value valuetype version vlink vspace width 
text password checkbox radio submit reset 
file hidden image 
',

--# As defined in "HTML5 differences from HTML4" Working Draft
--# http://www.w3.org/TR/html5-diff/
--html5.elements=\
--address article aside audio base canvas command details datalist embed \
--figure figcaption footer header hgroup keygen mark menu meter nav output \
--progress ruby rt rp section source time video wbr
--
--html5.attributes=\
--async autocomplete autofocus contenteditable contextmenu draggable \
--form formaction formenctype formmethod formnovalidate formtarget \
--list manifest max min novalidate pattern placeholder \
--required reversed role sandbox scoped seamless sizes spellcheck srcdoc step
 

'HTML keywords');

INSERT INTO Settings (key,value,description) VALUES('lexer.html.0',  '0x000000', 'Default');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.1',  '0xff0000', 'Tags');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.2',  '0x0000ff', 'Unknown Tags');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.3',  '0xff00ff', 'Attributes');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.4',  '0xff0000', 'Unknown Attributes');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.5',  '0x336699', 'Numbers');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.6',  '0xff00ff', 'Double String');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.7',  '0xff00ff', 'Single String');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.8',  '0x000000', 'Other');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.9',  '0x008000', 'Comment');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.10', '0x0000ff', 'Entity');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.11', '0xff00ff', 'Tag End');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.12', '0xff00ff', 'XML Start');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.13', '0xff00ff', 'XML End');
INSERT INTO Settings (key,value,description) VALUES('lexer.html.14', '0x336699', 'Script');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.15', '0xff00ff', 'ASP');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.16', '0xff00ff', 'ASPAT???');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.17', '0xff00ff', 'CDATA');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.18', '0xff00ff', 'Question???');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.19', '0xff00ff', 'Value');
--INSERT INTO Settings (key,value,description) VALUES('lexer.html.20', '0xff00ff', 'XComment???');

--#define SCE_H_SGML_DEFAULT 21
--#define SCE_H_SGML_COMMAND 22
--#define SCE_H_SGML_1ST_PARAM 23
--#define SCE_H_SGML_DOUBLESTRING 24
--#define SCE_H_SGML_SIMPLESTRING 25
--#define SCE_H_SGML_ERROR 26
--#define SCE_H_SGML_SPECIAL 27
--#define SCE_H_SGML_ENTITY 28
--#define SCE_H_SGML_COMMENT 29
--#define SCE_H_SGML_1ST_PARAM_COMMENT 30
--#define SCE_H_SGML_BLOCK_DEFAULT 31
--#define SCE_HJ_START 40
--#define SCE_HJ_DEFAULT 41
--#define SCE_HJ_COMMENT 42
--#define SCE_HJ_COMMENTLINE 43
--#define SCE_HJ_COMMENTDOC 44
--#define SCE_HJ_NUMBER 45
--#define SCE_HJ_WORD 46
--#define SCE_HJ_KEYWORD 47
--#define SCE_HJ_DOUBLESTRING 48
--#define SCE_HJ_SINGLESTRING 49
--#define SCE_HJ_SYMBOLS 50
--#define SCE_HJ_STRINGEOL 51
--#define SCE_HJ_REGEX 52
--#define SCE_HJA_START 55
--#define SCE_HJA_DEFAULT 56
--#define SCE_HJA_COMMENT 57
--#define SCE_HJA_COMMENTLINE 58
--#define SCE_HJA_COMMENTDOC 59
--#define SCE_HJA_NUMBER 60
--#define SCE_HJA_WORD 61
--#define SCE_HJA_KEYWORD 62
--#define SCE_HJA_DOUBLESTRING 63
--#define SCE_HJA_SINGLESTRING 64
--#define SCE_HJA_SYMBOLS 65
--#define SCE_HJA_STRINGEOL 66
--#define SCE_HJA_REGEX 67
--#define SCE_HB_START 70
--#define SCE_HB_DEFAULT 71
--#define SCE_HB_COMMENTLINE 72
--#define SCE_HB_NUMBER 73
--#define SCE_HB_WORD 74
--#define SCE_HB_STRING 75
--#define SCE_HB_IDENTIFIER 76
--#define SCE_HB_STRINGEOL 77
--#define SCE_HBA_START 80
--#define SCE_HBA_DEFAULT 81
--#define SCE_HBA_COMMENTLINE 82
--#define SCE_HBA_NUMBER 83
--#define SCE_HBA_WORD 84
--#define SCE_HBA_STRING 85
--#define SCE_HBA_IDENTIFIER 86
--#define SCE_HBA_STRINGEOL 87
--#define SCE_HP_START 90
--#define SCE_HP_DEFAULT 91
--#define SCE_HP_COMMENTLINE 92
--#define SCE_HP_NUMBER 93
--#define SCE_HP_STRING 94
--#define SCE_HP_CHARACTER 95
--#define SCE_HP_WORD 96
--#define SCE_HP_TRIPLE 97
--#define SCE_HP_TRIPLEDOUBLE 98
--#define SCE_HP_CLASSNAME 99
--#define SCE_HP_DEFNAME 100
--#define SCE_HP_OPERATOR 101
--#define SCE_HP_IDENTIFIER 102
--#define SCE_HPHP_COMPLEX_VARIABLE 104
--#define SCE_HPA_START 105
--#define SCE_HPA_DEFAULT 106
--#define SCE_HPA_COMMENTLINE 107
--#define SCE_HPA_NUMBER 108
--#define SCE_HPA_STRING 109
--#define SCE_HPA_CHARACTER 110
--#define SCE_HPA_WORD 111
--#define SCE_HPA_TRIPLE 112
--#define SCE_HPA_TRIPLEDOUBLE 113
--#define SCE_HPA_CLASSNAME 114
--#define SCE_HPA_DEFNAME 115
--#define SCE_HPA_OPERATOR 116
--#define SCE_HPA_IDENTIFIER 117
--#define SCE_HPHP_DEFAULT 118
--#define SCE_HPHP_HSTRING 119
--#define SCE_HPHP_SIMPLESTRING 120
--#define SCE_HPHP_WORD 121
--#define SCE_HPHP_NUMBER 122
--#define SCE_HPHP_VARIABLE 123
--#define SCE_HPHP_COMMENT 124
--#define SCE_HPHP_COMMENTLINE 125
--#define SCE_HPHP_HSTRING_VARIABLE 126
--#define SCE_HPHP_OPERATOR 12

