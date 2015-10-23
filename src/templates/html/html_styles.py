import string

import templates.themes

template_code_header = string.Template(
"""
<div class='code_header' style='width:80%;$style;'>
<span style='text-decoration:none;color:#ccc;' onmouseover="this.style.color='#0000ff';" onmouseout="this.style.color='#ccc';" onclick="e=document.getElementById('snippet_$id');display_code(e.innerHTML);">View Source</span> |
<span style='text-decoration:none;color:#ccc;' onmouseover="this.style.color='#0000ff';" onmouseout="this.style.color='#ccc';" onclick="print_code(document.getElementById('snippet_$id').innerHTML);">Print</span>
</div>
""")

template_source = string.Template(
"""
<div class='source' id="snippet_$id">
$source
</div>
""")

template_code_result = string.Template(
"""
    <br/>
    <div class='${code_result}'>${label}</div>
    <div class='${code}'>
        $result
    </div>
""")

template_code_result_no_output = string.Template(
"""
    <br/>
    <div class='${code_result}'>${label}</div>
""")


# This template is used to display errors to the user
# when a source code block was excuted and returned
# a failure code.
template_code_result_error = string.Template(
'''
    <br/>
    <div class='${code_result}'>${label} (Failed, rc=${rc}) <img style='height:25px;margin-top:-10px;margin-left:10px;position:absolute;' src="${image}"></img></div>
    <div class='${code}' style='border:3px solid red;'>
        $result
    </div>
    <br/>
''')

class html_styles():
    def __init__(self, theme="shorte"):
        
        self.m_theme = theme

        self.colors = templates.themes.theme().get_colors(theme)

    def get_toc_frame_styles(self):
        return string.Template('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<style>
* html {width: 500px;}
body {width: 500px;font-family:"Helvetica Neue",helvetica,arial,sans-serif;}
/* Table of Contents */
div.toc1 {margin-top:8px;margin-bottom:4px;}
div.toc1 a{margin-left:20px;font-size:1.1em;color:${toc_1_fg};}
div.toc2 {margin-top:4px;margin-bottom:2px;}
div.toc2 a{margin-left:40px;font-size:1.0em;color:${toc_2_fg};}
div.toc3 {margin-top:4px;margin-bottom:2px;}
div.toc3 a{margin-left:50px;font-size:0.9em;color:${toc_3_fg};}
div.toc4 a{margin-left:70px;font-size:0.9em;color:${toc_4_fg};}
div.toc5 a{margin-left:90px;font-size:0.9em;color:${toc_5_fg};}
</style>
</head>
<body style="background-color: white;white-space:nowrap;font-weight:bold;">
$cnts
</body>
</html>
''').substitute({"cnts"         : "$cnts",
                 "toc_1_fg" : self.colors["toc.1"].fg,
                 "toc_2_fg" : self.colors["toc.2"].fg,
                 "toc_3_fg" : self.colors["toc.3"].fg,
                 "toc_4_fg" : self.colors["toc.4"].fg,
                 "toc_5_fg" : self.colors["toc.5"].fg,
                 "toc_6_fg" : self.colors["toc.6"].fg})

    def get_print_styles(self):
        return '''
body
{
    width:100%;margin:0;float:none;
    font-family:times;

}
div.container
{
    width:100%;margin:0;float:none;

}
div.header
{
    display:none;
}
div.menu_div
{
    display:none;
}

div.footer
{
    display:block;
}

div.footer a
{
    display:none;
}

div.code_header
{
    display:none;
}

object
{
    display:none;
}

/* Styling of code segments */
div.snippet span.operator {color: purple;}
div.snippet span.kw {font-weight:bold;color: blue;} /* keyword */
div.snippet span.str {color: #9933CC;}
div.snippet span.def {color:#660000;}
div.snippet span.mstring {color: #9933CC;}
div.snippet span.cmt {color: #009900;}
div.snippet span.cmttg {color: #00dd00;}
div.snippet span.ln {color: #C0C0C0;}

/* Styling of text blocks */
div.tblkps {margin:0px;padding:0px;margin-top:5px;margin-bottom:5px;margin-left:20px;}
div.tblkp  {margin:0px;padding:0px;margin-top:5px;margin-bottom:5px;}

'''

    def get_screen_styles(self):
        return '''
  div.code_header
  {
      font-family: courier new;
      font-size: 0.9em;
      margin-bottom:0px;
      margin-top:10px;
      margin-left: 30px;
      /*background-color: white;*/
      border: 0px;
      width:100%;
      color:#ccc;
  }
  
  div.code_header a
  {
      text-decoration:none;
      color:#ccc;
  }

  /* Styling of code segments */
  div.snippet span.operator {color: purple;}
  div.snippet span.keyword {color: blue;}
  div.snippet span.kw {color: blue;}
  div.snippet span.str {color: #9933CC;}
  div.snippet span.def {color:#660000;}
  div.snippet span.mstring {color: #9933CC;}
  div.snippet span.cmt {color: #009900;}
  div.snippet span.cmttg {color: #00dd00;}
  div.snippet span.ln {color: #C0C0C0;}

  /* Styling of text blocks */
  div.tblkps {margin-left:4px;margin-top:10px;margin-bottom:10px;font-size:1.0em;}
  div.tblkp  {margin-left:4px;padding:0px;margin-top:10px;margin-bottom:10px;font-size:1.0em;}

  table div.tblkps {margin-left:4px;margin-top:5px;margin-bottom:5px;font-size:1.0em;}
  table div.tblkp  {margin-left:4px;padding:0px;margin-top:5px;margin-bottom:5px;font-size:1.0em;}

    '''
    
    def get_gallery_styles(self):
        return '''
div.gallery
  {
      margin-left:20px;
      margin-right:20px;
      margin-bottom:20px;
      border:1px solid #ddd;
      padding:4px;
      border-radius:4px;
      background-color:#eee;
  }

  div.gallery div.pic
  {
      float:left;
      padding:0px;
      margin:4px;
      border:0px solid #ccc;
      border-radius:0px;
  }

  div.gallery p
  {
      color:#aaa;font-size:0.8em;padding:0px;margin:0px;margin-top:1px;
  }
  
  div.gallery div.pic div.pic_header
  {
      height:30px;border:1px solid #ddd;text-align:center;background-color:white;
      border-top-left-radius:4px;
      border-top-right-radius:4px;
  }
  
  div.gallery div.pic div.pic_body
  {
      border-left:1px solid #ddd;border-right:1px solid #ddd;
  }
  
  div.gallery div.pic div.pic_footer
  {
      height:32px;background:#fff;border:1px solid #ddd;
      text-align:center;white-space:wrap;overflow:hidden;text-overflow:ellipsis;
      border-bottom-left-radius:4px;
      border-bottom-right-radius:4px;
  }


  div.gallery_modern
  {
      margin-left:20px;
      margin-right:20px;
      margin-bottom:20px;
      border:1px solid #eee;
      padding:10px;
      border-radius:2px;
  }

  div.gallery_modern div.pic
  {
      float:left;
      padding:0px;
      margin:2px;
      border:0px solid #ccc;
      border-radius:0px;
      background-color:black;
  }

  div.gallery_modern p
  {
      color:#aaa;font-size:0.8em;padding:0px;margin:0px;margin-top:1px;
  }
  
  div.gallery_modern div.pic div.pic_header
  {
      height:30px;border:0px solid #ddd;text-align:center;background-color:black;
  }
  
  div.gallery_modern div.pic div.pic_body
  {
      border-left:1px solid #000;border-right:1px solid #000;
  }
  
  div.gallery_modern div.pic div.pic_footer
  {
      height:32px;background:#000;border:0px solid #ddd;
      text-align:center;white-space:wrap;overflow:hidden;text-overflow:ellipsis;
      border-bottom-left-radius:4px;
      border-bottom-right-radius:4px;
  }
  
  
  div.gallery_magazine
  {
      margin-left:20px;
      margin-right:20px;
      border:0px solid #eee;
      padding:10px;
      border-radius:2px;
      text-align:left;
      align:left;
  }

  div.gallery_magazine div.pic
  {
      float:left;
      padding:10px;
      margin:2px;
      border:0px solid #ccc;
      border-radius:0px;
      background-color:white;
  }

  div.gallery_magazine p
  {
      color:#aaa;font-size:0.8em;padding:0px;margin:0px;margin-top:1px;
  }
  
  div.gallery_magazine div.pic div.pic_header
  {
      height:30px;border:0px solid #ddd;text-align:center;background-color:white;
  }
  
  div.gallery_magazine div.pic div.pic_body
  {
      border-left:0px solid #000;border-right:0px solid #000;
  }
  
  div.gallery_magazine div.pic div.pic_footer
  {
      background:white;border:0px solid #ddd;
      text-align:center;white-space:wrap;
      border-bottom-left-radius:4px;
      border-bottom-right-radius:4px;
  }
'''
  
    def get_common_styles(self, template='html'):

        styles_gallery = self.get_gallery_styles()

        if(template == 'html'):
            prefix = ''
            headings = string.Template('''
  h1{font-size: 1.3em;padding: 0px;padding-bottom: 3px;margin: 0px;margin-top:10px;margin-left: 5px;color:${heading_1_fg};}
  h2{font-size: 1.2em;padding: 0px;padding-top:12px;padding-bottom: 3px;font-weight: bold;color: ${heading_2_fg};margin: 0px;margin-left: 5px;}
  h3{font-size: 1.1em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_3_fg};}
  h4{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_4_fg};}
  h5{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_5_fg};}
  h6{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_6_fg};text-decoration:underline;}
''').substitute({"heading_1_fg"          : self.colors["heading.1"].fg,
                 "heading_2_fg"          : self.colors["heading.2"].fg,
                 "heading_3_fg"          : self.colors["heading.3"].fg,
                 "heading_4_fg"          : self.colors["heading.4"].fg,
                 "heading_5_fg"          : self.colors["heading.5"].fg,
                 "heading_6_fg"          : self.colors["heading.6"].fg})
        elif(template == 'revealjs'):
            prefix = '.reveal '
            headings = string.Template('''
  .reveal h1{font-size: 1.9em;padding: 0px;padding-bottom: 3px;margin: 0px;margin-top:10px;margin-left: 5px;color:${heading_1_fg};font-variant:small-caps;font-weight:bold;}
  .reveal h2{font-size: 1.6em;padding: 0px;padding-top:12px;padding-bottom: 3px;font-weight: bold;color: ${heading_2_fg};margin: 0px;margin-left: 5px;}
  .reveal h3{font-size: 1.4em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_3_fg};}
  .reveal h4{font-size: 1.3em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_4_fg};}
  .reveal h5{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_5_fg};}
  .reveal h6{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_6_fg};text-decoration:underline;}
''').substitute({"heading_1_fg"          : self.colors["heading.1"].fg,
                 "heading_2_fg"          : self.colors["heading.2"].fg,
                 "heading_3_fg"          : self.colors["heading.3"].fg,
                 "heading_4_fg"          : self.colors["heading.4"].fg,
                 "heading_5_fg"          : self.colors["heading.5"].fg,
                 "heading_6_fg"          : self.colors["heading.6"].fg})

        return string.Template('''
  a {color: ${color_hyperlink};font-weight: bold;font-size:0.9em;}
  a:hover {color: ${color_hyperlink_hover};font-weight: bold;text-decoration: underline;}
  a img {border: none;}
  a.name {color: black;}
 
  ${headings}
  
  p {margin-left: 20px;margin-bottom:10px;font-size: 1.0em;}
  p.caption {margin-left: 0px;text-align: center;margin-top: 5px;}

  /* Horizontal Rule */
  div.hr
  {
      width:100%;
      border-top:1px solid #ccc;
      height:1px;
      padding:0px;
      margin:0px;
      font-size:0px;
      line-height:0px;
  }

  div.tb
  {
      width:80%;
      margin:0px;
      padding:10px;
      margin-left:20px;
      border-radius: 15px;
      -moz-border-radius: 15px;
      border:4px solid #dfd3b3;
      background:#f5f4e5;
  }
        
  /* The tooltip popup */
  #dhtmltooltip
  {
      position: absolute;
      width: 450px;
      border: 3px solid #807B60; 
      padding: 5px;
      background-color: #E8DFAC;
      visibility: hidden;
      z-index: 200;
      border-radius: 7px;
      -moz-border-radius: 7px;
  }
  
  font.hilite
  {
      background-color:yellow;
      font-weight: bold;
  }

  a.nav_up {color:#eee;font-size:0.4em;position:relative;top:-10px;left:5px;}
  
  
  /* Table of Contents */
  div.toc  {border:1px solid #ccc;border-radius:0px;padding-bottom:10px;padding-top:10px;background-color:#f0f0f0;margin-left:12px;}
  div.toc1 {margin-top:8px;margin-bottom:4px;}
  div.toc1 a{margin-left:20px;font-size:1.1em;color:${toc_1_fg};}
  div.toc2 {margin-top:4px;margin-bottom:2px;}
  div.toc2 a{margin-left:40px;font-size:1.0em;color:${toc_2_fg};}
  div.toc3 {margin-top:4px;margin-bottom:2px;}
  div.toc3 a{margin-left:50px;font-size:0.9em;color:${toc_3_fg};}
  div.toc4 a{margin-left:70px;font-size:0.9em;color:${toc_4_fg};}
  div.toc5 a{margin-left:90px;font-size:0.9em;color:${toc_5_fg};}
  table {
      *border-collapse: collapse; /* IE7 and lower */
      border-spacing: 0;
  }
  
  ${prefix}.bordered {
      margin:10px;
      margin-left:20px;
      background-color:white;
      border: solid #ccc 4px;
      -moz-border-radius: 6px;
      -webkit-border-radius: 6px;
      border-radius: 6px;
      /*overflow-x:auto;*/
  }
  
  ${prefix}.bordered td, .bordered th {
      border-left: 1px solid #ccc;
      border-top: 1px solid #ccc;
      padding: 4px;
      text-align: left;    
  }
  
  ${prefix}.bordered th {
      background-color:${color_table_title_bg};
      color:${color_table_title_fg};
      border-top: none;
  }
  
  ${prefix}.bordered tr.alternaterow {
      background-color:${color_table_altrow_bg};
  }
  ${prefix}.bordered tr.caption {
      background-color:${color_table_caption_bg};
      color:${color_table_caption_fg};
  }
  
  ${prefix}.bordered tr.header td {
      font-weight:bold;
      background-color:${color_table_header_bg};
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  ${prefix}.bordered tr td.header {
      font-weight:bold;
      background-color:${color_table_header_bg};
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  ${prefix}.bordered tr td.subheader {
      background-color:${color_table_subheader_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
  }
  ${prefix}.bordered tr.reserved {
      background-color:${color_table_reserved_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
      color:${color_table_reserved_fg};
  }
  ${prefix}.bordered tr.spacer {
      border-top:1px solid #ccc;
      border-bottom:1px solid #ccc;
      color:${color_table_reserved_fg};
  }
  ${prefix}.bordered tr td.reserved {
      background-color:${color_table_reserved_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
      color:${color_table_reserved_fg};
  }
  
  ${prefix}.bordered td:first-child, .bordered th:first-child {
      border-left: none;
  }
  
  ${prefix}.bordered th:first-child {
      -moz-border-radius: 3px 0 0 0;
      -webkit-border-radius: 3px 0 0 0;
      border-radius: 3px 0 0 0;
  }
  
  ${prefix}.bordered th:last-child {
      -moz-border-radius: 0 3px 0 0;
      -webkit-border-radius: 0 3px 0 0;
      border-radius: 0 3px 0 0;
  }
  
  ${prefix}.bordered th:only-child{
      -moz-border-radius: 3px 3px 0 0;
      -webkit-border-radius: 3px 3px 0 0;
      border-radius: 3px 3px 0 0;
  }
  
  ${prefix}.bordered tr:last-child td:first-child {
      -moz-border-radius: 0 0 0 3px;
      -webkit-border-radius: 0 0 0 3px;
      border-radius: 0 0 0 3px;
  }
  
  ${prefix}.bordered tr:last-child td:last-child {
      -moz-border-radius: 0 0 3px 0;
      -webkit-border-radius: 0 0 3px 0;
      border-radius: 0 0 3px 0;
  }
  
  .image_inline
  {
      display:inline;
      text-align:center;
  }
  .image_inline table
  {
      display:inline;
      text-align:center;
  }
  .image_inline img
  {
      border:0px;
      max-width:100%;
      border:1px solid #ddd;
      padding:10px;
      margin:10px;
      border-radius:3px;
  }
  /* Question and answer blocks */
  div.question
  {
      background-color:#ddd;
      padding:10px;
  }
  div.answer
  {
      padding:10px;
  }
  
  ${prefix} div.code
  {
      border-radius: 8px;
      -moz-border-radius: 8px;
      padding-top:6px;
      padding-bottom:6px;
      padding-left:3px;
      padding-right:3px;
  
      font-family: courier new;
      font-size: 0.8em;
      margin-bottom: 0px;
      margin-top: 4px;
      margin-left:25px;
      margin-right:10px;
      margin-bottom:10px;
      background-color:#f0f0f0;
      border:3px solid #ccc;
      overflow:auto;
  }
  ${prefix} div.code2
  {
      font-family: courier new;
      font-size: 0.9em;
      margin-bottom: 10px;
      margin-top: 0px;
      margin-left:10px;
      margin-right:15px;
      background-color:#f0f0f0;
      border:1px solid #ccc;
  }
  ${prefix} div.code3
  {
      font-family: courier new;
      font-size: 0.9em;
  }

  ${prefix} div.cb_title
  {
      color:${color_codeblock_section};
      font-weight:bold;
  }

  
  div.code a
  {
      font-weight:normal;
  }
  div.prototype a
  {
      font-weight:normal;
  }
  
  div.source
  {
      visibility:hidden;
      display:block;
      height:0;
      width:0;
  }
  
  
  div.code_result
  {
     margin-left: 25px;
     color: ${heading_2_fg};
  }


  div.star
  {
      display:inline-block;
      position:relative;
      top:-10px;
      padding:0px;
      margin-right:-9px;
      margin-left:-9px;
      width:18px;
      height:18px;
      $star
  }

  /* Change the ordered list styles so that the
   * increment like 1.1, 1.1.3, etc. */
  ol
  {
      counter-reset: item;
  }
  ol li
  {
      display: block;
      margin-top:5px;
      margin-bottom:5px;
      position: relative;
  }
  ol li:before
  {
      color:#aaa;
      content: counters(item, ".")".";
      counter-increment: item;
      position: absolute;
      margin-right: 100%;
      right: 10px; /* space between number and text */
  }

  $styles_gallery

  $priority
  
  span.shorte_inline_code_span
  {
      background-color:#eee;
      border:1px solid #ccc;
      border-radius:2px;
      padding:4px;
      padding-top:2px;
      padding-bottom:2px;
      white-space:pre;
      font-family:monospace;
  }

  div.shorte_quote
  {
      margin-left: 20px;
      margin-top:10px;
      margin-bottom:0px;
      margin-right:30px;
      border-left:2px solid #ccc;background:#e0e0e;
      border-radius:2px;-moz-border-radius:2px;-webkit-border-radius:2px;
  }
  
  /* Indented code blocks inside text blocks */
  div.shorte_indented_code_block {margin:0px;padding:5px;margin-top:5px;margin-bottom:5px;margin-left:20px;white-space:pre;font-family:monospace;background-color:#eee;border:1px solid #ccc;border-radius:2px;}
  ''').substitute({"priority"              : "$priority",
                   "star"                  : "$star",
                   "headings"              : headings,
                   "prefix"                : prefix,
                   "heading_1_fg"          : self.colors["heading.1"].fg,
                   "heading_2_fg"          : self.colors["heading.2"].fg,
                   "heading_3_fg"          : self.colors["heading.3"].fg,
                   "heading_4_fg"          : self.colors["heading.4"].fg,
                   "heading_5_fg"          : self.colors["heading.5"].fg,
                   "heading_6_fg"          : self.colors["heading.6"].fg,
                   "toc_1_fg"              : self.colors["toc.1"].fg,
                   "toc_2_fg"              : self.colors["toc.2"].fg,
                   "toc_3_fg"              : self.colors["toc.3"].fg,
                   "toc_4_fg"              : self.colors["toc.4"].fg,
                   "toc_5_fg"              : self.colors["toc.5"].fg,
                   "toc_6_fg"              : self.colors["toc.6"].fg,
                   "color_table_title_bg"  : self.colors["table"]["title"].bg,
                   "color_table_title_fg"  : self.colors["table"]["title"].fg,
                   "color_table_altrow_bg" : self.colors["table"]["alt.row"].bg,
                   "color_table_header_bg" : self.colors["table"]["header"].bg,
                   "color_table_subheader_bg" : self.colors["table"]["subheader"].bg,
                   "color_table_reserved_bg" : self.colors["table"]["reserved"].bg,
                   "color_table_reserved_fg" : self.colors["table"]["reserved"].fg,
                   "color_table_caption_bg" : self.colors["table"]["caption"].bg,
                   "color_table_caption_fg" : self.colors["table"]["caption"].fg,
                   "color_hyperlink"       : self.colors["hyperlink"].fg,
                   "color_hyperlink_hover" : self.colors["hyperlink.hover"].fg,
                   "color_codeblock_section" : self.colors["codeblock.section"].fg,
                   "styles_gallery"          : styles_gallery})

