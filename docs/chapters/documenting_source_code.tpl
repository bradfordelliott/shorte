
@body
@h1 Documenting Source Code

@h2 Documenting C/C++
The following section describes how to format source code. The following
attributes are supported to assist in extracting useful documentation from
source code.

@table: title="Attributes"
- Attribute   | Format    | Description
- @brief      | Textblock | This tag is used to document the function description. It
                            is optional and may be used to separate the function
                            description from any shorte documentation or headings.
- @param      | Textblock | A textblock attribute used to document a function parameter.
- @return     | Text      | A textblock attribute used to document the return value of a function.
- @private    | None      | This attribute is used to mark the function as private so
                            that documentation won't be extracted. It has no data associated with it.
- @deprecated | Text      | This tag is used to mark an object as deprecated
- @since      | Text      | This attribute is used to indicate the version that an object
                            was first introduced.
- @example    | Code      | This attribute is used to provide a source code example of
                            how to use the object.
- @see        | Text      | Used to link to other similar or related objects.
- @requires   | Text      | Used to indicate a dependency or a requirement for using the object.

@h3 Creating Headings
It is possible to insert headings and the like into source
code snippets by placing shorte tags in either the file header
or in a source code comment associated with a source code object
such as a define, struct or prototype.

@c
/**
 * @h2 A Random Heading
 * A paragraph after a heading within a document
 * - A list
 *     - A second list item
 * - Another list
 *
 * @brief
 * This is a description of the function, enum, struct
 * or define.
 * ...
 */


@h3 Documenting Functions
The following example shows how to document functions.

@c
/**
 * This is a description of a function prototype
 * that acts like an @textblock tag.
 *
 * @param one [I] - A description of a parameter
 *                  that also acts like a textblock.
 * @param two [I] - A second parameter.
 *
 * @return
 * The description of the return statement that
 * also acts like a textblock.
 */
int function1(int one, int two)
{
    return 0;
}


@h3 Documenting Enumerations
The following example shows how to document enumerations.

@c
/**
 * This is a description of the enumeration
 * that acts like an @textblock tag.
 */
typedef enum data
{
    /** A description of the enumeration value that
        acts like an @textblock tag. */
    VAL1 = 0,

    /** A description of the enumeration value that
        acts like an @textblock tag. */
    VAL2 = 1,

};

@h3 Documenting Structures
The following example shows how to document structures.

@c
/**
 * This is a description of the structure that acts like
 * an @textblock tag.
 */
typedef struct blah_s
{
    /**
     * This is a structure field that acts like
     * an @textblock tag.
     */
    int field1;

    /**
     * This is second structure field that acts like
     * an @textblock tag.
     */
    int field2;
}blah_t;


@h3 Document Defines
The following example shows how to document defines.

@c
/**
 * This is a description of a define
 */
#define XYZ 10


@h2: if=0
Documenting Python

TBD
