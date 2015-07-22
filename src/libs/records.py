#+----------------------------------------------------------------------------
#|
#| SCRIPT:
#|   records.py
#|
#| DESCRIPTION:
#|   This module contains the definition of a record_t subclass on which
#|   all context memory records are based.
#|
#+----------------------------------------------------------------------------
#|
#| Copyright (c) 2010 Brad Elliott
#|
#+----------------------------------------------------------------------------
import sys
import os
import re
import string
from string import Template

from src.shorte_defines import *
shorte_import_cairo()
import cairo_access
from cairo_access import *

# Field attributes
NAME   = "name"
WIDTH  = "width"
DESC   = "desc"
VALUES = "values"
GROUP  = "group"

BIG_ENDIAN=0
LITTLE_ENDIAN=1

types = {}
types["uint"]   = "uint_t"
types["uint8"]  = "uint8_t"
types["uint16"] = "uint16_t"
types["uint32"] = "uint32_t"
types["uint64"] = "uint64_t"




#+-----------------------------------------------------------------------------
#|
#| CLASS:
#|     record_t
#|
#| DESCRIPTION:
#|     The base class from which all context memory records are defined.
#|
#+-----------------------------------------------------------------------------
class record_t:
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     __init__()
    #|
    #| PARAMETERS:
    #|     name (I) - The name of the record
    #|     desc (I) - The description associated with the record
    #|
    #| DESCRIPTION:
    #|     The constructor for the message.
    #|
    #+-----------------------------------------------------------------------------
    def __init__(self, name, desc):
        self.m_name = name
        self.m_desc = desc
        self.m_fields = []
        self.m_control = 0
        self.m_comment_style = COMMENT_STYLE_DEFAULT
        self.m_header_style  = HEADER_STYLE_DEFAULT
        self.m_define_prefix = ''
        
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     append_record()
    #|
    #| PARAMETERS:
    #|     source_record (I) - The record that is being appended.
    #|
    #| DESCRIPTION:
    #|     This method is called to append an entire record to the existing
    #|     record. This just appends the fields from the other record.
    #|
    #+-----------------------------------------------------------------------------
    def append_record(self, source_record):
        
        if(self == source_record):
            print "Uh oh!"; sys.exit(0);
        
        for field in source_record.m_fields:
            self.m_fields.append(field)
            
        return len(self.m_fields) - 1
    
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     append_field()
    #|
    #| PARAMETERS:
    #|     name        (I) - The name associated with the field being appended.
    #|     width       (I) - The width of the field being appended.
    #|     description (I) - The description of the field being appended.
    #|
    #| DESCRIPTION:
    #|     This method is called to add a single field to the end of a
    #|     record.
    #|
    #+-----------------------------------------------------------------------------
    def append_field(self, name, width, description, is_reserved=False, is_array=False, array_elem_size=8, type=""):
        field = {}
        field["name"]  = name
        field["width"] = width
        field["desc"]  = description
        field["is_array"] = is_array
        field["array_elem_size"] = array_elem_size
        field["is_reserved"] = is_reserved
        field["type"] = type
        
        self.m_fields.append(field)
        
        return len(self.m_fields) - 1

    def get_field(self, name):
        for field in self.m_fields:
            if(field["name"] == name):
                return field

        return 0

    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     append_field_ex()
    #|
    #| PARAMETERS:
    #|     field (I) - The input attributes to associate with the field.
    #|
    #| DESCRIPTION:
    #|     This method provides an alternative way to append a new field
    #|     definition.
    #|
    #+-----------------------------------------------------------------------------
    def append_field_ex(self, field):
        
        self.m_fields.append(field)
        
        return len(self.m_fields) - 1
   
    def append(self, field):
        self.append_field_ex(field)

    def append_reserved(self, width, is_array=False, array_elem_size=1, field_type=""):
        field = {}
        field[NAME] = "reserved"
        field[DESC] = "reserved"
        field[WIDTH] = width
        field["is_resource"] = False
        field["is_array"] = is_array
        field["array_elem_size"] = array_elem_size
        field["is_reserved"] = True
        field["type"] = field_type
        self.m_fields.append(field)
        
        return len(self.m_fields) - 1
    
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     set_field_options()
    #|
    #| PARAMETERS:
    #|     index (I) - the index of the field within the message (returned from
    #|                 append_field()
    #|     name  (I) - the name of the attribute/option to associate with
    #|                 the field
    #|     value (I) - the value to associate with the field.
    #|
    #| DESCRIPTION:
    #|     This method is called to associate an attribute/option with a field.
    #|
    #+-----------------------------------------------------------------------------
    def set_field_options(self, index, name, value):
        field = self.m_fields[index][name] = value
    
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     size()
    #|
    #| PARAMETERS:
    #|     None.
    #|
    #| DESCRIPTION:
    #|     This method is called to retrieve the combined size of all fields
    #|     in the record.
    #|
    #+-----------------------------------------------------------------------------
    def size(self):
        size = 0
        for field in self.m_fields:
            size += field[WIDTH]
        
        return size

    def format_field(self, name):

        name = name.lower()
        name = re.sub("\[\[(->)?(.*?)\]\]", "\\2", name)
        name = re.sub("[ -]", "_", name)
        name = re.sub(" +", " ", name)

        return name
    
    def to_c_native(self, order=BIG_ENDIAN):
        
        global types
        output = ''
        
        # Track the names of fields to avoid duplicates
        self.m_names = {}

        if(order == LITTLE_ENDIAN):
            self.m_fields.reverse()
        
        for field in self.m_fields:
            
            name = self._get_field_name(field["name"])
            field["display"] = ""
                    
            # DEBUG BRAD: This needs some work
            if(self.m_header_style == HEADER_STYLE_DOXYGEN):
                output += "    /** " + field["desc"]  + " */\n"
            else:
                output += "    /* " + field["desc"]  + " */\n"

            field_type = field["type"]
            if(field_type == ""):
                field_type = field["width"]
            
            if(field["is_array"]):
                print "Not supported yet"
                sys.exit(-1)
            else:
                if(field["type"] == "cs_uint64"):
                    field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%lld\\n\", type->%s);}\n" % (name, name, name)
                else:
                    field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%d\\n\", type->%s);}\n" % (name, name, name)
            
            output += "    %s %s;\n\n" % (field_type, name)

        return output


    def to_c_bitfields(self, order=BIG_ENDIAN):

        global types
        output = ''

        output_method = "dbg_dump(io_handle"

        # Track the names of fields to avoid duplicates
        self.m_names = {}
        
        bit_position = 0

        if(order == LITTLE_ENDIAN):
            self.m_fields.reverse()
        
        for field in self.m_fields:
            total_width = field["width"]
            desc_output = False
            values_output = False
            field["display"] = ""
            
            while(total_width > 0):
                width = total_width
                
                if(width > 0):
            
                    name = self._get_field_name(field["name"])
                    
                    # If we haven't output the description yet then append it. It is
                    # here because we might end up splitting a field because of ECC
                    # insertion
                    if(not desc_output):

                        # DEBUG BRAD: This needs some work
                        if(self.m_header_style == HEADER_STYLE_DOXYGEN):
                            output += "    /** " + field["desc"]  + " */\n"
                            #output += "    /*\n" + self._parse_description(field["desc"], "    ", 60) + "*/\n"
                        else:
                            output += "    /* " + field["desc"]  + " */\n"
                        
                        desc_output = True
                    else:
                        output += "    /* CONTINUED ...\n    * " + self._parse_description(field["desc"], "     * ", 60) + "*/"

                    bit_position += width
                    total_width -= width    

                    if(field["is_array"]):
                        elem_size = field["array_elem_size"]
                        output += "    %s%d %s[%s];\n" % (types["uint"], elem_size, name, field["width"]/elem_size)
                    
                        if(not field["is_reserved"]):
                            field["display"] = '''
    dbg_dump(io_handle, "    %-16s = ");
    for(i = 0; i < %d; i++)
    {
        dbg_dump(io_handle, "%%0%dX ", type->%s[i]);
    }
    dbg_dump(io_handle, "\\n");
''' % (name, field["width"]/elem_size, elem_size/4, name)

                        continue
                        

                    if(width > 64):
                        output += ("    %s %s[%d];\n" % (types["uint8"], name, width / 8));

                        if(not field["is_reserved"]):
                            field["display"] += '''
    for(i = 0; i < %d; i++)
    {
        dbg_dump(io_handle, "%%02X ", type->%s[i]);\n
    }
    dbg_dump(io_handle, "\\n");
''' % (width/8, name)
                        
                        if(width % 8):
                            output += ("    %s %s_of:%d;\n" % (types["uint8"], name, width % 8));

                            if(not field["is_reserved"]):
                                field["display"] += "    if(show_zero || type->%s_of != 0){dbg_dump(io_handle, \"    %-16s = %%llx\\n\", type->%s_of);}\n" % (name, name, name)

                    elif(width == 64):
                        output += ("    %s %s;\n" % (types["uint64"], name))
                        
                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%llx\\n\", type->%s);}\n" % (name, name, name)

                    elif(width < 64 and width > 32):
                        output += ("    %s %s[%d];\n" % (types["uint8"], name, width / 8));
                        
                        if(not field["is_reserved"]):
                            field["display"] += '''
    for(i = 0; i < %d; i++)
    {
        dbg_dump(io_handle, "%%02X ", type->%s[i]);\n
    }
    dbg_dump(io_handle, "\\n");
''' % (width/8, name)

                        if(width % 8):
                            output += ("    %s %s_of:%d;\n" % (types["uint8"], name, width % 8));
                            
                            if(not field["is_reserved"]):
                                field["display"] += "    if(show_zero || type->%s_of != 0){dbg_dump(io_handle, \"    %-16s = %%llx\\n\", type->%s_of);}\n" % (name, name, name)

                    elif(width == 32):
                        output += ("    %s %s;\n" % (types["uint32"], name))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)

                    elif(width < 32 and width > 16):
                        output += ("    %s %s:%d;\n" % (types["uint32"], name, width))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)

                    elif(width == 16):
                        output += ("    %s %s;\n" % (types["uint16"], name))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)

                    elif(width < 16 and field["width"] > 8):
                        output += ("    %s %s:%d;\n" % (types["uint16"], name, width))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)

                    elif(width == 8):
                        output += ("    %s %s;\n" % (types["uint8"], name))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)

                    else:
                        output += ("    %s %s:%d;\n" % (types["uint8"], name, width))

                        if(not field["is_reserved"]):
                            field["display"] += "    if(show_zero || type->%s != 0){dbg_dump(io_handle, \"    %-16s = %%x\\n\", type->%s);}\n" % (name, name, name)
                    
                    # Output the values if there are any defined
                    if(field.has_key(VALUES) and not values_output):
                        for val in field[VALUES]:
                            output += ("#    define %s %d\n" %(val, field[VALUES][val]))
                
            output += "\n"

        return output
    
    
      

    # This method is called to translate the input name into an appropriate
    # field name for the structure/record. If the name is already used it
    # automatically creates an alternate version for the structure.
    def _get_field_name(self, name):

        name = name.lower()
        name = re.sub("\[\[(->)?(.*?)\]\]", "\\2", name)
        name = re.sub("[ \-,/&.()]", "_", name)
        name = re.sub("_+", "_", name)
        name = re.sub(" +", " ", name)
        name = re.sub("_$", "", name)
        
        found = False

        while(not found):
            
            if(self.m_names.has_key(name)):
            
                matches = re.search("(.*?)_([0-9]+)", name, re.DOTALL)

                if(matches != None):
                    base = matches.groups()[0]
                    postfix = int(matches.groups()[1])
                    name = base + "_%d" % (postfix + 1)
                else:
                    name = name + "_0"
            else:
                found = True 

        self.m_names[name] = name

        return name

    # This method is called to format a field within a structure where
    # bitfields cannot be used
    def _output_field(self, field, width, xoffset):

        global types

        source = ''

        name = self._get_field_name(field["name"])
        field["c_name"] = name

        macro = field["name"].upper()
        desc = field["c_desc"]
        struct_name = self.format_field(self.m_name).upper()

        if(width == 64):

            if(not field["is_reserved"]):
                source += desc

            source += "    %s %s;\n" % (types["uint64"], name)

            # Don't try to translate reserved fields
            if(not field["is_reserved"]):

                if(not field.has_key("display")):
                    field["display"] = ''
                field["display"] += "    dbg_dump(io_handle, \"    %-16s = %%llx\\n\", type->%s);\n" % (name, name)

        else:
            if(xoffset == 0):
                source += "    %s control_%d;\n" % (types["uint64"], self.m_control)
                self.m_control += 1

            # Don't create macros for reserved fields
            if(not field["is_reserved"]):

                source += desc

                max_val = 2**width - 1
                source += "#define %s_SET_%s(val)  vBIT(val, %d, %d)\n" % (struct_name, macro, xoffset, width)
                source += "#define %s_UNSET_%s()   ~vBIT(0x%x, %d, %d)\n" % (struct_name, macro, max_val, xoffset, width)
                source += "#define %s_GET_%s(bits) bVALn(bits, %d, %d)\n" % (struct_name, macro, xoffset, width)

                if(not field.has_key("display")):
                    field["display"] = ''
                field["display"] += "    dbg_dump(io_handle, \"    %-16s = %%llx\\n\", %s_GET_%s(type->control_%d));\n" % (name, struct_name, macro, self.m_control - 1) 

        return source
   
    def to_c_byte_array(self):

        global types

        source = ''

        # Track the names of fields to avoid duplicates
        self.m_names = {}

        bit_position = 0
        
        num_fields = len(self.m_fields)

        width = 0
        for i in range(0, num_fields):
            field = self.m_fields[i]
            width += field["width"]

        source += "    %s bytes[%d];\n" % (types["uint8"], width/8)
        regs = "    %s regs[%d];\n" % (types["uint16"], width/16)
        
        for i in range(0, num_fields):
            
            field = self.m_fields[i]

            if(field["width"] == 0):
                continue
            
            if(field["is_reserved"]):
                bit_position += field["width"]
                continue
                    
            name = self._get_field_name(field["name"])
            field["c_name"] = name
            
            field_width = field["width"]
        
            define = self.m_define_prefix + name.upper()

            if(field_width > 32):
                source += "    #define GET_%s(vector)     GET_BITS_64(vector, %d, %d)\n" % (define, bit_position, field_width)
                source += "    #define SET_%s(vector,val) SET_BITS_64(vector, %d, %d, (uint64)val)\n" % (define, bit_position, field_width)
            else:
                source += "    #define GET_%s(vector)     GET_BITS(vector, %d, %d)\n" % (define, bit_position, field_width)
                source += "    #define SET_%s(vector,val) SET_BITS(vector, %d, %d, val)\n" % (define, bit_position, field_width)

            bit_position += field_width

        template = string.Template('''
#pragma pack(push, 1)
$header
typedef union ${struct_name}_s
{
    struct
    {
    $fields
    }bytes;

    struct
    {
    $regs
    }regs;
}${struct_name};
#pragma pack(pop)
''')
            
        struct_name = self.format_field(self.m_name)
        vars = {}
        vars["header"] = self._format_header(struct_name)
        vars["struct_name"] = struct_name
        vars["fields"] = source
        vars["regs"] = regs

        return template.substitute(vars)



    def to_c_no_bitfields(self):

        source = ''
        
        # Track the names of fields to avoid duplicates
        self.m_names = {}
        
        bit_position = 0
        alignment = 64
        xoffset = 0
        self.m_control = 0

        num_fields = len(self.m_fields)
        
        for i in range(0, num_fields):
            
            field = self.m_fields[i]

            if(field["width"] == 0):
                continue
            
            field_width = field["width"]

            if(self.m_comment_style == COMMENT_STYLE_SHORTE):
                field["c_desc"] = self._parse_description(field["desc"], "    // ", 60)
            else:
                field["c_desc"] = '    /* ' + self._parse_description(field["desc"], "       ", 60).strip() + ' */\n'

            # If the beginning and end of the array are aligned
            # then declare it as an array. Otherwise, treat it as a variable
            if(field["is_array"] == True):

                if((xoffset == 0) and (xoffset + field["width"]) % alignment == 0):

                    if(not field["is_reserved"]):
                        source += field["c_desc"]

                    name = self._get_field_name(field["name"])
                    field["c_name"] = name

                    elem_size = field["array_elem_size"]
                    #print "elem_size = %d" % elem_size

                    source += "    uint%d %s[%s];\n" % (elem_size, name, field["width"]/elem_size)

                    xoffset = 0

                    if(not field["is_reserved"]):
                        field["display"] = '''
    dbg_dump(io_handle, "    %-16s = ");
    for(i = 0; i < %d; i++)
    {
        dbg_dump(io_handle, "%%0%dX ", type->%s[i]);
    }
    dbg_dump(io_handle, "\\n");
''' % (name, field["width"]/elem_size, elem_size/4, name)

                    continue


            # Less than the alignment so we can fit more than the
            # current field in this line
            if((field["width"] + xoffset) < alignment):

                source += self._output_field(field, field_width, xoffset)

                xoffset += field_width

            # Exactly equal to the alignment
            elif((field["width"] + xoffset) == alignment):

                source += self._output_field(field, field_width, xoffset)

                xoffset = 0

            # greater than alignment so I need to wrap the field
            # to the next entry
            else:

                width_in_current_word = alignment - xoffset
                width_remainder = field["width"] - width_in_current_word
                first_block = 0

                source += self._output_field(field, width_in_current_word, xoffset)

                xoffset = 0
                first_block = 1

                if(width_remainder > alignment):

                    while(width_remainder > alignment):

                        source += self._output_field(field, width_remainder, xoffset)

                        xoffset = 0
                        width_remainder -= alignment
                        
                    source += self._output_field(field, width_remainder, xoffset)

                    xoffset = width_remainder

                    if(width_remainder == alignment):
                        xoffset = 0
                    
                elif(width_remainder == alignment):
                    
                    source += self._output_field(field, width_remainder, xoffset)

                    xoffset = 0

                else:
                    
                    source += self._output_field(field, width_remainder, xoffset)

                    xoffset = width_remainder

        return source

        
    def to_c_support_routines(self):
        
        struct_name = self.format_field(self.m_name)
        
        output = '''
void %s_display(void* io_handle, %s* type)
{
    int i;
    int show_zero = 0;

    dbg_dump(io_handle, "\\nstruct %s\\n");

''' % (struct_name, struct_name, struct_name)

        for field in self.m_fields:
            
            if(field.has_key("display")):
                output += field["display"]

        output += '''
}


'''
        return output
       

    def _format_header(self, struct_name):
        output = ''

        fields = ''

        for field in self.m_fields:

            if(field.has_key("c_name")):
                name = field["c_name"]
            else:
                name = field["name"]

            if(field["width"] > 0): # and (not field["is_reserved"])):

                if(self.m_header_style == HEADER_STYLE_KERNEL):
                    fields += '''
 * @%-14s - %s''' % (name, field["desc"])

        
        template = None

        if(self.m_header_style == HEADER_STYLE_KERNEL):

            template = string.Template('''
/**
 * struct ${name}
 * $fields
 *
 $desc
 */''')
        elif(self.m_header_style == HEADER_STYLE_DOXYGEN):
            template = string.Template('''
/**
 * ${desc}
 */''')

        else:

            template = string.Template('''
//+----------------------------------------------------------------------------
//|
//| STRUCTURE:
//|    ${name}
//|
//| DESCRIPTION:
${desc}
//|
//+----------------------------------------------------------------------------''')
        
        if(self.m_comment_style == COMMENT_STYLE_SHORTE):
            prefix = "//|    "
        elif(self.m_comment_style == COMMENT_STYLE_KERNEL):
            prefix = " * " 

        desc = self._parse_description(self.m_desc, prefix, 70).strip()
        
        vars = {}
        vars["name"] = struct_name
        vars["desc"] = desc
        vars["fields"] = fields

        return template.substitute(vars)
        
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     to_c()
    #|
    #| DESCRIPTION:
    #|     This method is called to generate a C description of the record.
    #|
    #+-----------------------------------------------------------------------------
    def to_c(self,
             output_format="bitfields",
             define_prefix='',
             comment_style=COMMENT_STYLE_SHORTE,
             header_style=HEADER_STYLE_DOXYGEN ):
        
        fields = ''

        struct_name = self.format_field(self.m_name)

        self.m_comment_style = comment_style
        self.m_header_style = header_style
        self.m_define_prefix = define_prefix

        if(output_format == "native"):
            fields += self.to_c_native()
        elif(output_format == "bitfields"):
            fields += self.to_c_bitfields()
        elif(output_format == "byte_array"):
            return self.to_c_byte_array()
        else:
            fields += self.to_c_no_bitfields()
        
        
        template = string.Template('''
#pragma pack(push, 1)
$header
typedef struct ${struct_name}_s
{
$fields
}${struct_name};
#pragma pack(pop)
''')
        vars = {}
        vars["header"] = self._format_header(struct_name)
        vars["struct_name"] = struct_name
        vars["fields"] = fields

        return template.substitute(vars)

    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     to_vera()
    #|
    #| PARAMETERS:
    #|     add_ecc (I) - True to insert ECC into the record definition.
    #|
    #| DESCRIPTION:
    #|     This method is called to generate a Vera description of the record.
    #|
    #+-----------------------------------------------------------------------------
    def to_vera(self):
        
        struct_name = string.lower(self.m_name)
        self.m_names = {}

        # If the structure is blank then skip it
        bits = 0
        for field in self.m_fields:
            bits += field["width"]

        if(bits == 0):
            return "// Skipping structure %s because it has no fields\n" % struct_name

        parser = re.compile(" ")
        struct_name = re.sub("[ -]", "_", struct_name)
        record_name = struct_name
        
        type = "TYPE_%s" % string.upper(struct_name)
        
        struct_name = "%s_c" % struct_name
        
        output = """
//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    %s 
//|
//| DESCRIPTION:
%s//|
//+-------------------------------------------------------------------------------
""" % (struct_name, self._parse_description(self.m_desc, "//|    ", 70))
        
        
        output += """
class %s extends s2io_data_c {
""" % struct_name
        
        bit_position = 0
        
        vera_invalidate = "";
        vera_display = "";
        vera_packed_rows = [];
        packed_fields = []
        alignment = 64
        names = {}
        
        for field in self.m_fields:

            total_width = field["width"]

            if(total_width == 0):
                continue

            field["name"] = self._get_field_name(field["name"])
            #field["desc"] = self._parse_description(field["desc"], "    // ", 60)

            name        = field["name"]
            desc_output = False
            values_output = False
            
            while(total_width > 0):
                bits_left = alignment - bit_position
                width = 0
                
                width = total_width
                    
                if(width > 0):
                    name = field["name"]
                    
                    is_reserved = 0
                    prefix = "rand "
                    if(field["is_reserved"]):
                        is_reserved = 1
                        prefix += "protected "
                    
                    # If we haven't output the description yet then append it. It is
                    # here because we might end up splitting a field because of ECC
                    # insertion
                    if(not desc_output):
                        output += self._parse_description(field["desc"], "    // ", 60)
                        desc_output = True
                    else:
                        output += "    // CONTINUED ...\n" + self._parse_description(field["desc"], "    // ", 60)
                    
                    bit_position += width
                    total_width -= width    
                    
                    output += "    %sbit [%d:0] %s;\n" % (prefix, width-1, name)
                    
                    packed_fields.append("this.%s" % name)
                    
                    # If it was a reserved field output zero instead of the name
                    if(not is_reserved):
                        vera_display += "    sprintf(data, \"%%s%%s%-15s: %%0h\\n\",data,prefix,this.%s);\n" % (name, name)
                        vera_invalidate += "    this.%s = %d'hx;\n" % (name, width);
                    else:
                        vera_invalidate += "    this.%s = %d'h0;\n" % (name, width);
                    
                    # Output the values if there are any defined
                    if(field.has_key(VALUES) and not values_output):
                        for val in field[VALUES]:
                            output += ("#    define CM_%s %d\n" %(val, field[VALUES][val]))
                
            output += "\n"

        vars = []
        bits = 0

        for field in self.m_fields:

            name = field["name"]
            width = field["width"]

            if(width == 0):
                continue

            bits += width
            var = "this.%s" % name
            vars.append(var)

        vera_pack = '''
    integer alignment, i;
    bit [%d:0] bitmap = {%s};

    bytes = new[%d];
    alignment = %d;

    for(i = %d/alignment; i > 0; i--)
    {
        // printf("bytes[%%d] = bitmap[%%d:%%d]\\n", i-1, ((i)*alignment) - 1, (i*alignment) - alignment  ); 
        bytes[i-1] = bitmap[(i*alignment) - 1:(i*alignment) - alignment];
    }
''' % ((bits - 1), ','.join(vars), (bits/alignment), alignment, bits)


        vera_unpack = '''
    integer alignment,i;
    bit [%d:0] bitmap;
    alignment = %d;

    for(i = %d/alignment; i > 0; i--)
    {
        // printf("bitmap[%%d:%%d] = bytes[%%d]\\n", ((i)*alignment) - 1, (i*alignment) - alignment, (i-1)+offset); 
        bitmap[(i*alignment) - 1: (i-1)*alignment] = bytes[i-1+offset];
    }

    '{%s} = bitmap;
''' % ((bits - 1), alignment, bits, ','.join(vars))
        

        template = string.Template("""
    
    // Construct a new record
    task new();
    
    // Invalidate the structure
    task invalidate();
    
    // Pack the structure into an array
    task byte_pack(var bit [63:0] bytes[*]);

    task byte_unpack(bit [63:0] bytes[*], integer offset);
    
    // Dump a string of the fields of the record
    function string get_fields_display(string prefix);
    
    // Display the record
    task display(string prefix);
    
} // end of ${struct_name}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    new()
//|
//| PARAMETERS:
//|    None.
//|
//| DESCRIPTION:
//|    This method is called to allocate the new ${struct_name}
//|
//| RETURNS:
//|    None 
//|
//+-------------------------------------------------------------------------------
task ${struct_name}::new() 
{
    super.new("${type}");
    this.invalidate();
}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    invalidate()
//|
//| PARAMETERS:
//|    None.
//|
//| DESCRIPTION:
//|    This method is called to invalidate the fields within the CM record. It
//|    is called on initialization to put the fields in the correct initial
//|    state.
//|
//| RETURNS:
//|    None 
//|
//+-------------------------------------------------------------------------------
task ${struct_name}::invalidate()
{
${vera_invalidate}
}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    byte_pack()
//|
//| PARAMETERS:
//|
//| DESCRIPTION:
//|    This method is called to pack the structure into an array.
//|
//| RETURNS:
//|    None 
//|
//+-------------------------------------------------------------------------------
task ${struct_name}::byte_pack(var bit [${bitwidth}:0] bytes[*])
{
${vera_pack}
}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    byte_unpack()
//|
//| PARAMETERS:
//|
//| DESCRIPTION:
//|    This method is called to unpack the structure from an input array.
//|
//| RETURNS:
//|    None 
//|
//+-------------------------------------------------------------------------------
task ${struct_name}::byte_unpack(bit [${bitwidth}:0] bytes[*], integer offset)
{
${vera_unpack}
}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    get_fields_display()
//|
//| PARAMETERS:
//|    prefix (I) - The prefix to insert in front of each line of the output.
//|
//| DESCRIPTION:
//|    This method is called to retrieve the CM record as a string.
//|
//| RETURNS:
//|    The string describing the record. 
//|
//+-------------------------------------------------------------------------------
// Get the CM record as a string
function string ${struct_name}::get_fields_display(string prefix)
{
    string data = "";
${vera_display}
    get_fields_display = data;
}


//+-------------------------------------------------------------------------------
//|
//| NAME:
//|    display()
//|
//| PARAMETERS:
//|    prefix (I) - The prefix to insert in front of each line of the output..
//|
//| DESCRIPTION:
//|    This method is called to display the contents of the ${struct_name} record.
//|
//| RETURNS:
//|    None 
//|
//+-------------------------------------------------------------------------------
task ${struct_name}::display(string prefix) 
{
    printf("%s", this.get_fields_display(prefix));
}



""")
        
        vera_write_to_cm = ""
        for row in vera_packed_rows:
            vera_write_to_cm += "    row = %s;\n    cm_if.write(cm_address, row, 2'b11, \"backdoor_%s\", 1);\ncm_address++;\n\n" % (row, record_name)
        
        vera_read_from_cm = ""
        for row in vera_packed_rows:
            vera_read_from_cm += "    row = cm_if.read(cm_address, 2'b11, 1);\n    '%s = row;\ncm_address++;\n\n" % row
        
        vars = {}
        vars["struct_name"] = struct_name
        vars["vera_invalidate"] = vera_invalidate
        vars["vera_pack"] = vera_pack
        vars["vera_unpack"] = vera_unpack
        vars["vera_display"] = vera_display
        vars["alignment"] = alignment
        vars["bitwidth"] = alignment - 1
        vars["type"] = type
        
        output += template.substitute(vars)
        
        return output
    
    #+-----------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     _parse_description()
    #|
    #| PARAMETERS:
    #|     desc   (I) - The description of that is being parsed
    #|     prefix (I) - The prefix to attach to each line of the formatted
    #|                  description
    #|     width  (I) - The width of lines in the formatted output.
    #|
    #| DESCRIPTION:
    #|     This method is called to parse an input description and convert it to
    #|     formatted version.
    #|
    #+-----------------------------------------------------------------------------
    def _parse_description(self, desc, prefix, width):
        segments = []
        list_expr = re.compile("([ ]+)?<ul>(.*?)</ul>", re.DOTALL)
        matches = list_expr.search(desc)
        if(matches):
            indent = matches.groups()[0]
            list   = matches.groups()[1]
            
            # Find the indent of the first <li> element
            indent_expr = re.compile("([ ]+)<li>", re.DOTALL)
            matches = indent_expr.search(list)
            if(matches):
                subindent = matches.groups()[0]
            
            entries_expr = re.compile("<li>", re.DOTALL)
            entries = entries_expr.split(list)
            
            for entry in entries:
                
                bspace_expr = re.compile("[ \t]{2,}")
                entry = bspace_expr.sub(" ", entry)
                
                nl_expr = re.compile("\n")
                entry = nl_expr.sub(" ", entry)
                
                bspace_expr = re.compile("\s")
                matches = bspace_expr.match(entry)
                
                if(not matches):
                    li_expr = re.compile("</li>")
                    entry = li_expr.sub("", entry)
                    
                    bspace_expr = re.compile("[ \t]{2,}")
                    entry = bspace_expr.sub(" ", entry)
                    
                    segments.append(subindent + entry)
        
        list = "<br>".join(segments)
        list += "<br>"
        
        desc = list_expr.sub(list, desc)
        
        #print desc
        
        tmp = desc
        
        expr = re.compile("\n")
        lines = expr.split(tmp)
        
        indent = 0
        
        # This is a really complicated way of dealing with
        # multi-line strings in order to determine the indent
        # level in order to strip out extraneous spaces caused
        # by wrapping and indentation.
        for line in lines:
            
            # Find the first blank line, that will tell us our
            # indent level
            wspace = re.compile("^([ \t]+)$", re.MULTILINE)
            matches = wspace.match(line)
            if(matches):
                indent = len(matches.groups()[0])
                if(indent != 0):
                    break
            
            # If there isn't a blank line then try the first
            # line that indenting at the front
            indented = re.compile("^([ \t]+)", re.MULTILINE)
            matches = indented.match(line)
            if(matches):
                indent = len(matches.groups()[0])
                if(indent != 0):
                    break
        
        desc = expr.sub("", desc)
        expr = re.compile("<br>")
        lines = expr.split(desc);
        desc = "";
        
        for line in lines:
            pos  = 0;
            slen = 0;
            segment = ""
            char = ""
            
            indent_expr = re.compile("[ ]{%d}" % (indent))
            matches = indent_expr.match(line)
            
            # First remove 'indent' characters from the
            # beginning of each line
            if(indent > 1):
                indent_expr = re.compile("[ ]{%d}" % (indent))
                line = indent_expr.sub(" ", line)
            
            if(line[0:1] == ' '):
                line = line[1:len(line)]
            
            while(pos <= len(line)):
                char = line[pos:pos+1]
                segment += char;
                
                if(slen > width):
                    if((char == " ") or (char == "\t")):
                        desc += (prefix + segment + "\n")
                        slen = 0
                        segment = ""
                
                pos += 1;
                slen += 1;
            
            if(segment != ""):
                desc += (prefix + segment + "\n")
            else:
                desc += prefix + "\n"
        
        expr = re.compile("<b>(.*?)</b>")
        desc = expr.sub("[\\1]", desc)
        
        expr = re.compile("<.*?>")
        desc = expr.sub("", desc)
        
        return desc;
    
    
    #+--------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     _xoffset()
    #|
    #| PARAMETERS:
    #|     
    #|
    #| DESCRIPTION:
    #|     
    #|
    #+--------------------------------------------------------------------------
    def _xoffset(self, bit_position):
        return self.m_lpad + (bit_position * self.m_width_of_bit)
    
    
    #+--------------------------------------------------------------------------
    #|
    #| FUNCTION:
    #|     draw()
    #|
    #| PARAMETERS:
    #|     
    #|
    #| DESCRIPTION:
    #|     
    #|
    #+--------------------------------------------------------------------------
    def draw(self, output_file, attributes={}):
        
        #draw_width  = 640
        draw_width  = 960
        draw_height = 1500

        bit_order = attributes["bitorder"]

        #print("DRAWING [%s]" % output_file)
        
        try:
            c = cairo(draw_width, draw_height);
        except:
            print "Can't construct images via cairo if cairo_access is not loaded"
            return ""


        c.set_antialias(CAIRO_ANTIALIAS_NONE);

        #if(sys.platform == "win32"):
        #    font_size = 14.0
        #    c.select_font_face("Arial", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
        #else:
        #    font_size = 13.0
        #    c.select_font_face("Lucida Grande", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
        font_size = 14.0
        #c.select_font_face("Arial", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
        c.set_font_size(font_size)
        
        image_map = "<map name=\"diagram_" + self.m_name + "\">"
        
        # Draw the background
        c.rectangle(0, 0, draw_width, draw_height)
        c.set_source_rgb(1, 1, 1)
        c.fill()
        
        #max_bit_width = 256
        max_bit_width = attributes["alignment"]
        self.m_lpad = 20
        self.m_rpad = 20
        y_offset = 22
        height_row = 40
        
        self.m_width_of_bit = (draw_width - self.m_lpad - self.m_rpad)/(max_bit_width * 1.0);
        
        c.set_line_width(1.0)
        
        # Set this flag to draw ECC at the end or split in the middle
        ecc_at_end = True
        
        bit_position = 0
        x_offset = self._xoffset(bit_position)
        bank = 0
        
        for field in self.m_fields:
            
            regex_tick = re.compile("'")
            regex_newline = re.compile("\n")
            regex_quote   = re.compile("\"")
            tooltip = field["desc"]
            tooltip = regex_tick.sub("\\'", tooltip)
            tooltip = regex_newline.sub(" ", tooltip)
            tooltip = regex_quote.sub("\\'", tooltip)
            
            #tooltip =~ s/\\n/<br>/g;
            #tooltip =~ s/\\t/$SPACER/g;
            #tooltip =~ s/{/</g;
            #tooltip =~ s/}/>/g;
            #tooltip =~ s/'/\\'/g;
            #tooltip =~ s/"/\\'/g;
            #tooltip =~ s/  /&nbsp;&nbsp;/g;
            tooltip = "<b>Name: </b><font style=\\\'color: blue;\\\'>%s (%d bits)</font><br>%s" % (field["name"], field["width"], tooltip)
            
            width = field[WIDTH]

            if(width == 0):
                continue

            #print "Field: %s is %d bits width" % (field["name"], field["width"])
            
            while(width > 0):
                
                if(field[NAME] == "reserved"):
                    c.set_source_rgb(0.8, 0.8, 0.8)
                elif(field[NAME] == "Preamble"):
                    c.set_source_rgb(0.8, 0.8, 0.8)
                else:
                    c.set_source_rgb(1, 1, 1);
                
                bit_width = max_bit_width
                
                # Field is too large so we have to split it into
                # one or more sections
                if(width > bit_width - bit_position):

                    tmp = bit_width - bit_position
                    
                    #print "    case 1: width = %d, bit_width = %d, bit_position = %d, tmp=%d" % (width, bit_width, bit_position, tmp)
                    c.rectangle(self._xoffset(bit_position)+1, 
                                y_offset, 
                                tmp * self.m_width_of_bit - 4,
                                height_row);

                    offset = 224

                    x1 = self._xoffset(bit_position)
                    y1 = y_offset
                    x2 = self._xoffset(bit_position) + (tmp * self.m_width_of_bit) - 4
                    y2 = y_offset + height_row


                    
                    image_map += "<area border=1 shape=\"rectangle\" "\
                                    "coords=\"%d,%d,%d,%d\" "\
                                    "href=\"#%s_%s\" "\
                                    "onMouseover=\"ddrivetip('%s');\" "\
                                    "onMouseout=\"hideddrivetip()\" >\n" %\
                                    (x1, y1, x2, y2,
                                     self.m_name, field[NAME], tooltip)
                    
                                    #(self._xoffset(bit_position),
                                    # y_offset,
                                    # self._xoffset(bit_position) + self._xoffset(offset - bit_position),
                                    # y_offset + height_row,
                    c.fill_preserve();
                    c.set_source_rgb(0, 0, 0);
                    c.stroke();
                    
                    name = field[NAME]
                    (x,y) = c.text_extents("%s" % name)
                    while(x > (max_bit_width - bit_position) * self.m_width_of_bit):
                        name = name[0:len(name)-1]
                        (x,y) = c.text_extents("%s" % name)
                    
                    center = self._xoffset(bit_position) + (self.m_width_of_bit * (max_bit_width - bit_position))/2 - x/2
                    c.move_to(center, y_offset + (height_row/2 + y/3))
                    c.show_text("%s" % name)
                    
                    width -= (bit_width - bit_position)
                    y_offset += height_row + 5

                    bit_position = 0

                
                elif(width < bit_width - bit_position):
                    
                    #print "    case 2: width = %d, bit_width = %d, bit_position = %d" % (width, bit_width, bit_position)
                    c.rectangle(self._xoffset(bit_position)+1, 
                                y_offset, 
                                (width * self.m_width_of_bit) - 4,
                                height_row);
                    
                    image_map += "<area border=1 shape=\"rectangle\" "\
                                    "coords=\"%d,%d,%d,%d\" "\
                                    "href=\"#%s_%s\" "\
                                    "onMouseover=\"ddrivetip('%s');\" "\
                                    "onMouseout=\"hideddrivetip();\" >\n" %\
                                    (self._xoffset(bit_position), \
                                     y_offset,
                                     self._xoffset(bit_position) + (width * self.m_width_of_bit),
                                     y_offset + height_row,
                                     self.m_name, field[NAME], tooltip)
                                     
                                     
                    c.fill_preserve();
                    c.set_source_rgb(0, 0, 0);
                    c.stroke();
                    (x,y) = c.text_extents("%s" % field[NAME])
                    name = field[NAME]
                    (x,y) = c.text_extents("%s" % name)
                    while(x > (width * self.m_width_of_bit)):
                        name = name[0:len(name)-1]
                        (x,y) = c.text_extents("%s" % name)
                    
                    center = self._xoffset(bit_position) + (self.m_width_of_bit * (width))/2 - x/2
                    c.move_to(center, y_offset + (height_row/2 + y/3))
                    c.show_text("%s" % name)
                    
                    bit_position += width
                    width = 0
                    
                else:
                    #print "    case 3: width = %d, bit_width = %d, bit_position = %d" % (width, bit_width, bit_position)
                    c.rectangle(self._xoffset(bit_position)+1, 
                                y_offset, 
                                (width * self.m_width_of_bit) - 4,
                                height_row);
                    
                    image_map += "<area border=1 shape=\"rectangle\" "\
                                    "coords=\"%d,%d,%d,%d\" "\
                                    "href=\"#%s_%s\" "\
                                    "onMouseover=\"ddrivetip('%s');\" "\
                                    "onMouseout=\"hideddrivetip()\" >\n" %\
                                    (self._xoffset(bit_position), \
                                     y_offset,
                                     self._xoffset(bit_position) + (width * self.m_width_of_bit),
                                     y_offset + height_row,
                                     self.m_name, field[NAME], tooltip)
                                     
                    c.fill_preserve();
                    c.set_source_rgb(0, 0, 0);
                    c.stroke();
                    (x,y) = c.text_extents("%s" % field[NAME])
                    name = field[NAME]
                    (x,y) = c.text_extents("%s" % name)
                    while(x > (width * self.m_width_of_bit)):
                        name = name[0:len(name)-1]
                        (x,y) = c.text_extents("%s" % name)
                    
                    center = self._xoffset(bit_position) + (self.m_width_of_bit * (width))/2 - x/2
                    c.move_to(center, y_offset + (height_row/2 + y/3))
                    c.show_text("%s" % name)
                    
                    width = 0
                    y_offset += height_row + 5
                    bit_position = 0

        if(bit_position != 0):
            y_offset += height_row + 5
        
        
        # Draw the header
        dashes = new_doubleArray(2);
        doubleArray_setitem(dashes, 0, 2.0);
        doubleArray_setitem(dashes, 1, 2.0);
        c.set_dash(dashes, 2, 0)
        delete_doubleArray(dashes);
        
        x_offset = self.m_lpad

        if(bit_order == "decrement"):
            for i in range(max_bit_width, -1, -1):
                top    = 10
                bottom = 20
                
                if(i % 8):
                    c.set_source_rgb(0.5, 0.5, 0.5)
                    top = 15
                else:
                    c.set_source_rgb(0, 0, 0)

                    (tx,ty) = c.text_extents("%d" % (max_bit_width - i))

                    c.move_to(x_offset + ((i) * self.m_width_of_bit) - (tx/2), top)
                    c.show_text("%d" % (max_bit_width - i))
                    
                    c.set_source_rgb(1.0, 0.7, 0.7)
                    bottom = y_offset
                
                c.move_to(x_offset + (i * self.m_width_of_bit), top)
                c.line_to(x_offset + (i * self.m_width_of_bit), bottom)
                c.stroke();
                
                c.move_to(x_offset + (i * self.m_width_of_bit), top)
        else:
            for i in range(0, max_bit_width + 1):
                top    = 10
                bottom = 20
                
                if(i % 8):
                    c.set_source_rgb(0.5, 0.5, 0.5)
                    top = 15
                else:
                    c.set_source_rgb(0, 0, 0)

                    (tx,ty) = c.text_extents("%d" % (i))

                    c.move_to(x_offset + (i * self.m_width_of_bit) - tx/2, top)
                    c.show_text("%d" % i)
                    
                    c.set_source_rgb(1.0, 0.7, 0.7)
                    bottom = y_offset
                
                c.move_to(x_offset + (i * self.m_width_of_bit), top)
                c.line_to(x_offset + (i * self.m_width_of_bit), bottom)
                c.stroke();
                
                c.move_to(x_offset + (i * self.m_width_of_bit), top)
            
        
        image_map += "</map>\n"
        
        c.write_to_png(output_file, draw_width, y_offset + 10);
        
        return image_map
