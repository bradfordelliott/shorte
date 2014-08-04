

class color():
    def __init__(self,bg="#ffffff",fg="#000000"):
        self.bg = bg
        self.fg = fg

class theme():
    def __init__(self):
        pass
            
    def get_colors(self, theme="shorte"):

        colors = {}

        if(theme == "shorte"):
            # Heading Colors
            colors["heading.1"] = color(fg="#000000")
            colors["heading.2"] = color(fg="#8ba327")
            colors["heading.3"] = color(fg="#8ba327")
            colors["heading.4"] = color(fg="#8ba327")
            colors["heading.5"] = color(fg="#8ba327")
            colors["heading.6"] = color(fg="#8ba327")
            
            # Table Colors
            colors["table"] = {}
            colors["table"]["title"]     = color(fg="#444", bg="#8ba327")
            colors["table"]["alt.row"]   = color(fg="#000000", bg="#f0f0f0")
            colors["table"]["header"]    = color(fg="#000000", bg="#a0a0a0")
            colors["table"]["subheader"] = color(fg="#000000", bg="#d0d0d0")
            colors["table"]["reserved"]  = color(fg="#a0a0a0", bg="#f0f0f0")

            # Hyperlink Colors
            colors["hyperlink"]       = color(fg="#8ba327")
            colors["hyperlink.hover"] = color(fg="#ccc")

        elif(theme in ("cortina", "cortina_web")):
            # Heading Colors
            colors["heading.1"] = color(fg="#000000")
            colors["heading.2"] = color(fg="#396592")
            colors["heading.3"] = color(fg="#0000ff")
            colors["heading.4"] = color(fg="#0000ff")
            colors["heading.5"] = color(fg="#0000ff")
            colors["heading.6"] = color(fg="#0000ff")
            
            # Table Colors
            colors["table"] = {}
            colors["table"]["title"]     = color(fg="#ffffff", bg="#396592")
            colors["table"]["header"]    = color(fg="#000000", bg="#b0b0b0")
            colors["table"]["alt.row"]   = color(fg="#000000", bg="#f0f0f0")
            colors["table"]["subheader"] = color(fg="#000000", bg="#d0d0d0")
            colors["table"]["reserved"]  = color(fg="#a0a0a0", bg="#f0f0f0")

            # Hyperlink Colors
            colors["hyperlink"]       = color(fg="#396592")
            colors["hyperlink.hover"] = color(fg="#ccc")

        return colors
