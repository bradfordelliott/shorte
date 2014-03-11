#ifndef WIDGETTOOLSPANEL_H
#define WIDGETTOOLSPANEL_H

#include <QWidget>
#include <QMap>

namespace Ui {
class WidgetToolsPanel;
}

class WidgetToolsPanel : public QWidget
{
    Q_OBJECT

public:
    explicit WidgetToolsPanel(QWidget *parent = 0);
    ~WidgetToolsPanel();

    void add_page(const QString& label, QWidget* widget);
    void set_page(const QString& label);

signals:
    /**
     * This signal is emitted when the user presses
     * the Close button.
     */
    void signal_close_panel(void);

private slots:
    void on_m_button_close_clicked();

private:
    Ui::WidgetToolsPanel *ui;

    QMap<QString, int> m_page_index;
};

#endif // WIDGETTOOLSPANEL_H
