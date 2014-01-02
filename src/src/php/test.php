<?php
include_once "shorte.php";

$shorte = new shorte_parser_t();

$text = <<<TEMPLATE
@h1 Heading 2
Hello world
- Test
- Test2

@table
- One | Two
- Three | Four

TEMPLATE;

print $shorte->parse($text);

?>

