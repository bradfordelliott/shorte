#include "dialogsettingsmanager.h"
#include "ui_dialogsettingsmanager.h"

DialogSettingsManager::DialogSettingsManager(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DialogSettingsManager)
{
    ui->setupUi(this);
    this->ui->m_settings_general->setColumnWidth(0, 250);
    this->ui->m_settings_general->setColumnWidth(1, 250);
    this->ui->m_settings_lexer->setColumnWidth(0, 250);
    this->ui->m_settings_lexer->setColumnWidth(1, 250);
    this->ui->m_settings_theme->setColumnWidth(0, 250);
    this->ui->m_settings_theme->setColumnWidth(1, 250);
}

DialogSettingsManager::~DialogSettingsManager()
{
    delete ui;
}

#include "widgets/common/settings/settingsmanager.h"
void DialogSettingsManager::set_database(SettingsManager* db)
{
    m_db = db;
}

bool DialogSettingsManager::set_keys(const QString& group, QMap<QString,QString>& keys)
{
    m_keys[group] = keys;

    QMap<QString, QMap<QString,QString> >::iterator giter;
    QMap<QString,QString>::iterator iter;

    this->ui->m_settings_general->clear();
    this->ui->m_settings_lexer->clear();
    this->ui->m_settings_theme->clear();

    int row = 0;

    for(giter = m_keys.begin(); giter != m_keys.end(); giter++)
    {
        /*
        // Add the section header
        QTableWidgetItem* item = new QTableWidgetItem(giter.key());
        item->setBackgroundColor(QColor(0xc0, 0xc0, 0xc0));

        target->setRowCount(row+1);
        target->setItem(row,0, item);
        target->setSpan(row,0,1,2);
        row += 1;
        */

        for(iter = m_keys[giter.key()].begin(); iter != m_keys[giter.key()].end(); iter++)
        {
            QTableWidget* target = NULL;

            if(iter.key().contains("lexer"))
            {
                target = this->ui->m_settings_lexer;
                row = target->rowCount();
            }
            else if(iter.key().contains("theme"))
            {
                target = this->ui->m_settings_theme;
                row = target->rowCount();
            }
            else
            {
                target = this->ui->m_settings_general;
                row = target->rowCount();
            }

            target->setRowCount(row+1);
            QTableWidgetItem* item = new QTableWidgetItem(iter.key());
            target->setItem(row,0,item);

            item = new QTableWidgetItem(iter.value());
            target->setItem(row,1,item);

            row++;
        }
    }

    return true;
}

void DialogSettingsManager::on_button_cancel_clicked()
{
    reject();
}

void DialogSettingsManager::on_button_save_clicked()
{
    for(int row = 0; row < this->ui->m_settings_general->rowCount(); row++)
    {
        QString key = this->ui->m_settings_general->item(row, 0)->text();
        QString value = this->ui->m_settings_general->item(row, 1)->text();

        m_db->set(key,value);
    }

    for(int row = 0; row < this->ui->m_settings_lexer->rowCount(); row++)
    {
        QString key = this->ui->m_settings_lexer->item(row, 0)->text();
        QString value = this->ui->m_settings_lexer->item(row, 1)->text();

        m_db->set(key,value);
    }

    for(int row = 0; row < this->ui->m_settings_theme->rowCount(); row++)
    {
        QString key = this->ui->m_settings_theme->item(row, 0)->text();
        QString value = this->ui->m_settings_theme->item(row, 1)->text();

        m_db->set(key,value);
    }

    accept();
}
