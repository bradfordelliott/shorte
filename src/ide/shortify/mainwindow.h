#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    void init(void);

private slots:
    void on_pushButton_clicked();

    void on_m_combo_element_type_activated(const QString &arg1);

    void on_m_button_run_clicked();

    void on_m_button_clear_clicked();

    void on_m_button_open_clicked();

    void on_m_button_save_clicked();

    void on_action_edit_settings();

    void on_action_find();

private:
    QString convert_output_to_html(const QString& input);

    Ui::MainWindow *ui;
};

#endif // MAINWINDOW_H
