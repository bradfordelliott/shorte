// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE
//
// This lexer is used to highlight code from the shorte
// documentation language:
//     https://github.com/bradfordelliott/shorte

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../../lib/codemirror"), require("../../addon/mode/simple"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../../lib/codemirror", "../../addon/mode/simple"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
"use strict";

  // Word boundaries used by auto-completion
  var WORD = /[@-\w$]+/, RANGE = 500;
 
  // The list of shorte keywords that can be used with
  // code completion
  var keyword_list = (
    // Document header
    "@doc.author @doc.filename @doc.number @doc.revisions @doc.subtitle @doc.title @doc.version " +
    // Body
    "@body " +
    // Headings
    "@h @h1 @h2 @h3 @h4 @h5 " +
    // Text Entry
    "@text @p @pre " +
    // Source Snippets
    "@bash @c @code @d @go @java @javascript @perl @python @swift @tcl @verilog @xml " +
    // Include Files
    "@include @include_child " +
    // Images and Diagrams
    "@sequence @graph @image @imagemap " +
    // Lists
    "@ul @ol " +
    // Tables
    "@table " +
    // Notes and Warnings
    "@note @tbd @warning @question " +
    // Code Elements
    "@define @enum @prototype @register @struct " +
    "--description: --examples: --fields: --function: --name: --params: --prototype: " + 
    "--pseudocode: --returns: --requires: --see: --seealso: --since: --value: --values:");

  // These are snippets that get expanded by code completion into pre-canned
  // blocks of code.
  var snippet_list = ("$c $define $doc $image $list_ordered $list_unordered $macro $macro_blank $macro_full $python $quote $quote_blank $struct $table $table_with_title $textblock_blank $textblock");
  var snippet_data = {};
   
  // An example document header
  snippet_data["$doc"] = "@doc.title    Document Title\n" +
                         "@doc.subtitle Document Subtitle\n" +
                         "@doc.version  1.0\n" +
                         "@doc.number   12345\n" +
                         "@doc.author   Author\n" +
                         "@doc.revisions\n" +
                         "- Version | Date              | Author  | Description\n" +
                         "- 1.0     | November 27, 2015 | Brad E. | A random description\n\n" +
                         "@body\n"
                         "@h1 First Heading\n";

  // Example tables
  snippet_data["$table"] = "@table\n" +
                           "-h Header 1 | Header 2\n" +
                           "   Column 1 | Column 2\n";
  snippet_data["$table_with_title"] = "@table: title=\"My Title\"\n" +
                           "-h Header 1 | Header 2\n" +
                           "   Column 1 | Column 2\n";
  snippet_data["$textblock"] = "@text\n" +
                               "...\n";
  snippet_data["$textblock_blank"] = "@text\n";
  snippet_data["$list_ordered"] = "@ol\n" + 
                                  "- One\n" +
                                  "- Two\n" +
                                  "    - A\n" +
                                  "- Three";
  snippet_data["$list_unordered"] = "@ul\n" +
                                  "- One\n" +
                                  "    - Two\n" +
                                  "- Three\n";
  snippet_data["$quote"]          = "@quote\n" +
                                    "This is a block of quoted text\n";
 
  snippet_data["$quote_blank"]    = "@quote\n";

  snippet_data["$image"] = "@image: src=\"...\" width=\"100%\" caption=\"An image caption here\" title=\"Image name\"\n";

  snippet_data["$macro"] = "<?=\"Expand a macro string\"?>";
  snippet_data["$macro_blank"] = "<?=\"\"?>";
  snippet_data["$macro_full"] = "<?result = \"\"\n" +
                                "result += \"Hello world\"" +
                                "?>\n";

  // Code Blocks
  snippet_data["$c"]      = "@c: exec=\"false\"\n" +
                            "...\n";
  snippet_data["$python"] = "@python: exec=\"false\"\n" +
                            "...\n";
  
  // Example struct tag
  snippet_data["$struct"] = "@struct\n" +
                            "--name:\n" +
                            "    my_structure\n" +
                            "--description:\n" +
                            "    A description of my structure\n" +
                            "--fields:\n" +
                            "- Field    | Name      | Description\n" +
                            "- uint8_t  | field_one | This is a description of this field\n" +
                            "- uint16_t | field_two | This is a description of field_two\n" +
                            "--since:\n" +
                            "    Introduced in version 1.0\n" +
                            "--requires:\n" +
                            "    Requires XYZ to be defined at compile time\n"; 

  // Example define tab
  snippet_data["$define"] = "@define\n" +
                            "--name:\n" +
                            "    MY_DEFINE\n" +
                            "--description:\n" +
                            "    A multi-line description of MY_DEFINE\n" +
                            "--value:\n" +
                            "    The value of MY_DEFINE\n" +
                            "--since:\n" +
                            "    Introduced in version 1.0\n" +
                            "--requires:\n" +
                            "    Requires XYZ to be defined at compile time\n";



  var keywords = keyword_list.split(" "); 
  var snippets = snippet_list.split(" ");

  // The styles associated with language elements
  var colors = {};
  colors["inline_tag"]            = "variable-3";
  colors["code_block"]            = "def";
  colors["code_block_attributes"] = "string";
  colors["code_block_data"]       = "atom";
  colors["tag"]                   = "keyword";
  colors["comment"]               = "comment";
  
  CodeMirror.defineSimpleMode("shorte",{
    start: [
        // If we hit @{ treat it as an inline tag
        {regex: /\@\{/,  token: colors["inline_tag"], next: "inline_tag"},

        // Style language blocks differently than other tags. I might eventually
        // be able to get them to style using the lexers for other languages.
        {regex: /@(bash|c|code|java|perl|python|shell|shorte|tcl|xml)$/,     token: colors["code_block"], next: "code_block_data", sol:true},
        {regex: /@(bash|c|code|java|perl|python|shell|shorte|tcl|xml)[: ]?/, token: colors["code_block"], next: "code_block_attributes",  sol:true},

        // If we hit an @ at the start of the line then treat it
        // as a shorte tag
        {regex: /@/,    token: colors["tag"], next: "tag", sol:true},

        // Single line comments start with the # like python
        {regex: /#.*/,   token: "comment"},

        // Multi-line comments use HTML syntax <!-- ... -->
        {regex: /<\!--/, token: "comment", next: "block_comment"},

        // PHP style expansion
        {regex: /<\?/,  token: "string", next: "php_block"},

        // Section defines for code constructs like @struct, @define, @enum, @prototype
        {regex: /--(description|example|fields|function|name|params|prototype|pseudocode|returns|requires|see|seealso|since|value|values)\s*:/, token: "def", sol:true},
    ],

    // Manage the styling of tags like @body, @h1.
    tag: [
        // If we hit a space then treat the remainder as tag data
        {regex: /\s/, token: "string",  next: "tag_data"},
        // If we hit end of line then reset the lexer to the start
        {regex: /.$/, token: colors["tag"], next: "start"},
        // Otherwise continue processing the tag
        {regex: /./,  token: colors["tag"]},
    ],
    // The remainder of the line after the tag declaration will be treated as a string.
    tag_data: [
        {regex: /.$/, token: "string", next: "start"},
        {regex: /./,  token: "string"},
    ],
    
    // This expression is used for styling code blocks like @c, @python, etc. It
    // styles anything on the first line after the @c tag. Once we hit the
    // end of line then we switch to the code_block_data state.
    code_block_attributes: [
        {regex: /.$/, token: colors["code_block_attributes"], next: "code_block_data"},
        {regex: /./,  token: colors["code_block_attributes"]},
    ],
    // The actual contents of the code block
    code_block_data: [
        {regex: /@/,  token: colors["tag"], next: "tag", sol:true},
        {regex: /./,  token: colors["code_block_data"]},
    ],

    // We've hit an inline or nested tag which looks like @{. We're in
    // it until we hit the closing }
    inline_tag: [
        {regex: /\}/,   token: colors["inline_tags"], next: "start"},
        {regex: /[^}]/, token: colors["inline_tags"], next: "inline_tag"}
    ],

    // We're in an HTML like multi-line comment. Stay here
    // till we hit the closing -->
    block_comment: [
        {regex: /-->/, token: colors["comment"], next: "start"},
        {regex: /.*/,  token: colors["comment"]}
    ],

    // We're in a PHP style expansion block. Stay here
    // till we hit the closing ?>
    php_block: [
        {regex: /\?>/, token: "string", next: "start"},
        {regex: /.*/,  token: "string"}
    ],

});

  
  CodeMirror.registerHelper("hint", "shorte", function(editor, options) {
    var word = options && options.word || WORD;
    var range = options && options.range || RANGE;
    var cur = editor.getCursor(), curLine = editor.getLine(cur.line);
    var end = cur.ch, start = end;

    while (start && word.test(curLine.charAt(start - 1))) --start;
    var curWord = start != end && curLine.slice(start, end);

    var list = options && options.list || [], seen = {};
    
    // Expand any snippet templates
    if(curWord.slice(0,1) == "$") {
        // If just the $ is active the pop up the list
        // of available snippets as a reminder
        if(curWord == "$") {
            for(var i = 0; i < snippets.length; i++) {
                list.push(snippets[i]);
            }
        }
        else {
            for(var i = 0; i < snippets.length; i++) {
                var idx = snippets[i].indexOf(curWord);
                if(idx == 0) {
                    var snippet_name = snippets[i];
                    var snippet_value = snippet_data[snippet_name];
                    list.push(snippet_value);
                    //seen[snippet_name] = true;
                }
            }
        }
    } 
    // Scan the list of keywords for matches first
    for(var i = 0; i < keywords.length; i++) {
        var idx = keywords[i].indexOf(curWord);
        if(idx == 0) {
            list.push(keywords[i]);
            seen[keywords[i]] = true;
        }
    }

    // After that search for anything instantiated in the
    // document.
    var re = new RegExp(word.source, "g");
    for (var dir = -1; dir <= 1; dir += 2) {
      var line = cur.line, endLine = Math.min(Math.max(line + dir * range, editor.firstLine()), editor.lastLine()) + dir;
      for (; line != endLine; line += dir) {
        var text = editor.getLine(line), m;
        while (m = re.exec(text)) {
          if (line == cur.line && m[0] === curWord) continue;
          if ((!curWord || m[0].lastIndexOf(curWord, 0) == 0) && !Object.prototype.hasOwnProperty.call(seen, m[0])) {
            seen[m[0]] = true;
            list.push(m[0]);
          }
        }
      }
    }
    return {list: list, from: CodeMirror.Pos(cur.line, start), to: CodeMirror.Pos(cur.line, end)};
  });
  
CodeMirror.defineMIME("text/shorte", "shorte");

});
