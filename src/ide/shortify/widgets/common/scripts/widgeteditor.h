#ifndef WIDGETEDITOR_H
#define WIDGETEDITOR_H

#include <QWidget>
#include <QMap>
#include <QString>
#include <QByteArray>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QDragLeaveEvent>
#include <QDropEvent>

#include "Scintilla.h"
#include "gui_types.h"

namespace Ui {
class WidgetEditor;
}

class WidgetEditor : public QWidget
{
    Q_OBJECT
    
public:
    /**
     * Constructor for the editor
     *
     * @param allow_tabs [I] - Allow or disallow the tabs to
     *                         be drawn.
     * @param parent     [I] - The parent widt.
     */
    explicit WidgetEditor(bool allow_tabs=true, QWidget *parent = 0);
    ~WidgetEditor();

    /**
     * This method is called to show or hide the tab bar in the
     * editor. This might be useful when there is only a single
     * tab to display.
     *
     * @param show [I] - true to show the tabs or false to hide them.
     */
    void show_tab_bar(bool show);

    /**
     * This method is called to show or hide whitespace characters
     *
     * @param show  [I] - true to show whitespace or false to hide it.
     * @param index [I] - The index of the document to change.
     */
    void show_whitespace(bool show, int index);


    /**
     * Create a new document in the editor and return its index.
     *
     * @param title    [I] - The title to assign to the document.
     * @param contents [I] - The initial contents of the document.
     * @param type     [I] - The type of the script being created.
     *
     *
     * @return The index of the created document.
     */
    int create_document(const QString& title="No Name", const QString& contents="", e_cs_script_type type=CS_SCRIPT_TYPE_C);

    /**
     * Pop up the open file dialog to open a script from disk.
     *
     * @return The path to the file that was opened. If the
     *         operation was cancelled then QString::null is returned.
     */
    QString open_file();

    /**
     * Navigate to the specified line in the current document.
     *
     * @param line [I] - The line to navigate to
     */
    void goto_line(int line, int index=CURRENT_DOC);

    /** Not implemented yet */
    void autocomplete(void);

    /** Not implemented yet */
    void set_wrap(void);

    /**
     * Check to see if there are any unsaved changes in
     * any of the open scripts.
     *
     * @return true if there are unsaved changes and false if
     *         nothing is modified.
     */
    bool are_there_unsaved_changes(void);

    /**
     * Close the specified document.
     *
     * @param index [I] - the index of the document to close.
     */
    void close_document(int index);

    /**
     * Close a document based on it's current tab label
     * which is the file name part of the path.
     * @param name [I] - The name of the file displayed in the
     *                   editor tab.
     */
    void close_document(const QString& name);

    /**
     * This method is called to highlight a particular line
     * within the editor for purposes such as displaying
     * syntax errors.
     *
     * @param line  [I] - The line in the document to highlight
     * @param index [I] - The index of the document to target
     */
    void highlight_line(int line, int index=CURRENT_DOC);

    void clear_selections(int index=CURRENT_DOC);

    void reload(int index=CURRENT_DOC);
    void undo(int index=CURRENT_DOC);
    void redo(int index=CURRENT_DOC);
    int count(void);
    int current_index(void);
    bool clear(int index=CURRENT_DOC);
    bool clear_no_warning(int index=CURRENT_DOC);

    /**
     * This method is called to find a particular string within
     * the selected document. It starts from the current position and
     * wraps around to the beginning if it is not found.
     *
     * @param text    [I] - The text to search for.
     * @param index   [I] - The index of the document to search within.
     * @param forward [I] - true to search forward in the document, falst
     *                      to search backward.
     */
    void find_text(const QString& text, int index=CURRENT_DOC, bool forward=true);

    QString doc_title(int index=CURRENT_DOC);
    void append_text(const QString& contents, int index=CURRENT_DOC);
    void set_text(const QString& contents, int index=CURRENT_DOC);
    void insert_text_at_cursor(const QString& contents, int index=CURRENT_DOC);

    QString get_text(int index=CURRENT_DOC);

    sptr_t call(int doc_index, unsigned int iMessage, uptr_t wParam=0, sptr_t lParam=0);
    void define_marker(int document_index, int marker, int markerType, int fore, int back);
    QByteArray get_range(int doc_index=CURRENT_DOC, int start=0, int end=-1);

    // Setup the list of hyperlinked words
    void set_link_words(QMap<QString, QString>& link_words);

    // Get the list of hyperlinked words
    QString get_link_words(void);

    void open_path(const QString& path);
    void reopen_path(const QString& path);

    /**
     * This method searches through the list of open documents
     * to see if a document with the specified path is open.
     *
     * @param path [I] - The path of the document to search for.
     *
     * @return true if the document is currently open, false if it is not.
     */
    bool is_open(const QString& path);

    bool save_file();
    bool save_file_as();
    void clone(int index);

    bool is_modified(int index=CURRENT_DOC);

    void set_lexer(int lexer, int index=CURRENT_DOC);

    QString get_link_category(const QString& word);

    // Get the directory of the document
    QString directory_of(int index=CURRENT_DOC);
    QString path_of(int index=CURRENT_DOC);


signals:
    void signal_hotspot_activated(const QString& text);
    void signal_intercept_drop(const QString& path, const QString& data, bool& allow_open);

protected:
    void dragEnterEvent(QDragEnterEvent *event)
    {
       event->accept();
    }

    void dragMoveEvent(QDragMoveEvent *event)
    {
       event->accept();
    }

    void dragLeaveEvent(QDragLeaveEvent *event)
    {
       event->accept();
    }

    void dropEvent(QDropEvent *event);

private slots:
    void receive_notify(Scintilla::SCNotification *pscn);
    void receive_command(uptr_t wParam, sptr_t lParam);
    void on_actionFind_Selection_triggered();

    void on_m_tabs_tabCloseRequested(int index);

    void on_script_changed(const QString& path);

    void on_m_tabs_customContextMenuRequested(const QPoint &pos);

private:
    void load_lexer_styles(int index, const QString& lexer_prefix, int num_styles);

    enum
    {
        CURRENT_DOC = -1
    }e_editor_types;

    void setup_styles(int lexer, int index=CURRENT_DOC);

    QString get_hot_spot_text(int pos);
    void doc_mark_modified(int index, bool is_modified);

    /** Return a pointer to the currently active document */
    QWidget* current_doc();

    // The list of links to mark as hyperlinks
    QMap<QString, QString> m_link_words;

    class QFileSystemWatcher* m_scripts_watcher;

    Ui::WidgetEditor *ui;

    // Whether or not the editor allows tabs
    bool m_allow_tabs;

};

#endif // WIDGETEDITOR_H
