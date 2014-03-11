#ifndef DIALOGRUNADVANCED_H
#define DIALOGRUNADVANCED_H

#include <QDialog>
#include <QTreeWidgetItem>
namespace Ui {
class DialogRunAdvanced;
}

class DialogRunAdvanced : public QDialog
{
    Q_OBJECT
    
public:
    explicit DialogRunAdvanced(QWidget *parent = 0);
    ~DialogRunAdvanced();

    int count();
    bool get(
        int      index,
        QString& path_script,
        QString& args,
        QString& path_output,
        QString& path_registers);

    bool close_when_finished();
    bool halt_on_error();
    
private slots:
    void on_m_button_add_script_clicked();

    void on_m_button_move_up_clicked();

    void on_m_button_move_down_clicked();

    void on_m_button_cancel_clicked();

    void on_m_button_run_clicked();

    void on_m_tree_script_list_itemActivated(QTreeWidgetItem *item, int column);

    void on_m_tree_script_list_itemSelectionChanged();

    /**
     * This slot is called when the user presses the "Remove Script" button
     * to remove a script from the execution list.
     */
    void on_m_button_remove_script_clicked();

    /**
     * This slot is called when the user presses the "Save Suite" button
     * to load a list of scripts to execute.
     */
    void on_m_button_save_suite_clicked();

    /**
     * This slot is called when the users presses the "Load Suite" button
     * to load a list of scripts to execute.
     */
    void on_m_button_load_suite_clicked();

private:
    Ui::DialogRunAdvanced *ui;
};

#endif // DIALOGRUNADVANCED_H
