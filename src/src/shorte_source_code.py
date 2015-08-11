#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   shorte_source_code.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a parser class used to
#|   tokenize source code such as C.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import re

from shorte_defines import *

class shorte_source_code_tag_t(object):
    __slots__ = ['data', 'type', 'start']
    def __init__(self, type, data):
        self.data = data
        self.type = type
        self.start = None

    #def __init__(self, type, data):
    #    self.__dict__.update(locals())
    #    del self.self

    def is_empty(self):
        if((len(self.data) == 0) and (self.type == 0)):
            return True
        return False
        

class source_code_t:
    def __init__(self):

        self.m_blah = 0

        keywords = {
            "vera" : '''
 after       coverage_group join reg
 all         coverage_option little_endian repeat
 any         coverage_val local return
 around      default m_bad_state rules
 assoc_index depth m_bad_trans shadow
 assoc_size  dist m_state soft
 async       do   m_trans state
 bad_state   else negedge static
 bad_trans   end new string
 before      enum newcov super
 begin       event non_rand task
 big_endian  export none terminate
 bind        extends not this
 bind_var    extern null trans
 bit         for or typedef
 bit_normal  foreach output unpacked
 bit_reverse fork packed var
 break       function port vca
 breakpoint  hdl_node posedge vector
 case        hdl_task proceed verilog_node
 casex       hide prod verilog_task
 casez       if prodget vhdl_node
 class       illegal_self_transition prodset vhdl_task
 CLOCK       illegal_state program virtual
 constraint  illegal_transition protected virtuals
 continue    in public void
 coverage_block inout rand while
 coverage_def input randc wildcard
 coverage_depth integer randcase with
 coverage_goal interface randseq
''',
        
            "verilog" : '''
 always    end          ifnone       or         rpmos     tranif1
 and       endcase      initial      output     rtran     tri
 assign    endmodule    inout        parameter  rtranif0  tri0
 begin     endfunction  input        pmos       rtranif1  tri1
 buf       endprimitive integer      posedge    scalared  triand
 bufif0    endspecify   join         primitive  small     trior
 bufif1    endtable     large        pull0      specify   trireg
 case      endtask      macromodule  pull1      specparam vectored
 casex     event        medium       pullup     strong0   wait
 casez     for          module       pulldown   strong1   wand
 cmos      force        nand         rcmos      supply0   weak0
 deassign  forever      negedge      real       supply1   weak1
 default   for          nmos         realtime   table     while
 defparam  function     nor          reg        task      wire
 disable   highz0       not          release    time      wor
 edge      highz1       notif0       repeat     tran      xnor
 else      if           notif1       rnmos      tranif0   xor
''',

            "bash" : '''
 alias     awk         break      builtin
 cal       case        cat        cd
 cfdisk    chgrp       chmod      chown
 chroot    cksum       clear      cmp 
 comm      command     continue   cp
 cron      crontab     csplit     cut
 date      dc          dd         declare
 df        diff        diff3
 dir       dircolors   dirname    dirs
 du        echo        ed         egrep
 eject     enable      env        eval
 exec      exit        expand     export
 expr      factor      false      fdformat
 fdisk     fgrep       find       fmt
 fold      for         format     free
 fsck      gawk        getopts    grep
 groups    gzip        hash       head
 hostname  id          if         import
 info      install     join       kill
 less      let         ln         local
 locate    logname     logout     lpc
 lpr       lprint      lprintd    lprintq
 lprm      ls          m4         man
 mkdir     mkfifo      mknod      more
 mount     mtools      mv         nice
 nl        nohup       passwd     paste
 pathchk   popd        pr         printcap
 printenv  printf      ps         pushd
 pwd       quota       quotacheck quotactl
 ram       rcp         read       readonly
 remsync   return      rm         rmdir
 rpm       rsync       screen     sdiff
 sed       select      seq        set
 shift     shopt       shutdown   sleep
 sort      source      split      stat
 su        sum         symlink    sync
 tac       tail        tar        tee
 test      time        times      touch
 top       traceroute  trap       tr
 true      tsort       tty        type
 ulimit    umask       umount     unalias
 uname     unexpand    uniq       units
 unset     unshar      until      useradd
 usermod   users       uuencode   uudecode
 v         vdir        vi         watch
 wc        whereis     which      while
 who       whoami      xargs      yes
''',

            "c" : '''
 and          and_eq      asm         auto
 bitand       bitor       bool        break
 case         catch       char        class
 compl        const       const_cast  continue
 default      delete      do          double
 dynamic_cast else        enum        explicit
 export       extern      false       float
 for          friend      goto        if
 inline       int         long        mutable
 namespace    new         not         not_eq
 operator     or          or_eq       private
 protected    public      register    reinterpret_cast
 return       short       signed      sizeof
 static       static_cast struct      switch
 template     this        throw       true
 try          typedef     typeid      typename
 union        unsigned    using       virtual
 void         volatile    wchar_t     while
 xor          xor_eq
 uint8        uint16      uint32      uint64
 cs_uint8     cs_uint16   cs_uint32   cs_uint64
 cs_status    cs_float    cs_boolean  cs_int16
 cs_int32     cs_int16
''',

            "python" : '''
 and       del       from      not       while
 as        elif      global    or        with
 assert    else      if        pass      yield
 break     except    import    print
 class     exec      in        raise
 continue  finally   is        return 
 def       for       lambda    try
''',
            "shorte" : '''
 @body
 @doctitle @docsubtitle @docversion @docnumber @docrevisions @docfilename
 @h1 @h2 @h3 @h4 @h5 @h
 @text @p @pre
 @code @c @python @java @perl @tcl @d @vera @verilog @bash @xml @swift @go @javascript
 @include @include_child
 @sequence
 @table
 @vector
 @note @tbd @warning @question
 @ul
 @ol
 @struct @enum @prototype
 @acronyms @questions
 @input @embed @columns @column
 @testcasesummary @testcase @functionsummary @typesummary
 @inkscape
 @checklist
 @imagemap
 @image
''',
            "xml" : '''
 xml version
''',

            "perl" : '''
 chomp chop chr crypt hex index lc lcfirst length oct ord
 pack reverse rindex sprintf substr uc ucfirst
 
 pos quotemeta split study
 
 abs atan2 cos exp hex int log oct rand sin sqrt srand
 
 pop push shift splice unshift
 
 grep join map reverse sort unpack
 
 delete each exists keys values
 
 binmode close closedir dbmclose dbmopen die eof fileno
 flock format getc print printf read readdir readline rewinddir
 seek seekdir select syscall sysread sysseek syswrite tell
 telldir truncate warn write
 
 pack read syscall sysread sysseek syswrite unpack vec
 
 chdir chmod chown chroot fcntl glob ioctl link lstat mkdir
 open opendir readlink rename rmdir stat symlink sysopen
 unask unlink utime
 
 caller continue die do dump eval exit goto last next prototype
 redo return sub wantarray
 
 caller import local my our package use
 
 defined dump eval formline local my our prototype reset scalar
 undef wantarray
 
 alarm exec fork getpgrp getppid getpriority kill pipe
 readpipe setpgrp setpriority sleep system times wait waitpid
 
 do import no package require use
 
 bless dbmclose dbmopen package ref tie tied untie use
 
 accept bind connect getpeername getsockname getsockopt
 listen recv send setsockopt shutdown socket socketpair
 
 msgctl msgget msgrcv msgsnd semctl semget semop shmctl
 shmget shmread shmwrite
 
 endgrent endhostent endnetent endpwent getgrent getgrgid
 getgrnam getlogin getpwent getpwnam getpwuid setgrent setpwent
 
 endprotoent endservent gethostbyaddr gethostbyname
 gethostent getnetbyaddr getnetbyname getnetent
 getprotobyname getprotobynumber getprotoent getservbyname
 getservbyport getservent sethostent setnetent setprotoent
 setservent
 
 gmtime localtime time times
''',

            "java" : '''
 abstract continue    for          new         switch
 assert   default     goto         package     synchronized
 boolean  do          if           private     this
 break    double      implements   protected   throw
 byte     else        import       public      throws
 case     enum        instanceof   return      transient
 catch    extends     int          short       try
 char     final       interface    static      void
 class    finally     long         strictfp    volatile
 const    float       native       super       while
            
''',
            "tcl" : '''
 puts
''',

            "sql" : '''
 CREATE TABLE INTEGER AUTO_INCREMENT
 TEXT DEFAULT PRIMARY KEY INSERT INTO VALUES WHERE LIKE
''',
            "gnuplot" : '''''',
            
            "batch" : '''
call cd chdir cls copy del dir echo @echo exit for if md mkdir
move rd rmdir readline ren rename set setlocal shift start title
CALL CD CHDIR CLS COPY DEL DIR ECHO @ECHO EXIT FOR IF MD MKDIR
MOVE RD RMDIR READLINE REN RENAME SET SETLOCAL SHIFT START TITLE
''',

            # Apple's swift programming language
            "swift" : '''
class deinit enum extension func import init inout internal
let operator private protocol public static struct subscript typealias var

break case continue default defer do else fallthrough for guard if in repeat return switch where while

as catch dynamicType false is nil rethrows super self Self throw throws true try __COLUMN__ __FILE__ __FUNCTION__ __LINE__

associativity convenience dynamic didSet final get infix lazy left mutating non nonumtating optional override postfix
precendence prefix Protocol required right set Type unowned weak willSet
''',

            # Google's GO programming language
            "go" : '''
break case chan const continue
default defer else fallthrough for
func go goto if import
interface map package range return
select struct switch type var

bool uint8 uint16 uint32 uint64 int8 int16 int32 int64 float32 float64
complex64 complex128 byte run uint int uintptr

true false iota nil

append cap close complex copy delete imag len
make new panic print println real recover
''',
            
            # The javascript language
            "javascript" : '''
abstract arguments boolean break byte
case catch char class const
continue debugger default delete do
double else enum eval export
extends false final finally float
for function goto if implements
import in instanceof int interface
let long native new null
package private protected public return
short static super switch synchronized
this throw throws transient true
try typeof var void volatile
while with yield

Array Date eval function hasOwnProperty
Infinity isFinite isNaN isPrototypeOf length
Math NaN name Number Object
prototype String toString undefined valueOf

alert all anchor anchors area
assign blur button checkbox clearInterval
clearTimeout clientInformation close closed confirm
constructor crypto decodeURI decodeURIComponent defaultStatus
document element elements embed embeds
encodeURI encodeURIComponent escape event fileUpload
focus form forms frame innerHeight
innerWidth layer layers link location
mimeTypes navigate navigator frames frameRate
hidden history image images offscreenBuffering
open opener option outerHeight outerWidth
packages pageXOffset pageYOffset parent parseFloat
parseInt password pkcs11 plugin propmt
propertyIsEnum radio reset screenX screenY
scroll secure select self setInterval
setTimeout status submit taint text
textarea top unescape untaint window

onblur onclick onerror onfocus
onkeydown onkeypress onkeyup onmouseover
onload onmouseup onmousedown onsubmit
'''
        }

        keywords["cpp"] = keywords["c"]
        keywords["pycairo"] = keywords["python"]
       
        self.m_keywords = {}

        for language in keywords:

            #print language

            keyword_string = keywords[language]
            keyword_string = keyword_string.replace("\n", " ")

            keyword_list = keyword_string.split(' ') #re.split(r'\n| +', keywords[language])

            self.m_keywords[language] = {}

            for keyword in keyword_list:
                word = keyword.strip()
                if(len(word) > 0):
                    #print "  keyword: [%s]" % word
                    self.m_keywords[language][word] = 1
        #sys.exit(-1)


    def get_keyword_list(self, language):

        if(language in ("c", "code")):
            return self.m_keywords["c"]

        return self.m_keywords[language]


    def parse_source_code(self, type, source, source_file, source_line):
        
        tags = []
        #print "BEFORE\n======\n%s" % source

        source_lang = type

        tmp = shorte_get_config('shorte', 'validate_line_length')
        if(tmp):
            parts = tmp.split('@')
            check  = parts[0]
            length = int(parts[1])

            if(check in ('warn', 'error')):
                lines = source.split('\n')
                i = 0
                for line in lines:
                    i += 1
                    if(len(line) > length):
                        if(check == 'warn'):
                            WARNING("Source line %d is too long (%d chars) in %s.%d\n  [%s]" % (i, len(line), source_file, source_line, line))
                        else:
                            ERROR("Source line %d is too long (%d chars) in %s.%d\n  [%s]" % (i, len(line), source_file, source_line, line))

        source = trim_blank_lines(source)

        source = source.rstrip()
        source = trim_leading_indent(source, allow_second_line_indent_check=False)

        # Now parse the source code into
        # a list of tags
        state = STATE_NORMAL
        
        i = 0
        end = len(source)
        tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')

        line = 1
        states = []
        states.append(state)

        is_sql = False
        is_batch = False
        if(source_lang == 'sql'):
            is_sql = True
        elif(source_lang == 'batch'):
            is_batch = True

        while i < end:

            #print "SOURCE:"
            #print source[0:i+1]

            state = states[-1]
            #print "STATE: %d" % state

            # If we hit an escape sequence then skip it
            # and move to the next character.
            #if(source[i] == '\\' and source[i+1] != '\\'):
            #    i+=1
            #    continue

            if(not (state in (STATE_MCOMMENT, STATE_COMMENT, STATE_PREPROCESSOR, STATE_INLINE_STYLING, STATE_STRING)) and (source[i] in (' ', '(', ')', ','))):
                type = tag.type
                tags.append(tag)

                if(source[i] == ' '):
                    tag = shorte_source_code_tag_t(TAG_TYPE_WHITESPACE, ' ')
                elif(source[i] in ('(', ')')):
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, source[i])
                elif(source[i] in (',')):
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, source[i])

                tags.append(tag)

                tag = shorte_source_code_tag_t(type, '')
                i += 1
                continue

            if(source[i] == '\n'):
                type = tag.type

                if(state == STATE_STRING):
                    tstart = tag.start

                #tag["d"] += source[i]

                if(not tag.is_empty()):
                    tags.append(tag)

                tag = shorte_source_code_tag_t(TAG_TYPE_NEWLINE, '\n')
                tags.append(tag)

                if(state in [STATE_COMMENT, STATE_PREPROCESSOR]):
                #if(state == STATE_COMMENT or state == STATE_PREPROCESSOR):
                    states.pop()
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                elif(state == STATE_STRING):
                    tag = shorte_source_code_tag_t(type, '')
                    tag.start = tstart
                else:
                    tag = shorte_source_code_tag_t(type, '')
                
                i += 1

                continue

            if(state == STATE_NORMAL):
                # Treat # as either a single line comment or
                # a pre-processor statement
                if(source[i] == '#'):

                    if(not (source_lang in ('c', 'cpp'))):
                        states.append(STATE_COMMENT)

                        if(not tag.is_empty()):
                            tags.append(tag)

                        tag = shorte_source_code_tag_t(TAG_TYPE_COMMENT, "#") 
                    else:
                        states.append(STATE_PREPROCESSOR)

                        if(not tag.is_empty()):
                            tags.append(tag)

                        tag = shorte_source_code_tag_t(TAG_TYPE_PREPROCESSOR, "#")

                # Treat // as a single line comment
                elif(source[i] == '/' and source[i+1] == '/'):
                    states.append(STATE_COMMENT)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_COMMENT, '/')

                # Treat -- as a single line comment in SQL blocks
                elif(is_sql and (source[i] == '-' and source[i+1] == '-')):
                    states.append(STATE_COMMENT)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_COMMENT, '-')

                # Treat rem as a single line comment in batch files
                elif(is_batch and (source[i:i+3] == 'rem')):
                    states.append(STATE_COMMENT)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_COMMENT, 'r')
                    
                # Treat /* as the start of a multi-line comment
                elif(source[i] == '/' and source[i+1] == '*'):
                    states.append(STATE_MCOMMENT)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_MCOMMENT, '/')


                # If this is an XML based document then treat
                # <!-- as a multi-line comment
                elif(source[i:i+4] == '<!--'):
                    states.append(STATE_XMLCOMMENT)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_XMLCOMMENT, '<')


                # Check for python style strings
                elif(source[i:i+3] == "'''" or source[i:i+3] == '"""'):
                    states.append(STATE_STRING)
                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_STRING, source[i:i+3])
                    tag.start = source[i:i+3]
                    i += 2
                
                # Treat " or ''' as the start of a string
                elif(source[i] in ('"', "'")): # or source[i] == "'"):
                    states.append(STATE_STRING)

                    if(not tag.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_STRING, source[i])
                    tag.start = source[i]

                #elif(source_lang == "python" and (source[i:i+3] == "'''")):
                #    states.append(STATE_STRING)
                #    tags.append(tag)
                #    tag = {}
                #    tag["d"] = "'"
                #    tag["t"] == TAG_TYPE_STRING

                # Treat @{ as inline styling
                elif(source[i] == '@' and source[i+1] == '{'):
                    states.append(STATE_INLINE_STYLING)
                    if(not tags.is_empty()):
                        tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '@')

                else:
                    tag.data += source[i] 

            elif(state in (STATE_COMMENT, STATE_PREPROCESSOR)):

                if(source[i] == '\n'):
                    tag.data += source[i]
                    tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, "")

                    states.pop()
                else:
                    tag.data += source[i]

            elif(state == STATE_MCOMMENT):
                #if(source[i-1] == '*' and source[i] == '/'):
                if(source[i-1:i+1] == '*/'):
                    tag.data += source[i]
                    tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, "")
                    states.pop()
                else:
                    tag.data += source[i]

            elif(state == STATE_XMLCOMMENT):
                #if(source[i-2] == '-' and source[i-1] == '-' and source[i] == '>'):
                if(source[i-2:i+1] == '-->'):
                    tag.data += source[i]
                    tags.append(tag)

                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, "")
                    states.pop()
                else:
                    tag.data += source[i]

            elif(state == STATE_INLINE_STYLING):
                if(source[i] == '}'):
                    tag.data += source[i]
                    tags.append(tag)
                    
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                    states.pop()

                else:
                    tag.data += source[i]

            elif(state == STATE_STRING):
                #if((tag.data.startswith("'''") and source[i:i+3] == "'''") or
                #   (tag.data.startswith('"""') and source[i:i+3] == '"""')):
                if((tag.start == '\'\'\'') and (source[i:i+3] == "'''")):

                    tag.data += source[i:i+3]
                    tags.append(tag)
                    i += 2 
                    
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                    states.pop()
                elif((tag.start == '"""') and (source[i:i+3] == '"""')):
                    tag.data += source[i:i+3]
                    tags.append(tag)
                    i += 2 
                    
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                    states.pop()

                elif(tag.start == '"' and source[i] == '"'):
                    tag.data += source[i]
                    tags.append(tag)
                    
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                    states.pop()

                elif(tag.start == "'" and source[i] == "'"):
                    tag.data += source[i]
                    tags.append(tag)
                    
                    tag = shorte_source_code_tag_t(TAG_TYPE_CODE, '')
                    states.pop()

                #elif(source_lang == "python" and (started_with ==  "'") and (source[i:i+3] == "'''")):
                #    tags["d"] += source[i:i+3]
                #    i += 2
                #    tags.append(tag)

                #    tag = {}
                #    tag["d"] = ''
                #    tag["t"] = TAG_TYPE_CODE
                #    states.pop()

                else:
                    tag.data += source[i]

            i += 1
        
        if(not tag.is_empty()):
            tags.append(tag)

        return tags

        tags_output = []
        for tag in tags:
            #if(tag.data == "" and tag.type == 0):
            if(tag.is_empty()):
                pass
            else:
                #print "TAG: [%s](%d)" % (tag["d"], tag["t"])
                #tmp = {}
                #tmp["d"] = tag.data
                #tmp["t"] = tag.type
                #tags_output.append(tmp)
                tags_output.append(tag)

        return tags_output


class type_t:
    def __init__(self):
        self.name = ""
        self.description = None
        self.description_unparsed=None
        self.deprecated = False
        self.deprecated_msg = ""
        self.private = False
        self.comment = None
        self.source = None
        self.example = None
        self.example_result = None
        self.file = None
        self.line = None
        self.type = ""
        self.see_also = None
        self.since = None
    
    def has_fields(self):
        return False
    def has_values(self):
        return False
    def has_returns(self):
        return False
    def has_params(self):
        return False

    def get_name(self):
        return self.name
    def get_title(self):
        return self.name
    def set_name(self, name):
        self.name = name.strip()

    def has_description(self,textblock=True):
        if(textblock == True):
            if(self.description == None):
                return False
            return True
        else:
            if(self.description_unparsed == None):
                return False
            return True

    def get_description(self,textblock=True):
        if(textblock==True):
            return self.description
        return self.description_unparsed

    def set_description(self,desc,textblock=True):
        if(textblock==True):
            self.description = desc
        else:
            self.description_unparsed = desc
    
    def get_file(self):
        return self.file
    def set_file(self, file):
        self.file = file

    def get_line(self):
        return self.line
    def set_line(self, line):
        self.line = line

    def has_example(self):
        if(None != self.example):
            return True
        return False
    def get_example(self):
        return self.example
    def set_example(self, example, analyzer=None, language=None):
        tmp = analyzer.parse_source_code(language, example, self.file, self.line)
        cb = code_block_t()
        cb.set_language(language)
        cb.set_parsed(tmp)
        cb.set_unparsed(example)
        self.example = cb

    def set_example_result(self, result):
        self.example_result = result
    def get_example_result(self):
        return self.example_result
    def has_example_result(self):
        if(None != self.example_result):
            return True
        return False

    def has_deprecated(self):
        if(self.deprecated in (None, False)):
            return False
        return True
    def get_deprecated(self):
        return self.deprecated
    def get_deprecated_msg(self):
        return self.deprecated_msg
    def set_deprecated(self, deprecated, msg):
        self.deprecated = deprecated
        self.deprecated_msg = msg

    def has_see_also(self):
        if(None != self.see_also):
            if(self.see_also.strip() == ""):
                return False
            return True
        return False
    def get_see_also(self):
        return self.see_also
    def set_see_also(self, see_also):
        self.see_also = see_also

    def get_private(self):
        return self.private
    def is_private(self):
        return self.private
    def set_private(self, priv):
        self.private = priv

    def has_since(self):
        if(None == self.since):
            return False
        return True
    def get_since(self):
        return self.since
    def set_since(self, since):
        self.since = since

    def set_comment(self, comment):
        self.comment = comment

class enum_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.values = {}
        self.max_cols = 0
        self.type = "enum"
    
    def has_values(self):
        return True

    def get_values(self):
        return self.values

    def __str__(self):
        attrs = "Enum"
        attrs += "  name:       %s\n" % self.name
        attrs += "  desc:       %s\n" % self.description
        attrs += "  deprecated: %s (%s)\n" % (self.deprecated, self.deprecated_msg)
        attrs += "  private:    %s\n" % self.private
        attrs += "  values:\n"  

        for val in self.values:
            attrs += "    "
            for col in val['cols']:
                attrs += col["text"]
                break
            attrs += "\n"

        return attrs

class enum_value_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.name = None
        self.desc = None
        self.desc_unparsed = None
        self.value = None

    def set_value(self, value):
        self.value = value
    def get_value(self):
        return self.value

class field_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.attrs = []
        self.is_reserved = False
        self.is_header = False
        self.is_title = False
        self.is_subheader = False
        self.is_spacer = False
        self.is_array = False
        self.array_elem_size = 1
        self.width = 0
        self.start = 0
        self.end = 0
        self.type = None
        self.name = None
        self.desc = None
        self.desc_unparsed = None
        self.attributes = None

    def get_bits(self):
        return "[%d:%d]" % (self.start, self.end)

    def from_hash(self, field):
        self.attrs = field["attrs"]
        self.is_reserved = field["is_reserved"]
        self.is_header = field["is_header"]
        self.is_title = field["is_title"]
        self.is_subheader = field["is_subheader"]
        self.is_spacer = field["is_spacer"]
        if(field.has_key("is_array")):
            self.is_array = field["is_array"]
        if(field.has_key("array_elem_size")):
            self.array_elem_size = field["array_elem_size"]
        
        if(self.is_spacer):
            self.type = "spacer"
            self.name = ""
            self.desc = ""
            self.desc_unparsed = ""
            self.attributes = ""
        else:
            self.type = self.attrs[0]["text"]
            self.name = self.attrs[1]["text"]
            self.desc = self.attrs[2]["textblock"]
            self.desc_unparsed = self.attrs[2]["text"]
            self.attributes = self.attrs[3]["text"]

        if(field.has_key("width")):
            self.width = field["width"]
            self.start = field["start"]
            self.end   = field["end"]
        #    self.type  = field["t"]
        #else:
        #    self.type = self.attrs[0]["text"]
        #else:
        #    print field
        #    WARNING("Field %s has no type" % self.name)
        #
        #
    
    def get_name(self):
        if(self.name == None):
            if(len(self.attrs) >= 2):
                return self.attrs[1]["text"]
            return ""
        return self.name
    #def get_title(self):
    #    return self.get_name()

    #def set_name(self, name):
    #    self.name = name

    def get_description(self):
        if(self.desc == None):
            if(len(self.attrs) >= 3):
                return self.attrs[2]["textblock"]
            return "empty"

        return self.desc
    def get_description_unparsed(self):
        return self.desc_unparsed

    def set_description(self, desc):
        self.desc = desc

    def set_description_unparsed(self, desc):
        self.desc_unparsed = desc

    def get_field_is_bits(self):
        bits = self.get_type()
        if(bits.find("'b") != -1):
            return True
        return False

    def get_is_header(self):
        return False

    def get_is_spacer(self):
        return self.is_spacer
    
    def get_is_reserved(self):
        return self.is_reserved

    def get_type(self):
        if(len(self.attrs) >= 2):
            # DEBUG BRAD: I should investigate changing this back
            return "%s" % self.type #return self.attrs[0]["text"]
        return self.type

    def append_attr(self, val):
        self.attrs.append(val)

        if(len(self.attrs) == 1):
            self.set_type(val["text"])
        elif(len(self.attrs) == 2):
            self.set_name(val["text"])
        elif(len(self.attrs) == 3):
            self.set_description(val["textblock"])
            self.set_description_unparsed(val["text"])
        else:
            self.attributes = val["text"]

    def has_attributes(self):
        if(self.attributes != None):
            return True
        return False

    def set_type(self, type):
        self.type = type

    def __str__(self):
        try:
            attrs =  "Field\n"
            attrs += "  type: %s\n" % self.type
            attrs += "  name: %s\n" % self.name
            attrs += "  desc: %s\n" % self.desc
            attrs += "  attrs:\n"
            attrs += "    %s\n" % self.attrs[1]["text"]
        except:
            WARNING(self.get_name())

        return attrs


class struct_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.fields = []
        self.record = None
        self.image = None
        self.type = "struct"

        # This contains a list of any headings to associate
        # with the structure.
        self.headings = {}

    def has_fields(self):
        return True

    def __str__(self):
        attrs = "Struct"
        attrs += "  name:     %s\n" % self.name
        attrs += "  desc:     %s\n" % self.description
        attrs += "  deprecated: %s (%s)\n" % (self.deprecated, self.deprecated_msg)
        attrs += "  private:    %s\n" % self.private
        attrs += "  file:       %s\n" % self.file
        if(self.line == None):
            attrs += "  line:       None\n"
        else:
            attrs += "  line:       %d\n" % self.line
        attrs += "  fields:\n"  

        fields = self.get_fields()

        for val in fields:
            attrs += val.__str__()

        return attrs

    def get_max_cols(self):
        return self.max_cols

    def has_headings(self):
        if(len(self.headings) > 0):
            return True
        return False

    def get_headings(self):

        return self.headings

    def get_fields(self):
        
        #fields = []
        #for f in self.fields:
        #    f2 = field_t()
        #    f2.from_hash(f)
        #    fields.append(f2)

        #return fields
        return self.fields

    def has_field_attributes(self):

        for f in self.fields:
            if(f.has_attributes()):
                return True
        
        return False



class param_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.param_io = None
        self.param_type = None

    def has_io(self):
        if(self.param_io != None):
            return True
        return False
    def get_io(self):
        return self.param_io
    def set_io(self, io):
        self.param_io = io

    def set_type(self, type):
        self.param_type = type
    def get_type(self):
        return self.param_type
    def has_type(self):
        if(self.param_type != None):
            return True
        return False

    def __str__(self):
        output = '''param_t
  name: %s
  type: %s
  io:   %s
  desc: %s
''' % (self.name, self.param_type, self.param_io, self.get_description(textblock=False))
        return output

class prototype_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.type = "prototype"
        self.prototype = None
        self.returns = None
        self.pseudocode = None
        self.params = None
        self.classobj = None
        self.access_spec = None

    def has_class(self):
        if(None != self.classobj):
            return True
        return False
    def set_class(self, obj):
        self.classobj = obj
    def get_class(self):
        return self.classobj

    def has_access_spec(self):
        if(None != self.access_spec):
            return True
        return False
    def set_access_spec(self, spec):
        self.access_spec = spec
    def get_access_spec(self):
        return self.access_spec


    def has_prototype(self):
        if(None != self.prototype):
            return True
        return False
    def get_prototype(self):
        return self.prototype
    
    def set_prototype(self, prototype, analyzer=None, language=None):
        tmp = analyzer.parse_source_code(language, prototype, self.file, self.line)
        cb = code_block_t()
        cb.set_language(language)
        cb.set_parsed(tmp)
        cb.set_unparsed(prototype)
        self.prototype = cb

    def has_returns(self):
        if(None != self.returns):
            return True

    def __str__(self):

        return False
    def get_returns(self):
        return self.returns
    def set_returns(self, returns):
        self.returns = returns

    def has_pseudocode(self):
        if(None != self.pseudocode):
            return True
        return False
    def get_pseudocode(self):
        return self.pseudocode
    def set_pseudocode(self, pseudocode, analyzer=None, language=None):
        tmp = analyzer.parse_source_code(language, pseudocode, self.file, self.line)
        cb = code_block_t()
        cb.set_language(language)
        cb.set_parsed(tmp)
        cb.set_unparsed(pseudocode)
        self.pseudocode = cb
    

    def has_params(self):
        if(None != self.params and len(self.params) > 0):
            return True
        return False
    def get_params(self):
        return self.params
    def set_params(self, params):
        self.params = params
    def validate_params(self):
        for param in self.params:
            if(not param.has_description()):
                WARNING("Parameter %s.%s has no description (%s @ line %d)" % (
                        self.get_name(), param.name, self.get_file(), self.get_line()))

    def has_called_by(self):
        return False
    def get_called_by(self):
        return "TBD"
    def has_calls(self):
        return False
    def get_calls(self):
        return "TBD"

    def __str__(self):
        attrs =  "Prototype:\n"
        attrs += "===================================================\n"
        attrs += "  Name:      %s\n" % self.name
        attrs += "  Prototype: %s\n" % self.prototype.get_unparsed()
        attrs += "  Description:\n"
        lines = self.get_description(textblock=False).split("\n")
        for line in lines:
            if(len(line) > 0):
                attrs += "    %s\n" % line
        attrs += "  Returns:\n"
        attrs += "    %s\n" % self.returns

        if(self.has_example()):
            attrs += "  Example:\n"
            attrs += indent_lines(self.get_example().get_unparsed(), '    ')

        return attrs


class code_block_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        
        self.language = None
        self.parsed = None
        self.unparsed = None

    def get_parsed(self):
        return self.parsed
    def set_parsed(self, parsed):
        self.parsed = parsed
    def get_unparsed(self):
        return self.unparsed
    def set_unparsed(self, unparsed):
        self.unparsed = unparsed
    def get_language(self):
        return self.language
    def set_language(self, language):
        self.language = language

    def __str__(self):
        output =  'code_block_t'
        output += '  language = %s' % self.language
        output += '  unparsed'
        output += indent_lines(self.unparsed, '    ')
        return output

class_uid = 0

class class_t(type_t):
    def __init__(self):
        global class_uid
        type_t.__init__(self)
        self.value = ""
        self.type = "class"
        self.m_prototypes = {}
        self.id = class_uid
        class_uid += 1
        self.m_types = {}

        self.m_members = {}
        self.m_members['public'] = {}
        self.m_members['private'] = {}
        self.m_members['property'] = {}

        self.m_methods = {}
        self.m_methods['public'] = {}
        self.m_methods['private'] = {}

    def prototype_add(self, ptype):
        print "Adding prototype %s" % ptype.get_name()
        self.m_prototypes[ptype.get_prototype().get_unparsed()] = ptype

    def method_add(self, method, access='public'):
        self.m_methods[access][method] = method

    def methods_get(self, access='public'):
        return self.m_methods[access]

    def member_add(self, member, access='public'):
        self.m_members[access][member] = member

    def members_get(self, access='public'):
        return self.m_members[access]

    #def prototype_add(self, category, pt):
    #    self.m_prototypes[category][pt] = pt

    def __str__(self):
        output = '''Class
  id:    %d
  name:  %s
''' % (self.id, self.name)

        if(len(self.m_prototypes) > 0):
            output += '  prototypes:\n'

            for key in self.m_prototypes:
                if(key != None):
                    print "KEY: %s" % key
                    output += '    ' + key + '\n'

        return output

class define_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.value = ""
        self.type = "define"

    def __str__(self):
        output = '''Define
  name:  %s
  value: %s
''' % (self.name, self.value)

        return output


class comment_t:
    def __init__(self):
        self.params = {}
        self.returns = None
        self.example = None
        self.private = False
        self.see_also = None
        self.deprecated = False
        self.deprecated_msg = None
        self.heading = None
        self.since = None
        self.modifiers = {}
        
        # For types that have pseudocode associated
        # with them, primarily function prototypes
        self.pseudocode = None

        self.description = None

    def is_private(self):
        return self.private

    def has_description(self):
        if(self.description != None):
            return True
        return False
    def get_description(self):
        return self.description

    def has_example(self):
        if(self.example != None):
            return True
        return False

    def get_example(self):
        return self.example

    def has_returns(self):
        if(self.returns != None):
            return True
        return False
    def get_returns(self):
        return self.returns

    def has_pseudocode(self):
        if(self.pseudocode != None):
            return True
        return False
    def get_pseudocode(self):
        return self.pseudocode

    def has_see_also(self):
        if(self.see_also != None):
            return True
        return False
    def get_see_also(self):
        return self.see_also

    def has_heading(self):
        if(self.heading != None):
            return True
        return False
    def get_heading(self):
        return self.heading

    def has_since(self):
        if(self.since != None):
            return True
        return False
    def get_since(self):
        return self.since

    def has_deprecated(self):
        if(self.deprecated_msg != None):
            return True
        return False
    def get_deprecated(self):
        return self.deprecated_msg

    def has_modifiers(self, section):
        if(self.modifiers.has_key(section)):
            return True
        return False
    def get_modifiers(self, section):
        return self.modifiers[section]

