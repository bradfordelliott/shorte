// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../../lib/codemirror"), require("../../addon/mode/simple"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../../lib/codemirror", "../../addon/mode/simple"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
"use strict";

CodeMirror.defineSimpleMode("shorte",{
    start: [
        // If we hit @{ then it is an inline tag
        {regex: /\@\{/,  token: "variable-3", next: "inline_tag"},
        // Style language blocks differently
        {regex: /@(bash|c|code|java|perl|python|shell|shorte|tcl|xml)$/, token: "def", next: "code_block_data", sol:true},
        {regex: /@(bash|c|code|java|perl|python|shell|shorte|tcl|xml)[: ]?/, token: "def", next: "code_block_tag", sol:true},
        // If we hit an @ at the start of the line then it
        // is a shorte tag.
        {regex: /@/,    token: "keyword", next: "tag", sol:true},
        {regex: /#.*/,   token: "comment"},
        {regex: /<\!--/, token: "comment", next: "block_comment"},
        {regex: /<\?=/,  token: "string", next: "php_block"},
        {regex: /--(description|example|fields|function|name|params|prototype|pseudocode|returns|see|seealso|value|values)\s*:/, token: "def", sol:true},
    ],
    tag: [
        {regex: /\s/, token: "string",  next: "tag_data"},
        {regex: /.$/, token: "keyword", next: "start"},
        {regex: /./,  token: "keyword"},
    ],
    tag_data: [
        {regex: /.$/, token: "string", next: "start"},
        {regex: /./,  token: "string"},
    ],
    
    // This expression is used for styling code blocks like @c, @python, etc. It
    // styles anything on the first line after the @c tag. Once we hit the
    // end of line then we switch to the code_block_data state.
    code_block_tag: [
        {regex: /.$/, token: "string", next: "code_block_data"},
        {regex: /./,  token: "string"},
    ],
    code_block_data: [
        {regex: /@/,  token: "keyword", next: "tag"},
        {regex: /./,  token: "atom"},
    ],

    inline_tag: [
        {regex: /\}/, token: "variable-3", next: "start"},
        {regex: /[^}]/, token: "variable-3", next: "inline_tag"}
    ],
    block_comment: [
        {regex: /-->/, token: "comment", next: "start"},
        {regex: /.*/, token: "comment"}
    ],
    php_block: [
        {regex: /\?>/, token: "string", next: "start"},
        {regex: /.*/, token: "string"}
    ],

  meta: {
    dontIndentStates: ["comment"],
    electricInput: /^\s*\}$/,
    blockCommentStart: "/*",
    blockCommentEnd: "*/",
    lineComment: "//",
    fold: "brace"
  }
});

CodeMirror.defineMIME("text/shorte", "shorte");

});
