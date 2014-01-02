<?php
include_once "shorte_defines.php";

class source_code_t
{
    function get_keyword_list($language)
    {
        $keywords = array();
        $keyword_str = '';
        

        if($language == "vera")
        {
            $keyword_str = <<<TEMPLATE
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
TEMPLATE;
        }

        else if($language == "verilog")
        {
            $keyword_str = <<<TEMPLATE
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
TEMPLATE;
        }

        else if($language == "bash")
        {
            $keyword_str = <<<TEMPLATE
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
TEMPLATE;
        }

        else if($language == "c" or $language == "code")
        {
            $keyword_str = <<<TEMPLATE
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
TEMPLATE;
        }

        else if($language == 'python')
        {
            $keyword_str = <<<TEMPLATE
and       del       from      not       while
as        elif      global    or        with
assert    else      if        pass      yield
break     except    import    print
class     exec      in        raise
continue  finally   is        return 
def       for       lambda    try
TEMPLATE;
        }

        else if($language == "perl")
        {
            $keyword_str = <<<TEMPLATE
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
TEMPLATE;
        }
        
        else if($language == "java")
        {
            $keyword_str = <<<TEMPLATE
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
            
TEMPLATE;
        }

        else if($language == "tcl")
        {
            $keyword_str = <<<TEMPLATE
puts
TEMPLATE;
        }

        $keyword_list = preg_split("/\n| +/", $keyword_str);

        foreach ($keyword_list as $keyword)
        {
            $keywords[trim($keyword)] = 1;
        }
        
        return $keywords;
    }

    function create_tag($type, $data)
    {
        $tag = array();
        $tag["data"] = $data;
        $tag["type"] = $type;

        return $tag;
    }
    
    function parse_source_code($type, $source)
    {
        $tags = array();
        //print "source = %s" % source

        $source = trim_blank_lines($source);
        $source = rtrim($source);
        $source = trim_leading_indent($source);

        // Now parse the source code into
        // a list of tags
        $state = STATE_NORMAL;
        
        $i = 0;
        $end = strlen($source);
        $tag = $this->create_tag(TAG_TYPE_CODE, "");

        $line = 1;
        $states = array();
        array_push($states, $state);

        while($i < $end)
        {
            $state = end($states);

            //if(not (state in (STATE_MCOMMENT, STATE_COMMENT)) and (source[i] in (' ', '(', ')', ','))):
            if(!(($state == STATE_MCOMMENT || $state == STATE_COMMENT)) and
                 ($source[$i] == ' ' ||
                  $source[$i] == '(' ||
                  $source[$i] == ')' ||
                  $source[$i] == ','))
            {

                $type = $tag["type"];
                array_push($tags, $tag);

                if($source[$i] == " ")
                {
                    $tag = $this->create_tag(TAG_TYPE_WHITESPACE, ' ');
                }
                else if($source[$i] == '(' or $source[$i] == ')')
                {
                    $tag = $this->create_tag(TAG_TYPE_CODE, $source[$i]);
                }
                else if($source[$i] == ',')
                {
                    $tag = $this->create_tag(TAG_TYPE_CODE, $source[$i]);
                }

                array_push($tags, $tag);

                $tag = $this->create_tag($type, '');
                $i += 1;
                continue;
            }

            if($source[$i] == "\n")
            {
                $type = $tag["type"];

                //tag["data"] += source[i]
                array_push($tags, $tag);

                $tag = $this->create_tag(TAG_TYPE_NEWLINE, "\n");
                array_push($tags, $tag);

                if($state == STATE_COMMENT)
                {
                    array_pop($states);
                    $tag = $this->create_tag(TAG_TYPE_CODE, '');
                }
                else
                {
                    $tag = $this->create_tag($type, '');
                }
                
                $i += 1;

                continue;
            }

    
            if($state == STATE_NORMAL)
            {
                if($source[$i] == '#')
                {
                    array_push($states, STATE_COMMENT);
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = "#";
                    $tag["type"] = TAG_TYPE_COMMENT;
                }

                else if($source[$i] == "/" and $source[$i+1] == "/")
                {
                    array_push($states, STATE_COMMENT);
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = "/";
                    $tag["type"] = TAG_TYPE_COMMENT;
                }
                    
                else if($source[$i] == "/" and $source[$i+1] == "*")
                {
                    array_push($states, STATE_MCOMMENT);
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = "/";
                    $tag["type"] = TAG_TYPE_MCOMMENT;
                }

                else if($source[$i] == '"')
                {
                    array_push($states, STATE_STRING);
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = '"';
                    $tag["type"] = TAG_TYPE_STRING;
                }
                else
                {
                    $tag["data"] .= $source[$i]; 
                }
            }
            else if($state == STATE_COMMENT)
            {
                if($source[$i] == "\n")
                {
                    $tag["data"] .= $source[$i];
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = "";
                    $tag["type"] = TAG_TYPE_CODE;

                    array_pop($states);
                }
                else
                {
                    $tag["data"] .= $source[$i];
                }
            }

            else if($state == STATE_MCOMMENT)
            {
                if($source[$i-1] == '*' and $source[$i] == '/')
                {
                    $tag["data"] .= $source[$i];
                    array_push($tags, $tag);

                    $tag = array();
                    $tag["data"] = "";
                    $tag["type"] = TAG_TYPE_CODE;
                    array_pop($states);
                }
                else
                {
                    $tag["data"] .= $source[$i];
                }
            }

            else if($state == STATE_STRING)
            {
                if($source[$i] == '"')
                {
                    $tag["data"] .= $source[$i];
                    array_push($tags, $tag);
                    
                    $tag = array();
                    $tag["data"] = '';
                    $tag["type"] = TAG_TYPE_CODE;
                    array_pop($states);
                }
                else
                {
                    $tag["data"] .= $source[$i];
                }
            }

            $i += 1;
        }
        
        array_push($tags, $tag);

        $tags_output = array();

        foreach($tags as $tag)
        {
            if($tag["data"] == "" and $tag["type"] == 0)
            {
                $do_nothing = 1;
            }
            else
            {
                // print "TAG: [%s](%d)" % (tag["data"], tag["type"])
                array_push($tags_output, $tag);
            }
        }

        return $tags_output;
    }
};


