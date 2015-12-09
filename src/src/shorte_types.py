
class variable_list_item_t(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

class variable_list_t(object):
    def __init__(self):
        self.items = []

    def add(self, name, value):
        self.items.append(variable_list_item_t(name, value))

    def get_items(self):
        return self.items


class table_t(object):
    def __init__(self):
        self.rows = []
        self.modifiers = {}
        self.max_cols = 1
        self.widths = None
        self.width = None
        self.title = None
        self.caption = None

        # Attributes primarily for ODT
        self.table_style_name = None
        self.column_styles = None

        self.style = None
        self.source = None

    def set_source(self, source):
        self.source = source
    def has_source(self):
        if(self.source != None):
            return True
        return False
    def get_source(self):
        return self.source

    def get_title(self):
        return self.title
    def has_title(self):
        if(self.title != None and len(self.title) > 0):
            return True
        return False

    def get_widths(self):
        return self.widths
    def has_widths(self):
        if(self.widths != None and len(self.widths) > 0):
            return True
        return False

    def has_style(self):
        if(self.style != None):
            return True
        return False
    def get_style(self):
        return self.style

    def get_max_cols(self):
        return self.max_cols

    def set_caption(self, caption):
        self.caption = caption
    def get_caption(self):
        return self.caption
    def has_caption(self):
        if(self.caption != None):
            return True
        return False

    def add_row(self, row):
        self.rows.append(row)

    def get_rows(self):
        return self.rows
    def get_num_rows(self):
        return len(self.rows)

    def has_column_styles(self):
        if(self.column_styles != None):
            return True
        return False

    def get_column_styles(self):
        return self.column_styles
