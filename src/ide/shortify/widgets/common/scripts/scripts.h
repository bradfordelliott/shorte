#ifndef SCRIPTS_H
#define SCRIPTS_H

#include <QWidget>
#include <QString>
#include <QFileSystemWatcher>
#include "gui_defines.h"
#include "controllers/cs_device_interface.h"
namespace Ui {
    class Scripts;
}

class Scripts : public QWidget
{
    Q_OBJECT

public:
    explicit Scripts(
        e_cs_chip_id chip,
        QWidget *parent = 0);
    ~Scripts();

    /**
     * This method is called to add text to a script. It can create a new
     * script if requested and also run the script.
     *
     * @param lines      [I] - The lines of text to add to the script.
     * @param create_new [I] - true if a new script should be created or false
     *                         if the text should be added to the current
     *                         script.
     * @param run        [I] - CS_GUI_SCRIPT_RUN_PYTHON, CS_GUI_SCRIPT_RUN_C,
     *                         if the script should be run.
     *
     * @return true if the text was added or false otherwise.
     */
    bool add_script_text(const QString& lines, bool create_new=false, int run=0);

    /**
     * This method is called to open a script by path.
     *
     * @param path [I] - The path to the script to open.
     *
     * @return true if the script was loaded correctly and false otherwise.
     */
    bool load_script(QString path);

private slots:
    void on_button_open_clicked();

    void on_m_button_scripts_library_clicked();

    void on_m_button_refresh_clicked();

    void on_m_button_save_script_clicked();

    void on_m_button_save_as_clicked();

    void on_m_button_save_log_clicked();

    void on_m_button_run_c_clicked();

    void on_m_button_send_clicked();

    void on_m_button_new_script_clicked();

    void on_m_button_clear_log_clicked();

    void on_m_button_run_python_clicked();

    void on_open_script(QString& path);

    void on_m_button_clear_clicked();

    void on_m_button_undo_clicked();

    void on_m_script_input_highlighted(const QUrl &arg1);

    void on_m_script_input_cursorPositionChanged();

    void on_open_link(const QString& link);

    void on_find_activate(const QString& current_word);
    void on_find_text_entered(const QString& text);
    void on_find_last(const QString& text);
    void on_find_close_panel();
    void on_goto_line(int line, const QString& path);

    // Called when the current doc is changed to
    // track the change in the tab title
    void on_current_doc_changed(void);

    void on_m_tab_scripts_tabCloseRequested(int index);

    void on_toolButton_clicked();

    void on_m_button_find_clicked();

    /**
     * Called when the user selects an option from the
     * drop down menu associated with the new button.
     *
     * @param action [I] - The action associated with
     *                     the button.
     */
    void on_new_script_action(QAction* action);

    void on_pushButton_clicked();

    /**
     * This method is called when the page slider changes
     * in order to switch between the text and HTML views.
     * @param value
     */
    void on_m_page_slider_valueChanged(int value);

    /**
     * This action is called when the user clicks on the
     * "Archive" button in the scripts tab to save the results
     * to disk or copy them to clipboard.
     *
     * @param action [I] - The action from the drop down menu.
     */
    void on_archive_output_action(QAction* action);

    void on_spacer_clicked();

    void on_comboBox_activated(const QString &arg1);

    void on_m_combo_shorte_templates_activated(const QString &arg1);

    /**
     * This method is called to support the dropdown menu
     * next to the run button in order to handle the actions in that menu.
     *
     * @param action [I] - The action from the run dropdown
     *                     menu.
     */
    void on_run_advanced(QAction* action);

    /**
     * This method is called to support the dropdown menu
     * next to the compile button in order to handle the actions in that menu.
     *
     * @param action [I] - The action from the compile dropdown
     *                     menu.
     */
    void on_compile_advanced(QAction* action);

    void on_m_button_goto_clicked();

protected:
      bool event ( QEvent * event );

private:

    /**
     * This method is called to save a register dump to file.
     *
     * @param input_path [I] - The path to save the register dump to.
     *
     * @return true on success, false on failure.
     */
    bool save_registers(const QString& input_path);

    /**
     * This method is called to save the log file from running
     * a script to file.
     *
     * @param input_path [I] - The path to save the log file to.
     *
     * @return true on success, false on failure.
     */
    bool save_log(const QString& path = "");

    /**
     * Get the index of the currently selected document.
     *
     * @return The index of the document
     */
    int current_doc();

    /**
     * This method is called to open a new tab with an existing document
     * or the contents of a new document.
     *
     * @param path     [I] - The path to the document to create or open
     * @param contents [I] - The contents of the document
     * @param type     [I] - The language type of the document.
     */
    void create_document_in_tab(
        const QString&   path,
        const QString&   contents,
        e_cs_script_type type=CS_SCRIPT_TYPE_C);

    /**
     * This method is called to determine if a particular script is
     * currently open in the editor or not.
     *
     * @param path [I] - The path to the script to check.
     *
     * @return TRUE if the script is open or FALSE otherwise.
     */
    bool is_script_open(const QString& path);

    /**
     * This method is called to determine if the script at 'index'
     *is currently modified or not.
     *
     * @param index [I] - The index of the script (or -1 for current
     *                    document.
     *
     * @return true if the document is modified, false otherwise.
     */
    bool check_modified(int index=-1);

    /**
     * This method is called to close a document by path instead of
     * by selected tab. This is called by the advanced run dialog
     * to close scripts after they are executed.
     *
     * @param path [I] - The path of the script to close.
     */
    void close_tab(const QString& path);


    void current_doc_mark_modified(bool is_modified);
    void doc_mark_modified(int index, bool is_modified);

    /**
     * Retrieve the title of the current document.
     *
     * @return The title of the current document.
     */
    QString current_doc_title(void);


    bool m_has_python_support;
    bool m_has_c_support;

    e_cs_chip_id m_chip;
    Ui::Scripts *ui;
    QFileSystemWatcher* m_scripts_watcher;
    QString m_last_path;

    /** The run dropdown menu */
    class QMenu* m_menu_run_advanced;
    /** The compile dropdown menu */
    class QMenu* m_menu_compile_advanced;

    /** The archive output drop down menu */
    class QMenu* m_menu_archive_output;

    /** The scripts library dialog */
    class DialogScriptsLibrary* m_dialog_scripts_library;

    /** The advanced run dialog - allows script arguments or groups of scripts */
    class DialogRunAdvanced* m_run_advanced;

    /** The find panel */
    class WidgetFindPanel* m_widget_find;

    /** The goto panel */
    class WidgetGotoPanel* m_widget_goto;
};

#endif // SCRIPTS_H
