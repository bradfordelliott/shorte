<?php
//date_default_timezone_set('America/Toronto');
//

class shorte_parser_t
{
    public function parse($input)
    {
        file_put_contents("shorte.scratch.tpl", $input);

        if(PHP_OS == "Linux")
        {
            $path_python = "/auto/tools/common/c5b64/activestate/ActivePython-2.7.2.5/bin/python";
            $path_shorte = "/home/belliott/tools/c5b64/shorte/shorte.py";
        }
        else
        {
            $path_python = "C:/usr/tools/python26/python.exe";
            $path_shorte = "C:/usr/work/shorte/src/shorte.py";
        }

        $path_tmpfile = "shorte.scratch.tpl";
    
        $output = `$path_python $path_shorte -f $path_tmpfile -p html_inline -s "html.inline_toc=0;html.header_numbers=0;" -t raw -o test`;

        return file_get_contents("test/index.html");
    }
}

?>
