#ifndef WIDGETFINDPANEL_H
#define WIDGETFINDPANEL_H

#include <QWidget>

namespace Ui {
class WidgetFindPanel;
}

class WidgetFindPanel : public QWidget
{
    Q_OBJECT
    
public:
    explicit WidgetFindPanel(QWidget *parent = 0);
    ~WidgetFindPanel();

    void show_close_button(bool allow);
    
signals:
    /**
     * This signal is emitted when the user presses
     * the Find Next button.
     */
    void signal_text_entered(const QString&);

    /**
     * This signal is emitted when the user presses
     * the Find Last button.
     */
    void signal_find_last(const QString&);

    /**
     * This signal is emitted when the user presses
     * one of the replace buttons.
     */
    void signal_replace(const QString&,const QString&, bool, bool);

    /**
     * This signal is emitted when the user presses
     * the Close button.
     */
    void signal_close_panel(void);


public slots:
    void on_activate(const QString& text);

private slots:
    /**
     * This slot is called when the user presses
     * <Enter> in the find text entry to find the
     * next entry.
     */
    void on_m_edit_find_returnPressed();

    /**
     * This slot is called when the user presses
     * the Find Next button to find the next occurrence
     * of the selected text.
     */
    void on_m_button_find_clicked();

    /**
     * This slot is called when the user presses
     * the close button to close the panel.
     */
    void on_m_button_close_clicked();

    /**
     * This slot is called when the user presses the
     * Find Last button to find the last occurrance of
     * the selected text.
     */
    void on_m_button_find_last_clicked();

    /**
     * This method is called when the user selects
     * an item from the history list in order to
     * search for it.
     *
     * @param arg1
     */
    void on_m_combo_history_activated(const QString &arg1);

    void on_m_replace_clicked();

    void on_m_replace_all_clicked();

private:

    /**
     * Add an item to the list of seaches that have been
     * performed. Only 10 are remembered.
     *
     * @param item [I] - The item to add to the list.
     */
    void add_to_history(const QString& item);

    /**
     * The size of the history list
     */
    int m_history_size;

    Ui::WidgetFindPanel *ui;
};

#endif // WIDGETFINDPANEL_H
