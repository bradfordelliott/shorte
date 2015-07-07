
import os
from src.shorte_defines import *

class color():
    def __init__(self,bg="#ffffff",fg="#000000"):
        self.bg = bg
        self.fg = fg

class theme():
    def __init__(self):

        self.colors = {}

        # Heading Colors
        self.colors["shorte"] = {}
        self.colors["shorte"]["heading.1"] = color(fg="#000000")
        self.colors["shorte"]["heading.2"] = color(fg="#8ba327")
        self.colors["shorte"]["heading.3"] = color(fg="#666")
        self.colors["shorte"]["heading.4"] = color(fg="#aaa")
        self.colors["shorte"]["heading.5"] = color(fg="#8ba327")
        self.colors["shorte"]["heading.6"] = color(fg="#8ba327")
        
        # Table of Contents Colors
        self.colors["shorte"]["toc.1"] = color(fg="#000000")
        self.colors["shorte"]["toc.2"] = color(fg="#000000")
        self.colors["shorte"]["toc.3"] = color(fg="#000000")
        self.colors["shorte"]["toc.4"] = color(fg="#000000")
        self.colors["shorte"]["toc.5"] = color(fg="#000000")
        self.colors["shorte"]["toc.6"] = color(fg="#000000")
        
        # Table Colors
        self.colors["shorte"]["table"] = {}
        self.colors["shorte"]["table"]["title"]     = color(fg="#ffffff", bg="#8ba327")
        self.colors["shorte"]["table"]["header"]    = color(fg="#000000", bg="#B0B0B0")
        self.colors["shorte"]["table"]["alt.row"]   = color(fg="#000000", bg="#f0f0f0")
        self.colors["shorte"]["table"]["subheader"] = color(fg="#000000", bg="#d0d0d0")
        self.colors["shorte"]["table"]["reserved"]  = color(fg="#a0a0a0", bg="#f0f0f0")
        self.colors["shorte"]["table"]["normal"]    = color(fg="#000000", bg="#ffffff")

        # Hyperlink Colors
        self.colors["shorte"]["hyperlink"]       = color(fg="#586a0d") #color(fg="#8ba327")
        self.colors["shorte"]["hyperlink.hover"] = color(fg="#666")

        # Code Bocks
        self.colors["shorte"]["codeblock.section"] = color(fg="#8ba327")

        self.colors["unstyled"] = self.colors["shorte"]


        dir_templates = shorte_get_startup_path() + os.path.sep + "templates"
        templates = os.listdir(dir_templates)
        sys.path.append(dir_templates)

        for t in templates:
            if("theme_" in t and t.endswith(".py")):
                module_name = os.path.splitext(t)[0]
                module = __import__("%s" % module_name)
                module.load_colors(self.colors)

            
    def get_colors(self, theme="shorte"):

        return self.colors[theme]
