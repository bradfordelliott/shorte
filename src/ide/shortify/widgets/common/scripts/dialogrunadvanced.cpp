#include "dialogrunadvanced.h"
#include "ui_dialogrunadvanced.h"
#include <QFileDialog>
#include <QMessageBox>
#include <QTextStream>

QString CS_GUI_GET_GLOBAL_SETTING(const QString& name);
void CS_GUI_SET_GLOBAL_SETTING(const QString& name, const QString& data);


DialogRunAdvanced::DialogRunAdvanced(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DialogRunAdvanced)
{
    ui->setupUi(this);
    ui->m_tree_script_list->header()->resizeSection(0, 200);
    ui->m_tree_script_list->header()->resizeSection(0, 150);

    // Initially the save suite should be disabled since
    // there are no scripts loaded.
    this->ui->m_button_save_suite->setDisabled(true);

    on_m_tree_script_list_itemSelectionChanged();
}

DialogRunAdvanced::~DialogRunAdvanced()
{
    delete ui;
}

void DialogRunAdvanced::on_m_button_add_script_clicked()
{
    QStringList script;

     // Lookup the path of the last file that was saved
    QString last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");

    // Lookup the path of the last file that was saved
    QString path = QFileDialog::getOpenFileName(
                this,
                QString("Open Script"),
                last_opened,
                QString("Scripts (*.py *.txt *.c)"));

    if(path != QString::null)
    {
        CS_GUI_SET_GLOBAL_SETTING("path.last_opened", path);
        QFileInfo info(path);
        script.append(info.fileName());
        QTreeWidgetItem* item = new QTreeWidgetItem(script);
        ui->m_tree_script_list->addTopLevelItem(item);
        item->setData(0, Qt::UserRole, path);
        item->setToolTip(0, path);

        this->ui->m_button_save_suite->setDisabled(false);
    }
}


void DialogRunAdvanced::on_m_button_move_up_clicked()
{
    QList<QTreeWidgetItem*> list = ui->m_tree_script_list->selectedItems();

    if(list.count() > 0)
    {
        QTreeWidgetItem* item = list.at(0);
        int index = ui->m_tree_script_list->indexOfTopLevelItem(item);

        if(index > 0)
        {
            ui->m_tree_script_list->takeTopLevelItem(index);
            ui->m_tree_script_list->insertTopLevelItem(index-1, item);
            ui->m_tree_script_list->setCurrentItem(item);
        }
        // Move to end
        else
        {
            ui->m_tree_script_list->takeTopLevelItem(index);
            ui->m_tree_script_list->addTopLevelItem(item);
            ui->m_tree_script_list->setCurrentItem(item);
        }
        //emit signal_move_favorite(item->text(0), CS_FAVORITE_MOVE_UP);
    }
}

void DialogRunAdvanced::on_m_button_move_down_clicked()
{
    QList<QTreeWidgetItem*> list = ui->m_tree_script_list->selectedItems();

    if(list.count() > 0)
    {
        QTreeWidgetItem* item = list.at(0);
        int index = ui->m_tree_script_list->indexOfTopLevelItem(item);
        if(index < (ui->m_tree_script_list->topLevelItemCount()-1))
        {
            ui->m_tree_script_list->takeTopLevelItem(index);
            ui->m_tree_script_list->insertTopLevelItem(index+1, item);
            ui->m_tree_script_list->setCurrentItem(item);
        }
        else
        {
            ui->m_tree_script_list->takeTopLevelItem(index);
            ui->m_tree_script_list->insertTopLevelItem(0, item);
            ui->m_tree_script_list->setCurrentItem(item);
        }

        //emit signal_move_favorite(item->text(0), CS_FAVORITE_MOVE_DOWN);
    }

}

void DialogRunAdvanced::on_m_button_cancel_clicked()
{
    reject();
}

void DialogRunAdvanced::on_m_button_run_clicked()
{
    accept();
}

#include <QInputDialog>
void DialogRunAdvanced::on_m_tree_script_list_itemActivated(QTreeWidgetItem *item, int column)
{
    QString text = item->text(column);

    // The script name
    if(column == 0)
    {
        QString last_opened = text;
        if(last_opened.length() == 0)
        {
            last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
        }

        // Lookup the path of the last file that was saved
        text = QFileDialog::getOpenFileName(
                this,
                QString("Open Script"),
                last_opened,
                QString("Scripts (*.py *.txt *.c)"));

        if(text != QString::null)
        {
            QFileInfo info(text);
            item->setData(column, Qt::UserRole, text);
            item->setText(column, info.fileName());
            item->setToolTip(column, text);
            CS_GUI_SET_GLOBAL_SETTING("path.last_opened", text);
            return;
        }
    }
    // The script arguments
    else if(column == 1)
    {
        text = QInputDialog::getText(this,
            "Script Arguments",
            "Enter Script Arguments",
            QLineEdit::Normal,
            text);
        if(text != QString::null)
        {
            item->setText(column, text);
        }
    }
    // The output log file
    else if(column == 2)
    {
        QString last_saved = text;
        if(last_saved.length() == 0)
        {
            last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
        }

        // Lookup the path of the last file that was saved
        text = QFileDialog::getSaveFileName(
                this,
                QString("Save Output"),
                last_saved,
                QString("Script Log (*.txt)"));

        if(text != QString::null)
        {
            QFileInfo info(text);
            item->setData(column, Qt::UserRole, text);
            item->setText(column, info.fileName());
            item->setToolTip(column, text);
            CS_GUI_SET_GLOBAL_SETTING("path.last_saved", text);
            return;
        }
    }
    // The output register dump file
    else if(column == 3)
    {
        QString last_saved = text;
        if(last_saved.length() == 0)
        {
            last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
        }

        // Lookup the path of the last file that was saved
        text = QFileDialog::getSaveFileName(
                this,
                QString("Save Registers"),
                last_saved,
                QString("Register Dump (*.txt)"));

        if(text != QString::null)
        {
            QFileInfo info(text);
            item->setData(column, Qt::UserRole, text);
            item->setText(column, info.fileName());
            item->setToolTip(column, text);
            CS_GUI_SET_GLOBAL_SETTING("path.last_saved", text);
            return;
        }
    }
}


int DialogRunAdvanced::count()
{
    return this->ui->m_tree_script_list->topLevelItemCount();
}

bool DialogRunAdvanced::get(
    int      index,
    QString& path_script,
    QString& args,
    QString& path_output,
    QString& path_registers)
{
    int count = this->ui->m_tree_script_list->topLevelItemCount();

    if(index < count)
    {
        QTreeWidgetItem* item = this->ui->m_tree_script_list->topLevelItem(index);
        path_script = item->data(0, Qt::UserRole).toString();
        args = item->text(1);
        path_output = item->data(2, Qt::UserRole).toString();
        path_registers = item->data(3, Qt::UserRole).toString();

        return true;
    }

    return false;
}

void DialogRunAdvanced::on_m_tree_script_list_itemSelectionChanged()
{
    int count = this->ui->m_tree_script_list->topLevelItemCount();

    if(count == 0)
    {
        this->ui->m_button_move_down->setDisabled(true);
        this->ui->m_button_move_up->setDisabled(true);
        this->ui->m_button_remove_script->setDisabled(true);
    }
    else
    {
        // Only enable the move buttons if there is more than
        // one script.
        if(count > 1)
        {
            this->ui->m_button_move_down->setDisabled(false);
            this->ui->m_button_move_up->setDisabled(false);
        }
        this->ui->m_button_remove_script->setDisabled(false);
    }
}

void DialogRunAdvanced::on_m_button_remove_script_clicked()
{
    QList<QTreeWidgetItem*> list = ui->m_tree_script_list->selectedItems();

    for (int i = 0; i < list.size(); ++i)
    {
        QTreeWidgetItem* item = list.at(i);

        if(item->childCount() == 0)
        {
            int i = ui->m_tree_script_list->indexOfTopLevelItem(item);
            ui->m_tree_script_list->takeTopLevelItem(i);

            delete item;

            on_m_tree_script_list_itemSelectionChanged();
        }
    }

    if(this->ui->m_tree_script_list->topLevelItemCount() == 0)
    {
        this->ui->m_button_save_suite->setDisabled(true);
    }
}

void DialogRunAdvanced::on_m_button_save_suite_clicked()
{
    // Save a suite of tests for later execution
    QString contents;
    int count = this->ui->m_tree_script_list->topLevelItemCount();

    for(int i = 0; i < count; i++)
    {
        QTreeWidgetItem* item = this->ui->m_tree_script_list->topLevelItem(i);
        QString path_script = item->data(0, Qt::UserRole).toString();
        QString args = item->text(1);
        QString path_output = item->data(2, Qt::UserRole).toString();
        QString path_registers = item->data(3, Qt::UserRole).toString();

        contents += QString("%1,%2,%3,%4\n").arg(path_script).arg(args).arg(path_output).arg(path_registers);
    }

    QString last_saved = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");

    QString path = QFileDialog::getSaveFileName(
                this,
                QString("Save Script Suite"),
                last_saved,
                QString("Script Suite (*.txt)"));

    if(path != QString::null)
    {
        CS_GUI_SET_GLOBAL_SETTING("path.last_saved", path);

        QFile file(path);
        if(!file.open(QIODevice::WriteOnly | QIODevice::Text))
        {
            QMessageBox::warning(this, "Failed Saving Script Suite",
            QString("Failed saving %1").arg(path));
            return;
        }
        QTextStream output(&file);
        output << contents;
    }
}

void DialogRunAdvanced::on_m_button_load_suite_clicked()
{
    // Load a previously saved suite of tests
    QString last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_opened");
    if(last_opened.length() == 0)
    {
        last_opened = CS_GUI_GET_GLOBAL_SETTING("path.last_saved");
    }

    // Lookup the path of the last file that was saved
    QString path = QFileDialog::getOpenFileName(
                this,
                QString("Open Script Suite"),
                last_opened,
                QString("Script Suite (*.txt)"));

    if(path != QString::null)
    {
        CS_GUI_SET_GLOBAL_SETTING("path.last_opened", path);

        QFile script(path);
        if(!script.open(QIODevice::ReadOnly))
        {
            QMessageBox::warning(this, "File Open Failure",
                QString("Failed opening %1").arg(path));
            return;
        }

        QTextStream input(&script);
        QString contents = input.readAll();
        QTextStream::Status status = input.status();
        if(status != QTextStream::Ok)
        {
            QMessageBox::warning(this, "Failed Loading Script Suite",
                QString("Failed loading %1").arg(path));
            return;
        }

        QStringList lines = contents.split("\n");
        this->ui->m_tree_script_list->clear();

        for(int i = 0; i < lines.count(); i++)
        {
            QStringList parts = lines[i].split(",");

            if(parts.count() != 4)
            {
                continue;
            }
            QString script_path   = parts[0];
            QString script_args   = parts[1];
            QString script_output = parts[2];
            QString script_regs   = parts[3];

            QFileInfo info(script_path);


            QStringList items;
            items.append(info.fileName());

            items.append(script_args);

            info.setFile(script_output);
            items.append(info.fileName());

            info.setFile(script_regs);
            items.append(info.fileName());

            QTreeWidgetItem* item = new QTreeWidgetItem(items);
            item->setData(0, Qt::UserRole, script_path);
            item->setData(2, Qt::UserRole, script_output);
            item->setData(3, Qt::UserRole, script_regs);

            this->ui->m_tree_script_list->addTopLevelItem(item);

            // Re-enable the save button in the event it was previously
            // disabled.
            this->ui->m_button_save_suite->setDisabled(false);
        }
    }
}

bool DialogRunAdvanced::close_when_finished()
{
    return this->ui->m_check_close_scripts_on_exit->isChecked();
}

bool DialogRunAdvanced::halt_on_error()
{
    return false;
}
