#include "widgetgotopanel.h"
#include "ui_widgetgotopanel.h"

WidgetGotoPanel::WidgetGotoPanel(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::WidgetGotoPanel)
{
    ui->setupUi(this);
}

WidgetGotoPanel::~WidgetGotoPanel()
{
    delete ui;
}

void WidgetGotoPanel::on_m_button_go_to_clicked()
{
    emit signal_go_to_line(this->ui->m_edit_line_number->text().toInt(), "");
}
