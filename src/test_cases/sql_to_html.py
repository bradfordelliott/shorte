import sqlite3

class sql_to_html_t():
    def __init__(self):
        pass

    def connect():
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        
        # Load the attributes associated with all bitfields
        # and cache them in a field_attributes dictionary. They will
        # be mapped to fields in a later step.
        field_attributes = {}
        cursor.execute('''SELECT a.id, a.belongs_to, a.type, a.name, a.value FROM bitfields f, attributes a WHERE a.belongs_to = f.id AND a.type=2''')
        for row in cursor:
            attr = {}
            attr["id"] = int(row[0])
            f_id = int(row[1])
            attr["type"] = row[2]
            attr["name"] = row[3]
            attr["value"] = row[4]
