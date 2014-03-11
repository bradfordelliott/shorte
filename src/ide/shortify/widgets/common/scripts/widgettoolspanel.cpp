#include "widgettoolspanel.h"
#include "ui_widgettoolspanel.h"

WidgetToolsPanel::WidgetToolsPanel(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::WidgetToolsPanel)
{
    ui->setupUi(this);
}

WidgetToolsPanel::~WidgetToolsPanel()
{
    delete ui;
}

void WidgetToolsPanel::on_m_button_close_clicked()
{
    emit signal_close_panel();
}

void WidgetToolsPanel::add_page(const QString& label, QWidget* widget)
{
    int index = this->ui->m_pages->addWidget(widget);
    m_page_index[label] = index;
    this->ui->m_pages->setCurrentIndex(index);
}

void WidgetToolsPanel::set_page(const QString& label)
{
    if(m_page_index.contains(label))
    {
        this->ui->m_pages->setCurrentIndex(m_page_index[label]);
    }
}
