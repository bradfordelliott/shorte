#include "widgetfindpanel.h"
#include "ui_widgetfindpanel.h"
#include <QMessageBox>

WidgetFindPanel::WidgetFindPanel(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::WidgetFindPanel)
{
    m_history_size = 10;
    ui->setupUi(this);
}

WidgetFindPanel::~WidgetFindPanel()
{
    delete ui;
}

void WidgetFindPanel::show_close_button(bool allow)
{
    this->ui->m_button_close->setVisible(allow);
}

void WidgetFindPanel::on_m_edit_find_returnPressed()
{
    on_m_button_find_clicked();
}

void WidgetFindPanel::on_m_button_find_clicked()
{
    QString current_text = this->ui->m_edit_find->text();
    emit signal_text_entered(current_text);
    add_to_history(current_text);
}

void WidgetFindPanel::on_activate(const QString& text)
{
    //QMessageBox::information(NULL, "current text", text);
    if(this->ui->m_edit_find->text().length() == 0)
    {
        if(text.length() == 0)
        {
            this->ui->m_edit_find->setText("Enter a string to find");
        }
        else
        {
            this->ui->m_edit_find->setText(text);
        }
    }
    this->ui->m_edit_find->setSelection(0, 1000);
    this->ui->m_edit_find->setFocus();
}



void WidgetFindPanel::on_m_button_close_clicked()
{
    emit signal_close_panel();
}

void WidgetFindPanel::add_to_history(const QString& item)
{
    bool found = false;
    int count = this->ui->m_combo_history->count();

    for(int i = 0; i < this->ui->m_combo_history->count(); i++)
    {
        if(this->ui->m_combo_history->itemText(i) == item)
        {
            this->ui->m_combo_history->setCurrentIndex(i);
            found = true;
        }
    }

    if(!found)
    {
        // If the list of entries gets too long then remove
        // an entry in order to keep the list manageable.
        if(count > (m_history_size-1))
        {
            this->ui->m_combo_history->removeItem(count-1);
        }

        this->ui->m_combo_history->insertItem(0, item);
        this->ui->m_combo_history->setCurrentIndex(0);
    }
}

void WidgetFindPanel::on_m_button_find_last_clicked()
{
    QString current_text = this->ui->m_edit_find->text();

    add_to_history(current_text);

    emit signal_find_last(current_text);
}

void WidgetFindPanel::on_m_combo_history_activated(const QString &arg1)
{
    this->ui->m_edit_find->setText(arg1);
}

void WidgetFindPanel::on_m_replace_clicked()
{
    QString search_text = this->ui->m_edit_find->text();
    QString replace_text = this->ui->m_edit_replace->text();
    bool replace_all = false;
    bool replace_forward = true;

    emit signal_replace(search_text, replace_text, replace_forward, replace_all);
}

void WidgetFindPanel::on_m_replace_all_clicked()
{
    QString search_text = this->ui->m_edit_find->text();
    QString replace_text = this->ui->m_edit_replace->text();
    bool replace_all = true;
    bool replace_forward = true;

    emit signal_replace(search_text, replace_text, replace_forward, replace_all);
}
