#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "widgets/common/settings/settingsmanager.h"
#include "widgets/common/scripts/widgeteditor.h"
#include "gui_types.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

#include <QMessageBox>
SettingsManager* g_settings = NULL;

QString CS_GUI_GET_GLOBAL_SETTING(const QString& key)
{
    return g_settings->get(key);
}

void CS_GUI_SET_GLOBAL_SETTING(const QString& key, const QString& data)
{
    g_settings->set(key, data);
}

void MainWindow::init(void)
{
    g_settings = new SettingsManager();
    g_settings->load("settings.db");

    this->setStyleSheet(CS_GUI_GET_GLOBAL_SETTING("theme.main_content_stylesheet"));

    QMenu* menu_file = this->ui->menuBar->addMenu("File");
    QMenu* menu_edit = this->ui->menuBar->addMenu("Edit");

    menu_edit->addAction("Settings", this, SLOT( on_action_edit_settings()));

    for(int i = 0; i < this->ui->widget->count(); i++)
    {
        QString stylesheet = this->ui->widget->get_tabs()->widget(i)->styleSheet();
        stylesheet = CS_GUI_GET_GLOBAL_SETTING("theme.main_tab_content_stylesheet") + stylesheet;
        this->ui->widget->get_tabs()->widget(i)->setStyleSheet(stylesheet);
    }

    menu_edit->addAction("Find", this, SLOT(on_action_find()));

    //QMessageBox::information(this, "Default Chip", g_settings->get("default.chip"));

    on_pushButton_clicked();
    this->setWindowState(this->windowState() ^ Qt::WindowMaximized);

    QList<int> sizes;
    int height = this->ui->splitter->height();

    sizes.append(height * 0.80);
    sizes.append(height * 0.20);

    this->ui->splitter->setSizes(sizes);
    this->ui->widget->show_tools_panel(false);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_pushButton_clicked()
{
    ui->widget->show_tab_bar(true);
    ui->widget->create_document("New Document", "", CS_SCRIPT_TYPE_SHORTE);

    on_m_combo_element_type_activated("Page Header");
}

void MainWindow::on_m_combo_element_type_activated(const QString &arg1)
{
    if(arg1 == "Page Header")
    {
        ui->widget->insert_text_at_cursor("@doctitle My Title\n@docsubtitle My Subtitle\n@docversion 1.0\n@docauthor My Name\n@docrevisions\n-Revision | Date | Description\n-1.0 | Today | ...\n\n@body\n");
    }
    else if(arg1 == "Heading")
    {
        ui->widget->insert_text_at_cursor("@h1 ...\n\n");
    }
    else if(arg1 == "Table")
    {
        ui->widget->insert_text_at_cursor("@table\n- header1 | header21\n- data1 | data2\n\n");
    }
    else if(arg1 == "Paragraph")
    {
        ui->widget->insert_text_at_cursor("@text\n...\n\n");
    }
    else if(arg1 == "List (ordered)")
    {
        ui->widget->insert_text_at_cursor("@ol\n- one\n    - two\n");
    }
    else if(arg1 == "List (unordered)")
    {
        ui->widget->insert_text_at_cursor("@ul\n- one\n    - two\n");
    }
    else if(arg1 == "Prototype")
    {
        ui->widget->insert_text_at_cursor(
"@h3 my_function2\n"
"@prototype:\n"
"-- function: my_function2\n"
"-- description:\n"
"    This is a description of my function with some more text.\n"
"-- prototype:\n"
"    cs_status my_function2(int val1 [], int val2 [][5]);\n"
"-- returns:\n"
"    TRUE on success, FALSE on failure\n"
"-- params:\n"
"-- val1 | I |\n"
"        blah blah\n"
"        @{table\n"
"        - one\n"
"        - two}\n"
"-- val2 | I |\n"
"        - *1* = blah blah\n"
"        - *2* - blah @{b,bold}\n\n");
    }
}

#include <QTemporaryFile>
#include <QDir>
#include <QTextStream>
#include <QProcess>

QString MainWindow::convert_output_to_html(const QString& input)
{
    QString output;

    output = input;
    output.replace("\n", "<br/>");
    output.replace("[91m", "<span style='color:red'>");
    output.replace("[93m", "<span style='color:orange'>");

    output.replace("[0m", "</span>");

    return output;
}

void MainWindow::on_m_button_run_clicked()
{
    QTemporaryFile* tmp = new QTemporaryFile(QString("%1/xxxx.tpl").arg(QDir::tempPath()));
    tmp->open();
    QString path_input = tmp->fileName();

    QTextStream stream(tmp);
    stream << this->ui->widget->get_text();
    stream.flush();

    QString package = this->ui->m_combo_package->currentText();
    QString theme = this->ui->m_combo_theme->currentText();

    QString working_directory = QApplication::applicationDirPath();
    if(this->ui->m_working_directory->text().length() > 0)
    {
        working_directory = this->ui->m_working_directory->text();
    }

    QString output_directory = working_directory + "/build-output/";

    QString path_python = CS_GUI_GET_GLOBAL_SETTING("path.python");
    QString path_shorte = CS_GUI_GET_GLOBAL_SETTING("path.shorte");

    QString command = QString("\"%1\" \"%2\" -f \"%3\" -p \"%4\" -t \"%5\" -w \"%6\" -o \"%7\"").arg(path_python).arg(path_shorte).arg(path_input).arg(package).arg(theme).arg(working_directory).arg(output_directory);
    QProcess process(this);

    QStringList env = QProcess::systemEnvironment();
    env << "PYTHONHOME=" << CS_GUI_GET_GLOBAL_SETTING("env.pythonhome");
    env << "PYTHONPATH=" << CS_GUI_GET_GLOBAL_SETTING("env.pythonpath");
    process.setEnvironment(env);

    process.setProcessChannelMode(QProcess::MergedChannels);
    process.start(command);
    bool finished = process.waitForFinished();

    this->ui->m_log_window->appendHtml(command + "<br/>");

    if(!finished)
    {    
        QString output = convert_output_to_html(process.errorString());
        this->ui->m_log_window->appendHtml(output);
    }
    else
    {
        QString output = convert_output_to_html(process.readAll());
        this->ui->m_log_window->appendHtml(output);
    }
    process.close();

    WidgetEditor::open_in_file_browser(output_directory);

    tmp->close();

}

void MainWindow::on_m_button_clear_clicked()
{
    this->ui->m_log_window->clear();
}

void MainWindow::on_m_button_open_clicked()
{
    this->ui->widget->open_file();
    this->ui->m_working_directory->setText(this->ui->widget->directory_of());
}

void MainWindow::on_m_button_save_clicked()
{
    this->ui->widget->save_file();
}

#include "widgets/common/settings/dialogsettingsmanager.h"

void MainWindow::on_action_edit_settings()
{
    DialogSettingsManager dlg(this);
    QMap<QString,QString> settings;

    g_settings->get_globals(settings);
    dlg.set_keys("global", settings);
    dlg.set_database(g_settings);

    if(QDialog::Accepted == dlg.exec())
    {

    }
    else
    {

    }
}

void MainWindow::on_action_find(void)
{
    this->ui->widget->show_tools_panel(true);
}
