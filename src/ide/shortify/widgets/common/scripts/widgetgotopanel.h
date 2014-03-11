#ifndef WIDGETGOTOPANEL_H
#define WIDGETGOTOPANEL_H

#include <QWidget>

namespace Ui {
class WidgetGotoPanel;
}

class WidgetGotoPanel : public QWidget
{
    Q_OBJECT

signals:
    void signal_go_to_line(int line_number, const QString& path);

public:
    explicit WidgetGotoPanel(QWidget *parent = 0);
    ~WidgetGotoPanel();

private slots:
    void on_m_button_go_to_clicked();

private:
    Ui::WidgetGotoPanel *ui;
};

#endif // WIDGETGOTOPANEL_H
