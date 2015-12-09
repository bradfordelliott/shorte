
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

