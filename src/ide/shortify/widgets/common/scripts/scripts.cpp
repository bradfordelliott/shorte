#include <QString>
#include <QFileDialog>
#include <QMessageBox>
#include <QTextStream>
#include <QSyntaxHighlighter>
#include <QFileInfo>
#include <QMap>
#include <QUrl>
#include <QProgressDialog>
#include <QDesktopServices>
#include <QClipboard>
#include <QMimeData>

#include "mainwindow.h"
#include "scripts.h"
#include "ui_scripts.h"

#include "cs_usb_driver.h"

#include "widgets/common/dialogs/dialogsendmessage.h"

#include "widgets/common/dialogs/scripts/dialogscriptslibrary.h"
#include "libraries/smtp/smtp.h"
#include "widgets/common/scripts/dialogrunadvanced.h"

#include "widgets/common/widgetplaintextwithdrag.h"
#include "widgets/common/scripts/scriptsyntaxhighlighter.h"

#include "widgets/common/scripts/widgeteditor.h"
#include "widgets/common/scripts/widgettoolspanel.h"
#include "widgets/common/find/widgetfindpanel.h"
#include "widgets/common/scripts/widgetgotopanel.h"


bool CS_GUI_API_GET_KEYWORDS(QMap<QString, QString>& keywords);

Scripts* glb_scripts = NULL;

Scripts::Scripts(
    e_cs_chip_id chip,
    QWidget *parent) :

    QWidget(parent),
    ui(new Ui::Scripts)
{
    glb_scripts = this;

    m_has_python_support = CS_GUI_GET_DEVICE_SETTING(chip, "scripts.python.allow").toInt();
    m_has_c_support = CS_GUI_GET_DEVICE_SETTING(chip, "scripts.c.allow").toInt();

    bool allow_send_script = CS_GUI_GET_GLOBAL_SETTING("permissions.allow_send_script").toInt();
    bool allow_scripts_library = CS_GUI_GET_GLOBAL_SETTING("permissions.allow_scripts_library").toInt();

    m_chip = chip;

    m_last_path = QApplication::applicationDirPath();

    ui->setupUi(this);

    ui->m_button_run_c->setEnabled(m_has_c_support);
    if(!m_has_c_support)
    {
        ui->m_button_run_c->setToolTip("C code execution disabled for this target");
    }

    ui->m_button_run_python->setEnabled(m_has_python_support);
    if(!m_has_python_support)
    {
        ui->m_button_run_python->setToolTip("Python execution disabled for this target");
    }

    if(!allow_scripts_library)
    {
        this->ui->m_button_scripts_library->hide();
    }

    ui->m_button_send->setVisible(allow_send_script);

    connect(this->ui->m_tools_panel,
            SIGNAL(signal_close_panel()),
            this,
            SLOT(on_find_close_panel()));

    m_widget_find = new WidgetFindPanel(this);
    m_widget_goto = new WidgetGotoPanel(this);

    // Use the close button from the tools panel instead of the find panel
    m_widget_find->show_close_button(false);

    this->ui->m_tools_panel->add_page("Find", m_widget_find);
    this->ui->m_tools_panel->add_page("Goto", m_widget_goto);

    CS_GUI_CHECK_CONNECT(connect(m_widget_find,
            SIGNAL(signal_text_entered(const QString&)),
            this,
            SLOT(on_find_text_entered(const QString&))));

    CS_GUI_CHECK_CONNECT(connect(m_widget_find,
            SIGNAL(signal_find_last(const QString&)),
            this,
            SLOT(on_find_last(const QString&))));

    CS_GUI_CHECK_CONNECT(connect(m_widget_goto,
            SIGNAL(signal_go_to_line(int,QString)),
            this,
            SLOT(on_goto_line(int,const QString))));

    bool result = connect(this->ui->m_editor,
            SIGNAL(signal_hotspot_activated(const QString&)),
            this,
            SLOT(on_open_link(const QString&)));
    if(!result)
    {
        QMessageBox::information(this, "Failed to connect hotspot indicator", "Failed to connect hotspot indicator");
    }

    m_dialog_scripts_library = NULL;
    m_run_advanced = NULL;

    // Initially hide the tools panel
    this->ui->m_tools_panel->setVisible(false);

    QMap<QString, QString> link_words;
    CS_GUI_API_GET_KEYWORDS(link_words);
    ui->m_editor->set_link_words(link_words);

    ui->m_editor->create_document(
        "No Name",
        "You can enter your script here or use the\n"
"\"Open\" button to load an existing script.\n"
"\n"
"The \"Load from Library\" button provides\n"
"access to a set of built-in scripts\n"
"for the target device.\n"
"\n"
"When you are done you can press the \"Run C\"\n"
"button to execute the cs4224_reg_set, cs4224_reg_get() script.\n"
"\n"
"Press <CTRL> + click to follow links.");

    int width = this->ui->widget_3->width();
    QList<int> sizes;
    sizes.append(width/2);
    sizes.append(width - (width/2));
    this->ui->splitter_2->setSizes(sizes);

    this->ui->toolButton->setVisible(false);

    // See if there are any templates for creating new scripts
    // for this ASIC.
    QString scripts = CS_GUI_GET_DEVICE_SETTING(CS_GUI_GET_ACTIVE_DEVICE(), "scripts.templates");
    QStringList script_list = scripts.split(";", QString::SkipEmptyParts);

    if(script_list.count() > 0)
    {
        QMenu* new_script_menu = new QMenu(this->ui->m_button_new_script);

        for(int s = 0; s < script_list.count(); s++)
        {
            QString info = script_list.at(s);
            QStringList parts = info.split("+");

            if(parts.count() == 3)
            {
                QString script_name = parts[0].trimmed();
                QString script_type = parts[1].trimmed();
                QString script_template = parts[2].trimmed();

                QString script_data = CS_GUI_GET_DEVICE_SETTING(CS_GUI_GET_ACTIVE_DEVICE(), script_template);

                QAction* action = new_script_menu->addAction(script_name);
                action->setProperty("template", script_data);
                action->setProperty("language", script_type);
            }
        }

        this->ui->m_button_new_script->setMenu(new_script_menu);

        connect(new_script_menu, SIGNAL(triggered(QAction*)),
            this,
            SLOT(on_new_script_action(QAction*)));
    }

    m_menu_archive_output = new QMenu(this);
    QAction* action = m_menu_archive_output->addAction("Save to File");
    action->setShortcut(QKeySequence("Ctrl+Shift+A"));
    action = m_menu_archive_output->addAction("Copy to clipboard");
    action->setShortcut(QKeySequence("Ctrl+Shift+C"));
    this->ui->m_button_save_log->setMenu(m_menu_archive_output);

    connect(m_menu_archive_output, SIGNAL(triggered(QAction*)),
            this,
            SLOT(on_archive_output_action(QAction*)));

    // By default hide the script command line widget
    this->ui->m_widget_script_command_line->setVisible(false);

    m_menu_run_advanced = new QMenu(this);
    m_menu_run_advanced->addAction("Run with Arguments");
    this->ui->m_button_run_advanced->setMenu(m_menu_run_advanced);
    connect(m_menu_run_advanced, SIGNAL(triggered(QAction*)),
            this,
            SLOT(on_compile_advanced(QAction*)));

    m_menu_compile_advanced = new QMenu(this);
    m_menu_compile_advanced->addAction("Run with Arguments");
    this->ui->m_button_compile_advanced->setMenu(m_menu_compile_advanced);

    connect(m_menu_compile_advanced, SIGNAL(triggered(QAction*)),
            this,
            SLOT(on_compile_advanced(QAction*)));

    // By default hide the shorte toolbar since it is an internal thing
    // for now.
    this->ui->widget_shorte->setVisible(false);
}

Scripts::~Scripts()
{
    this->blockSignals(true);

    delete m_menu_run_advanced;
    delete m_menu_archive_output;
    delete m_menu_compile_advanced;

    delete m_dialog_scripts_library;
    delete m_run_advanced;

    delete ui;
}

void Scripts::on_new_script_action(QAction* action)
{
    QString contents = action->property("template").toString();
    QString language = action->property("language").toString();

    if(language == "c")
    {
        this->ui->m_editor->create_document("No Name", contents, CS_SCRIPT_TYPE_C);
    }
    else
    {
        this->ui->m_editor->create_document("No Name", contents, CS_SCRIPT_TYPE_PYTHON);
    }
}

void Scripts::on_open_script(QString& path)
{
    load_script(path);
}


int EventLogCallbackType = 2000;

class EventLogCallback : public QEvent
{
public:
    EventLogCallback(
        const char* message): QEvent((QEvent::Type)EventLogCallbackType)
    {
        m_message = message;
    }
    EventLogCallback(const EventLogCallback& rhs) : QEvent((QEvent::Type)EventLogCallbackType)
    {
        m_message = rhs.m_message;
    }

    virtual ~EventLogCallback()
    {
    }

    QString m_message;
};


int logger(const char* message)
{
    EventLogCallback* evt = new EventLogCallback(message);
    QCoreApplication::postEvent((QObject*)glb_scripts, evt);
    QApplication::processEvents();

    return 0;
}


void Scripts::on_m_button_run_python_clicked()
{
    bool error_occurred = false;

    this->ui->m_editor->clear_selections();

    this->ui->m_output_stack->setCurrentIndex(0);

    this->ui->m_script_output->setStyleSheet("");

    //QString script = ui->m_script_input->toPlainText();
    QString script = this->ui->m_editor->get_text();

    // If the script starts with #!apish then translate it
    if(script.startsWith("#!apish"))
    {
        bool preview_only = false;
        if(script.startsWith("#!apish_preview"))
        {
            preview_only = true;
        }

        QString prefix = CS_GUI_GET_ACTIVE_DEVICE_SETTING("scripts.python.apish");

        script = prefix + script;

        script = script.replace("=>", "=");

        QRegExp exp("([0-9]*'b[01Xx ]+)");
        script = script.replace(exp, "\"\\1\"");

        if(preview_only)
        {
            this->ui->m_script_output->setPlainText(script);
            return;
        }
    }

    script = script.replace("//", "#");
    script = script.replace("VILLA_", "CS4224_");
    script = script.replace("K2_", "CS4224_");

    bool show_script = false;
    if("true" == CS_GUI_GET_GLOBAL_SETTING("scripts.python.show_script"))
    {
        show_script = true;
    }

    QProgressDialog progress("Running script", "", 0, 100, this);
    progress.setRange(0,0);
    progress.setWindowTitle("Running Python Script");
    progress.setWindowModality(Qt::WindowModal);
    //Qt::WindowFlags flags = progress.windowFlags();
    //flags &= ~Qt::WindowCloseButtonHint;
    progress.setModal(true);
    progress.setWindowFlags( ( (progress.windowFlags() | Qt::CustomizeWindowHint)
                       & ((~Qt::WindowCloseButtonHint) | Qt::Window)) );

    //progress.setValue(0);
    //progress.setMinimumDuration(5);
    progress.setCancelButton(NULL);
    progress.show();

    qApp->processEvents();

    try
    {
        QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
        CS_GUI_RECORD_EVENT_REFRESH_DISABLE();

        // Record the initial register access count in order
        // to track how many registers were accessed
        int initial_read_count = CS_GUI_GET_REG_READ_COUNT();
        int initial_write_count = CS_GUI_GET_REG_WRITE_COUNT();

        void* handle = NULL;
        cs_usb_script_open("support/drivers", 0, 0);
        cs_usb_set_log_callback(logger);
        QString scripts_path = CS_GUI_GET_DEVICE_SETTING(this->m_chip, "scripts.python.path");
        int result = 0;
        QString prefix;
        CS_GUI_LOAD_TEMPLATE(QString("%1/script_prefix.py").arg(scripts_path), prefix);

        QString paths_to_append = CS_GUI_GET_DEVICE_SETTING(this->m_chip, "scripts.python.append_to_path");

        prefix += paths_to_append;

        if(this->m_chip == CS_TARGET_T100)
        {
            QString xmlrpc_host = CS_GUI_GET_GLOBAL_SETTING("global.last_ip");

            prefix += QString("t100_util.connect('http://%1:8080')\n").arg(xmlrpc_host);

            script = QString("%1\n\n%2").arg(prefix).arg(script);
        }
        else
        {
            if(this->m_chip == CS_TARGET_LEEDS ||
               this->m_chip == CS_TARGET_LEEDSB)
            {
                script = script.replace("leeds", "cs4321");
                script = script.replace("LEEDS", "CS4321");
                script = script.replace("RETIMER", "LOCAL_TIMING");
                script = script.replace("RECLOCKER", "THROUGH_TIMING");
            }

            // Setup the scripts to talk to the local server
            if(CS_GUI_GET_TARGET_CONNECT_METHOD() != TARGET_CONNECT_VIA_USB_PROTOCOL)
            {
                int spy_port = CS_GUI_GET_GLOBAL_SETTING("global.listen_port").toInt();
                QString port_format = CS_GUI_GET_GLOBAL_SETTING("global.listen_port_format");
                if(port_format == "spy")
                {
                    port_format = "spy2";
                }

                prefix += QString(
                    "try:\n"
                    "    set_server('127.0.0.1', %1, protocol='%2')\n"
                    "except:\n"
                    "    set_server('127.0.0.1', %1)\n")
                    .arg(spy_port)
                    .arg(port_format);
            }

            script = QString("%1\n\n%2").arg(prefix).arg(script);
        }

        if(this->ui->m_clear_log->isChecked())
        {
            if(show_script)
            {
                ui->m_script_output->setPlainText(script);
            }
            else
            {
                ui->m_script_output->clear();
            }
        }
        else
        {
            if(show_script)
            {
                ui->m_script_output->appendPlainText(script);
            }
        }

        // Set any command line arguments associated with the script
        QString args = ui->m_script_command_line->text().toStdString().c_str();

        cs_usb_script_set_command_line_args(ui->m_script_command_line->text().toStdString().c_str());

        cs_usb_script_var_set("brad", "this");
        cs_usb_script_var_set("test", "is");
        cs_usb_script_var_set("blah", "pretty cool");

        // Figure out the length of the prefix
        int prefix_len = prefix.split("\n", QString::KeepEmptyParts).count();

        int rc = cs_usb_script_run(handle, script.toStdString().c_str(), &result);
        if(rc == 0)
        {
            this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
            error_occurred = true;

            // If a script error occurred attempt to highlight the
            // errored line.
            int lineno = cs_usb_script_results_error_line_number();

            // DEBUG BRAD: Need to highlight current line!!!
            this->ui->m_editor->highlight_line(lineno - prefix_len);
        }
        QApplication::processEvents();

        //const char* blah = cs_usb_script_var_get("blah");

        int length = 0;
        cs_usb_script_results_get_length(result, &length);
        char* buffer = new char[length];
        cs_usb_script_results_read(result, buffer, length);

        if(length > 0)
        {
            buffer[length-1]=0;
        }
        else
        {
            buffer[0] = 0;
        }

        //ui->m_script_output->appendPlainText(QString("blah = %1").arg(blah));
        ui->m_script_output->appendPlainText(QString(buffer));

        cs_usb_set_log_callback(NULL);

        QApplication::restoreOverrideCursor();
        CS_GUI_RECORD_EVENT_REFRESH_ENABLE();

        delete [] buffer;

        cs_usb_script_close();

        // Figure out how many registers were accessed
        // and display a summary of the register accesses.
        int new_read_count = CS_GUI_GET_REG_READ_COUNT();
        int new_write_count = CS_GUI_GET_REG_WRITE_COUNT();

        QString summary = QString(
            "Summary\n"
            "=======\n"
            " register reads = %1\n"
            " register writes = %2\n")
            .arg(new_read_count - initial_read_count)
            .arg(new_write_count - initial_write_count);
        this->ui->m_script_output->appendPlainText(summary);

        /* BUG #41934: There appears to be an issue with the scrollbar of
         * a QPlainTextEdit. This seems to clean it up. One of these calls
         * clears up the scroll bar being very slow but I'm not sure which
         * one */
        if(!error_occurred)
        {
            this->ui->m_script_output->setStyleSheet("");
        }
    }
    catch(std::exception& e)
    {
        ui->m_script_output->setPlainText(QString(e.what()));
    }
    catch(...)
    {
        ui->m_script_output->setPlainText(QString("Unknown error occurred"));
    }
}

void Scripts::on_m_button_clear_log_clicked()
{
    this->ui->m_output_html->setHtml("");
    ui->m_script_output->setPlainText(QString(""));
    this->ui->m_script_output->setStyleSheet("");
}

void Scripts::on_button_open_clicked()
{
    this->ui->m_editor->open_file();
}

void Scripts::create_document_in_tab(const QString& path, const QString& contents, e_cs_script_type type)
{
    this->ui->m_editor->create_document(path, contents, type);
}

bool Scripts::load_script(QString path)
{
    this->ui->m_editor->open_path(path);

    return true;
}

bool Scripts::is_script_open(const QString& path)
{
    return this->ui->m_editor->is_open(path);
}

void Scripts::on_m_button_scripts_library_clicked()
{
    static QString last_scripts_path;
    static QString last_examples_path;

    QString app_path = QApplication::applicationDirPath();

    QString scripts_path = CS_GUI_GET_ACTIVE_DEVICE_SETTING("scripts.python.examples");
    QString examples_path = CS_GUI_GET_ACTIVE_DEVICE_SETTING("scripts.c.examples");
    QFileInfo info(scripts_path);

    if(info.isRelative())
    {
        scripts_path = QString("%1/%2/").arg(app_path).arg(scripts_path);
    }
    QFileInfo exinfo(examples_path);
    if(exinfo.isRelative())
    {
        examples_path = QString("%1/%2/").arg(app_path).arg(examples_path);
    }

    if(m_dialog_scripts_library == NULL)
    {
        m_dialog_scripts_library = new DialogScriptsLibrary(
        scripts_path, examples_path,
        m_has_python_support,
        m_has_c_support,
        this);
    }

    if(scripts_path != last_scripts_path ||
       examples_path != last_examples_path)
    {
        //QMessageBox::information(this, "Got here!", scripts_path);

        // If the scripts directory changed from the previous
        // path then rescan the directory.
        m_dialog_scripts_library->rescan(scripts_path, examples_path);
    }

    last_scripts_path = scripts_path;
    last_examples_path = examples_path;

    if(QDialog::Accepted == m_dialog_scripts_library->exec())
    {
        QString path = m_dialog_scripts_library->get_script_path();

        if(path != QString::null)
        {
            QString script_path = path.trimmed();

            load_script(script_path);
        }
    }
}

bool Scripts::check_modified(int index)
{
    (void)index;
    return false;
}


void Scripts::on_m_button_refresh_clicked()
{
    this->ui->m_editor->reload();
}

void Scripts::on_m_button_save_script_clicked()
{
    this->ui->m_editor->save_file();
}

void Scripts::on_m_button_save_as_clicked()
{
    this->ui->m_editor->save_file_as();
}

bool Scripts::save_log(const QString& input_path)
{
    QString contents = ui->m_script_output->toPlainText();

    // Lookup the path of the last file that was saved
    QString last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
    if(last_saved.length() == 0)
    {
        last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
    }

    QString extension = "Log (*.txt)";
    if(this->ui->m_output_stack->currentIndex() == 1)
    {
        extension = "HTML (*.html)";
    }

    QString path = input_path;

    if(path == QString::null || path.length() == 0)
    {
        path = QFileDialog::getSaveFileName(
         this,
         "Save Script Output",
         last_saved,
         extension);
    }

    if(path == QString::null)
    {
        return false;
    }

    // Save the path of the new file
    CS_GUI_SET_GLOBAL_SETTING("path.last_saved", path);

    QFile file(path);
    if(!file.open(QIODevice::WriteOnly | QIODevice::Text))
    {
        QMessageBox::warning(this, "Failed Saving Log File",
            QString("Failed saving %1").arg(path));
        return false;
    }

    QTextStream output(&file);
    output << contents;
    output.flush();
    QTextStream::Status status = output.status();
    if(status != QTextStream::Ok)
    {
        QMessageBox::warning(this, "Failed Saving Log File",
            QString("Failed saving %1").arg(path));

    }

    file.close();

    return true;
}


void Scripts::on_m_button_save_log_clicked()
{
    save_log();
}



#include <QProcess>
#include <QTemporaryFile>
#include <QFileInfo>
#include <QDateTime>

void Scripts::on_m_button_run_c_clicked()
{
    bool error_occurred = false;

    this->ui->m_editor->clear_selections();

    bool show_script = false;

    this->ui->m_output_stack->setCurrentIndex(0);

    this->ui->m_script_output->setStyleSheet("");

    // Determine from the settings.db file whether we should echo
    // the actual C file back to screen. This is for debugging purposes
    if("true" == CS_GUI_GET_GLOBAL_SETTING("scripts.c.show_script"))
    {
        show_script = true;
    }

    // Record the initial register access count in order
    // to track how many registers were accessed
    int initial_read_count = CS_GUI_GET_REG_READ_COUNT();
    int initial_write_count = CS_GUI_GET_REG_WRITE_COUNT();

    QProgressDialog progress("Running C Script", "Abort", 0, 305, this);
    progress.setWindowTitle("Running C Script");
    progress.setWindowModality(Qt::WindowModal);
    progress.setModal(true);
    progress.setValue(0);
    progress.setMinimumDuration(100);

    qApp->processEvents();

    // This temporarily disables the event recorder while running
    // the script so that every register access doesn't referesh
    // the tree
    CS_GUI_RECORD_EVENT_REFRESH_DISABLE();

    // Change the cursor while we're running the script since I
    // can't practically do a scrollbar
    //QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));

    // Create a temporary .c file where the C code will get stored
    // so it can be executed by the compiler
    QTemporaryFile* tmp = new QTemporaryFile(QString("%1/XXXXXX.c").arg( QDir::tempPath()));

    // Create a temporary .exe file which will be executed to grab the output. Probably
    // don't need the .exe extension on Linux or MacOS
    QTemporaryFile* tmp_output = new QTemporaryFile(QString("%1/XXXXXX.exe").arg(QDir::tempPath()));
    tmp->open();
    tmp_output->open();
    QString path_input = tmp->fileName();
    QString path_output = tmp_output->fileName();
    tmp_output->close();
    delete tmp_output;

    if(this->ui->m_clear_log->isChecked())
    {
        ui->m_script_output->clear();
    }

    // Temporarily yield to the GUI to update the log window
    QApplication::processEvents();

    // Write the script input window to the temporary .c file
    // we created above.
    QTextStream stream(tmp);
    //stream << this->ui->m_script_input->toPlainText();
    stream << this->ui->m_editor->get_text();
    stream.flush();
    tmp->close();

    QString obj_path = CS_GUI_GET_ACTIVE_DEVICE_SETTING("scripts.c.driver_object_file");
    //QMessageBox::information(this, "Driver object 1", tmp2);
    QString app_path = QApplication::applicationDirPath();
    QString driver_object = QString(obj_path).arg(app_path);
    bool build_driver = false;

    //QMessageBox::information(this, "Driver object 2", driver_object.right(30));
    //driver_object += ".o";
    driver_object = QDir::toNativeSeparators(driver_object);
    driver_object = driver_object.replace("\"", "");

    //QMessageBox::information(this, "Driver object", driver_object.right(30));

    if(!QFile::exists(driver_object))
    {
        //QMessageBox::information(this,
        //    "Driver object not found",
        //    QString("Driver object %1 not found").arg(driver_object));

        build_driver = true;
    }
    else
    {
        QString driver_source = driver_object;
        driver_source.replace(".o", ".c");

        if(!QFile::exists(driver_source))
        {
            //QMessageBox::warning(this, "Driver source not found",
            //    QString("Driver source %1 not found").arg(driver_source));
            build_driver = true;
        }

        QFileInfo source_info(driver_source);
        QFileInfo object_info(driver_object);

        //QMessageBox::information(this,
        //    "Mod times",
        //    QString("source: %1/%2, object: %3/%4")
        //        .arg(driver_source)
        //        .arg(source_info.lastModified().toString())
        //        .arg(driver_object)
        //        .arg(object_info.lastModified().toString()));

        if(source_info.lastModified() > object_info.lastModified())
        {
            //QMessageBox::information(this, "Source file modified",
            //    "Re-building the driver");
            build_driver = true;
        }
    }

    if(build_driver)
    {
        // Load the C command used to build the driver from the settings.db file
        QString build_command = CS_GUI_GET_DEVICE_SETTING(this->m_chip, "scripts.c.build_driver");
        // Substitute the arguments into the build string so that the compiler
        // knows how to build the target.
        QString command = QString(build_command).arg(QApplication::applicationDirPath());

        if(show_script)
        {
            this->ui->m_script_output->appendPlainText(command);
        }

        // Start the compilation of the .c file and wait for
        // it to finish. Try to capture both standard error and standard
        // output.
        QProcess process(this);
        process.setProcessChannelMode(QProcess::MergedChannels);
        process.start(command);
        progress.setValue(1);
        bool finished = process.waitForFinished();

        // If an error occurred then report it in the output pane
        if(!finished)
        {
            this->ui->m_script_output->appendPlainText("Failed building\n");
            this->ui->m_script_output->appendPlainText(process.errorString());
            QApplication::processEvents();
        }
        else
        {
            this->ui->m_script_output->appendPlainText(process.readAll());
            QApplication::processEvents();
        }
        process.close();
    }
    progress.setValue(2);

    // Load the C command used to build the script from the settings.db file
    QString build_command = CS_GUI_GET_DEVICE_SETTING(this->m_chip, "scripts.c.build_command");

    // Substitute the arguments into the build string so that the compiler
    // knows how to build the target.
    QString command = QString(build_command).arg(QApplication::applicationDirPath()).arg(path_output).arg(path_input);

    // If debugging is enabled append the contents of the .c file to
    // the output window.
    if(show_script)
    {
        this->ui->m_script_output->appendPlainText(command);
        this->ui->m_script_output->appendPlainText("\n");
        QApplication::processEvents();
    }

    progress.setValue(3);

    // Start the compilation of the .c file and wait for
    // it to finish. Try to capture both standard error and standard
    // output.
    QProcess process(this);
    process.setProcessChannelMode(QProcess::MergedChannels);
    process.start(command);
    bool finished = process.waitForFinished();

    progress.setValue(4);

    // If an error occurred then report it in the output pane
    if(!finished)
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
        error_occurred = true;

        this->ui->m_script_output->appendPlainText("Failed building\n");
        this->ui->m_script_output->appendPlainText(process.errorString());
        QApplication::processEvents();
    }
    else
    {
        if(process.exitCode() != 0)
        {
            this->ui->m_script_output->setStyleSheet(
                    "QPlainTextEdit{border:5px solid red;}");
            error_occurred = true;
        }
        this->ui->m_script_output->appendPlainText(process.readAll());
        QApplication::processEvents();
    }
    process.close();



    // Start a second process once compilation has completed to run
    // the executable. This probably should only happen if the
    // compilation phase was successful.
    QProcess process2(this);
    process2.setProcessChannelMode(QProcess::MergedChannels);

    // For T100 we're connecting directly to the XML-RPC target
    // to read and write registers. This is the XML-RPC host that
    // we specified when first connecting to T100.
    if(this->m_chip == CS_TARGET_T100)
    {
        command = QString("\"%1\" %2 %3 %4")
            .arg(path_output)
            .arg(CS_GUI_GET_GLOBAL_SETTING("global.last_ip"))
            .arg(CS_GUI_GET_GLOBAL_SETTING("global.last_port"))
            .arg(ui->m_script_command_line->text());
    }
    // For everything else connect back to the GUI to
    // read and write registers.
    else
    {
        command = QString("\"%1\" %2 %3 \"%4\" %5")
            .arg(path_output)
            .arg("127.0.0.1")
            .arg(CS_GUI_GET_GLOBAL_SETTING("global.listen_port"))
            .arg(CS_GUI_GET_GLOBAL_SETTING("global.listen_port_format"))
            .arg(ui->m_script_command_line->text());
    }

    // Debugging information
    if(show_script)
    {
        this->ui->m_script_output->appendPlainText(QString("Executing %1\n").arg(command));
        QApplication::processEvents();
    }

    // Start the execution of the process
    process2.start(command, QIODevice::ReadOnly);

    // Wait iteratively for the executable to finish running
    // and periodically yield to the GUI to get it to refresh.
    int iterations = 0;
    finished = FALSE;
    //process2.waitForStarted(3000);
    while(!finished && iterations < 3000)
    {
        if(progress.wasCanceled())
        {
            process2.kill();
            break;
        }

        progress.setValue(iterations+5);

        if(process.waitForReadyRead())
        {
            iterations = 0;
        }

        QProcess::ProcessState curr_state = process2.state();

        if((curr_state != QProcess::Running) && (curr_state != QProcess::Starting))
        {
            finished = true;//process2.waitForFinished();
        }
        else
        {
            cs_usb_usleep(1000*1000);
        }

        QString tmp = process2.readAll();
        if(tmp.length() != 0)
        {
            this->ui->m_script_output->appendPlainText(tmp);
            tmp = this->ui->m_script_output->toPlainText();
            if(tmp.startsWith("<html>"))
            {
                this->ui->m_output_html->setHtml(tmp);
                this->ui->m_output_stack->setCurrentIndex(1);
            }
        }

        QApplication::processEvents();
        iterations++; 
    }

    // If there were any errors then report them.
    if(!finished)
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
        error_occurred = true;

        this->ui->m_script_output->appendPlainText("Failed executing output!!!\n");
        this->ui->m_script_output->appendPlainText(process2.errorString());
        QApplication::processEvents();
    }
    else
    {
        this->ui->m_script_output->appendPlainText("Finished Execution\n");
        this->ui->m_script_output->appendPlainText(process2.readAll());
        QApplication::processEvents();
    }

    bool crashed = false;

    // Check for crashes when running the executable
    if(process2.exitStatus() != QProcess::NormalExit)
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
        error_occurred = true;

        this->ui->m_script_output->appendPlainText(process.readAllStandardError());
        this->ui->m_script_output->appendPlainText(process2.errorString());
        this->ui->m_script_output->appendPlainText("ERROR: Process looks like it crashed\n");
        crashed = true;
    }

    if(0 != process2.exitCode())
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
        error_occurred = true;
    }

    process2.close();

    bool remove_temporaries = true;

    if(crashed == true || finished == false)
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
        error_occurred = true;

        if(QMessageBox::Yes == QMessageBox::question(this,
            "Process crashed",
            "Do you want to keep the output file?",
            QMessageBox::Yes,
            QMessageBox::No))
        {
            QFileInfo info(path_input);
            QString path = info.dir().path();
            QMessageBox::information(this, "Opening URL", path_input);

            QDesktopServices::openUrl(QUrl("file:///" + path));
            remove_temporaries = false;
            tmp->setAutoRemove(false);
        }
    }


    // Remove the temporary .c and .exe files after we're done
    // with them. Otherwise the temporary directory will get cluttered.
    if(remove_temporaries)
    {
        QFile::remove(path_input);
        QFile::remove(path_output);
    }

    delete tmp;

    progress.setValue(305);

    // Restore the cursor now that we're done.
    //QApplication::restoreOverrideCursor();

    // Re-enable the event recorder refresh operation to re-render
    // the output every register access.
    CS_GUI_RECORD_EVENT_REFRESH_ENABLE();

    // Figure out how many registers were accessed
    // and display a summary of the register accesses.
    int new_read_count = CS_GUI_GET_REG_READ_COUNT();
    int new_write_count = CS_GUI_GET_REG_WRITE_COUNT();

    QString summary = QString(
        "Summary\n"
        "=======\n"
        " register reads = %1\n"
        " register writes = %2\n")
        .arg(new_read_count - initial_read_count)
        .arg(new_write_count - initial_write_count);
    this->ui->m_script_output->appendPlainText(summary);

    /* BUG #41934: There appears to be an issue with the scrollbar of
     * a QPlainTextEdit. This seems to clean it up. One of these calls
     * clears up the scroll bar being very slow but I'm not sure which
     * one */
    if(!error_occurred)
    {
        this->ui->m_script_output->setStyleSheet("");
    }
    else
    {
        this->ui->m_script_output->setStyleSheet(
                "QPlainTextEdit{border:5px solid red;}");
    }
}

void Scripts::on_m_button_send_clicked()
{
    QString to("brad.elliott@cortina-systems.com");
    QString from("brad.elliott@cortina-systems.com");

    DialogSendMessage* dlg = new DialogSendMessage(
        this,
        QString("Send Script"),
        QString("GUI Script"),
        from,
        to);

    if(QDialog::Accepted == dlg->exec())
    {
        QString message = "<pre>";
        message += dlg->get_message();
        message += "</pre>";

        QString server = CS_GUI_GET_GLOBAL_SETTING("smtp-server");
        QString user = ""; //your SMTP username
        QString pass = ""; //your SMTP password

        QStringList to_list;
        to_list = to.split(";");

        // DEBUG BRAD: Really need to handle the deletion
        //             of this object once it finishes. Otherwise
        //             it will be left around forever.
        /*Smtp *newMail  = */new Smtp(
            server, user, pass,
            from,
            to_list,
            QString("Script"),
            message,
            //this->ui->m_script_input->toPlainText(),
            this->ui->m_editor->get_text(),
            this->ui->m_script_output->toPlainText());
    }
}

void Scripts::on_m_button_new_script_clicked()
{
    this->ui->m_editor->create_document("No Name", "");
}

bool Scripts::add_script_text(const QString& lines, bool create_new, int run_format)
{
    if(lines.count() == 0)
    {
        return false;
    }

    //this->ui->m_script_input->appendPlainText(line);
    // If we're creating a new script or if there is currently no script
    // open then create a new one.
    if(create_new || (this->ui->m_editor->count() == 0))
    {
        on_m_button_new_script_clicked();
    }

    if(lines.at(0) != '\n')
    {
        this->ui->m_editor->append_text("\n");
    }

    this->ui->m_editor->append_text(lines);;

    if(run_format == CS_GUI_SCRIPT_RUN_PYTHON)
    {
        this->ui->m_editor->set_lexer(2);
        on_m_button_run_python_clicked();
    }
    else if(run_format == CS_GUI_SCRIPT_RUN_C)
    {
        this->ui->m_editor->set_lexer(3);
        on_m_button_run_c_clicked();
    }

    return true;
}

void Scripts::on_m_button_clear_clicked()
{
    this->ui->m_editor->clear();
}

void Scripts::on_m_button_undo_clicked()
{
    this->ui->m_editor->undo();
}

void Scripts::on_m_script_input_highlighted(const QUrl &arg1)
{
    QMessageBox::information(this, "URL", arg1.toString());
}

void Scripts::on_m_script_input_cursorPositionChanged()
{
    //current_doc()->cursorChanged();
}

void CS_GUI_API_LOAD(const QString&);

void Scripts::on_open_link(const QString& link)
{
    QString category = this->ui->m_editor->get_link_category(link);

    CS_GUI_API_LOAD(category);
}

void Scripts::on_find_activate(const QString& current_text)
{
    this->ui->m_tools_panel->setVisible(true);
    this->ui->m_tools_panel->set_page("Find");
    m_widget_find->on_activate(current_text);
}

void Scripts::on_find_text_entered(const QString& key)
{
    this->ui->m_editor->find_text(key);
}

void Scripts::on_find_last(const QString& key)
{
    this->ui->m_editor->find_text(key, -1, false);
}

void Scripts::on_find_close_panel()
{
    this->ui->m_tools_panel->setVisible(false);
}

void Scripts::on_goto_line(int line, const QString& path)
{
    if(path.length() > 0)
    {
        this->ui->m_editor->open_path(path);
    }

    this->ui->m_editor->highlight_line(line);
}


bool Scripts::event(QEvent * event )
{
    if(event->type() == (QEvent::Type)EventLogCallbackType)
    {
        EventLogCallback* evt = static_cast<EventLogCallback*>(event);
        if(evt->m_message.length() > 0)
        {
            this->ui->m_script_output->moveCursor(QTextCursor::End);
            this->ui->m_script_output->insertPlainText(evt->m_message);

            QString tmp = this->ui->m_script_output->toPlainText();
            if(tmp.startsWith("<html>"))
            {
                this->ui->m_output_stack->setCurrentIndex(1);
                this->ui->m_output_html->setHtml(tmp);
            }
        }
        return true;
    }

    return QWidget::event(event);
}

int Scripts::current_doc()
{
    if(this->ui->m_editor->count() > 0)
    {
        return this->ui->m_editor->current_index();
    }

    // If no doc was open then create a new one
    return this->ui->m_editor->create_document("No Name");
}

QString Scripts::current_doc_title(void)
{
    return this->ui->m_editor->doc_title();
}

void Scripts::on_m_tab_scripts_tabCloseRequested(int index)
{
    (void)index;
}

void Scripts::close_tab(const QString& path)
{
    this->ui->m_editor->close_document(path);
}

void Scripts::on_current_doc_changed(void)
{
}

void Scripts::current_doc_mark_modified(bool is_modified)
{
    (void)is_modified;
}

void Scripts::doc_mark_modified(int index, bool is_modified)
{
    (void)index;
    (void)is_modified;
}

void Scripts::on_toolButton_clicked()
{
    this->ui->m_output_stack->setCurrentIndex(1);
    this->ui->m_output_stack->setContentsMargins(0,0,0,0);

    this->ui->m_output_html->setHtml(
"<html>"
"<head>"
"<style>"
"body{font-family:\"Times New Roman\";}"
"</style>"
"</head>"
"<body><h1>This is a test</h1><p>Blah blah blah</p></body></html>");
}


void Scripts::on_m_button_find_clicked()
{
    on_find_activate("Enter text to find");
}

#include <QTemporaryFile>
#include <QFileInfo>

void Scripts::on_pushButton_clicked()
{
    this->ui->m_script_output->clear();
    this->ui->m_output_stack->setCurrentIndex(0);
    this->ui->m_page_slider->setSliderPosition(0);

    QByteArray bytes = this->ui->m_editor->get_range();

    QTemporaryFile tmp;
    tmp.open();
    tmp.write(bytes);
    tmp.flush();
    tmp.fileName();
    QString path = tmp.fileName();
    QFileInfo info(path);
    QString output_path = this->ui->m_edit_shorte_output_path->text();
    output_path = output_path.replace("\\", "/");

    QString shorte_path = QApplication::applicationDirPath() + "/support/shorte/shorte.exe";

    QProcess process(this);
    process.setProcessChannelMode(QProcess::MergedChannels);
    //QString command = QString("\"C:\\usr\\tools\\python\\python.exe\" \"C:\\Users\\belliott\\Documents\\GitHub\\shorte\\src\\shorte.py\" -f \"%1\" -o \"%2\" -p html_inline").arg(tmp.fileName()).arg(output_path);
    QString command = QString(this->ui->m_edit_shorte_cmdline->text())
        .arg(shorte_path)
        .arg(tmp.fileName())
        .arg(output_path);

    process.start(command);
    bool finished = process.waitForFinished();

    // If an error occurred then report it in the output pane
    if(!finished)
    {
        this->ui->m_script_output->appendPlainText("Failed building\n");
        this->ui->m_script_output->appendPlainText(process.errorString());
        QApplication::processEvents();
    }
    else
    {
        this->ui->m_script_output->appendPlainText(bytes);
        this->ui->m_script_output->appendPlainText(process.readAll());
        QApplication::processEvents();
    }
    process.close();

    if(finished)
    {
        QFile file(output_path + "\\index.html");
        file.open(QIODevice::ReadOnly);
        QByteArray contents = file.readAll();
        file.close();

        this->ui->m_output_html->setHtml(contents);
        this->ui->m_output_stack->setCurrentIndex(1);
        this->ui->m_page_slider->setSliderPosition(1);
    }
}

void Scripts::on_m_page_slider_valueChanged(int value)
{
    this->ui->m_output_stack->setCurrentIndex(value);
}

#include <QWebFrame>
void Scripts::on_archive_output_action(QAction* action)
{
   if(action->text() == "Save to File")
   {
       on_m_button_save_log_clicked();
   }
   else
   {
       QClipboard* clip = QApplication::clipboard();

       if(this->ui->m_output_stack->currentIndex() == 1)
       {
           QMimeData* data = new QMimeData();
           QString html = this->ui->m_output_html->page()->currentFrame()->toHtml();
           data->setHtml(html); //this->ui->m_script_output->toPlainText());
           clip->setMimeData(data);
       }
       else
       {
           clip->setText(this->ui->m_script_output->toPlainText());
       }
   }
}

void Scripts::on_spacer_clicked()
{
    if(CS_GUI_GET_GLOBAL_SETTING("permissions.allow_lab_features").toInt())
    {
        this->ui->widget_shorte->setVisible(!this->ui->widget_shorte->isVisible());
    }
}

void Scripts::on_comboBox_activated(const QString &arg1)
{
    (void)arg1;
}

void Scripts::on_m_combo_shorte_templates_activated(const QString &arg1)
{
    QString text;

    if(arg1 == "Document Header")
    {
        text =
"@doctitle My Document\n"
"@docsubtitle My Document Subtitle\n"
"@docnumber N/A\n"
"@docversion 1.0\n"
"@docrevisions\n"
"- Revision | Date | Description\n"
"- 1.0      | ---  | Initial draft\n\n"
"@body\n\n";
    }
    else if(arg1 == "Heading 1")
    {
        text = "@h1 My Heading 1\n\n";
    }
    else if(arg1 == "Heading 2")
    {
        text = "@h2 My Heading 2\n\n";
    }
    else if(arg1 == "Heading 3")
    {
        text = "@h3 My Heading 3\n\n";
    }
    else if(arg1 == "Table")
    {
        text =
"@table\n"
"- Heading 1 | Heading 2 | Heading 3\n"
"- Cell 1    | Cell 2    | Cell 3\n\n";
    }
    else if(arg1 == "Paragraph")
    {
        text =
"@text\n"
"This is some text here\n\n";
    }
    else if(arg1 == "C Code")
    {
        text =
"@c\n"
"printf(\"Hello world!\")\n";
    }

    this->ui->m_editor->append_text(text);
}


void Scripts::on_run_advanced(QAction* action)
{
    if(action->text() == "Run with Arguments")
    {
        this->ui->m_script_command_line->setText("--help");
        on_m_button_run_python_clicked();
    }
}

bool Scripts::save_registers(const QString& input_path)
{
    cs_device_interface* dev = CS_GUI_GET_DEVICE_INTERFACE();
    int total = dev->get_num_slices() * dev->get_num_registers();

    QProgressDialog progress("Exporting registers", "Abort", 0, total, this);
    progress.setWindowTitle("Exporting Registers");
    progress.setWindowModality(Qt::WindowModal);
    progress.setValue(0);
    progress.setModal(true);

    bool verbose = false;
    int slice=-1;
    dev->export_registers(input_path, &progress, verbose, slice);

    progress.setValue(total);

    return true;
}

#include <widgets/common/scripts/dialogrunadvanced.h>

void Scripts::on_compile_advanced(QAction* action)
{
    if(action->text() == "Run with Arguments")
    {
        this->ui->m_script_command_line->setText("--help");

        if(m_run_advanced == NULL)
        {
            m_run_advanced = new DialogRunAdvanced(this);
        }

        bool m_command_line_was_visible = this->ui->m_script_command_line->isVisible();

        if(QDialog::Accepted == m_run_advanced->exec())
        {
            int count = m_run_advanced->count();
            for(int i = 0; i < count; i++)
            {
                QString path_script;
                QString args;
                QString path_output;
                QString path_registers;

                if(m_run_advanced->get(i, path_script, args, path_output, path_registers))
                {
                    QFileInfo info(path_script);

                    if(info.exists())
                    {
                        bool script_was_opened = is_script_open(path_script);

                        load_script(path_script);

                        if(args.length() > 0)
                        {
                            this->ui->m_widget_script_command_line->setVisible(true);
                            this->ui->m_script_command_line->setText(args);
                        }

                        if(info.suffix() == "c")
                        {
                            on_m_button_run_c_clicked();
                        }
                        else
                        {
                            on_m_button_run_python_clicked();
                        }

                        if(path_output.length() > 0)
                        {
                            save_log(path_output);
                        }

                        if(path_registers.length() > 0)
                        {
                            save_registers(path_registers);
                        }

                        // Close the script if the user specified and it wasn't
                        // already opened.
                        if(m_run_advanced->close_when_finished() && !script_was_opened)
                        {
                            close_tab(path_script);
                        }
                    }
                }
            }

            if(m_command_line_was_visible)
            {
                this->ui->m_widget_script_command_line->setVisible(true);
            }
            else
            {
                this->ui->m_widget_script_command_line->setVisible(false);
            }
        }
    }
}

void Scripts::on_m_button_goto_clicked()
{
    this->ui->m_tools_panel->setVisible(true);
    this->ui->m_tools_panel->set_page("Goto");
}
