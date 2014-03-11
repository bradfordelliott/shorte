#include "widgetscriptlibrary.h"
#include "ui_widgetscriptlibrary.h"

WidgetScriptLibrary::WidgetScriptLibrary(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::WidgetScriptLibrary)
{
    ui->setupUi(this);
}

WidgetScriptLibrary::~WidgetScriptLibrary()
{
    delete ui;
}
