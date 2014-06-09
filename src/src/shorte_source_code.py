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
 @doctitle @docsubtitle @docversion @docnumber @docrevisions
 @h1 @h2 @h3 @h4 @h5
 @text @p @pre
 @c @python @java @perl @tcl @d @vera @verilog
 @include @include_child
 @sequence
 @table
 @struct
 @vector
 @note
 @ul
 @ol
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
'''
        }
       
        self.m_keywords = {}

        for language in keywords:

            #print language

            keyword_list = keywords[language].split(' ') #re.split(r'\n| +', keywords[language])

            self.m_keywords[language] = {}

            for keyword in keyword_list:
                word = keyword.strip()
                if(len(word) > 0):
                    #print "keyword: %s" % word
                    self.m_keywords[language][word] = 1


    def get_keyword_list(self, language):

        if(language in ("c", "code")):
            return self.m_keywords["c"]

        return self.m_keywords[language]


    def create_tag(self, type, data):

        tag = {}
        tag["data"] = data
        tag["type"] = type

        return tag
    
    def parse_source_code(self, type, source):
        
        tags = []
        #print "BEFORE\n======\n%s" % source

        source_lang = type

        source = trim_blank_lines(source)

        #print "AFTER 1\n======\n%s" % source

        source = source.rstrip()
        source = trim_leading_indent(source)
        
        #print "AFTER 2\n======\n%s" % source

        # Now parse the source code into
        # a list of tags
        state = STATE_NORMAL
        
        i = 0
        end = len(source)
        tag = self.create_tag(TAG_TYPE_CODE, '')

        line = 1
        states = []
        states.append(state)

        while i < end:

            state = states[-1]
            #print "STATE: %d" % state

            # If we hit an escape sequence then skip it
            # and move to the next character.
            if(source[i] == '\\' and source[i+1] != '\\'):
                i+=1
                continue

            if(not (state in (STATE_MCOMMENT, STATE_COMMENT, STATE_INLINE_STYLING, STATE_STRING)) and (source[i] in (' ', '(', ')', ','))):
                type = tag["type"]
                tags.append(tag)

                if(source[i] == ' '):
                    tag = self.create_tag(TAG_TYPE_WHITESPACE, ' ')
                elif(source[i] in ('(', ')')):
                    tag = self.create_tag(TAG_TYPE_CODE, source[i])
                elif(source[i] in (',')):
                    tag = self.create_tag(TAG_TYPE_CODE, source[i])

                tags.append(tag)

                tag = self.create_tag(type, '')
                i += 1
                continue

            if(source[i] == '\n'):
                type = tag["type"]

                #tag["data"] += source[i]
                tags.append(tag)

                tag = self.create_tag(TAG_TYPE_NEWLINE, '\n')
                tags.append(tag)

                if(state == STATE_COMMENT):
                    states.pop()
                    tag = self.create_tag(TAG_TYPE_CODE, '')
                else:
                    tag = self.create_tag(type, '')
                
                i += 1

                continue

    
            if(state == STATE_NORMAL):
                # Treat # as a single line comment
                if(source[i] == '#'):
                    states.append(STATE_COMMENT)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = "#"
                    tag["type"] = TAG_TYPE_COMMENT

                # Treat // as a single line comment
                elif(source[i] == '/' and source[i+1] == '/'):
                    states.append(STATE_COMMENT)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = '/'
                    tag["type"] = TAG_TYPE_COMMENT

                # Treat -- as a single line comment in SQL blocks
                elif(source_lang == "sql" and (source[i] == '-' and source[i+1] == '-')):
                    states.append(STATE_COMMENT)
                    tags.append(tag)
                    tag = {}
                    tag["data"] = '-'
                    tag["type"] = TAG_TYPE_COMMENT
                    
                # Treat /* as the start of a multi-line comment
                elif(source[i] == '/' and source[i+1] == '*'):
                    states.append(STATE_MCOMMENT)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = '/'
                    tag["type"] = TAG_TYPE_MCOMMENT


                # If this is an XML based document then treat
                # <!-- as a multi-line comment
                elif(source[i:i+4] == '<!--'):
                    states.append(STATE_XMLCOMMENT)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = '<'
                    tag["type"] = TAG_TYPE_XMLCOMMENT

                # Treat " or ''' as the start of a string
                elif(source[i] == '"'): # or source[i] == "'"):
                    states.append(STATE_STRING)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = '"'
                    tag["type"] = TAG_TYPE_STRING

                # Check for python style strings
                elif(source[i:i+3] == "'''" or source[i:i+3] == '"""'):
                    states.append(STATE_STRING)
                    i += 2
                    tags.append(tag)

                    tag = {}
                    tag["data"] = "'''"
                    tag["type"] = TAG_TYPE_STRING

                #elif(source_lang == "python" and (source[i:i+3] == "'''")):
                #    states.append(STATE_STRING)
                #    tags.append(tag)
                #    tag = {}
                #    tag["data"] = "'"
                #    tag["type"] == TAG_TYPE_STRING

                # Treat @{ as inline styling
                elif(source[i] == '@' and source[i+1] == '{'):
                    states.append(STATE_INLINE_STYLING)
                    tags.append(tag)

                    tag = {}
                    tag["data"] = '@'
                    tag["type"] = TAG_TYPE_CODE

                else:
                    tag["data"] += source[i] 

            elif(state == STATE_COMMENT):

                if(source[i] == '\n'):
                    tag["data"] += source[i]
                    tags.append(tag)

                    tag = {}
                    tag["data"] = ""
                    tag["type"] = TAG_TYPE_CODE

                    states.pop()
                else:
                    tag["data"] += source[i]

            elif(state == STATE_MCOMMENT):
                if(source[i-1] == '*' and source[i] == '/'):
                    tag["data"] += source[i]
                    tags.append(tag)

                    tag = {}
                    tag["data"] = ""
                    tag["type"] = TAG_TYPE_CODE
                    states.pop()
                else:
                    tag["data"] += source[i]

            elif(state == STATE_XMLCOMMENT):
                if(source[i-2] == '-' and source[i-1] == '-' and source[i] == '>'):
                    tag["data"] += source[i]
                    tags.append(tag)

                    tag = {}
                    tag["data"] = ""
                    tag["type"] = TAG_TYPE_CODE
                    states.pop()
                else:
                    tag["data"] += source[i]

            elif(state == STATE_INLINE_STYLING):
                if(source[i] == '}'):
                    tag["data"] += source[i]
                    tags.append(tag)
                    
                    tag = {}
                    tag["data"] = ''
                    tag["type"] = TAG_TYPE_CODE
                    states.pop()

                else:
                    tag["data"] += source[i]

            elif(state == STATE_STRING):

                if((tag["data"].startswith("'''") and source[i:i+3] == "'''") or
                   (tag["data"].startswith('"""') and source[i:i+3] == '"""')):

                    tag["data"] += source[i:i+3]
                    tags.append(tag)
                    i += 2 
                    
                    tag = {}
                    tag["data"] = ''
                    tag["type"] = TAG_TYPE_CODE
                    states.pop()

                elif(source[i] == '"'):
                    tag["data"] += source[i]
                    tags.append(tag)
                    
                    tag = {}
                    tag["data"] = ''
                    tag["type"] = TAG_TYPE_CODE
                    states.pop()

                #elif(source_lang == "python" and (started_with ==  "'") and (source[i:i+3] == "'''")):
                #    tags["data"] += source[i:i+3]
                #    i += 2
                #    tags.append(tag)

                #    tag = {}
                #    tag["data"] = ''
                #    tag["type"] = TAG_TYPE_CODE
                #    states.pop()

                else:
                    tag["data"] += source[i]

            i += 1
        
        tags.append(tag)

        tags_output = []
        for tag in tags:
            if(tag["data"] == "" and tag["type"] == 0):
                do_nothing = 1 
            else:
                #print "TAG: [%s](%d)" % (tag["data"], tag["type"])
                tags_output.append(tag)

        return tags_output


class type_t:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.deprecated = False
        self.deprecated_msg = ""
        self.private = False
        self.comment = None
        self.source = None
        self.example = None
        self.type = ""

class enum_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.values = {}
        self.max_cols = 0
        self.type = "enum"

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

class struct_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.fields = {}
        self.record = None
        self.image = None
        self.type = "struct"
        self.private = False

        # This contains a list of any headings to associate
        # with the structure.
        self.headings = {}

    def __str__(self):
        attrs = "Struct"
        attrs += "  name:     %s\n" % self.name
        attrs += "  desc:     %s\n" % self.description
        attrs += "  deprecated: %s (%s)\n" % (self.deprecated, self.deprecated_msg)
        attrs += "  private:    %s\n" % self.private
        attrs += "  fields:\n"  

        for val in self.fields:
            attrs += "    "
            for col in val['cols']:
                attrs += col["text"]
                break
            attrs += "\n"

        return attrs

    def has_headings(self):
        if(len(self.headings) > 0):
            return True
        return False

    def get_headings(self):

        return self.headings



class prototype_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.type = "prototype"

    def __str__(self):
        attrs =  "Prototype"
        attrs += "  name:      %s\n" % self.name
        attrs += "  desc:      %s\n" % self.description

        return attrs


class define_t(type_t):
    def __init__(self):
        type_t.__init__(self)
        self.value = ""
        self.type = "define"


