#include <QUrl>
#include <QFileDialog>
#include <QMessageBox>
#include <QFileSystemWatcher>
#include <QMenu>
#include <QProcess>
#include <QFont>
#include <QClipboard>
#include <QSplitter>

#include "widgeteditor.h"
#include "ui_widgeteditor.h"
#include "SciLexer.h"
#include "ScintillaEditBase.h"

using namespace Scintilla;

QString CS_GUI_GET_GLOBAL_SETTING(const QString& name);
void CS_GUI_SET_GLOBAL_SETTING(const QString& name, const QString& data);

QMap<QString, QVariant> m_properties;

#include "widgets/common/scripts/widgetgotopanel.h"
#include "widgets/common/scripts/widgetfindpanel.h"

WidgetEditor::WidgetEditor(bool allow_tabs, QWidget *parent) :
    QWidget(parent),
    ui(new Ui::WidgetEditor)
{
    ui->setupUi(this);
    setAcceptDrops(true);

    m_scripts_watcher = new QFileSystemWatcher(parent);

    connect(this->m_scripts_watcher,
        SIGNAL(fileChanged(const QString&)),
        this,
        SLOT(on_script_changed(const QString&)));

    ui->m_tabs->setContextMenuPolicy(Qt::CustomContextMenu);

    m_allow_tabs = allow_tabs;

    if(!allow_tabs)
    {
        show_tab_bar(false);
    }

    // Default properties - these should come from the settings
    // database.
    m_properties["SETVIEWWS"] = SCWS_INVISIBLE;
    m_properties["SETVIRTUALSPACEOPTIONS"] = SCVS_RECTANGULARSELECTION | SCVS_USERACCESSIBLE;
    m_properties["SETUSETABS"] = false;
    m_properties["SETINDENT"] = 4;
    m_properties["SETTABINDENTS"] = true;
    m_properties["SETBACKSPACEUNINDENTS"] = true;
    m_properties["FOLD"] = "1";
    m_properties["SETMARGINWIDTH"] = 45;
    m_properties["SETEDGEMODE"] = EDGE_LINE;
    m_properties["SETEDGECOLUMN"] = 80;
    m_properties["SETEDGECOLOUR"] = 0xe0e0e0;

    m_properties["SETHIGHLIGHTGUIDE"] = 80;

    m_properties["SETCARETLINEVISIBLE"] = true;
    m_properties["SETCARETLINEBACK"] = 0xf0f0f0;

    m_properties["EOLMODE"] = SC_EOL_LF;

    WidgetGotoPanel* panel_goto = new WidgetGotoPanel(this);

    if(!connect(panel_goto, SIGNAL(signal_go_to_line(int)),
           this,
            SLOT(on_goto_line(int))))
    {
        QMessageBox::information(this, "Failed connecting", "Failed connecting");
    }

    WidgetFindPanel* panel_find = new WidgetFindPanel(this);
    panel_find->show_close_button(false);

    connect(panel_find, SIGNAL(signal_text_entered(const QString&)),
           this,
            SLOT(on_find_next(const QString&)));

    connect(panel_find, SIGNAL(signal_find_last(const QString&)),
           this,
            SLOT(on_find_last(const QString&)));

    connect(panel_find, SIGNAL(signal_replace(const QString&, const QString&, bool, bool)),
            this,
            SLOT(on_find_replace(const QString&, const QString&, bool, bool)));

    connect(this->ui->m_tools_panel, SIGNAL(signal_close_panel()),
            this,
            SLOT(on_close_tools_panel()));
    this->ui->m_tools_panel->add_page("Goto", panel_goto);
    this->ui->m_tools_panel->add_page("Find", panel_find);

}

WidgetEditor::~WidgetEditor()
{
    delete ui;
}

void WidgetEditor::show_tab_bar(bool show)
{
    // If the tab bar is disabled then don't allow it
    // to showed.
    if(!m_allow_tabs && show == true)
    {
        return;
    }

    // This is a really bizarre way of hiding the tab bar if it
    // isn't necessary (i.e. if there is only one document. The
    // tabBar() method is protected so we can't access it. Instead
    // search all the child tabs and see if any of them have the class
    // name "QTabBar".
    QObjectList children = ui->m_tabs->children();
    for(int i = 0; i < children.count(); i++)
    {
        QObject* child = children.at(i);
        QString class_name = child->metaObject()->className();

        if(class_name == "QTabBar")
        {
            QWidget* widget = (QWidget*)child;

            if(show)
            {
                widget->setVisible(true);
            }
            else
            {
                widget->setVisible(false);
            }
            break;
        }
    }
}

QTabWidget* WidgetEditor::get_tabs(void)
{
    return ui->m_tabs;
}

void WidgetEditor::show_whitespace(bool show, int index)
{
    if(show)
    {
        m_properties["SETVIEWWS"] = SCWS_INVISIBLE;
    }
    else
    {
        m_properties["SETVIEWWS"] = SCWS_VISIBLEALWAYS;
    }

    call(index, SCI_SETVIEWWS, m_properties["SETVIEWWS"].toInt());
}

void WidgetEditor::on_script_changed(const QString& path)
{
    if(QMessageBox::Yes == QMessageBox::question(this, "File Changed",
        QString("File %1 changed outside this process, do you want to reload it?").arg(path),
        QMessageBox::Yes, QMessageBox::No))
    {
        reopen_path(path);
    }
}

sptr_t WidgetEditor::call(int document_index, unsigned int iMessage, uptr_t wParam, sptr_t lParam)
{
    QSplitter* splitter = NULL;

    if(document_index != CURRENT_DOC)
    {
        splitter = (QSplitter*)this->ui->m_tabs->widget(document_index);
    }
    else
    {
        splitter = (QSplitter*)this->ui->m_tabs->currentWidget();
    }

    sptr_t result = NULL;

    for(int i = 0; i < splitter->count(); i++)
    {
        if(i > 0)
        {
            if(iMessage == SCI_SETTEXT ||
               iMessage == SCI_INSERTTEXT ||
               iMessage == SCI_APPENDTEXT)
            {
                break;
            }
        }

        ScintillaEditBase* sci = (ScintillaEditBase*)splitter->widget(i);

        if(sci != NULL)
        {
            result = sci->send(iMessage, wParam, lParam);
        }
    }

    return result;
}

void WidgetEditor::define_marker(int document_index, int marker, int markerType, int fore, int back) {
    call(document_index, SCI_MARKERDEFINE, marker, markerType);
    call(document_index, SCI_MARKERSETFORE, marker, fore);
    call(document_index, SCI_MARKERSETBACK, marker, back);
}

void WidgetEditor::load_lexer_styles(int index, const QString& lexer_prefix, int num_styles)
{
    for(int i = 0; i < 4; i++)
    {
        QString keywords = CS_GUI_GET_GLOBAL_SETTING(QString("%1.keywords.%2").arg(lexer_prefix).arg(i));
        call(index, SCI_SETKEYWORDS, i, (sptr_t)keywords.toStdString().c_str());
    }

    //call(index, SCI_STYLESETBACK, STYLE_DEFAULT, 0xA0A0A0);

    for(int i = 0; i < num_styles; i++)
    {
        //call(index, SCI_STYLESETBACK, i, 0xA0A0A0);

        QString style = CS_GUI_GET_GLOBAL_SETTING(QString("%1.%2").arg(lexer_prefix).arg(i));

        if(style.length() > 0)
        {
            quint32 color = 0;
            quint32 background = 0;

            bool has_background = false;
            bool is_bold = false;
            bool is_hotspot = false;

            if(style.contains(";") || style.contains("="))
            {
                QStringList styles = style.split(";");
                for(int i = 0; i < styles.length(); i++)
                {
                    QStringList segments = styles.at(i).split("=");

                    if(segments.count() == 2)
                    {
                        if(segments[0] == "bold")
                        {
                            if(segments[1] == "1")
                            {
                                is_bold = true;
                            }
                        }
                        else if(segments[0] == "fore" || segments[0] == "color")
                        {
                            color = segments[1].toInt(0,16);
                        }
                        else if(segments[0] == "back")
                        {
                            has_background = true;
                            background = segments[1].toInt(0,16);
                        }
                        else if(segments[0] == "hotspot")
                        {
                            if(segments[1] == "1")
                            {
                                is_hotspot = true;
                            }
                        }
                    }
                }
            }
            else
            {
                color = style.toInt(0,16);
            }

            call(index, SCI_STYLESETFORE, i, color);

            if(has_background)
            {
                call(index, SCI_STYLESETBACK, i, background);
            }

            if(is_bold)
            {
                call(index, SCI_STYLESETBOLD, i, 1);
            }

            if(is_hotspot)
            {
                call(index, SCI_STYLESETHOTSPOT, i, 1);
            }
        }
    }


}


void WidgetEditor::setup_styles(int lexer, int index)
{
    call(index, SCI_SETLEXER, lexer);

    /* Setup the default font sizes in the editor. Should be able to
     * change this but can't right now */
#if defined(Q_OS_MAC)
    call(index, SCI_STYLESETSIZE, STYLE_DEFAULT, 13);
#else
    call(index, SCI_STYLESETSIZE, STYLE_DEFAULT, 10);
#endif

    call(index, SCI_STYLECLEARALL);

    switch(lexer)
    {
        case SCLEX_CPP:
        {
            load_lexer_styles(index, "lexer.c++", 26);

            /*const char *keywords =
            "and and_eq asm auto bitand bitor bool break "
            "case catch char class compl const const_cast continue "
            "default delete do double dynamic_cast else enum explicit export extern false float for "
            "friend goto if inline int long mutable namespace new not not_eq "
            "operator or or_eq private protected public "
            "register reinterpret_cast return short signed sizeof static static_cast struct switch "
            "template this throw true try typedef typeid typename union unsigned using "
            "virtual void volatile wchar_t while xor xor_eq";

            call(index, SCI_SETKEYWORDS, 0, (sptr_t)keywords);
            */
            call(index, SCI_SETKEYWORDS, 1, (sptr_t)get_link_words().toStdString().c_str());
            /*call(index, SCI_SETKEYWORDS, 4, (sptr_t)"");

            call(index, SCI_STYLESETFORE, SCE_C_COMMENT, 0x008000);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTLINE, 0x008000);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTDOC, 0x008040);
            call(index, SCI_STYLESETITALIC, SCE_C_COMMENTDOC, 1);
            call(index, SCI_STYLESETFORE, SCE_C_NUMBER, 0x808000);
            call(index, SCI_STYLESETFORE, SCE_C_WORD, 0x800000);
            call(index, SCI_STYLESETBOLD, SCE_C_WORD, 1);
            call(index, SCI_STYLESETFORE, SCE_C_STRING, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_C_PREPROCESSOR, 0x008080);
            call(index, SCI_STYLESETBOLD, SCE_C_OPERATOR, 1);

            call(index, SCI_STYLESETFORE, SCE_C_IDENTIFIER, 0x000000);
            */


            /*
            DEBUG BRAD: Leaving this in here to save some typing in the future
                        in case I want to tune these styles.
            call(index, SCI_STYLESETFORE, SCE_C_PREPROCESSORCOMMENT, 0x008080);
            call(index, SCI_STYLESETFORE, SCE_C_HASHQUOTEDSTRING, 0x008080);
            call(index, SCI_STYLESETUNDERLINE, SCE_C_PREPROCESSORCOMMENT, false);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTLINEDOC, 0x008040);
            call(index, SCI_STYLESETFORE, SCE_C_VERBATIM, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_STRINGRAW, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_TRIPLEVERBATIM, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_GLOBALCLASS, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTDOCKEYWORDERROR, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTDOCKEYWORD, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_WORD2, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_COMMENTLINEDOC, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_REGEX, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_VERBATIM, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_STRINGEOL, 0x009090);
            call(index, SCI_STYLESETFORE, SCE_C_IDENTIFIER, 0x009090);

            //call(index, SCI_STYLESETFORE, SCE_C_GLOBALCLASS, 0x009090);
            //call(index, SCI_STYLESETBACK, SCE_C_GLOBALCLASS, 0x009090);
            //call(index, SCI_STYLESETUNDERLINE, SCE_C_GLOBALCLASS, false);
            */

            call(index, SCI_SETPROPERTY, (uptr_t)("styling.within.preprocessor"), (sptr_t)"0");

            /* DEBUG BRAD: For the time being disable preprocessor tracking till I can figure
             * out what causes the obnoxious squiggles */
            call(index, SCI_SETPROPERTY, (uptr_t)("lexer.cpp.track.preprocessor"), (sptr_t)"0");
            call(index, SCI_SETPROPERTY, (uptr_t)("lexer.cpp.update.preprocessor"), (sptr_t)"0");

            /* DEBUG BRAD: This doesn't seem to work right now
            call(index, SCI_SETPROPERTY, (uptr_t)("braces.check"), (sptr_t)"1");
            */

            /* DEBUG BRAD: Inactive styles don't work for some reason.
            call(index, SCI_STYLESETFORE, STYLE_BRACEBAD, 0x0000ff);
            for(int i = 64; i <= 88; i++)
            {
                call(index, SCI_STYLESETFORE, i, 0xF0F0F0);
            }
            /*

            /* DEBUG BRAD: This is currently a bit of a hack to get #if 0 blocks
             *             to display correctly. For some reason they don't show up
             *             as greyed out but instead have a small T under them by default.
             */
            call(index, SCI_INDICSETSTYLE, 0, INDIC_SQUIGGLE);
            call(index, SCI_INDICSETSTYLE, 1, INDIC_SQUIGGLE);
            call(index, SCI_INDICSETSTYLE, 2, INDIC_SQUIGGLE);
            call(index, SCI_INDICSETFORE, 0, 0xC0C0C0);
            call(index, SCI_INDICSETFORE, 1, 0xC0C0C0);
            call(index, SCI_INDICSETFORE, 2, 0xC0C0C0);

            /* Highlight hyperlinked keywords */
            //call(index, SCI_STYLESETHOTSPOT, SCE_C_WORD2, true);
            //call(index, SCI_STYLESETFORE, SCE_C_WORD2, 0xff0000);

            break;
        }
        case SCLEX_PYTHON:
        {
            load_lexer_styles(index, "lexer.python", 16);
            call(index, SCI_SETKEYWORDS, 1, (sptr_t)get_link_words().toStdString().c_str());

            /*call(index, SCI_SETKEYWORDS, 0, (sptr_t)keywords);

            call(index, SCI_SETKEYWORDS, 1, (sptr_t)get_link_words().toStdString().c_str());

            call(index, SCI_STYLESETFORE, SCE_P_DEFAULT, 0x000000);

            call(index, SCI_STYLESETFORE, SCE_P_COMMENTLINE, 0x008000);
            call(index, SCI_STYLESETFORE, SCE_P_NUMBER, 0x336699);
            call(index, SCI_STYLESETFORE, SCE_P_STRING, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_P_WORD, 0x800000);
            call(index, SCI_STYLESETFORE, SCE_P_TRIPLE, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_P_TRIPLEDOUBLE, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_P_CHARACTER, 0xcc33ff);
            call(index, SCI_STYLESETFORE, SCE_P_CLASSNAME, 0);
            call(index, SCI_STYLESETFORE, SCE_P_DEFNAME, 0);
            call(index, SCI_STYLESETBOLD, SCE_P_OPERATOR, 1);
            call(index, SCI_STYLESETFORE, SCE_P_IDENTIFIER, 0);
            call(index, SCI_STYLESETFORE, SCE_P_COMMENTBLOCK, 0x008000);
            call(index, SCI_STYLESETFORE, SCE_P_STRINGEOL, 0);
            call(index, SCI_STYLESETHOTSPOT, SCE_P_WORD2, true);
            call(index, SCI_STYLESETFORE, SCE_P_WORD2, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_P_DECORATOR, 0);
            */

            break;
        }
        case SCLEX_HTML:
        {
            load_lexer_styles(index, "lexer.html", 128);

            break;
        }
        case SCLEX_SHORTE:
        {
            load_lexer_styles(index, "lexer.shorte", 20);

            /*
            const char *keywords =
"@doctitle @docsubtitle @docnumber @docrevisions @docversion @docfilename "
"@body @h1 @h2 @h3 @h4 @h5 @include "
"@input @columns @column @testcasesummary @testcase @functionsummary @typesummary "
"@questions "
"@pre @p @text @table @ol @ul @embed @endcolumns "
"@perl @inkscape @sequence @bash @java @c @vera @python @verilog @tcl @checklist @vector @struct @prototype @acronyms @enum @imagemap @image "
"@note"
;
            //call(index, SCI_SETKEYWORDS, 0, (sptr_t)"");
            //call(index, SCI_SETKEYWORDS, 1, (sptr_t)get_link_words().toStdString().c_str());

            //call(index, SCI_SETKEYWORDS, 2, (sptr_t)keywords);
            //call(index, SCI_SETKEYWORDS, 1, (sptr_t)keywords);
            //call(index, SCI_SETKEYWORDS, 0, (sptr_t)get_link_words().toStdString().c_str());
            //call(index, SCI_SETKEYWORDS, 1, (sptr_t)get_link_words().toStdString().c_str());

            call(index, SCI_STYLESETFORE, SCE_SHORTE_DEFAULT, 0x000000);

            // Shorte keywords
            call(index, SCI_SETKEYWORDS, 2, (sptr_t)keywords);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_MACRO, 0x800000);
            call(index, SCI_STYLESETBOLD, SCE_SHORTE_MACRO, true);


            call(index, SCI_STYLESETFORE, SCE_SHORTE_STRING, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_CONDITIONAL_EVAL, 0x00ff00);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_COMMENT, 0x008000);

            //call(index, SCI_STYLESETHOTSPOT, SCE_SHORTE_KEYWORD, true);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_KEYWORD, 0xff0000);

            call(index, SCI_STYLESETHOTSPOT, SCE_SHORTE_FUNCTION, true);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_FUNCTION, 0xff0000);

            call(index, SCI_STYLESETFORE, SCE_SHORTE_NUMBER, 0xff0000);
            //call(index, SCI_STYLESETFORE, SCE_SHORTE_FUNCTION, 0xff0000);
            //call(index, SCI_STYLESETFORE, SCE_SHORTE_KEYWORD, 0xff0000);
            //call(index, SCI_STYLESETFORE, SCE_SHORTE_MACRO, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_STRING, 0xff00ff);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_OPERATOR, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_VARIABLE, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_SENT, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_PREPROCESSOR, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_SPECIAL, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_EXPAND, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_COMOBJ, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_UDF, 0xff0000);
            //call(index, SCI_STYLESETFORE, SCE_SHORTE_CONDITIONAL_EVAL, 0xff0000);

            // Code blocks - if they are supported
            const char* code_blocks =
                "@perl @bash @java @c @vera @python @verilog @tcl";
            call(index, SCI_SETKEYWORDS, 3, (sptr_t)code_blocks);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_CODE_BLOCK, 0x66AA22);
            //call(index, SCI_STYLESETBACK, SCE_SHORTE_CODE_BLOCK, 0xf7f7f7);

            call(index, SCI_STYLESETFORE, SCE_SHORTE_LINK, 0xff0000);
            call(index, SCI_STYLESETFORE, SCE_SHORTE_INLINE_TAG, 0xff0000);
            */

            break;
        }
        default:
        {
        }
    }

    /* Customize the styles */
    call(index, SCI_SETMARGINWIDTHN, 0, m_properties["SETMARGINWIDTH"].toInt());
    call(index, SCI_SETSCROLLWIDTH, 200, 0);
    call(index, SCI_SETSCROLLWIDTHTRACKING, 1, 0);


    //call(CURRENT_DOC, SCI_STYLESETFORE, SCI_STYLESETHOTSPOT, 0x0000ff);
    //call(index, SCI_SETSEL, 8, 4);
    call(index, SCI_SETMULTIPLESELECTION, 1);
    call(index, SCI_SETVIRTUALSPACEOPTIONS, m_properties["SETVIRTUALSPACEOPTIONS"].toInt());
    call(index, SCI_SETADDITIONALSELECTIONTYPING, 1);

    call(index, SCI_STYLESETFORE, STYLE_INDENTGUIDE, 0x808080);
    call(index, SCI_SETINDENTATIONGUIDES, SC_IV_LOOKBOTH);
    call(index, SCI_SETVIEWWS, m_properties["SETVIEWWS"].toInt());

    call(index, SCI_SETFOLDMARGINCOLOUR, 1, 0xffD0D0);
    call(index, SCI_SETFOLDMARGINHICOLOUR, 1, 0xD0ffD0);
    call(index, SCI_SETMARGINTYPEN, 2, SC_MARGIN_SYMBOL);
    call(index, SCI_SETMARGINWIDTHN, 1, 10);
    call(index, SCI_SETMARGINWIDTHN, 2, 14);
    call(index, SCI_SETMARGINMASKN, 2, SC_MASK_FOLDERS);
    call(index, SCI_SETMARGINSENSITIVEN, 2, 1);

    call(index, SCI_SETEDGEMODE, m_properties["SETEDGEMODE"].toInt());
    call(index, SCI_SETEDGECOLUMN, m_properties["SETEDGECOLUMN"].toInt());
    call(index, SCI_SETEDGECOLOUR, m_properties["SETEDGECOLOUR"].toInt());

    call(index, SCI_SETCARETLINEVISIBLE, m_properties["SETCARETLINEVISIBLE"].toBool());
    call(index, SCI_SETCARETLINEBACK, m_properties["SETCARETLINEBACK"].toInt());

    call(index, SCI_SETHIGHLIGHTGUIDE, m_properties["SETHIGHLIGHTGUIDE"].toInt());

    /* Use spaces instead of tabs */
    call(index, SCI_SETUSETABS, m_properties["SETUSETABS"].toBool());
    /* Use indentation setting of 4 */
    call(index, SCI_SETINDENT, m_properties["SETINDENT"].toInt());

    /* Force tab to indent in block selections */
    call(index, SCI_SETTABINDENTS, m_properties["SETTABINDENTS"].toBool());
    call(index, SCI_SETBACKSPACEUNINDENTS, m_properties["SETBACKSPACEUNINDENTS"].toBool());

    call(index, SCI_SETPROPERTY, (uptr_t)("fold"), (sptr_t)m_properties["FOLD"].toString().toLatin1().constData());
    define_marker(index, SC_MARKNUM_FOLDEROPEN, SC_MARK_BOXMINUS, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDER, SC_MARK_BOXPLUS, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDERSUB, SC_MARK_VLINE, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDERTAIL, SC_MARK_LCORNER, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDEREND, SC_MARK_BOXPLUSCONNECTED, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDEROPENMID, SC_MARK_BOXMINUSCONNECTED, 0xffffff, 0x808080);
    define_marker(index, SC_MARKNUM_FOLDERMIDTAIL, SC_MARK_TCORNER, 0xffffff, 0x808080);

    call(index, SCI_GRABFOCUS);

    call(index, SCI_COLOURISE, 0, -1);
}

int WidgetEditor::create_document(const QString& title, const QString& contents, e_cs_script_type type)
{
    QSplitter* splitter = new QSplitter(this);
    ScintillaEditBase *sci = new ScintillaEditBase(this);

    splitter->addWidget(sci);

    int index = this->ui->m_tabs->addTab(splitter, title);
    this->ui->m_tabs->setCurrentIndex(index);
    QString init_data;

/* DEBUG BRAD: Don't hide tabs for now if there is only one doc
    if(this->ui->m_tabs->count() > 1)
    {
        show_tab_bar(true);
    }
    else
    {
        show_tab_bar(false);
    }
*/

    this->ui->m_tabs->currentWidget()->setProperty("path", title);

    if(contents.length() > 0)
    {
        init_data = contents;
    }

    int lexer = SCLEX_NULL;

    if(type == CS_SCRIPT_TYPE_C)
    {
        lexer = SCLEX_CPP;
    }
    else if(type == CS_SCRIPT_TYPE_PYTHON)
    {
        lexer = SCLEX_PYTHON;
    }
    else if(type == CS_SCRIPT_TYPE_SHORTE)
    {
        lexer = SCLEX_SHORTE;
    }

    QFileInfo path(title);
    QString suffix = path.completeSuffix();
    if(suffix == "py" || suffix == "txt")
    {
        lexer = SCLEX_PYTHON;
    }
    else if(suffix == "c" || suffix == "h" || suffix == "cpp")
    {
        lexer = SCLEX_CPP;
    }
    else if(suffix == "html")
    {
        lexer = SCLEX_HTML;
    }
    else if(suffix == "tpl")
    {
        lexer = SCLEX_SHORTE;
    }

    /* Set common styles */
    call(CURRENT_DOC, SCI_STYLESETFONT, STYLE_DEFAULT , (sptr_t)"Courier New");
    call(CURRENT_DOC, SCI_STYLESETSIZE, STYLE_DEFAULT , 10);
    /* Apply the default styles */
    call(CURRENT_DOC, SCI_STYLECLEARALL);
    call(CURRENT_DOC, SCI_SETEOLMODE, m_properties["EOLMODE"].toInt());
    setup_styles(lexer);

    call(CURRENT_DOC, SCI_INSERTTEXT, 0, (sptr_t)(void *)init_data.toStdString().c_str());

    //ui->actionLatin_1->setChecked(true);

    connect(sci, SIGNAL(notify(SCNotification *)), this, SLOT(receive_notify(SCNotification *)));
    connect(sci, SIGNAL(command(uptr_t, sptr_t)), this, SLOT(receive_command(uptr_t, sptr_t)));

    // Mark the newly created file as unmodified
    call(CURRENT_DOC, SCI_SETSAVEPOINT);

    return index;
}

void WidgetEditor::receive_notify(SCNotification *pscn)
{
    // Implement support for folding
    if(pscn->nmhdr.code == SCN_MARGINCLICK)
    {
        //const int modifiers = pscn->modifiers;
        const int position = pscn->position;
        const int margin = pscn->margin;
        const int line_number = call(CURRENT_DOC, SCI_LINEFROMPOSITION, position, 0);

        switch (margin)
        {
            case 2:
            {
                call(CURRENT_DOC, SCI_TOGGLEFOLD, line_number, 0);
                break;
            }
        }
    }
    else if(pscn->nmhdr.code  == SCN_HOTSPOTCLICK)
    {
        QString text = get_hot_spot_text(pscn->position);
        int modifiers = pscn->modifiers;

        if(SCMOD_CTRL == modifiers)
        {
            emit signal_hotspot_activated(text);
        }
        //this->ui->m_hotspot_info->setText(text);
    }
    // DEBUG BRAD: Eventually want to use to mark when the
    //             document is un-modified.
    else if(pscn->nmhdr.code == SCN_SAVEPOINTREACHED)
    {
        doc_mark_modified(CURRENT_DOC, false);
    }
    // DEBUG BRAD: Eventually want to use to mark when the
    //             document is modified.
    else if(pscn->nmhdr.code == SCN_SAVEPOINTLEFT)
    {
        doc_mark_modified(CURRENT_DOC, true);
    }
    else if(pscn->nmhdr.code == SCN_CHARADDED)
    {
        /*
         * Implements a smart indent whereby new lines
         * get indented based on the indentation of the previous
         * line
         */
        if  (pscn->ch  ==  '\r'  ||  pscn->ch  ==  '\n')
        {
             char  linebuf[1000];
             int cur_pos = call(CURRENT_DOC, SCI_GETCURRENTPOS);
             int cur_line = call(CURRENT_DOC, SCI_LINEFROMPOSITION, cur_pos);
             //int curLine  = GetCurrentLineNumber();
             int line_length  =  call(CURRENT_DOC, SCI_LINELENGTH, cur_line);

             //Platform::DebugPrintf("[CR] %d len = %d\n", curLine, lineLength);
             if  (cur_line  >  0  &&  line_length  <=  2)
             {
                 int  prev_line_length  = call(CURRENT_DOC, SCI_LINELENGTH,  cur_line  -  1);
                 if  (prev_line_length  <  sizeof(linebuf))
                 {
                     int  buflen  =  sizeof(linebuf);
                     memcpy(linebuf,  &buflen,  sizeof(buflen));
                     call(CURRENT_DOC, SCI_GETLINE,  cur_line  -  1, reinterpret_cast<sptr_t>(linebuf));
                     linebuf[prev_line_length]  =  '\0';
                     for  (int  pos  =  0;  linebuf[pos];  pos++)  {
                          if  (linebuf[pos]  !=  ' '  &&  linebuf[pos]  !=  '\t')
                          linebuf[pos]  =  '\0';
                     }
                     call(CURRENT_DOC, SCI_REPLACESEL,  0, reinterpret_cast<sptr_t>(linebuf));
                 }
             }
        }
    }
    else
    {
        Q_UNUSED(pscn)
    }
}

void WidgetEditor::doc_mark_modified(int index, bool is_modified)
{
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    QString title = this->ui->m_tabs->tabText(index);

    if(is_modified)
    {
        if(!title.contains("+ "))
        {
            title = QString("+ %1").arg(title);
        }
    }
    else
    {
        title = title.remove("+ ");
    }
    this->ui->m_tabs->setTabText(index, title);
}


void WidgetEditor::set_link_words(QMap<QString, QString>& link_words)
{
    this->m_link_words = link_words;
}

QString WidgetEditor::get_link_words(void)
{
    QList<QString> words = m_link_words.keys();

    QString list;

    for(int i = 0; i < words.count(); i++)
    {
        list.append(words[i] + " ");
    }

    return list.trimmed();
}

QString WidgetEditor::get_link_category(const QString& word)
{
    if(m_link_words.end() != m_link_words.find(word))
    {
        return m_link_words[word];
    }

    return QString();
}

QString WidgetEditor::get_hot_spot_text(int pos)
{
    int style = call(CURRENT_DOC, SCI_GETSTYLEAT, pos);
    int max = call(CURRENT_DOC, SCI_GETLENGTH);

    // go up to get the right-most character with the style
    int i = pos;
    int new_style = style;
    int end = pos;

    while((style == new_style) && (i < max))
    {
       end = i;
       i += 1;
       new_style = call(CURRENT_DOC, SCI_GETSTYLEAT,i);
    }

    // go down to get left-most character with the style
    i = pos;
    new_style = style;
    int start = pos;

    while((style == new_style) && (i > -1))
    {
        start = i;
        i -= 1;
        new_style = call(CURRENT_DOC, SCI_GETSTYLEAT,i);
    }

    return QString(get_range(CURRENT_DOC, start, end+1));
}


void WidgetEditor::receive_command(uptr_t wParam, sptr_t lParam) {
    Q_UNUSED(wParam)
    Q_UNUSED(lParam)
/*
    int notifyCode = wParam >> 16;
    if ((notifyCode == SCEN_SETFOCUS) || (notifyCode == SCEN_KILLFOCUS)){
        call(SCI_SETINDICATORCURRENT, INDIC_CONTAINER);
        call(SCI_INDICATORCLEARRANGE, 0, call(SCI_GETLENGTH));

        call(SCI_MARKERADD, (int line, int markerNumber)

        call(SCI_SETWRAPMODE, call(SCI_GETWRAPMODE) ? SC_WRAP_NONE : SC_WRAP_WORD);

        if (notifyCode == SCEN_SETFOCUS)
            call(SCI_INDICATORFILLRANGE, 0, 2);
    }
*/
}

QString WidgetEditor::path_of(int index)
{
    if(index > this->ui->m_tabs->count())
    {
        return QString::null;
    }

    QString path = QString::null;

    if(index == CURRENT_DOC)
    {
        QWidget* widget = current_doc();
        if(widget)
        {
            path = widget->property("path").toString();
        }
    }
    else
    {
        path = this->ui->m_tabs->widget(index)->property("path").toString();
    }

    return path;
}

QString WidgetEditor::directory_of(int index)
{
    QString path = path_of(index);

    if(path.isNull())
    {
        return QString::null;
    }

    QFileInfo info(path);
    return info.absolutePath();
}

QString WidgetEditor::open_file()
{
    // Lookup the path of the last file that was saved
    QString last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
    if(last_opened.length() == 0)
    {
        last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
    }

    QString path = QFileDialog::getOpenFileName(
            this,
            QString("Open Script"),
            last_opened,
            QString("Scripts (*.py *.txt *.c *.h);;Text files (*.txt);;All files (*.*)"));

    if(path != QString::null)
    {
        CS_GUI_SET_GLOBAL_SETTING("path.last_opened", path);
        open_path(path);
        return path;
    }

    return QString::null;
}


QWidget* WidgetEditor::current_doc()
{
    return this->ui->m_tabs->currentWidget();
}

bool WidgetEditor::save_file()
{
    QString path = current_doc()->property("path").toString();
    QString saved_path = path;
    bool was_created = false;

    QDir tmp;
    if(!tmp.exists(path))
    {
        // Lookup the path of the last file that was saved
        QString last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
        if(last_saved.length() == 0)
        {
            last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
        }

        path = QFileDialog::getSaveFileName(
            this,
            "Save Script",
            last_saved,
            tr("Scripts (*.py *.txt *.c)"));

        if(path == QString::null)
        {
            return false;
        }

        CS_GUI_SET_GLOBAL_SETTING("path.last_saved", path);
        was_created = true;
    }

    if(path != saved_path)
    {
        current_doc()->setProperty("path", path);
    }

    // First save the watches so that we don't get an a popup
    // saying that the file has changed
    this->m_scripts_watcher->removePath(path);

    // DEBUG BRAD: Force the line endings to /r/n until
    // I figure out what is causing line endings save
    // problem.
    //call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CRLF);

    QFile file(path);
    if(!file.open(QIODevice::WriteOnly))
    {
        QMessageBox::warning(this, "Failed Saving Script File",
            QString("Failed saving %1").arg(path));
        return false;
    }

    QByteArray bytes = get_range(CURRENT_DOC, 0, -1);

    if(m_properties["EOLMODE"] == SC_EOL_LF)
    {
        /* Remove any \r characters */
        for(int i = 0; i < bytes.count(); i++)
        {
            if(bytes.at(i) == '\r')
            {
                bytes.remove(i, 1);
            }
        }
    }

    file.write(bytes);

    file.close();

    // Mark the document as unmodified since it was just saved
    call(CURRENT_DOC, SCI_SETSAVEPOINT);

    // Now, after updating the script restore the
    // watch list.
    this->m_scripts_watcher->addPath(path);

    if(was_created)
    {
        reopen_path(path);
    }

    return true;
}

bool WidgetEditor::save_file_as()
{
    QString path = current_doc()->property("path").toString();
    QString saved_path = path;

    QFileInfo info(path);

    // If the file doesn't exist then lookup the last
    // save directory.
    QString last_saved;
    if(!info.exists())
    {
        // Lookup the path of the last file that was saved
        last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
        if(last_saved.length() == 0)
        {
            last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
        }
    }
    else
    {
        last_saved = info.filePath();
    }

    path = QFileDialog::getSaveFileName(
        this,
        "Save Script",
        last_saved,
        tr("Scripts (*.py *.txt *.c)"));

    if(path == QString::null)
    {
        return false;
    }

    CS_GUI_SET_GLOBAL_SETTING("path.last_saved", path);

    // First save the watches so that we don't get an a popup
    // saying that the file has changed
    this->m_scripts_watcher->removePath(path);

    current_doc()->setProperty("path", path);

    QFile file(path);
    if(!file.open(QIODevice::WriteOnly))
    {
        QMessageBox::warning(this, "Failed Saving Script File",
            QString("Failed saving %1").arg(path));
        return false;
    }

    // DEBUG BRAD: Force the line endings to /r/n until
    // I figure out what is causing line endings save
    // problem.
    //call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CRLF);

    QByteArray bytes = get_range(CURRENT_DOC, 0, -1);

    if(m_properties["EOLMODE"] == SC_EOL_LF)
    {
        /* Remove any \r characters */
        for(int i = 0; i < bytes.count(); i++)
        {
            if(bytes.at(i) == '\r')
            {
                bytes.remove(i, 1);
            }
        }
    }

    file.write(bytes);

    file.close();

    // Mark the document as unmodified since it was just saved
    call(CURRENT_DOC, SCI_SETSAVEPOINT);

    // Now, after updating the script restore the
    // watch list.
    this->m_scripts_watcher->addPath(path);

    reopen_path(path);

    return true;
}


void WidgetEditor::open_path(const QString& path)
{
    QFileInfo info(path);

    m_scripts_watcher->addPath(path);

    /* Check to see if the path is already open and if it is then
     * activate that tab */
    for(int i = 0; i < this->ui->m_tabs->count(); i++)
    {
        if(path == this->ui->m_tabs->widget(i)->property("path"))
        {
            this->ui->m_tabs->setCurrentIndex(i);
            return;
        }
    }

    int index = create_document(info.fileName());

    this->ui->m_tabs->setCurrentIndex(index);
    this->ui->m_tabs->currentWidget()->setProperty("path", path);

    call(CURRENT_DOC, SCI_CLEARALL);
    QFile file(path);
    file.open(QIODevice::ReadOnly);
    QByteArray contents = file.readAll();
    call(CURRENT_DOC, SCI_ADDTEXT, contents.length(), reinterpret_cast<sptr_t>(contents.data()));

    if(m_properties["EOLMODE"] == SC_EOL_LF)
    {
        // Convert to Unix line endings for consistency
        call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_LF);
    }
    else
    {
        // Convert to Windows line endings for consistency
        call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CRLF);
    }

    call(CURRENT_DOC, SCI_COLOURISE, 0, -1);

    // Mark the document as unmodified since it was just opened
    call(CURRENT_DOC, SCI_SETSAVEPOINT);


}

void WidgetEditor::reopen_path(const QString& path)
{
    QFileInfo info(path);

    /* Check to see if the path is already open and if it is then
     * activate that tab */
    for(int i = 0; i < this->ui->m_tabs->count(); i++)
    {
        if(path == this->ui->m_tabs->widget(i)->property("path"))
        {
            QDir tmp;
            // Can't reload a document that doesn't exist
            if(!tmp.exists(path))
            {
                return;
            }

            this->ui->m_tabs->setCurrentIndex(i);

            // If the file is not modified then just reload it
            bool is_modified = call(CURRENT_DOC, SCI_GETMODIFY);
            if(is_modified)
            {
                if(QMessageBox::No == QMessageBox::question(this, "Document is modified",
                    "The document has been modified, do you want to discard the changes?", QMessageBox::Yes, QMessageBox::No))
                {
                    return;
                }
            }

            this->ui->m_tabs->setTabText(i, info.fileName());

            QString suffix = info.completeSuffix();
            int lexer = call(CURRENT_DOC, SCI_GETLEXER);
            if((lexer != SCLEX_PYTHON) && (suffix == "py" || suffix == "txt"))
            {
                setup_styles(SCLEX_PYTHON);
            }
            else if((lexer != SCLEX_CPP) && (suffix == "c" || suffix == "h"))
            {
                setup_styles(SCLEX_CPP);
            }
            else if((lexer != SCLEX_SHORTE) && (suffix == "tpl"))
            {
                setup_styles(SCLEX_SHORTE);
            }
            else
            {
                setup_styles(lexer);
            }

            call(CURRENT_DOC, SCI_CLEARALL);
            QFile file(path);
            file.open(QIODevice::ReadOnly);
            QByteArray contents = file.readAll();
            call(CURRENT_DOC, SCI_ADDTEXT, contents.length(), reinterpret_cast<sptr_t>(contents.data()));

            if(m_properties["EOLMODE"] == SC_EOL_LF)
            {
                // Convert to Unix line endings for consistency
                call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_LF);
            }
            else
            {
                // Convert to Windows line endings for consistency
                call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CRLF);
            }

            // Mark the document as unmodified since it was just opened
            call(CURRENT_DOC, SCI_SETSAVEPOINT);

            break;
        }
    }
}

QByteArray WidgetEditor::get_range(int index, int start, int end)
{
    if(end == -1)
    {
        end = call(index, SCI_GETTEXTLENGTH);
    }

    QByteArray bytes(end, 0);
    Sci_TextRange tr;
    tr.chrg.cpMin = start;
    tr.chrg.cpMax = end;
    tr.lpstrText = bytes.data();
    call(index, SCI_GETTEXTRANGE, 0, (sptr_t)&tr);
    return bytes;
}

void WidgetEditor::on_actionFind_Selection_triggered() {
    int selStart = call(CURRENT_DOC, SCI_GETSELECTIONSTART);
    int selEnd = call(CURRENT_DOC, SCI_GETSELECTIONEND);
    int lenDoc = call(CURRENT_DOC, SCI_GETLENGTH);

    const int indicatorHightlightCurrentWord = INDIC_CONTAINER;
    call(CURRENT_DOC, SCI_INDICSETSTYLE, indicatorHightlightCurrentWord, INDIC_ROUNDBOX);
    call(CURRENT_DOC, SCI_INDICSETFORE, indicatorHightlightCurrentWord, 0xff0000);
    call(CURRENT_DOC, SCI_SETINDICATORCURRENT, indicatorHightlightCurrentWord);
    call(CURRENT_DOC, SCI_INDICATORCLEARRANGE, 0, lenDoc);
    call(CURRENT_DOC, SCI_INDICATORFILLRANGE, selStart, selEnd - selStart);

    QByteArray wordToFind = get_range(CURRENT_DOC, selStart, selEnd);
    call(CURRENT_DOC, SCI_SETSEARCHFLAGS, 0);
    call(CURRENT_DOC, SCI_SETTARGETSTART, selEnd);
    call(CURRENT_DOC, SCI_SETTARGETEND, lenDoc);
    int indexOf = call(CURRENT_DOC, SCI_SEARCHINTARGET,
               wordToFind.length()-1, (sptr_t)wordToFind.data());
    if (indexOf < 0) {	// Wrap around
        call(CURRENT_DOC, SCI_SETTARGETSTART, 0);
        call(CURRENT_DOC, SCI_SETTARGETEND, selEnd);
        indexOf = call(CURRENT_DOC, SCI_SEARCHINTARGET,
                   wordToFind.length()-1, (sptr_t)wordToFind.data());
    }
    if (indexOf >= 0) {
        call(CURRENT_DOC, SCI_SETSELECTIONSTART, indexOf);
        call(CURRENT_DOC, SCI_SETSELECTIONEND, indexOf+(selEnd - selStart));
    }
}


bool WidgetEditor::find_text(const QString& text, int index, bool forward)
{
    const int indicatorHightlightCurrentWord = INDIC_CONTAINER;
    int lenDoc = call(index, SCI_GETLENGTH);

    if(lenDoc <= 0)
    {
        return false;
    }

    // Set the format of the selection
    call(index, SCI_INDICSETSTYLE, indicatorHightlightCurrentWord, INDIC_ROUNDBOX);
    call(index, SCI_INDICSETFORE, indicatorHightlightCurrentWord, 0xff0000);
    call(index, SCI_SETINDICATORCURRENT, indicatorHightlightCurrentWord);
    call(index, SCI_INDICATORCLEARRANGE, 0, lenDoc);

    // Start searching from the current cursor
    int cur_pos = call(index, SCI_GETCURRENTPOS);

    // Search from the current position to the end of the document
    if(forward)
    {
        call(index, SCI_SETTARGETSTART, cur_pos);
        call(index, SCI_SETTARGETEND,   lenDoc);
    }
    else
    {
        call(index, SCI_SETTARGETSTART, cur_pos-1);
        call(index, SCI_SETTARGETEND,   0);
    }

    // See if we can find the search string in that range
    int indexOf = call(index, SCI_SEARCHINTARGET,
               text.length(), (sptr_t)text.toStdString().c_str());

    // If it is found then highlight the section and jump to the
    // associated line number.
    if(indexOf >= 0)
    {
        const int line_number = call(CURRENT_DOC, SCI_LINEFROMPOSITION, indexOf, 0);
        goto_line(line_number, index);
        call(index, SCI_SETSELECTIONSTART, indexOf);
        call(index, SCI_SETSELECTIONEND, indexOf+text.length());
    }
    // If it wasn't found then try again at the beginning of the
    // document.
    else
    {
        // If no result was found try again from the beginning
        if(forward)
        {
            call(index, SCI_SETTARGETSTART, 0);
            call(index, SCI_SETTARGETEND, cur_pos);
        }
        else
        {
            call(index, SCI_SETTARGETSTART, lenDoc);
            call(index, SCI_SETTARGETEND,   cur_pos);
        }

        int indexOf = call(index, SCI_SEARCHINTARGET,
                   text.length(), (sptr_t)text.toStdString().c_str());

        if(indexOf >= 0)
        {
            const int line_number = call(CURRENT_DOC, SCI_LINEFROMPOSITION, indexOf, 0);
            goto_line(line_number, index);
            call(index, SCI_SETSELECTIONSTART, indexOf);
            call(index, SCI_SETSELECTIONEND, indexOf+text.length());
        }
        else
        {
            return false;
        }
    }

    return true;
}

void WidgetEditor::on_goto_line(int line)
{
    highlight_line(line, CURRENT_DOC);
}

void WidgetEditor::goto_line(int line, int index)
{
    line -= 1;
    call(index, SCI_ENSUREVISIBLEENFORCEPOLICY, line);
    call(index, SCI_GOTOLINE, line);
}

void WidgetEditor::clear_selections(int index)
{
    call(index, SCI_CLEARSELECTIONS);
}

void WidgetEditor::highlight_line(int line, int index)
{
    line -= 1;
    call(index, SCI_ENSUREVISIBLEENFORCEPOLICY, line);
    call(index, SCI_GOTOLINE, line);

    int start_of_line = call(index, SCI_POSITIONFROMLINE, line);
    int line_length = call(index, SCI_LINELENGTH, line);

    call(CURRENT_DOC, SCI_STYLESETFORE, SCI_STYLESETHOTSPOT, 0x0000ff);
    call(index, SCI_SETSEL, start_of_line, start_of_line+line_length);
}


/* XPM */
static const char * arrow_xpm[] = {
"12 12 3 1",
" 	c None",
".	c #000000",
"+	c #808080",
"            ",
"     .+     ",
"      .+    ",
"      +.+   ",
" ........+  ",
" .........+ ",
" .........+ ",
" ........+  ",
"      +.+   ",
"      .+    ",
"     .+     ",
"            "};

/* XPM */
static const char * box_xpm[] = {
"12 12 2 1",
" 	c None",
".	c #000000",
"   .........",
"  .   .   ..",
" .   .   . .",
".........  .",
".   .   .  .",
".   .   . ..",
".   .   .. .",
".........  .",
".   .   .  .",
".   .   . . ",
".   .   ..  ",
".........   "};

void WidgetEditor::autocomplete(void)
{
    const char *words = "Babylon-5?1 Battlestar-Galactica Millenium-Falcon?2 Moya?2 Serenity Voyager";
    call(CURRENT_DOC, SCI_AUTOCSETIGNORECASE, 1);
    call(CURRENT_DOC, SCI_REGISTERIMAGE, 1, (sptr_t)arrow_xpm);
    call(CURRENT_DOC, SCI_REGISTERIMAGE, 2, (sptr_t)box_xpm);
    call(CURRENT_DOC, SCI_AUTOCSHOW, 0, (sptr_t)words);
}

void WidgetEditor::set_wrap(void)
{
    call(CURRENT_DOC, SCI_SETWRAPMODE, call(CURRENT_DOC, SCI_GETWRAPMODE) ? SC_WRAP_NONE : SC_WRAP_WORD);
}

void WidgetEditor::on_m_tabs_tabCloseRequested(int index)
{
    bool is_modified = call(index, SCI_GETMODIFY);
    if(is_modified)
    {
         if(QMessageBox::No == QMessageBox::question(this, "Document is modified",
                    "The document has been modified, do you want to discard the changes?",
                    QMessageBox::Yes, QMessageBox::No))
         {
             return;
         }
    }

    close_document(index);
}

void WidgetEditor::close_document(int index)
{
    if(index == CURRENT_DOC)
    {
        for(int i = 0; i < this->ui->m_tabs->count(); i++)
        {
            if(this->ui->m_tabs->widget(i) == this->ui->m_tabs->currentWidget())
            {
                index = i;
                break;
            }
        }
    }

    if(index != -1)
    {
        return;
    }

    QString path = this->ui->m_tabs->widget(index)->property("path").toString();

    m_scripts_watcher->removePath(path);

    this->ui->m_tabs->removeTab(index);

/* DEBUG BRAD: Don't hide tabs for now if there is only one tab
    if(this->ui->m_tabs->count() > 1)
    {
        show_tab_bar(true);
    }
    else
    {
        show_tab_bar(false);
    }
*/
}

void WidgetEditor::close_document(const QString& path)
{
    for(int i = 0; i < this->ui->m_tabs->count(); i++)
    {
        QString tab_path = this->ui->m_tabs->widget(i)->property("path").toString();
        if(tab_path == path)
        {
            close_document(i);
            break;
        }
    }
}

bool WidgetEditor::is_open(const QString& path)
{
    // The tab has just the file name so we need to search for
    // the 'path' property associated with the tab containing the document.
    for(int i = 0; i < this->ui->m_tabs->count(); i++)
    {
        QString tab_path = this->ui->m_tabs->widget(i)->property("path").toString();
        if(tab_path == path)
        {
            return true;
        }
    }
    return false;
}

bool WidgetEditor::are_there_unsaved_changes(void)
{
    for(int index = 0; index < this->ui->m_tabs->count(); index++)
    {
        bool is_modified = call(index, SCI_GETMODIFY);

        if(is_modified)
        {
            return true;
        }
    }

    return false;
}

#include <QMimeData>
#include <QTemporaryFile>
#include <QNetworkReply>
#include "widgets/common/widgetfiledownloader.h"

void WidgetEditor::dropEvent(QDropEvent *event)
{
    const QMimeData* mimeData = event->mimeData();

    // check for our needed mime type, here a file or a list of files
    if (mimeData->hasUrls())
    {
        QStringList pathList;
        QList<QUrl> urlList = mimeData->urls();

        QTemporaryFile tmp;

        if(urlList.size() > 0)
        {
            QUrl url = urlList.at(0);
            QString url_path = url.toString();
            QString path;

            if(url_path.contains("http://"))
            {
                WidgetFileDownloader downloader(url, this);

                // Now wait for the file to be downloaded
                while(!downloader.is_finished())
                {
                    qApp->processEvents();
                }

                if(downloader.is_errored())
                {
                    return;
                }


                tmp.open();
                tmp.write(downloader.downloadedData());
                path = tmp.fileName();
            }
            else
            {
                path = url.toLocalFile();
            }

            bool allow_open = true;

            QFile file(path);
            file.open(QIODevice::ReadOnly);
            QByteArray contents = file.readAll();
            file.close();

            signal_intercept_drop(path, contents, allow_open);

            if(allow_open)
            {
                open_path(path);
            }
        }
    }
}


void WidgetEditor::clone(int index)
{
    QByteArray bytes = get_range(index, 0, -1);
    QString copy(bytes);

    create_document("Copy", copy);
}

void WidgetEditor::on_m_tabs_customContextMenuRequested(const QPoint &pos)
{
    QMenu* menu = new QMenu(ui->m_tabs);

    QMenu* submenu = menu->addMenu("Lexers");
    QAction* action_lexer_python = submenu->addAction("Python");
    QAction* action_lexer_cpp = submenu->addAction("C++");
    QAction* action_lexer_text = submenu->addAction("Text");
    QAction* action_lexer_html = submenu->addAction("HTML");
    QAction* action_lexer_shorte = submenu->addAction("Shorte");

    QAction* action_close_file = menu->addAction("Close File");
    QAction* action_close_all_files = menu->addAction("Close All Files");

    QAction* action_clone_file = menu->addAction("Clone File");
    QAction* action_reload_file = menu->addAction("Reload");
    QAction* action_copy_to_clipboard = menu->addAction("Copy File to Clipboard");


    QAction* action_open_in_file_browser = NULL;
    QAction* action_copy_path_to_clipboard = NULL;

    QString path = this->ui->m_tabs->currentWidget()->property("path").toString();
    QDir tmp;
    if(tmp.exists(path))
    {
#ifdef Q_OS_MAC
        action_open_in_file_browser = menu->addAction("Show in Finder");
#elif defined(Q_OS_WIN)
        action_open_in_file_browser = menu->addAction("Show in Explorer");
#else
        action_open_in_file_browser = menu->addAction("Show in File Browser");
#endif
        action_copy_path_to_clipboard = menu->addAction("Copy path to Clipboard");
    }

    QAction* action_tabs_to_spaces = menu->addAction("Convert Tabs to Spaces");

    QMenu* eol_menu = menu->addMenu("End of lines");

    QAction* action_show_eol = NULL;
    bool eol_visible = call(CURRENT_DOC, SCI_GETVIEWEOL);
    if(eol_visible)
    {
        action_show_eol = eol_menu->addAction("Hide end of lines");
    }
    else
    {
        action_show_eol = eol_menu->addAction("Show end of lines");
    }

    QAction* action_convert_eol_to_linux = eol_menu->addAction("Unix (\\n)");
    QAction* action_convert_eol_to_win   = eol_menu->addAction("Windows (\\r\\n)");
    QAction* action_convert_eol_to_mac   = eol_menu->addAction("Mac (\\r)");

    QAction* action_result = menu->exec(ui->m_tabs->mapToGlobal(pos));

    if(action_result == NULL)
    {
        delete menu;
        return;
    }

    if(action_result == action_lexer_python)
    {
        setup_styles(SCLEX_PYTHON);
    }
    else if(action_result == action_lexer_cpp)
    {
        setup_styles(SCLEX_CPP);
    }
    else if(action_result == action_lexer_text)
    {
        setup_styles(SCLEX_NULL);
    }
    else if(action_result == action_lexer_html)
    {
        setup_styles(SCLEX_HTML);
    }
    else if(action_result == action_lexer_shorte)
    {
        setup_styles(SCLEX_SHORTE);
    }
    else if(action_result == action_clone_file)
    {
        // Get a copy of the current file
        clone(CURRENT_DOC);
    }
    else if(action_result == action_copy_to_clipboard)
    {
        QClipboard *clipboard = QApplication::clipboard();
        clipboard->setText(get_text(), QClipboard::Clipboard);
    }
    else if(action_result == action_reload_file)
    {
        reload(CURRENT_DOC);
    }
    else if(action_result == action_show_eol)
    {
        call(CURRENT_DOC, SCI_SETVIEWEOL, !eol_visible);
    }
    // Convert line endings to \n
    else if(action_result == action_convert_eol_to_linux)
    {
        call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_LF);
        m_properties["EOLMODE"] = SC_EOL_LF;
    }
    // Convert line endings to \r
    else if(action_result == action_convert_eol_to_mac)
    {
        call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CR);
        m_properties["EOLMODE"] = SC_EOL_CR;
    }
    // Convert line endings to \r\n
    else if(action_result == action_convert_eol_to_win)
    {
        call(CURRENT_DOC, SCI_CONVERTEOLS, SC_EOL_CRLF);
        m_properties["EOLMODE"] = SC_EOL_CRLF;
    }
    // Open the file in Explorer
    else if(action_result == action_open_in_file_browser)
    {
#if defined(Q_OS_MAC)
        QStringList args;
            args << "-e";
            args << "tell application \"Finder\"";
            args << "-e";
            args << "activate";
            args << "-e";
            args << "select POSIX file \""+path+"\"";
            args << "-e";
            args << "end tell";
            QProcess::startDetached("osascript", args);
#elif defined(Q_OS_WIN)
        QStringList args;
        args << "/select," << QDir::toNativeSeparators(path);
        QProcess::startDetached("explorer", args);
#else
        QStringList args;

        QProcess process;
        process.start("xdg-mime query default inode/directory");
        bool finished = process.waitForFinished();
        if(finished)
        {
            QString data;
            data.append(process.readAll());

            args.clear();
            args << QDir::toNativeSeparators(path);

            if(data.contains("nautilus"))
            {
                QProcess::startDetached("nautilus", args);
            }
            else if(data.contains("thunar"))
            {
                QProcess::startDetached("thunar", args);
            }
            else if(data.contains("konqueror"))
            {
                QProcess::startDetached("konqueror", args);
            }
            else
            {
                finished = false;
            }
        }
        process.close();

        if(!finished)
        {
            QDesktopServices::openUrl(QUrl("file:///" + QDir::toNativeSeparators(path)));
        }
#endif
    }
    else if(action_result == action_copy_path_to_clipboard)
    {
        QClipboard *clipboard = QApplication::clipboard();
        clipboard->setText(path, QClipboard::Clipboard);
    }
    else if(action_result == action_tabs_to_spaces)
    {
        QString text = get_text();
        text = text.replace("\t", "    ");
        set_text(text);
    }
    else if(action_result == action_close_file)
    {
        on_m_tabs_tabCloseRequested();
    }
    else if(action_result == action_close_all_files)
    {
        while(this->ui->m_tabs->count())
        {
            on_m_tabs_tabCloseRequested();
        }
    }


    delete menu;
}

 bool WidgetEditor::is_modified(int index)
 {
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    bool is_modified = call(index, SCI_GETMODIFY);

    if(is_modified)
    {
        return true;
    }

    return false;
 }

void WidgetEditor::reload(int index)
{
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    QString path = this->ui->m_tabs->widget(index)->property("path").toString();

    reopen_path(path);
}

void WidgetEditor::undo(int index)
{
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    call(index, SCI_UNDO);
}

void WidgetEditor::redo(int index)
{
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    call(index, SCI_REDO);
}

QString WidgetEditor::doc_title(int index)
{
    if(index == CURRENT_DOC)
    {
        index = this->ui->m_tabs->currentIndex();
    }

    return this->ui->m_tabs->tabText(index);
}

void WidgetEditor::append_text(const QString& contents, int index)
{
    call(index, SCI_APPENDTEXT, contents.length(), reinterpret_cast<sptr_t>(contents.toStdString().c_str()));
}

void WidgetEditor::set_text(const QString& contents, int index)
{
    call(index, SCI_SETTEXT, contents.length(), reinterpret_cast<sptr_t>(contents.toStdString().c_str()));
}

void WidgetEditor::insert_text_at_cursor(const QString &contents, int index)
{
    call(index, SCI_INSERTTEXT, -1, reinterpret_cast<sptr_t>(contents.toStdString().c_str()));

    // Start searching from the current cursor
    int cur_pos = call(index, SCI_GETCURRENTPOS);
    cur_pos += contents.length() + 1;
    int line_number = call(CURRENT_DOC, SCI_LINEFROMPOSITION, cur_pos, 0);
    line_number += 1;

    goto_line(line_number, index);
}

QString WidgetEditor::get_text(int index)
{
    QByteArray bytes = get_range(index, 0, -1);

    return QString(bytes);
}

int WidgetEditor::count(void)
{
    return this->ui->m_tabs->count();
}

int WidgetEditor::current_index(void)
{
    return this->ui->m_tabs->currentIndex();
}

bool WidgetEditor::clear(int index)
{
    if(!is_modified(index))
    {
        call(index, SCI_CLEARALL);
        call(index, SCI_SETSAVEPOINT);
        return true;
    }
    else
    {
        if(QMessageBox::Yes == QMessageBox::question(this,
            "Discard Changes?",
            "Do you want to discard the changes you have made to this script?",
            QMessageBox::No, QMessageBox::Yes))
        {
            call(index, SCI_CLEARALL);
            //call(index, SCI_SETSAVEPOINT);
            return true;
        }

    }

    return false;
}

bool WidgetEditor::clear_no_warning(int index)
{
    call(index, SCI_CLEARALL);
    return true;
}


void WidgetEditor::set_lexer(int lexer, int index)
{
    setup_styles(lexer, index);
}

void WidgetEditor::open_in_file_browser(const QString& path)
{
#ifdef Q_OS_MAC
        QStringList args;
            args << "-e";
            args << "tell application \"Finder\"";
            args << "-e";
            args << "activate";
            args << "-e";
            args << "select POSIX file \""+path+"\"";
            args << "-e";
            args << "end tell";
            QProcess::startDetached("osascript", args);
#else
        QStringList args;
        args << "/select," << QDir::toNativeSeparators(path);
        QProcess::startDetached("explorer", args);
#endif
}

void WidgetEditor::on_find_next(const QString& text)
{
    find_text(text, CURRENT_DOC, true);
}

void WidgetEditor::on_find_last(const QString& text)
{
    find_text(text, CURRENT_DOC, false);
}

void WidgetEditor::on_find_replace(
    const QString& search_text,
    const QString& replace_text,
    bool replace_forward,
    bool replace_all)
{
    while(find_text(search_text, CURRENT_DOC, replace_forward))
    {
        call(CURRENT_DOC, SCI_REPLACESEL,
               search_text.length(), (sptr_t)replace_text.toStdString().c_str());

        if(!replace_all)
        {
            break;
        }
    }
}

void WidgetEditor::on_close_tools_panel(void)
{
    this->ui->m_tools_panel->setVisible(false);
}

void WidgetEditor::show_tools_panel(bool show)
{
    this->ui->m_tools_panel->setVisible(show);
}

void WidgetEditor::unsplit(int index)
{

}

void WidgetEditor::split(int document_index)
{
    ScintillaEditBase* sci = NULL;

    if(document_index != CURRENT_DOC)
    {
        sci = (ScintillaEditBase*)this->ui->m_tabs->widget(document_index);
    }
    else
    {
        sci = (ScintillaEditBase*)this->ui->m_tabs->currentWidget();
    }
}

void WidgetEditor::on_m_button_split_clicked()
{
    QSplitter* splitter = NULL;

    splitter = (QSplitter*)this->ui->m_tabs->currentWidget();

    if(splitter == NULL)
    {
        return;
    }

    ScintillaEditBase *sci = (ScintillaEditBase*)splitter->widget(0);
    void* ptr = (void*)sci->send(SCI_GETDOCPOINTER, 0, 0);

    // Create the new split
    sci = new ScintillaEditBase(this);
    sci->send(SCI_SETDOCPOINTER, 0, (sptr_t)ptr);

    splitter->addWidget(sci);
    splitter->setOrientation(Qt::Vertical);

    /* Set common styles */
    call(CURRENT_DOC, SCI_STYLESETFONT, STYLE_DEFAULT , (sptr_t)"Courier New");
    call(CURRENT_DOC, SCI_STYLESETSIZE, STYLE_DEFAULT , 10);
    /* Apply the default styles */
    call(CURRENT_DOC, SCI_STYLECLEARALL);
    call(CURRENT_DOC, SCI_SETEOLMODE, m_properties["EOLMODE"].toInt());
    setup_styles(SCLEX_SHORTE);

    //call(CURRENT_DOC, SCI_INSERTTEXT, 0, (sptr_t)(void *)init_data.toStdString().c_str());

    //ui->actionLatin_1->setChecked(true);

    connect(sci, SIGNAL(notify(SCNotification *)), this, SLOT(receive_notify(SCNotification *)));
    connect(sci, SIGNAL(command(uptr_t, sptr_t)), this, SLOT(receive_command(uptr_t, sptr_t)));
}

void WidgetEditor::on_m_button_unsplit_clicked()
{
    QSplitter* splitter = (QSplitter*)this->ui->m_tabs->currentWidget();

    if(splitter == NULL)
    {
        return;
    }

    // Don't allow removing the base editor widget. Only remove
    // splits.
    if(splitter->count() > 1)
    {
        ScintillaEditBase* sci = (ScintillaEditBase*)splitter->widget(splitter->count() - 1);
        delete sci;
    }
}

void WidgetEditor::on_m_button_split_horizontal_clicked()
{
    QSplitter* splitter = NULL;

    splitter = (QSplitter*)this->ui->m_tabs->currentWidget();

    if(splitter == NULL)
    {
        return;
    }

    ScintillaEditBase *sci = (ScintillaEditBase*)splitter->widget(0);
    void* ptr = (void*)sci->send(SCI_GETDOCPOINTER, 0, 0);

    // Create the new split
    sci = new ScintillaEditBase(this);
    sci->send(SCI_SETDOCPOINTER, 0, (sptr_t)ptr);

    splitter->addWidget(sci);
    splitter->setOrientation(Qt::Horizontal);

    /* Set common styles */
    call(CURRENT_DOC, SCI_STYLESETFONT, STYLE_DEFAULT , (sptr_t)"Courier New");
    call(CURRENT_DOC, SCI_STYLESETSIZE, STYLE_DEFAULT , 10);
    /* Apply the default styles */
    call(CURRENT_DOC, SCI_STYLECLEARALL);
    call(CURRENT_DOC, SCI_SETEOLMODE, m_properties["EOLMODE"].toInt());
    setup_styles(SCLEX_SHORTE);

    //call(CURRENT_DOC, SCI_INSERTTEXT, 0, (sptr_t)(void *)init_data.toStdString().c_str());

    //ui->actionLatin_1->setChecked(true);

    connect(sci, SIGNAL(notify(SCNotification *)), this, SLOT(receive_notify(SCNotification *)));
    connect(sci, SIGNAL(command(uptr_t, sptr_t)), this, SLOT(receive_command(uptr_t, sptr_t)));
}
