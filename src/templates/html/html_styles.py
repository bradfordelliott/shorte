import string

import templates.themes

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
div.toc1 {margin-top:8px;margin-bottom:4px;"}
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
div.snippet span.def {color:red;}
div.snippet span.mstring {color: #9933CC;}
div.snippet span.cmt {color: #009900;}
div.snippet span.cmttg {color: #00cc00;}
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
      background-color: white;
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
  div.snippet span.def {color:red;}
  div.snippet span.mstring {color: #9933CC;}
  div.snippet span.cmt {color: #009900;}
  div.snippet span.cmttg {color: #00cc00;}
  div.snippet span.ln {color: #C0C0C0;}

  /* Styling of text blocks */
  div.tblkps {margin-left:4px;margin-top:10px;margin-bottom:10px;font-size:1.0em;}
  div.tblkp  {margin-left:4px;padding:0px;margin-top:10px;margin-bottom:10px;font-size:1.0em;}

  table div.tblkps {margin-left:4px;margin-top:5px;margin-bottom:5px;font-size:1.0em;}
  table div.tblkp  {margin-left:4px;padding:0px;margin-top:5px;margin-bottom:5px;font-size:1.0em;}
    '''
  
    def get_common_styles(self):
        return string.Template('''
  a {color: ${color_hyperlink};font-weight: bold;font-size:0.9em;}
  a:hover {color: ${color_hyperlink_hover};font-weight: bold;text-decoration: underline;}
  a img {border: none;}
  a.name {color: black;}
  
  h1{font-size: 1.3em;padding: 0px;padding-bottom: 3px;margin: 0px;margin-top:10px;margin-left: 5px;color:${heading_1_fg};}
  h2{font-size: 1.2em;padding: 0px;padding-top:12px;padding-bottom: 3px;font-weight: bold;color: ${heading_2_fg};margin: 0px;margin-left: 5px;}
  h3{font-size: 1.1em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_3_fg};}
  h4{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_4_fg};}
  h5{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_5_fg};}
  h6{font-size: 1.0em;padding: 0px;padding-top:12px;padding-bottom: 3px;margin: 0px;margin-left: 5px;color: ${heading_6_fg};text-decoration:underline;}
  
  p {margin-left: 20px;margin-bottom:10px;font-size: 1.0em;}
  p.caption {margin-left: 0px;text-align: center;margin-top: 5px;}

  
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
  
  font.hilite
  {
      background-color:yellow;
      font-weight: bold;
  }
  
  
  /* Table of Contents */
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
  
  .bordered {
      margin:10px;
      margin-left:20px;
      background-color:white;
      border: solid #ccc 4px;
      -moz-border-radius: 6px;
      -webkit-border-radius: 6px;
      border-radius: 6px;
      /*overflow-x:auto;*/
  }
  
  .bordered td, .bordered th {
      border-left: 1px solid #ccc;
      border-top: 1px solid #ccc;
      padding: 4px;
      text-align: left;    
  }
  
  .bordered th {
      background-color:${color_table_title_bg};
      color:${color_table_title_fg};
      border-top: none;
  }
  
  .bordered tr.alternaterow {
      background-color:#{color_table_altrow_bg};
  }
  .bordered tr.caption {
      background-color:#8C9CB8;
      color:white;
  }
  
  .bordered tr.header td {
      font-weight:bold;
      background-color:${color_table_header_bg};
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  .bordered tr td.header {
      font-weight:bold;
      background-color:${color_table_header_bg};
      border-top:0px solid #ccc;
      border-bottom:2px solid #ccc;
  }
  .bordered tr td.subheader {
      background-color:${color_table_subheader_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
  }
  .bordered tr.reserved {
      background-color:${color_table_reserved_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
      color:${color_table_reserved_fg};
  }
  .bordered tr.spacer {
      border-top:1px solid #ccc;
      border-bottom:1px solid #ccc;
      color:${color_table_reserved_fg};
  }
  .bordered tr td.reserved {
      background-color:${color_table_reserved_bg};
      border-top:1px solid #ccc;
      border-bottom:0px solid #ccc;
      color:${color_table_reserved_fg};
  }
  
  .bordered td:first-child, .bordered th:first-child {
      border-left: none;
  }
  
  .bordered th:first-child {
      -moz-border-radius: 3px 0 0 0;
      -webkit-border-radius: 3px 0 0 0;
      border-radius: 3px 0 0 0;
  }
  
  .bordered th:last-child {
      -moz-border-radius: 0 3px 0 0;
      -webkit-border-radius: 0 3px 0 0;
      border-radius: 0 3px 0 0;
  }
  
  .bordered th:only-child{
      -moz-border-radius: 3px 3px 0 0;
      -webkit-border-radius: 3px 3px 0 0;
      border-radius: 3px 3px 0 0;
  }
  
  .bordered tr:last-child td:first-child {
      -moz-border-radius: 0 0 0 3px;
      -webkit-border-radius: 0 0 0 3px;
      border-radius: 0 0 0 3px;
  }
  
  .bordered tr:last-child td:last-child {
      -moz-border-radius: 0 0 3px 0;
      -webkit-border-radius: 0 0 3px 0;
      border-radius: 0 0 3px 0;
  }
  
  .image_inline
  {
      display:inline;
  }
  .image_inline table
  {
      display:inline;
      text-align:center;
  }
  .image_inline img
  {
      border:0px;
      margin-left:20px;
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
  
  div.code
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
  }
  div.code2
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
  div.code3
  {
      font-family: courier new;
      font-size: 0.9em;
  }

  div.cb_title
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
     color: #396592;
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

  div.gallery
  {
      margin-left:20px;
      margin-right:20px;
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

  $priority
  ''').substitute({"priority"              : "$priority",
                   "star"                  : "$star",
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
                   "color_hyperlink"       : self.colors["hyperlink"].fg,
                   "color_hyperlink_hover" : self.colors["hyperlink.hover"].fg,
                   "color_codeblock_section" : self.colors["codeblock.section"].fg})

